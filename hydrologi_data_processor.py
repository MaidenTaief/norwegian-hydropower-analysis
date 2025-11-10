#!/usr/bin/env python3
"""
Hydrologi Data Processor
========================

Processes Norwegian hydrological measurement station data from shapefile format
and converts it to CSV for analysis. Based on the same methodology used in
the Norway hydropower analysis.

This script handles the Hydrologi_MaleserieMalestasjon shapefile data.
"""

import pandas as pd
import geopandas as gpd
import numpy as np
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

class HydrologiDataProcessor:
    """
    Processor for Norwegian hydrological measurement station data.
    Converts shapefile data to CSV format for further analysis.
    """
    
    def __init__(self, data_dir="Hydrologi"):
        self.data_dir = Path(data_dir)
        self.output_dir = Path("Hydrologi_Analysis")
        self.output_dir.mkdir(exist_ok=True)
        
        print("🔄 Initializing Hydrologi Data Processor...")
        self.load_data()
        
    def load_data(self):
        """Load hydrological measurement station data."""
        print("📊 Loading hydrological measurement station data...")
        
        try:
            # Load the shapefile
            self.hydrologi_gdf = gpd.read_file(self.data_dir / "Hydrologi_MaleserieMalestasjon.shp")
            print(f"✅ Loaded {len(self.hydrologi_gdf)} hydrological measurement stations")
            
            # Display basic information about the data
            self.display_data_info()
            
        except Exception as e:
            print(f"❌ Error loading hydrological data: {e}")
            raise
    
    def display_data_info(self):
        """Display comprehensive information about the loaded data."""
        print("\n" + "="*80)
        print("📋 HYDROLOGI MEASUREMENT STATION DATA SUMMARY")
        print("="*80)
        
        # Basic info
        print(f"🔢 Total number of measurement stations: {len(self.hydrologi_gdf):,}")
        print(f"📐 Coordinate Reference System: {self.hydrologi_gdf.crs}")
        print(f"📊 Data shape: {self.hydrologi_gdf.shape}")
        
        # Column information
        print(f"\n📝 Columns ({len(self.hydrologi_gdf.columns)}):")
        for i, col in enumerate(self.hydrologi_gdf.columns, 1):
            dtype = self.hydrologi_gdf[col].dtype
            non_null = self.hydrologi_gdf[col].notna().sum()
            print(f"   {i:2d}. {col:25} | {str(dtype):15} | {non_null:,} non-null values")
        
        # Sample data
        print(f"\n📋 Sample data (first 3 rows):")
        print(self.hydrologi_gdf.head(3).to_string())
        
        # Geometry info
        if 'geometry' in self.hydrologi_gdf.columns:
            bounds = self.hydrologi_gdf.total_bounds
            print(f"\n🗺️ Geographic bounds:")
            print(f"   Min longitude: {bounds[0]:.6f}")
            print(f"   Min latitude:  {bounds[1]:.6f}")
            print(f"   Max longitude: {bounds[2]:.6f}")
            print(f"   Max latitude:  {bounds[3]:.6f}")
        
        # Data quality check
        print(f"\n🔍 Data Quality Summary:")
        for col in self.hydrologi_gdf.columns:
            if col != 'geometry':
                null_count = self.hydrologi_gdf[col].isna().sum()
                null_pct = (null_count / len(self.hydrologi_gdf)) * 100
                print(f"   {col:25} | {null_count:,} nulls ({null_pct:.1f}%)")
    
    def create_csv_output(self):
        """Convert shapefile data to CSV format with geometry coordinates."""
        print("\n🔄 Converting to CSV format...")
        
        # Create a copy of the dataframe
        df_output = self.hydrologi_gdf.copy()
        
        # Extract coordinates from geometry
        if 'geometry' in df_output.columns:
            # Get X and Y coordinates
            df_output['longitude'] = df_output.geometry.x
            df_output['latitude'] = df_output.geometry.y
            
            # Drop the geometry column for CSV export
            df_output = df_output.drop('geometry', axis=1)
        
        # Save to CSV
        csv_path = self.output_dir / "Hydrologi_MaleserieMalestasjon.csv"
        df_output.to_csv(csv_path, index=False, encoding='utf-8')
        
        print(f"✅ CSV file created: {csv_path}")
        print(f"📊 CSV contains {len(df_output)} rows and {len(df_output.columns)} columns")
        
        # Create a summary file
        self.create_data_summary(df_output)
        
        return df_output
    
    def create_data_summary(self, df):
        """Create a comprehensive data summary report."""
        summary_path = self.output_dir / "HYDROLOGI_DATA_SUMMARY.md"
        
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write("# Hydrologi Measurement Station Data Summary\n\n")
            f.write(f"**Generated:** {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("## Dataset Overview\n\n")
            f.write(f"- **Source file:** Hydrologi_MaleserieMalestasjon.shp\n")
            f.write(f"- **Total stations:** {len(df):,}\n")
            f.write(f"- **Columns:** {len(df.columns)}\n")
            f.write(f"- **Geographic coverage:** Norwegian hydrological measurement stations\n\n")
            
            f.write("## Column Information\n\n")
            f.write("| Column | Data Type | Non-null Count | Description |\n")
            f.write("|--------|-----------|----------------|-------------|\n")
            
            for col in df.columns:
                dtype = str(df[col].dtype)
                non_null = df[col].notna().sum()
                # Try to infer description based on column name
                desc = self._infer_column_description(col)
                f.write(f"| {col} | {dtype} | {non_null:,} | {desc} |\n")
            
            f.write("\n## Data Quality\n\n")
            f.write("| Column | Missing Values | Missing % |\n")
            f.write("|--------|----------------|----------|\n")
            
            for col in df.columns:
                null_count = df[col].isna().sum()
                null_pct = (null_count / len(df)) * 100
                f.write(f"| {col} | {null_count:,} | {null_pct:.1f}% |\n")
            
            # Geographic bounds
            if 'longitude' in df.columns and 'latitude' in df.columns:
                f.write("\n## Geographic Coverage\n\n")
                f.write(f"- **Longitude range:** {df['longitude'].min():.6f} to {df['longitude'].max():.6f}\n")
                f.write(f"- **Latitude range:** {df['latitude'].min():.6f} to {df['latitude'].max():.6f}\n")
            
            f.write("\n## Sample Data\n\n")
            f.write("```\n")
            f.write(df.head().to_string())
            f.write("\n```\n")
            
            f.write("\n## Usage\n\n")
            f.write("This CSV file can be used for:\n")
            f.write("- Hydrological station analysis\n")
            f.write("- Geographic mapping of measurement networks\n")
            f.write("- Integration with weather and climate data\n")
            f.write("- Statistical analysis of measurement station distribution\n")
        
        print(f"📄 Data summary created: {summary_path}")
    
    def _infer_column_description(self, col_name):
        """Infer column description based on name."""
        col_lower = col_name.lower()
        
        descriptions = {
            'stasjon': 'Station identifier',
            'navn': 'Station name',
            'type': 'Station type',
            'hoh': 'Height above sea level',
            'kommune': 'Municipality',
            'fylke': 'County',
            'vassomr': 'Water area/watershed',
            'vassdrag': 'Watercourse',
            'lon': 'Longitude coordinate',
            'lat': 'Latitude coordinate',
            'longitude': 'Longitude coordinate (extracted from geometry)',
            'latitude': 'Latitude coordinate (extracted from geometry)',
            'eier': 'Owner',
            'drift': 'Operation status',
            'fra_dato': 'Start date',
            'til_dato': 'End date',
        }
        
        for key, desc in descriptions.items():
            if key in col_lower:
                return desc
        
        return 'Data field (description to be determined)'
    
    def run_analysis(self):
        """Run the complete analysis pipeline."""
        print("\n🚀 Starting Hydrologi data processing...")
        
        # Convert to CSV
        df_csv = self.create_csv_output()
        
        print("\n✅ Hydrologi data processing completed!")
        print(f"📁 Output directory: {self.output_dir}")
        print(f"📄 CSV file: Hydrologi_MaleserieMalestasjon.csv")
        print(f"📄 Summary file: HYDROLOGI_DATA_SUMMARY.md")
        
        return df_csv

def main():
    """Main execution function."""
    print("🌊 Norwegian Hydrologi Data Processor")
    print("="*50)
    
    try:
        # Initialize processor
        processor = HydrologiDataProcessor()
        
        # Run analysis
        df_result = processor.run_analysis()
        
        print(f"\n🎉 Processing complete! CSV ready for analysis.")
        
    except Exception as e:
        print(f"\n❌ Error during processing: {e}")
        raise

if __name__ == "__main__":
    main()
