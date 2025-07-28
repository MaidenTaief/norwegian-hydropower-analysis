#!/usr/bin/env python3
"""
Import Existing NVE Dam Data
===========================

This script imports your existing Norwegian dam data from NVE shapefiles
into the monitoring database. It preserves all existing analysis while
adding real-time monitoring capabilities.

Usage:
    python import_existing_data.py --data-dir Data/
"""

import asyncio
import asyncpg
import geopandas as gpd
import pandas as pd
import argparse
import logging
from pathlib import Path
from datetime import datetime
import json
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class NVEDataImporter:
    """Import NVE shapefile data into monitoring database."""
    
    def __init__(self, data_dir: str):
        self.data_dir = Path(data_dir)
        self.connection = None
        
        # Verify data files exist
        self.required_files = [
            'Vannkraft_DamPunkt.shp',
            'Vannkraft_DamLinje.shp', 
            'Vannkraft_Magasin.shp'
        ]
        
        self.verify_data_files()
    
    def verify_data_files(self):
        """Verify all required data files exist."""
        missing_files = []
        
        for file in self.required_files:
            if not (self.data_dir / file).exists():
                missing_files.append(file)
        
        if missing_files:
            logger.error(f"Missing data files: {missing_files}")
            sys.exit(1)
        
        logger.info("✅ All required NVE data files found")
    
    async def connect_database(self, db_url: str = None):
        """Connect to monitoring database."""
        if not db_url:
            db_url = "postgresql://postgres:dam_monitor_2024@localhost:5432/dam_monitoring"
        
        try:
            self.connection = await asyncpg.connect(db_url)
            logger.info("✅ Connected to monitoring database")
        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
            sys.exit(1)
    
    async def load_nve_data(self):
        """Load and prepare NVE data."""
        logger.info("📊 Loading NVE data files...")
        
        # Load dam points (main dam registry)
        self.dam_punkt = gpd.read_file(self.data_dir / "Vannkraft_DamPunkt.shp")
        logger.info(f"Loaded {len(self.dam_punkt)} dam points")
        
        # Load dam lines
        self.dam_linje = gpd.read_file(self.data_dir / "Vannkraft_DamLinje.shp")
        logger.info(f"Loaded {len(self.dam_linje)} dam lines")
        
        # Load reservoirs
        self.magasin = gpd.read_file(self.data_dir / "Vannkraft_Magasin.shp")
        logger.info(f"Loaded {len(self.magasin)} reservoirs")
        
        # Convert to WGS84 if needed
        if self.dam_punkt.crs.to_string() != 'EPSG:4326':
            logger.info("Converting coordinates to WGS84...")
            self.dam_punkt = self.dam_punkt.to_crs('EPSG:4326')
            self.dam_linje = self.dam_linje.to_crs('EPSG:4326')
            self.magasin = self.magasin.to_crs('EPSG:4326')
        
        logger.info("✅ NVE data loaded and prepared")
    
    async def import_dams(self):
        """Import dam points as main dam registry."""
        logger.info("🏗️ Importing dams...")
        
        imported_count = 0
        skipped_count = 0
        
        for idx, dam in self.dam_punkt.iterrows():
            try:
                # Extract dam information
                dam_id = str(dam.get('damNr', f'NVE_{idx:06d}'))
                dam_name = dam.get('damNavn', f'Dam {dam_id}')
                
                # Handle construction year
                construction_year = None
                if pd.notna(dam.get('idriftAar')):
                    try:
                        construction_year = int(dam['idriftAar'])
                    except (ValueError, TypeError):
                        pass
                
                # Extract coordinates
                if hasattr(dam.geometry, 'x') and hasattr(dam.geometry, 'y'):
                    longitude = float(dam.geometry.x)
                    latitude = float(dam.geometry.y)
                else:
                    logger.warning(f"Invalid geometry for dam {dam_id}, skipping")
                    skipped_count += 1
                    continue
                
                # Determine dam type and other attributes
                dam_type = dam.get('damType', 'unknown')
                owner = dam.get('eier', None)
                capacity_mw = None
                if pd.notna(dam.get('instEffekt')):
                    try:
                        capacity_mw = float(dam['instEffekt'])
                    except (ValueError, TypeError):
                        pass
                
                # Prepare metadata
                metadata = {}
                for col in dam.index:
                    if col not in ['geometry'] and pd.notna(dam[col]):
                        metadata[col] = str(dam[col])
                
                # Insert into database
                await self.connection.execute("""
                    INSERT INTO dams (
                        dam_id, dam_name, dam_type, construction_year,
                        latitude, longitude, location, owner, capacity_mw,
                        nve_dam_nr, metadata, created_at
                    ) VALUES (
                        $1, $2, $3, $4, $5, $6, 
                        ST_SetSRID(ST_MakePoint($6, $5), 4326),
                        $7, $8, $9, $10, NOW()
                    )
                    ON CONFLICT (dam_id) DO UPDATE SET
                        dam_name = EXCLUDED.dam_name,
                        dam_type = EXCLUDED.dam_type,
                        construction_year = EXCLUDED.construction_year,
                        latitude = EXCLUDED.latitude,
                        longitude = EXCLUDED.longitude,
                        location = EXCLUDED.location,
                        owner = EXCLUDED.owner,
                        capacity_mw = EXCLUDED.capacity_mw,
                        metadata = EXCLUDED.metadata,
                        updated_at = NOW()
                """, dam_id, dam_name, dam_type, construction_year,
                    latitude, longitude, owner, capacity_mw, dam_id, 
                    json.dumps(metadata))
                
                imported_count += 1
                
                if imported_count % 100 == 0:
                    logger.info(f"Imported {imported_count} dams...")
                    
            except Exception as e:
                logger.error(f"Error importing dam {dam_id}: {e}")
                skipped_count += 1
                continue
        
        logger.info(f"✅ Dam import completed: {imported_count} imported, {skipped_count} skipped")
    
    async def link_reservoirs(self):
        """Link reservoir data to dams."""
        logger.info("🌊 Linking reservoir data...")
        
        linked_count = 0
        
        for idx, reservoir in self.magasin.iterrows():
            try:
                # Find nearest dam within reasonable distance (e.g., 5km)
                reservoir_centroid = reservoir.geometry.centroid
                
                # Simple nearest neighbor approach
                min_distance = float('inf')
                nearest_dam_id = None
                
                for dam_idx, dam in self.dam_punkt.iterrows():
                    if hasattr(dam.geometry, 'x') and hasattr(dam.geometry, 'y'):
                        dam_point = dam.geometry
                        distance = reservoir_centroid.distance(dam_point)
                        
                        if distance < min_distance and distance < 0.05:  # ~5km threshold
                            min_distance = distance
                            nearest_dam_id = str(dam.get('damNr', f'NVE_{dam_idx:06d}'))
                
                if nearest_dam_id:
                    # Extract reservoir data
                    reservoir_area = None
                    reservoir_volume = None
                    
                    if pd.notna(reservoir.get('areal')):
                        try:
                            reservoir_area = float(reservoir['areal']) / 1000000  # Convert to km²
                        except (ValueError, TypeError):
                            pass
                    
                    if pd.notna(reservoir.get('volum')):
                        try:
                            reservoir_volume = float(reservoir['volum']) / 1000000  # Convert to million m³
                        except (ValueError, TypeError):
                            pass
                    
                    # Update dam with reservoir info
                    await self.connection.execute("""
                        UPDATE dams 
                        SET reservoir_area_km2 = COALESCE($2, reservoir_area_km2),
                            reservoir_volume_mm3 = COALESCE($3, reservoir_volume_mm3),
                            updated_at = NOW()
                        WHERE dam_id = $1
                    """, nearest_dam_id, reservoir_area, reservoir_volume)
                    
                    linked_count += 1
                    
            except Exception as e:
                logger.error(f"Error linking reservoir {idx}: {e}")
                continue
        
        logger.info(f"✅ Reservoir linking completed: {linked_count} reservoirs linked")
    
    async def create_sample_sensors(self):
        """Create sample sensors for demonstration."""
        logger.info("📡 Creating sample sensors...")
        
        # Get list of imported dams
        dams = await self.connection.fetch("SELECT dam_id, latitude, longitude FROM dams LIMIT 10")
        
        sensor_types = [
            ('displacement', 'mm', 'Displacement monitoring'),
            ('seepage', 'L/min', 'Seepage monitoring'),
            ('water_level', 'm', 'Water level monitoring'),
            ('temperature', '°C', 'Temperature monitoring')
        ]
        
        sensor_count = 0
        
        for dam in dams:
            dam_id = dam['dam_id']
            lat = float(dam['latitude'])
            lon = float(dam['longitude'])
            
            for sensor_type, unit, description in sensor_types:
                sensor_id = f"{dam_id}_{sensor_type}_001"
                
                # Add small random offset for sensor location
                import random
                sensor_lat = lat + random.uniform(-0.001, 0.001)
                sensor_lon = lon + random.uniform(-0.001, 0.001)
                
                await self.connection.execute("""
                    INSERT INTO sensors (
                        sensor_id, dam_id, sensor_type, manufacturer,
                        latitude, longitude, location, measurement_unit,
                        installation_date, status
                    ) VALUES (
                        $1, $2, $3, 'Demo Sensors AS',
                        $4, $5, ST_SetSRID(ST_MakePoint($5, $4), 4326),
                        $6, $7, 'active'
                    )
                    ON CONFLICT (sensor_id) DO NOTHING
                """, sensor_id, dam_id, sensor_type, sensor_lat, sensor_lon,
                    unit, datetime.now().date())
                
                sensor_count += 1
        
        logger.info(f"✅ Created {sensor_count} sample sensors")
    
    async def generate_initial_health_scores(self):
        """Generate initial health scores for all dams."""
        logger.info("💯 Generating initial health scores...")
        
        dams = await self.connection.fetch("SELECT dam_id, construction_year FROM dams")
        
        for dam in dams:
            dam_id = dam['dam_id']
            construction_year = dam['construction_year']
            
            # Calculate age-based score
            if construction_year:
                age = datetime.now().year - construction_year
                age_factor = max(0.5, 1.0 - (age * 0.003))  # Gradual degradation
            else:
                age_factor = 0.8  # Unknown age penalty
            
            # Generate realistic scores
            import random
            
            base_structural = random.uniform(70, 95)
            base_hydraulic = random.uniform(75, 95)
            base_environmental = random.uniform(80, 95)
            
            structural_score = base_structural * age_factor
            hydraulic_score = base_hydraulic * age_factor
            environmental_score = base_environmental * age_factor
            
            overall_score = (
                structural_score * 0.4 +
                hydraulic_score * 0.4 +
                environmental_score * 0.2
            )
            
            # Determine risk level
            if overall_score >= 85:
                risk_level = "very_low"
            elif overall_score >= 70:
                risk_level = "low"
            elif overall_score >= 55:
                risk_level = "medium"
            elif overall_score >= 40:
                risk_level = "high"
            else:
                risk_level = "very_high"
            
            await self.connection.execute("""
                INSERT INTO health_scores (
                    time, dam_id, overall_score, structural_score,
                    hydraulic_score, environmental_score, risk_level,
                    confidence_level, trend_direction
                ) VALUES (
                    NOW(), $1, $2, $3, $4, $5, $6, 75.0, 'stable'
                )
            """, dam_id, round(overall_score, 2), round(structural_score, 2),
                round(hydraulic_score, 2), round(environmental_score, 2), risk_level)
        
        logger.info(f"✅ Generated initial health scores for {len(dams)} dams")
    
    async def close_connection(self):
        """Close database connection."""
        if self.connection:
            await self.connection.close()
            logger.info("✅ Database connection closed")

