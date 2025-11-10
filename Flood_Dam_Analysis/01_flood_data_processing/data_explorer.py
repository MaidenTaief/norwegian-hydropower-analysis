#!/usr/bin/env python3
"""
NVE Flood Data Explorer
======================
Comprehensive exploration of Norwegian flood and water infrastructure data
for flood-dam risk analysis.

Author: Taief
Date: August 2024
Purpose: PhD research preparation - Understanding flood data structure
"""

import geopandas as gpd
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

class NVEFloodDataExplorer:
    """
    Explore and analyze NVE flood data to understand structure, 
    features, and research potential
    """
    
    def __init__(self, data_dir="./"):
        self.data_dir = Path(data_dir)
        self.datasets = {}
        
    def load_all_datasets(self):
        """Load all NVE flood-related datasets"""
        
        print("🗄️ LOADING NVE FLOOD AND WATER INFRASTRUCTURE DATA")
        print("=" * 60)
        
        # Flood zones
        flood_files = {
            "flood_100yr": "Flomsone/Flomsone_100Aar.shp",
            "flood_200yr": "Flomsone/Flomsone_200Aar.shp", 
            "flood_200yr_climate": "Flomsone/Flomsone_200AarKlimatilpasset.shp"
        }
        
        # Historical flood events
        event_files = {
            "flood_events": "Flom_Flomhendelse/Flom_FlomhendelseAreal.shp"
        }
        
        # Flood awareness/caution areas
        caution_files = {
            "flood_caution_rivers": "Flom_Aktsomhet/Flom_AktsomhetElv.shp",
            "flood_caution_areas": "Flom_Aktsomhet/Flom_AktsomhetOmr.shp"
        }
        
        # River networks
        river_files = {
            "river_network": "Elv/Elv_Elvenett.shp",
            "main_rivers": "Elv/Elv_Hovedelv.shp"
        }
        
        # Hydropower infrastructure
        power_files = {
            "hydropower_plants": "Vannkraft/Vannkraft_Vannkraftverk.shp",
            "water_intakes": "Vannkraft/Vannkraft_Inntakspunkt.shp",
            "water_ways": "Vannkraft/Vannkraft_Vannvei.shp"
        }
        
        all_files = {**flood_files, **event_files, **caution_files, **river_files, **power_files}
        
        for name, filepath in all_files.items():
            try:
                full_path = self.data_dir / filepath
                if full_path.exists():
                    gdf = gpd.read_file(full_path)
                    self.datasets[name] = gdf
                    print(f"✅ {name}: {len(gdf):,} records loaded")
                else:
                    print(f"❌ {name}: File not found at {full_path}")
            except Exception as e:
                print(f"❌ {name}: Error loading - {e}")
        
        print(f"\n📊 Successfully loaded {len(self.datasets)} datasets")
        return self.datasets
    
    def explore_dataset_structure(self):
        """Analyze the structure of each dataset"""
        
        print("\n🔍 DATASET STRUCTURE ANALYSIS")
        print("=" * 60)
        
        for name, gdf in self.datasets.items():
            print(f"\n📋 {name.upper()}")
            print("-" * 40)
            print(f"Records: {len(gdf):,}")
            print(f"Columns: {len(gdf.columns)}")
            print(f"Geometry type: {gdf.geometry.geom_type.value_counts().index[0] if not gdf.empty else 'None'}")
            print(f"CRS: {gdf.crs}")
            
            # Show column names and types
            print(f"Columns: {list(gdf.columns)}")
            
            # Show data types
            print("Data types:")
            for col in gdf.columns:
                if col != 'geometry':
                    dtype = gdf[col].dtype
                    null_count = gdf[col].isnull().sum()
                    print(f"  {col}: {dtype} (nulls: {null_count})")
            
            print()
    
    def analyze_flood_zones(self):
        """Detailed analysis of flood zone data"""
        
        print("\n🌊 FLOOD ZONE ANALYSIS")
        print("=" * 60)
        
        flood_datasets = ['flood_100yr', 'flood_200yr', 'flood_200yr_climate']
        
        for dataset_name in flood_datasets:
            if dataset_name in self.datasets:
                gdf = self.datasets[dataset_name]
                print(f"\n📊 {dataset_name.upper()}")
                print("-" * 30)
                
                # Basic stats
                print(f"Total flood zones: {len(gdf):,}")
                print(f"Total area: {gdf.geometry.area.sum() / 1e6:.1f} km²")
                
                # Key columns analysis
                if 'gjentakint' in gdf.columns:
                    print(f"Return intervals: {gdf['gjentakint'].unique()}")
                
                if 'statusKart' in gdf.columns:
                    print("Map status distribution:")
                    print(gdf['statusKart'].value_counts())
                
                if 'malemetode' in gdf.columns:
                    print("Measurement methods:")
                    print(gdf['malemetode'].value_counts())
                
                # Show sample data
                print("\nSample records:")
                print(gdf.head(3)[['objType', 'fsID', 'gjentakint', 'statusKart', 'malemetode']].to_string())
    
    def analyze_historical_floods(self):
        """Analyze historical flood events"""
        
        print("\n📜 HISTORICAL FLOOD EVENTS ANALYSIS")
        print("=" * 60)
        
        if 'flood_events' in self.datasets:
            gdf = self.datasets['flood_events']
            
            print(f"Total historical events: {len(gdf):,}")
            
            # Date analysis
            if 'dato' in gdf.columns:
                # Convert date column
                gdf['year'] = pd.to_datetime(gdf['dato'], errors='coerce').dt.year
                
                print(f"Date range: {gdf['year'].min()} - {gdf['year'].max()}")
                print(f"Events with valid dates: {gdf['year'].notna().sum():,}")
                
                # Decade analysis
                gdf['decade'] = (gdf['year'] // 10) * 10
                decade_counts = gdf['decade'].value_counts().sort_index()
                print("\nEvents by decade:")
                for decade, count in decade_counts.items():
                    if pd.notna(decade):
                        print(f"  {int(decade)}s: {count} events")
            
            # Flood origin analysis
            if 'opphav' in gdf.columns:
                print("\nFlood origins:")
                print(gdf['opphav'].value_counts())
            
            # Show sample events
            print("\nSample events:")
            sample_cols = ['flomID', 'navn', 'dato', 'opphav', 'flomnavn']
            available_cols = [col for col in sample_cols if col in gdf.columns]
            print(gdf[available_cols].head(5).to_string())
    
    def analyze_river_network(self):
        """Analyze river network data"""
        
        print("\n🏞️ RIVER NETWORK ANALYSIS")
        print("=" * 60)
        
        if 'river_network' in self.datasets and 'main_rivers' in self.datasets:
            river_net = self.datasets['river_network']
            main_rivers = self.datasets['main_rivers']
            
            print(f"Total river segments: {river_net['geometry'].length.sum() / 1000:.0f} km")
            print(f"Main river segments: {main_rivers['geometry'].length.sum() / 1000:.0f} km")
            
            # Show column structure
            print(f"\nRiver network columns: {list(river_net.columns)}")
            print(f"Main rivers columns: {list(main_rivers.columns)}")
    
    def analyze_hydropower_infrastructure(self):
        """Analyze hydropower infrastructure"""
        
        print("\n⚡ HYDROPOWER INFRASTRUCTURE ANALYSIS")
        print("=" * 60)
        
        if 'hydropower_plants' in self.datasets:
            plants = self.datasets['hydropower_plants']
            print(f"Hydropower plants: {len(plants):,}")
            
            # Show key attributes
            print(f"Plant columns: {list(plants.columns)}")
            
            if not plants.empty:
                print("\nSample plants:")
                print(plants.head(3).to_string())
        
        if 'water_intakes' in self.datasets:
            intakes = self.datasets['water_intakes']
            print(f"Water intake points: {len(intakes):,}")
    
    def create_summary_report(self):
        """Create comprehensive summary report"""
        
        print("\n📋 COMPREHENSIVE DATA SUMMARY")
        print("=" * 60)
        
        summary = {
            "Dataset": [],
            "Records": [],
            "Geometry Type": [],
            "Key Features": []
        }
        
        for name, gdf in self.datasets.items():
            summary["Dataset"].append(name)
            summary["Records"].append(len(gdf))
            summary["Geometry Type"].append(gdf.geometry.geom_type.value_counts().index[0] if not gdf.empty else 'None')
            summary["Key Features"].append(", ".join([col for col in gdf.columns if col != 'geometry'][:5]))
        
        summary_df = pd.DataFrame(summary)
        print(summary_df.to_string(index=False))
        
        # Research potential assessment
        print("\n🎯 RESEARCH POTENTIAL ASSESSMENT")
        print("=" * 60)
        
        print("✅ FLOOD FREQUENCY ANALYSIS:")
        print("   - 100-year and 200-year flood zones available")
        print("   - Climate-adapted scenarios for future projections")
        print("   - Historical events for model validation")
        
        print("\n✅ CLIMATE CHANGE ASSESSMENT:")
        print("   - Standard vs climate-adapted flood zones comparison")
        print("   - Quantitative climate impact analysis possible")
        
        print("\n✅ DAM-FLOOD INTERACTION:")
        print("   - Hydropower infrastructure data available")
        print("   - River network for connectivity analysis")
        print("   - Spatial intersection analysis feasible")
        
        print("\n✅ POPULATION RISK ANALYSIS:")
        print("   - Flood zone polygons for exposure calculation")
        print("   - Historical events for calibration")
        
        print("\n🎓 PhD RESEARCH VALUE:")
        print("   - Covers flood reconstructions (historical events)")
        print("   - Enables long-term risk assessment")
        print("   - Supports climate-driven modeling")
        print("   - Provides applied relevance with NVE data")
        
        return summary_df
    
    def save_exploration_results(self):
        """Save exploration results for reference"""
        
        results_dir = Path("../05_results")
        results_dir.mkdir(exist_ok=True)
        
        # Create detailed data dictionary
        data_dict = {}
        for name, gdf in self.datasets.items():
            data_dict[name] = {
                "records": len(gdf),
                "columns": list(gdf.columns),
                "geometry_type": gdf.geometry.geom_type.value_counts().to_dict() if not gdf.empty else {},
                "crs": str(gdf.crs),
                "sample_data": gdf.head(2).drop('geometry', axis=1).to_dict() if not gdf.empty else {}
            }
        
        # Save as JSON
        import json
        with open(results_dir / "nve_data_exploration.json", "w") as f:
            json.dump(data_dict, f, indent=2, default=str)
        
        print(f"\n💾 Exploration results saved to {results_dir / 'nve_data_exploration.json'}")

def main():
    """Run complete data exploration"""
    
    print("🔬 NVE FLOOD DATA EXPLORATION FOR PHD RESEARCH")
    print("=" * 70)
    
    explorer = NVEFloodDataExplorer()
    
    # Load all datasets
    explorer.load_all_datasets()
    
    # Comprehensive analysis
    explorer.explore_dataset_structure()
    explorer.analyze_flood_zones()
    explorer.analyze_historical_floods()
    explorer.analyze_river_network()
    explorer.analyze_hydropower_infrastructure()
    
    # Summary and research assessment
    summary_df = explorer.create_summary_report()
    
    # Save results
    explorer.save_exploration_results()
    
    print("\n🎯 NEXT STEPS FOR PHD RESEARCH:")
    print("1. Create spatial database with all datasets")
    print("2. Develop dam-flood intersection analysis")
    print("3. Build climate change comparison models")
    print("4. Implement cascade failure scenarios")
    
    return explorer

if __name__ == "__main__":
    explorer = main()



