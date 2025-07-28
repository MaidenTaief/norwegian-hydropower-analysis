#!/usr/bin/env python3
"""Quick NVE Data Import for Docker Database"""

import geopandas as gpd
import pandas as pd
import asyncpg
import asyncio
from pathlib import Path

async def import_nve_dams():
    """Import real NVE dam data."""
    print("📊 Loading your NVE dam data...")
    
    # Load your real NVE dam data
    dam_punkt = gpd.read_file("Data/Vannkraft_DamPunkt.shp")
    print(f"Found {len(dam_punkt)} real Norwegian dams from NVE!")
    
    # Convert to WGS84 if needed
    if dam_punkt.crs.to_string() != 'EPSG:4326':
        dam_punkt = dam_punkt.to_crs('EPSG:4326')
    
    # Connect to Docker database
    conn = await asyncpg.connect(
        'postgresql://postgres:dam_monitor_2024@localhost:5432/dam_monitoring'
    )
    
    imported = 0
    
    # Import first 10 dams as examples
    for idx, dam in dam_punkt.head(10).iterrows():
        try:
            dam_id = f"NVE_{dam.get('damNr', idx):06d}"
            dam_name = dam.get('damNavn', f'Norwegian Dam {dam_id}')
            
            if hasattr(dam.geometry, 'x') and hasattr(dam.geometry, 'y'):
                lat = float(dam.geometry.y)
                lon = float(dam.geometry.x)
                
                construction_year = None
                if pd.notna(dam.get('idriftAar')):
                    try:
                        construction_year = int(dam['idriftAar'])
                    except:
                        pass
                
                # Insert real Norwegian dam
                await conn.execute("""
                    INSERT INTO dams (dam_id, dam_name, latitude, longitude, construction_year, region)
                    VALUES ($1, $2, $3, $4, $5, $6)
                    ON CONFLICT (dam_id) DO NOTHING
                """, dam_id, dam_name, lat, lon, construction_year, 'Norway')
                
                imported += 1
                print(f"✅ Imported: {dam_name} at {lat:.4f}, {lon:.4f}")
                
        except Exception as e:
            print(f"⚠️ Skipped dam {idx}: {e}")
    
    await conn.close()
    print(f"🎉 Successfully imported {imported} real Norwegian dams!")
    print("🌤️ Now getting live weather data for each one...")

if __name__ == "__main__":
    asyncio.run(import_nve_dams())