async def main():
    """Main import function."""
    parser = argparse.ArgumentParser(description='Import NVE dam data into monitoring system')
    parser.add_argument('--data-dir', default='Data/', help='Directory containing NVE shapefiles')
    parser.add_argument('--db-url', help='Database connection URL')
    parser.add_argument('--skip-sensors', action='store_true', help='Skip creating sample sensors')
    parser.add_argument('--skip-health', action='store_true', help='Skip generating initial health scores')
    
    args = parser.parse_args()
    
    logger.info("🚀 Starting NVE data import")
    
    # Initialize importer
    importer = NVEDataImporter(args.data_dir)
    
    try:
        # Connect to database
        await importer.connect_database(args.db_url)
        
        # Load NVE data
        await importer.load_nve_data()
        
        # Import dams
        await importer.import_dams()
        
        # Link reservoirs
        await importer.link_reservoirs()
        
        # Create sample sensors (optional)
        if not args.skip_sensors:
            await importer.create_sample_sensors()
        
        # Generate initial health scores (optional)
        if not args.skip_health:
            await importer.generate_initial_health_scores()
        
        logger.info("🎉 Import completed successfully!")
        logger.info("You can now start the monitoring system with: docker-compose up -d")
        
    except Exception as e:
        logger.error(f"❌ Import failed: {e}")
        sys.exit(1)
    
    finally:
        await importer.close_connection()

if __name__ == "__main__":
    asyncio.run(main()) 