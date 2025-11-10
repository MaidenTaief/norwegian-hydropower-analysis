#!/usr/bin/env python3
"""
ARCTIC FLOOD DATA EXTRACTOR
============================
Extracts flood and river data for Arctic regions (66.5°N+) following the same 
patterns as the existing Arctic dam analysis.

Maintains consistency with arctic_dam_locator.py and arctic_risk_analyzer_improved.py
"""

import pandas as pd
import geopandas as gpd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import logging
from dataclasses import dataclass
import sqlite3
import warnings
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)

@dataclass
class ArcticFloodZone:
    """Structure for Arctic flood zone information"""
    zone_id: str
    zone_type: str  # '100yr', '200yr', 'climate'
    return_period: float
    latitude_center: float
    longitude_center: float
    area_km2: float
    arctic_distance_km: float  # Distance north of Arctic Circle
    status: str
    mapping_method: str
    date_mapped: str

@dataclass 
class ArcticRiver:
    """Structure for Arctic river information"""
    river_id: str
    river_name: str
    length_km: float
    watershed_code: str
    latitude_start: float
    longitude_start: float
    arctic_distance_km: float

class ArcticFloodExtractor:
    """
    Extracts and analyzes flood and river data for Arctic regions
    Follows same patterns as ArcticDamLocator and ArcticRiskAnalyzer
    """
    
    # Same Arctic Circle definition as existing analysis
    ARCTIC_CIRCLE_LATITUDE = 66.5  # 66°33′N - matches arctic_dam_locator.py
    
    # Arctic zone classifications (same as arctic_risk_analyzer_improved.py)
    ARCTIC_ZONES = {
        "sub_arctic": {"lat_min": 66.5, "lat_max": 68.0},     # Arctic Circle
        "high_arctic": {"lat_min": 68.0, "lat_max": 70.0},    # Northern Norway  
        "extreme_arctic": {"lat_min": 70.0, "lat_max": 90.0}  # Svalbard-like
    }
    
    def __init__(self, data_dir: str = "./"):
        """Initialize with data directory path"""
        self.data_dir = Path(data_dir)
        self.flood_data = {}
        self.river_data = {}
        self.arctic_flood_zones = []
        self.arctic_rivers = []
        
    def load_flood_datasets(self) -> Dict:
        """Load all flood-related datasets"""
        
        print("🌊 LOADING FLOOD DATA FOR ARCTIC EXTRACTION")
        print("=" * 60)
        
        flood_files = {
            "flood_100yr": "Flomsone/Flomsone_100Aar.shp",
            "flood_200yr": "Flomsone/Flomsone_200Aar.shp", 
            "flood_climate": "Flomsone/Flomsone_200AarKlimatilpasset.shp",
            "historical_floods": "Flom_Flomhendelse/Flom_FlomhendelseAreal.shp"
        }
        
        for name, filepath in flood_files.items():
            try:
                full_path = self.data_dir / filepath
                if full_path.exists():
                    print(f"📂 Loading {name}...")
                    gdf = gpd.read_file(full_path)
                    
                    # Ensure consistent CRS (same as Arctic dam analysis)
                    if gdf.crs.to_string() != 'EPSG:4326':
                        gdf = gdf.to_crs('EPSG:4326')
                        
                    self.flood_data[name] = gdf
                    print(f"✅ {name}: {len(gdf):,} records loaded")
                else:
                    print(f"❌ {name}: File not found")
                    
            except Exception as e:
                print(f"❌ {name}: Error - {e}")
        
        return self.flood_data
    
    def load_river_datasets(self) -> Dict:
        """Load river network datasets"""
        
        print("\n🏞️ LOADING RIVER DATA FOR ARCTIC EXTRACTION")
        print("=" * 60)
        
        river_files = {
            "main_rivers": "Elv/Elv_Hovedelv.shp",
            "river_network": "Elv/Elv_Elvenett.shp"  # Only load if needed
        }
        
        for name, filepath in river_files.items():
            try:
                full_path = self.data_dir / filepath
                if full_path.exists():
                    print(f"📂 Loading {name}...")
                    
                    # For large river network, sample first
                    if name == "river_network":
                        gdf = gpd.read_file(full_path, rows=10000)  # Sample large dataset
                        print(f"📊 Sampled 10,000 records from large river network")
                    else:
                        gdf = gpd.read_file(full_path)
                    
                    # Ensure consistent CRS
                    if gdf.crs.to_string() != 'EPSG:4326':
                        gdf = gdf.to_crs('EPSG:4326')
                        
                    self.river_data[name] = gdf
                    print(f"✅ {name}: {len(gdf):,} records loaded")
                    
            except Exception as e:
                print(f"❌ {name}: Error - {e}")
        
        return self.river_data
    
    def extract_arctic_flood_zones(self) -> List[ArcticFloodZone]:
        """Extract flood zones above Arctic Circle"""
        
        print(f"\n❄️ EXTRACTING ARCTIC FLOOD ZONES (>{self.ARCTIC_CIRCLE_LATITUDE}°N)")
        print("=" * 60)
        
        self.arctic_flood_zones = []
        
        for dataset_name, gdf in self.flood_data.items():
            if gdf is None or gdf.empty:
                continue
                
            print(f"\n🔍 Processing {dataset_name}...")
            
            # Calculate centroid coordinates for each polygon
            gdf['centroid'] = gdf.geometry.centroid
            gdf['lat_center'] = gdf.centroid.y
            gdf['lon_center'] = gdf.centroid.x
            
            # Filter for Arctic regions (same logic as arctic_dam_locator.py)
            arctic_floods = gdf[gdf['lat_center'] > self.ARCTIC_CIRCLE_LATITUDE].copy()
            
            if len(arctic_floods) == 0:
                print(f"   📊 No Arctic flood zones found in {dataset_name}")
                continue
            
            # Calculate Arctic distance (same formula as existing analysis)
            arctic_floods['arctic_distance_km'] = (
                arctic_floods['lat_center'] - self.ARCTIC_CIRCLE_LATITUDE
            ) * 111.32  # degrees to km conversion
            
            # Calculate area in km²
            arctic_floods['area_km2'] = arctic_floods.geometry.area / 1e6
            
            # Map zone types
            zone_type_mapping = {
                "flood_100yr": "100yr",
                "flood_200yr": "200yr", 
                "flood_climate": "climate",
                "historical_floods": "historical"
            }
            zone_type = zone_type_mapping.get(dataset_name, "unknown")
            
            # Create ArcticFloodZone objects
            for idx, row in arctic_floods.iterrows():
                
                # Extract return period
                return_period = row.get('gjentakint', 0)
                if pd.isna(return_period):
                    if zone_type == "100yr":
                        return_period = 100
                    elif zone_type == "200yr":
                        return_period = 200
                    elif zone_type == "climate":
                        return_period = 2100  # Climate projection year
                    else:
                        return_period = 0
                
                arctic_zone = ArcticFloodZone(
                    zone_id=f"{zone_type}_{row.get('fsID', idx)}",
                    zone_type=zone_type,
                    return_period=float(return_period),
                    latitude_center=row['lat_center'],
                    longitude_center=row['lon_center'],
                    area_km2=row['area_km2'],
                    arctic_distance_km=row['arctic_distance_km'],
                    status=str(row.get('statusKart', 'unknown')),
                    mapping_method=str(row.get('malemetode', 'unknown')),
                    date_mapped=str(row.get('digDato', 'unknown'))
                )
                
                self.arctic_flood_zones.append(arctic_zone)
            
            print(f"   ✅ Found {len(arctic_floods)} Arctic flood zones")
            print(f"   📍 Latitude range: {arctic_floods['lat_center'].min():.2f}°N - {arctic_floods['lat_center'].max():.2f}°N")
            print(f"   📏 Arctic distance: {arctic_floods['arctic_distance_km'].min():.0f} - {arctic_floods['arctic_distance_km'].max():.0f} km north")
        
        print(f"\n🎯 TOTAL ARCTIC FLOOD ZONES: {len(self.arctic_flood_zones)}")
        return self.arctic_flood_zones
    
    def extract_arctic_rivers(self) -> List[ArcticRiver]:
        """Extract main rivers in Arctic regions"""
        
        print(f"\n🏞️ EXTRACTING ARCTIC RIVERS (>{self.ARCTIC_CIRCLE_LATITUDE}°N)")
        print("=" * 60)
        
        self.arctic_rivers = []
        
        if "main_rivers" not in self.river_data:
            print("❌ Main rivers data not available")
            return self.arctic_rivers
        
        gdf = self.river_data["main_rivers"]
        
        # Get start point of each river linestring
        gdf['start_point'] = gdf.geometry.apply(lambda x: x.coords[0] if x.geom_type == 'LineString' else None)
        gdf['lat_start'] = gdf['start_point'].apply(lambda x: x[1] if x else None)
        gdf['lon_start'] = gdf['start_point'].apply(lambda x: x[0] if x else None)
        
        # Filter for Arctic rivers
        arctic_rivers_gdf = gdf[gdf['lat_start'] > self.ARCTIC_CIRCLE_LATITUDE].copy()
        
        if len(arctic_rivers_gdf) == 0:
            print("📊 No Arctic rivers found")
            return self.arctic_rivers
        
        # Calculate Arctic distance
        arctic_rivers_gdf['arctic_distance_km'] = (
            arctic_rivers_gdf['lat_start'] - self.ARCTIC_CIRCLE_LATITUDE
        ) * 111.32
        
        # Calculate length in km
        arctic_rivers_gdf['length_km'] = arctic_rivers_gdf['elvelengde'] / 1000
        
        # Create ArcticRiver objects
        for idx, row in arctic_rivers_gdf.iterrows():
            arctic_river = ArcticRiver(
                river_id=f"river_{row.get('nbfVassNr', idx)}",
                river_name=str(row.get('elvenavn', 'unnamed')),
                length_km=row['length_km'],
                watershed_code=str(row.get('nbfVassNr', 'unknown')),
                latitude_start=row['lat_start'],
                longitude_start=row['lon_start'],
                arctic_distance_km=row['arctic_distance_km']
            )
            
            self.arctic_rivers.append(arctic_river)
        
        print(f"✅ Found {len(arctic_rivers_gdf)} Arctic rivers")
        print(f"📍 Latitude range: {arctic_rivers_gdf['lat_start'].min():.2f}°N - {arctic_rivers_gdf['lat_start'].max():.2f}°N")
        print(f"📏 Total river length: {arctic_rivers_gdf['length_km'].sum():.0f} km")
        
        return self.arctic_rivers
    
    def classify_arctic_zones(self):
        """Classify Arctic flood zones by latitude (same as risk analyzer)"""
        
        print(f"\n🎯 CLASSIFYING ARCTIC ZONES")
        print("=" * 60)
        
        zone_counts = {"sub_arctic": 0, "high_arctic": 0, "extreme_arctic": 0}
        
        for flood_zone in self.arctic_flood_zones:
            lat = flood_zone.latitude_center
            
            if lat >= self.ARCTIC_ZONES["extreme_arctic"]["lat_min"]:
                flood_zone.arctic_classification = "extreme_arctic"
                zone_counts["extreme_arctic"] += 1
            elif lat >= self.ARCTIC_ZONES["high_arctic"]["lat_min"]:
                flood_zone.arctic_classification = "high_arctic" 
                zone_counts["high_arctic"] += 1
            else:
                flood_zone.arctic_classification = "sub_arctic"
                zone_counts["sub_arctic"] += 1
        
        print(f"📊 Zone classification:")
        print(f"   🌡️  Sub-Arctic (66.5-68°N): {zone_counts['sub_arctic']} zones")
        print(f"   ❄️  High Arctic (68-70°N): {zone_counts['high_arctic']} zones") 
        print(f"   🧊 Extreme Arctic (70°N+): {zone_counts['extreme_arctic']} zones")
        
        return zone_counts
    
    def save_to_csv(self, output_dir: str = "../05_results"):
        """Save Arctic flood and river data to CSV files"""
        
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        print(f"\n💾 SAVING ARCTIC DATA TO CSV")
        print("=" * 60)
        
        # Save Arctic flood zones
        if self.arctic_flood_zones:
            flood_df = pd.DataFrame([
                {
                    'zone_id': zone.zone_id,
                    'zone_type': zone.zone_type,
                    'return_period': zone.return_period,
                    'latitude_center': zone.latitude_center,
                    'longitude_center': zone.longitude_center,
                    'area_km2': zone.area_km2,
                    'arctic_distance_km': zone.arctic_distance_km,
                    'arctic_classification': getattr(zone, 'arctic_classification', 'unknown'),
                    'status': zone.status,
                    'mapping_method': zone.mapping_method,
                    'date_mapped': zone.date_mapped
                }
                for zone in self.arctic_flood_zones
            ])
            
            flood_csv = output_path / "arctic_flood_zones.csv"
            flood_df.to_csv(flood_csv, index=False)
            print(f"✅ Arctic flood zones saved: {flood_csv}")
            print(f"   📊 Records: {len(flood_df)}")
        
        # Save Arctic rivers
        if self.arctic_rivers:
            river_df = pd.DataFrame([
                {
                    'river_id': river.river_id,
                    'river_name': river.river_name,
                    'length_km': river.length_km,
                    'watershed_code': river.watershed_code,
                    'latitude_start': river.latitude_start,
                    'longitude_start': river.longitude_start,
                    'arctic_distance_km': river.arctic_distance_km
                }
                for river in self.arctic_rivers
            ])
            
            river_csv = output_path / "arctic_rivers.csv"
            river_df.to_csv(river_csv, index=False)
            print(f"✅ Arctic rivers saved: {river_csv}")
            print(f"   📊 Records: {len(river_df)}")
        
        return output_path
    
    def save_to_sqlite(self, db_path: str = "../05_results/arctic_flood_data.db"):
        """Save to SQLite database for integration with Arctic dam analysis"""
        
        db_file = Path(db_path)
        db_file.parent.mkdir(exist_ok=True)
        
        print(f"\n🗄️ SAVING TO SQLITE DATABASE")
        print("=" * 60)
        
        conn = sqlite3.connect(db_file)
        
        # Save flood zones
        if self.arctic_flood_zones:
            flood_df = pd.DataFrame([
                {
                    'zone_id': zone.zone_id,
                    'zone_type': zone.zone_type,
                    'return_period': zone.return_period,
                    'latitude_center': zone.latitude_center,
                    'longitude_center': zone.longitude_center,
                    'area_km2': zone.area_km2,
                    'arctic_distance_km': zone.arctic_distance_km,
                    'arctic_classification': getattr(zone, 'arctic_classification', 'unknown'),
                    'status': zone.status,
                    'mapping_method': zone.mapping_method,
                    'date_mapped': zone.date_mapped
                }
                for zone in self.arctic_flood_zones
            ])
            
            flood_df.to_sql('arctic_flood_zones', conn, if_exists='replace', index=False)
            print(f"✅ arctic_flood_zones table created: {len(flood_df)} records")
        
        # Save rivers
        if self.arctic_rivers:
            river_df = pd.DataFrame([
                {
                    'river_id': river.river_id,
                    'river_name': river.river_name,
                    'length_km': river.length_km,
                    'watershed_code': river.watershed_code,
                    'latitude_start': river.latitude_start,
                    'longitude_start': river.longitude_start,
                    'arctic_distance_km': river.arctic_distance_km
                }
                for river in self.arctic_rivers
            ])
            
            river_df.to_sql('arctic_rivers', conn, if_exists='replace', index=False)
            print(f"✅ arctic_rivers table created: {len(river_df)} records")
        
        conn.close()
        print(f"💾 Database saved: {db_file}")
        
        return db_file
    
    def generate_summary_report(self):
        """Generate summary report matching Arctic analysis style"""
        
        print(f"\n📋 ARCTIC FLOOD DATA SUMMARY REPORT")
        print("=" * 70)
        
        print(f"🎯 GEOGRAPHIC SCOPE:")
        print(f"   Arctic Circle boundary: {self.ARCTIC_CIRCLE_LATITUDE}°N")
        print(f"   Analysis follows same patterns as arctic_dam_locator.py")
        
        print(f"\n📊 FLOOD ZONE STATISTICS:")
        if self.arctic_flood_zones:
            zone_types = {}
            for zone in self.arctic_flood_zones:
                if zone.zone_type not in zone_types:
                    zone_types[zone.zone_type] = 0
                zone_types[zone.zone_type] += 1
            
            for zone_type, count in zone_types.items():
                print(f"   🌊 {zone_type}: {count} zones")
            
            # Geographic distribution
            lats = [zone.latitude_center for zone in self.arctic_flood_zones]
            print(f"\n📍 GEOGRAPHIC DISTRIBUTION:")
            print(f"   Northernmost flood zone: {max(lats):.2f}°N")
            print(f"   Southernmost flood zone: {min(lats):.2f}°N")
            print(f"   Total Arctic coverage: {max(lats) - min(lats):.2f}° latitude")
        
        print(f"\n🏞️ RIVER NETWORK STATISTICS:")
        if self.arctic_rivers:
            total_length = sum(river.length_km for river in self.arctic_rivers)
            print(f"   🌊 Arctic rivers: {len(self.arctic_rivers)}")
            print(f"   📏 Total length: {total_length:.0f} km")
        
        print(f"\n🔗 INTEGRATION POTENTIAL:")
        print(f"   ✅ Ready for integration with Arctic dam analysis")
        print(f"   ✅ Consistent data structure and geographic boundaries")
        print(f"   ✅ Compatible with existing risk assessment framework")
        
        print(f"\n🎓 PhD RESEARCH VALUE:")
        print(f"   ✅ Arctic-specific flood risk assessment")
        print(f"   ✅ Climate change scenario analysis ready")
        print(f"   ✅ Historical flood context available")
        print(f"   ✅ Spatial infrastructure interaction analysis possible")

def main():
    """Run Arctic flood data extraction"""
    
    print("❄️ ARCTIC FLOOD DATA EXTRACTOR")
    print("Following patterns from arctic_dam_locator.py and arctic_risk_analyzer_improved.py")
    print("=" * 80)
    
    extractor = ArcticFloodExtractor()
    
    # Load all datasets
    extractor.load_flood_datasets()
    extractor.load_river_datasets()
    
    # Extract Arctic data
    arctic_floods = extractor.extract_arctic_flood_zones()
    arctic_rivers = extractor.extract_arctic_rivers()
    
    # Classify zones
    extractor.classify_arctic_zones()
    
    # Save results
    extractor.save_to_csv()
    extractor.save_to_sqlite()
    
    # Generate report
    extractor.generate_summary_report()
    
    print(f"\n🎯 NEXT STEPS:")
    print(f"1. Review generated CSV/SQLite files")
    print(f"2. Integrate with existing Arctic dam analysis")
    print(f"3. Develop flood-dam risk intersection analysis")
    print(f"4. Create climate change scenario comparisons")
    
    return extractor

if __name__ == "__main__":
    extractor = main()



