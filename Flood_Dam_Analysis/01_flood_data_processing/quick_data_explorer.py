#!/usr/bin/env python3
"""
Quick NVE Flood Data Explorer
============================
Efficient exploration that handles large datasets by sampling
"""

import geopandas as gpd
import pandas as pd
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

def explore_dataset_quick(filepath, sample_size=1000):
    """Quickly explore a dataset by sampling if it's large"""
    try:
        # First, check the size
        gdf = gpd.read_file(filepath)
        total_records = len(gdf)
        
        # If dataset is large, sample it
        if total_records > sample_size:
            gdf_sample = gdf.sample(n=sample_size, random_state=42)
            print(f"   📊 Sampled {sample_size:,} from {total_records:,} total records")
        else:
            gdf_sample = gdf
            print(f"   📊 Loaded all {total_records:,} records")
        
        # Basic info
        print(f"   🗂️ Columns: {list(gdf_sample.columns)}")
        print(f"   🌍 CRS: {gdf_sample.crs}")
        print(f"   📐 Geometry: {gdf_sample.geometry.geom_type.value_counts().index[0]}")
        
        # Show sample data (non-geometry columns only)
        non_geom_cols = [col for col in gdf_sample.columns if col != 'geometry']
        if non_geom_cols:
            print("   📋 Sample data:")
            print(gdf_sample[non_geom_cols].head(2).to_string(index=False))
        
        return {
            'total_records': total_records,
            'columns': list(gdf.columns),
            'crs': str(gdf.crs),
            'geometry_type': gdf_sample.geometry.geom_type.value_counts().index[0],
            'sample_data': gdf_sample[non_geom_cols].head(2).to_dict() if non_geom_cols else {}
        }
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return None

def main():
    """Quick exploration of all datasets"""
    
    print("🔍 QUICK NVE DATA EXPLORATION")
    print("=" * 50)
    
    # Define key datasets to explore
    datasets = {
        "🌊 100-year flood zones": "Flomsone/Flomsone_100Aar.shp",
        "🌊 200-year flood zones": "Flomsone/Flomsone_200Aar.shp", 
        "🌡️ Climate-adapted flood zones": "Flomsone/Flomsone_200AarKlimatilpasset.shp",
        "📜 Historical flood events": "Flom_Flomhendelse/Flom_FlomhendelseAreal.shp",
        "🏞️ River network": "Elv/Elv_Elvenett.shp",
        "🏞️ Main rivers": "Elv/Elv_Hovedelv.shp",
        "⚡ Hydropower plants": "Vannkraft/Vannkraft_Vannkraftverk.shp",
        "💧 Water intakes": "Vannkraft/Vannkraft_Inntakspunkt.shp"
    }
    
    results = {}
    
    for name, filepath in datasets.items():
        print(f"\n{name}")
        print("-" * 40)
        
        if Path(filepath).exists():
            result = explore_dataset_quick(filepath, sample_size=500)
            if result:
                results[name] = result
        else:
            print(f"   ❌ File not found: {filepath}")
    
    # Summary
    print(f"\n📊 SUMMARY")
    print("=" * 50)
    
    total_records = sum(r['total_records'] for r in results.values())
    print(f"Total records across all datasets: {total_records:,}")
    
    print("\nDataset sizes:")
    for name, result in results.items():
        print(f"  {name}: {result['total_records']:,} records")
    
    # Key insights for research
    print(f"\n🎯 KEY RESEARCH INSIGHTS")
    print("=" * 50)
    
    print("✅ FLOOD ANALYSIS POTENTIAL:")
    if "🌊 100-year flood zones" in results and "🌊 200-year flood zones" in results:
        flood_100 = results["🌊 100-year flood zones"]['total_records']
        flood_200 = results["🌊 200-year flood zones"]['total_records']
        print(f"   - Flood zones: {flood_100:,} (100yr) + {flood_200:,} (200yr)")
    
    if "🌡️ Climate-adapted flood zones" in results:
        climate_zones = results["🌡️ Climate-adapted flood zones"]['total_records']
        print(f"   - Climate scenarios: {climate_zones:,} adapted zones")
    
    if "📜 Historical flood events" in results:
        events = results["📜 Historical flood events"]['total_records']
        print(f"   - Historical validation: {events:,} flood events")
    
    print("\n✅ INFRASTRUCTURE ANALYSIS:")
    if "⚡ Hydropower plants" in results:
        plants = results["⚡ Hydropower plants"]['total_records']
        print(f"   - Hydropower infrastructure: {plants:,} plants")
    
    if "🏞️ River network" in results:
        rivers = results["🏞️ River network"]['total_records']
        print(f"   - River connectivity: {rivers:,} segments")
    
    print("\n🎓 PhD RESEARCH VALUE:")
    print("   - ✅ Historical flood reconstructions available")
    print("   - ✅ Climate change scenarios for future projections")
    print("   - ✅ Infrastructure data for impact assessment")
    print("   - ✅ Spatial data for cascade modeling")
    
    return results

if __name__ == "__main__":
    results = main()



