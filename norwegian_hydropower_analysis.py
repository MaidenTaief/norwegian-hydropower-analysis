#!/usr/bin/env python3
"""
Norwegian Hydropower Data Analysis Workflow
===========================================

This script demonstrates a complete workflow for loading, exploring, and preparing 
Norwegian hydropower data (dams and reservoirs) provided in shapefile format.

The workflow includes:
1. Data loading and conversion (.dbf to .csv)
2. Understanding data content
3. Spatial data exploration (.shp loading)
4. Combining attributes and geometry (export to CSV with WKT)
5. Export for visualization (to KML)

Author: Data Analysis Workflow
Date: 2024
"""

import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Set up plotting style
plt.style.use('default')
sns.set_palette("husl")

class NorwegianHydropowerAnalyzer:
    """
    A comprehensive analyzer for Norwegian hydropower data from NVE.
    """
    
    def __init__(self, data_dir="Data"):
        """
        Initialize the analyzer with the data directory.
        
        Parameters:
        -----------
        data_dir : str
            Path to the directory containing the shapefile data
        """
        self.data_dir = Path(data_dir)
        self.output_dir = Path("output")
        self.output_dir.mkdir(exist_ok=True)
        
        # Initialize data containers
        self.dam_linje_df = None
        self.dam_punkt_df = None
        self.magasin_df = None
        self.dam_linje_gdf = None
        self.dam_punkt_gdf = None
        self.magasin_gdf = None
        
        print(f"Norwegian Hydropower Data Analyzer initialized")
        print(f"Data directory: {self.data_dir}")
        print(f"Output directory: {self.output_dir}")
    
    def load_dbf_files(self):
        """
        Step 1: Load .dbf files and convert to CSV format.
        """
        print("\n" + "="*60)
        print("STEP 1: Loading .dbf files and converting to CSV")
        print("="*60)
        
        try:
            # Load dam line data
            print("Loading Vannkraft_DamLinje.dbf...")
            self.dam_linje_df = pd.read_csv(self.data_dir / "Vannkraft_DamLinje.dbf", 
                                          encoding='latin-1', low_memory=False)
            
            # Load dam point data
            print("Loading Vannkraft_DamPunkt.dbf...")
            self.dam_punkt_df = pd.read_csv(self.data_dir / "Vannkraft_DamPunkt.dbf", 
                                          encoding='latin-1', low_memory=False)
            
            # Load reservoir data
            print("Loading Vannkraft_Magasin.dbf...")
            self.magasin_df = pd.read_csv(self.data_dir / "Vannkraft_Magasin.dbf", 
                                        encoding='latin-1', low_memory=False)
            
            # Save as CSV files
            print("Saving converted CSV files...")
            self.dam_linje_df.to_csv(self.output_dir / "Vannkraft_DamLinje.csv", index=False)
            self.dam_punkt_df.to_csv(self.output_dir / "Vannkraft_DamPunkt.csv", index=False)
            self.magasin_df.to_csv(self.output_dir / "Vannkraft_Magasin.csv", index=False)
            
            print("✓ Successfully loaded and converted all .dbf files to CSV")
            
        except Exception as e:
            print(f"Error loading .dbf files: {e}")
            # Try alternative approach with simpledbf if available
            try:
                from simpledbf import Dbf5
                print("Trying alternative approach with simpledbf...")
                
                # Load dam line data
                dbf = Dbf5(str(self.data_dir / "Vannkraft_DamLinje.dbf"))
                self.dam_linje_df = dbf.to_dataframe()
                
                # Load dam point data
                dbf = Dbf5(str(self.data_dir / "Vannkraft_DamPunkt.dbf"))
                self.dam_punkt_df = dbf.to_dataframe()
                
                # Load reservoir data
                dbf = Dbf5(str(self.data_dir / "Vannkraft_Magasin.dbf"))
                self.magasin_df = dbf.to_dataframe()
                
                # Save as CSV files
                self.dam_linje_df.to_csv(self.output_dir / "Vannkraft_DamLinje.csv", index=False)
                self.dam_punkt_df.to_csv(self.output_dir / "Vannkraft_DamPunkt.csv", index=False)
                self.magasin_df.to_csv(self.output_dir / "Vannkraft_Magasin.csv", index=False)
                
                print("✓ Successfully loaded and converted all .dbf files to CSV using simpledbf")
                
            except ImportError:
                print("simpledbf not available. Please install it with: pip install simpledbf")
                return False
            except Exception as e2:
                print(f"Error with simpledbf approach: {e2}")
                return False
        
        return True
    
    def explore_data_content(self):
        """
        Step 2: Understand the content of the loaded data.
        """
        print("\n" + "="*60)
        print("STEP 2: Understanding Data Content")
        print("="*60)
        
        if self.dam_linje_df is None or self.dam_punkt_df is None or self.magasin_df is None:
            print("❌ Data not loaded. Please run load_dbf_files() first.")
            return
        
        # Explore dam line data
        print("\n--- Dam Line Data (Vannkraft_DamLinje) ---")
        print(f"Shape: {self.dam_linje_df.shape}")
        print(f"Columns: {list(self.dam_linje_df.columns)}")
        print("\nFirst few rows:")
        print(self.dam_linje_df.head())
        print("\nData types and non-null counts:")
        print(self.dam_linje_df.info())
        
        # Explore dam point data
        print("\n--- Dam Point Data (Vannkraft_DamPunkt) ---")
        print(f"Shape: {self.dam_punkt_df.shape}")
        print(f"Columns: {list(self.dam_punkt_df.columns)}")
        print("\nFirst few rows:")
        print(self.dam_punkt_df.head())
        print("\nData types and non-null counts:")
        print(self.dam_punkt_df.info())
        
        # Explore reservoir data
        print("\n--- Reservoir Data (Vannkraft_Magasin) ---")
        print(f"Shape: {self.magasin_df.shape}")
        print(f"Columns: {list(self.magasin_df.columns)}")
        print("\nFirst few rows:")
        print(self.magasin_df.head())
        print("\nData types and non-null counts:")
        print(self.magasin_df.info())
        
        # Basic statistics for key columns
        print("\n--- Key Statistics ---")
        
        # Check for construction year data
        if 'idriftAar' in self.dam_linje_df.columns:
            print(f"\nDam Line Construction Years:")
            print(self.dam_linje_df['idriftAar'].describe())
        
        if 'idriftAar' in self.dam_punkt_df.columns:
            print(f"\nDam Point Construction Years:")
            print(self.dam_punkt_df['idriftAar'].describe())
        
        # Check for reservoir area data
        if 'areal_km2' in self.magasin_df.columns:
            print(f"\nReservoir Areas (km²):")
            print(self.magasin_df['areal_km2'].describe())
        
        # Check for capacity data
        if 'volOppdemt' in self.magasin_df.columns:
            print(f"\nReservoir Volumes (million m³):")
            print(self.magasin_df['volOppdemt'].describe())
    
    def load_spatial_data(self):
        """
        Step 3: Load spatial data from .shp files.
        """
        print("\n" + "="*60)
        print("STEP 3: Loading Spatial Data (.shp files)")
        print("="*60)
        
        success = True
        
        try:
            # Load dam line spatial data
            print("Loading Vannkraft_DamLinje.shp...")
            self.dam_linje_gdf = gpd.read_file(self.data_dir / "Vannkraft_DamLinje.shp")
            print(f"✓ Loaded {len(self.dam_linje_gdf)} dam line features")
        except Exception as e:
            print(f"⚠️  Warning: Could not load dam line spatial data: {e}")
            print("   Continuing with attribute data only...")
            success = False
        
        try:
            # Load dam point spatial data
            print("Loading Vannkraft_DamPunkt.shp...")
            self.dam_punkt_gdf = gpd.read_file(self.data_dir / "Vannkraft_DamPunkt.shp")
            print(f"✓ Loaded {len(self.dam_punkt_gdf)} dam point features")
        except Exception as e:
            print(f"⚠️  Warning: Could not load dam point spatial data: {e}")
            print("   Continuing with attribute data only...")
            success = False
        
        try:
            # Load reservoir spatial data
            print("Loading Vannkraft_Magasin.shp...")
            self.magasin_gdf = gpd.read_file(self.data_dir / "Vannkraft_Magasin.shp")
            print(f"✓ Loaded {len(self.magasin_gdf)} reservoir features")
        except Exception as e:
            print(f"⚠️  Warning: Could not load reservoir spatial data: {e}")
            print("   Continuing with attribute data only...")
            success = False
        
        # Display spatial information for successfully loaded data
        if self.dam_linje_gdf is not None:
            print(f"\n--- Spatial Information ---")
            print(f"Dam Lines CRS: {self.dam_linje_gdf.crs}")
            print(f"Dam Lines Bounds: {self.dam_linje_gdf.total_bounds}")
        
        if self.dam_punkt_gdf is not None:
            print(f"Dam Points CRS: {self.dam_punkt_gdf.crs}")
            print(f"Dam Points Bounds: {self.dam_punkt_gdf.total_bounds}")
        
        if self.magasin_gdf is not None:
            print(f"Reservoirs CRS: {self.magasin_gdf.crs}")
            print(f"Reservoirs Bounds: {self.magasin_gdf.total_bounds}")
        
        return success
    
    def combine_attributes_geometry(self):
        """
        Step 4: Combine attributes and geometry, export to CSV with WKT.
        """
        print("\n" + "="*60)
        print("STEP 4: Combining Attributes and Geometry (WKT Export)")
        print("="*60)
        
        success = True
        
        # Process dam line data
        if self.dam_linje_gdf is not None:
            try:
                print("Processing dam line data...")
                dam_linje_with_geom = self.dam_linje_gdf.copy()
                dam_linje_with_geom['geometry_wkt'] = dam_linje_with_geom.geometry.to_wkt()
                dam_linje_with_geom = dam_linje_with_geom.drop(columns=['geometry'])
                dam_linje_with_geom.to_csv(self.output_dir / "Vannkraft_DamLinje_with_geometry.csv", index=False)
                print(f"✓ Exported {len(dam_linje_with_geom)} dam line records with WKT geometry")
            except Exception as e:
                print(f"❌ Error processing dam line geometry: {e}")
                success = False
        else:
            print("⚠️  Skipping dam line geometry processing (no spatial data)")
        
        # Process dam point data
        if self.dam_punkt_gdf is not None:
            try:
                print("Processing dam point data...")
                dam_punkt_with_geom = self.dam_punkt_gdf.copy()
                dam_punkt_with_geom['geometry_wkt'] = dam_punkt_with_geom.geometry.to_wkt()
                dam_punkt_with_geom = dam_punkt_with_geom.drop(columns=['geometry'])
                dam_punkt_with_geom.to_csv(self.output_dir / "Vannkraft_DamPunkt_with_geometry.csv", index=False)
                print(f"✓ Exported {len(dam_punkt_with_geom)} dam point records with WKT geometry")
            except Exception as e:
                print(f"❌ Error processing dam point geometry: {e}")
                success = False
        else:
            print("⚠️  Skipping dam point geometry processing (no spatial data)")
        
        # Process reservoir data
        if self.magasin_gdf is not None:
            try:
                print("Processing reservoir data...")
                magasin_with_geom = self.magasin_gdf.copy()
                magasin_with_geom['geometry_wkt'] = magasin_with_geom.geometry.to_wkt()
                magasin_with_geom = magasin_with_geom.drop(columns=['geometry'])
                magasin_with_geom.to_csv(self.output_dir / "Vannkraft_Magasin_with_geometry.csv", index=False)
                print(f"✓ Exported {len(magasin_with_geom)} reservoir records with WKT geometry")
            except Exception as e:
                print(f"❌ Error processing reservoir geometry: {e}")
                success = False
        else:
            print("⚠️  Skipping reservoir geometry processing (no spatial data)")
        
        return success
    
    def export_for_visualization(self):
        """
        Step 5: Export data for visualization (multiple formats).
        """
        print("\n" + "="*60)
        print("STEP 5: Export for Visualization")
        print("="*60)
        
        success = True
        
        # Process dam line data
        if self.dam_linje_gdf is not None:
            try:
                # Prepare dam line data for export
                print("Preparing dam line data for visualization...")
                dam_linje_subset = self.dam_linje_gdf.copy()
                
                # Select relevant columns
                relevant_columns = ['damNavn', 'idriftAar', 'formal_L', 'geometry']
                available_columns = [col for col in relevant_columns if col in dam_linje_subset.columns]
                
                if available_columns:
                    dam_linje_subset = dam_linje_subset[available_columns]
                
                # Convert to WGS84 for visualization
                if dam_linje_subset.crs != 'EPSG:4326':
                    dam_linje_subset = dam_linje_subset.to_crs('EPSG:4326')
                
                # Export to GeoJSON (widely supported)
                dam_linje_subset.to_file(self.output_dir / "Vannkraft_DamLinje_visualization.geojson", 
                                       driver='GeoJSON')
                print(f"✓ Exported {len(dam_linje_subset)} dam line features to GeoJSON")
                
                # Try KML export if available
                try:
                    dam_linje_subset.to_file(self.output_dir / "Vannkraft_DamLinje_subset.kml", 
                                           driver='KML')
                    print(f"✓ Exported {len(dam_linje_subset)} dam line features to KML")
                except Exception as kml_error:
                    print(f"⚠️  KML export not available: {kml_error}")
                    print("   GeoJSON format can be used in Google Earth Pro and many other tools")
                
            except Exception as e:
                print(f"❌ Error processing dam line data for visualization: {e}")
                success = False
        else:
            print("⚠️  Skipping dam line visualization (no spatial data)")
        
        # Process dam point data
        if self.dam_punkt_gdf is not None:
            try:
                print("Preparing dam point data for visualization...")
                dam_punkt_subset = self.dam_punkt_gdf.copy()
                
                # Select relevant columns
                relevant_columns = ['damNavn', 'idriftAar', 'formal_L', 'geometry']
                available_columns = [col for col in relevant_columns if col in dam_punkt_subset.columns]
                
                if available_columns:
                    dam_punkt_subset = dam_punkt_subset[available_columns]
                
                # Convert to WGS84 for visualization
                if dam_punkt_subset.crs != 'EPSG:4326':
                    dam_punkt_subset = dam_punkt_subset.to_crs('EPSG:4326')
                
                # Export to GeoJSON
                dam_punkt_subset.to_file(self.output_dir / "Vannkraft_DamPunkt_visualization.geojson", 
                                       driver='GeoJSON')
                print(f"✓ Exported {len(dam_punkt_subset)} dam point features to GeoJSON")
                
            except Exception as e:
                print(f"❌ Error processing dam point data for visualization: {e}")
                success = False
        else:
            print("⚠️  Skipping dam point visualization (no spatial data)")
        
        # Process reservoir data
        if self.magasin_gdf is not None:
            try:
                print("Preparing reservoir data for visualization...")
                magasin_subset = self.magasin_gdf.copy()
                
                # Select relevant columns
                relevant_columns = ['magNavn', 'areal_km2', 'volOppdemt', 'geometry']
                available_columns = [col for col in relevant_columns if col in magasin_subset.columns]
                
                if available_columns:
                    magasin_subset = magasin_subset[available_columns]
                
                # Simplify complex geometries to reduce file size
                print("Simplifying reservoir geometries...")
                magasin_simplified = magasin_subset.copy()
                magasin_simplified['geometry'] = magasin_simplified.geometry.simplify(tolerance=50)  # 50 meters
                
                # Convert to WGS84 for visualization
                if magasin_simplified.crs != 'EPSG:4326':
                    magasin_simplified = magasin_simplified.to_crs('EPSG:4326')
                
                # Export to GeoJSON
                magasin_simplified.to_file(self.output_dir / "Vannkraft_Magasin_simplified_50m.geojson", 
                                         driver='GeoJSON')
                print(f"✓ Exported {len(magasin_simplified)} simplified reservoir features to GeoJSON")
                
                # Try KML export if available
                try:
                    magasin_simplified.to_file(self.output_dir / "Vannkraft_Magasin_simplified_50m.kml", 
                                             driver='KML')
                    print(f"✓ Exported {len(magasin_simplified)} simplified reservoir features to KML")
                except Exception as kml_error:
                    print(f"⚠️  KML export not available: {kml_error}")
                    print("   GeoJSON format can be used in Google Earth Pro and many other tools")
                
            except Exception as e:
                print(f"❌ Error processing reservoir data for visualization: {e}")
                success = False
        else:
            print("⚠️  Skipping reservoir visualization (no spatial data)")
        
        return success
    
    def create_visualizations(self):
        """
        Create basic visualizations of the data.
        """
        print("\n" + "="*60)
        print("Creating Basic Visualizations")
        print("="*60)
        
        if self.dam_linje_gdf is None or self.magasin_gdf is None:
            print("❌ Spatial data not loaded. Please run load_spatial_data() first.")
            return
        
        try:
            # Create a map showing all features
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 8))
            
            # Plot dam lines
            self.dam_linje_gdf.plot(ax=ax1, color='red', linewidth=0.5, alpha=0.7)
            ax1.set_title('Norwegian Dam Lines')
            ax1.set_xlabel('Longitude')
            ax1.set_ylabel('Latitude')
            ax1.grid(True, alpha=0.3)
            
            # Plot reservoirs
            self.magasin_gdf.plot(ax=ax2, color='blue', alpha=0.6)
            ax2.set_title('Norwegian Reservoirs')
            ax2.set_xlabel('Longitude')
            ax2.set_ylabel('Latitude')
            ax2.grid(True, alpha=0.3)
            
            plt.tight_layout()
            plt.savefig(self.output_dir / "norwegian_hydropower_overview.png", 
                       dpi=300, bbox_inches='tight')
            print("✓ Saved overview map to norwegian_hydropower_overview.png")
            
            # Create histograms for key attributes
            fig, axes = plt.subplots(2, 2, figsize=(15, 10))
            
            # Construction year histogram (if available)
            if 'idriftAar' in self.dam_linje_gdf.columns:
                self.dam_linje_gdf['idriftAar'].hist(ax=axes[0,0], bins=30, alpha=0.7, color='red')
                axes[0,0].set_title('Dam Construction Years')
                axes[0,0].set_xlabel('Year')
                axes[0,0].set_ylabel('Number of Dams')
            
            # Reservoir area histogram (if available)
            if 'areal_km2' in self.magasin_gdf.columns:
                self.magasin_gdf['areal_km2'].hist(ax=axes[0,1], bins=30, alpha=0.7, color='blue')
                axes[0,1].set_title('Reservoir Areas')
                axes[0,1].set_xlabel('Area (km²)')
                axes[0,1].set_ylabel('Number of Reservoirs')
            
            # Reservoir volume histogram (if available)
            if 'volOppdemt' in self.magasin_gdf.columns:
                self.magasin_gdf['volOppdemt'].hist(ax=axes[1,0], bins=30, alpha=0.7, color='green')
                axes[1,0].set_title('Reservoir Volumes')
                axes[1,0].set_xlabel('Volume (million m³)')
                axes[1,0].set_ylabel('Number of Reservoirs')
            
            # Combined map
            ax_combined = axes[1,1]
            self.magasin_gdf.plot(ax=ax_combined, color='blue', alpha=0.4)
            self.dam_linje_gdf.plot(ax=ax_combined, color='red', linewidth=0.5, alpha=0.8)
            ax_combined.set_title('Combined View: Dams and Reservoirs')
            ax_combined.set_xlabel('Longitude')
            ax_combined.set_ylabel('Latitude')
            
            plt.tight_layout()
            plt.savefig(self.output_dir / "norwegian_hydropower_analysis.png", 
                       dpi=300, bbox_inches='tight')
            print("✓ Saved analysis plots to norwegian_hydropower_analysis.png")
            
        except Exception as e:
            print(f"❌ Error creating visualizations: {e}")
    
    def generate_summary_report(self):
        """
        Generate a comprehensive summary report.
        """
        print("\n" + "="*60)
        print("Generating Summary Report")
        print("="*60)
        
        report = []
        report.append("NORWEGIAN HYDROPOWER DATA ANALYSIS REPORT")
        report.append("=" * 50)
        report.append("")
        
        if self.dam_linje_df is not None:
            report.append(f"Dam Lines: {len(self.dam_linje_df)} features")
        if self.dam_punkt_df is not None:
            report.append(f"Dam Points: {len(self.dam_punkt_df)} features")
        if self.magasin_df is not None:
            report.append(f"Reservoirs: {len(self.magasin_df)} features")
        
        report.append("")
        report.append("OUTPUT FILES GENERATED:")
        report.append("-" * 30)
        
        # List generated files
        output_files = list(self.output_dir.glob("*"))
        for file in output_files:
            if file.is_file():
                size_mb = file.stat().st_size / (1024 * 1024)
                report.append(f"• {file.name} ({size_mb:.2f} MB)")
        
        report.append("")
        report.append("NEXT STEPS:")
        report.append("-" * 30)
        report.append("1. Open KML files in Google Earth for interactive visualization")
        report.append("2. Use CSV files with WKT geometry for further spatial analysis")
        report.append("3. Analyze attribute data for patterns and trends")
        report.append("4. Integrate with external datasets (weather, population, etc.)")
        report.append("5. Create custom visualizations and dashboards")
        
        # Save report
        report_text = "\n".join(report)
        with open(self.output_dir / "analysis_report.txt", "w") as f:
            f.write(report_text)
        
        print("✓ Generated summary report: analysis_report.txt")
        print("\n" + report_text)
    
    def run_complete_workflow(self):
        """
        Run the complete analysis workflow.
        """
        print("🚀 Starting Norwegian Hydropower Data Analysis Workflow")
        print("=" * 60)
        
        # Step 1: Load and convert data
        if not self.load_dbf_files():
            print("❌ Failed to load .dbf files. Stopping workflow.")
            return False
        
        # Step 2: Explore data content
        self.explore_data_content()
        
        # Step 3: Load spatial data
        if not self.load_spatial_data():
            print("❌ Failed to load spatial data. Stopping workflow.")
            return False
        
        # Step 4: Combine attributes and geometry
        if not self.combine_attributes_geometry():
            print("❌ Failed to combine attributes and geometry. Stopping workflow.")
            return False
        
        # Step 5: Export for visualization
        self.export_for_visualization()
        # Continue even if visualization export has issues
        
        # Create visualizations
        self.create_visualizations()
        
        # Generate summary report
        self.generate_summary_report()
        
        print("\n🎉 Workflow completed successfully!")
        print(f"All output files saved to: {self.output_dir}")
        return True


def main():
    """
    Main function to run the analysis.
    """
    # Create analyzer instance
    analyzer = NorwegianHydropowerAnalyzer()
    
    # Run complete workflow
    success = analyzer.run_complete_workflow()
    
    if success:
        print("\n✅ Analysis completed successfully!")
        print("Check the 'output' directory for all generated files.")
    else:
        print("\n❌ Analysis failed. Please check the error messages above.")


if __name__ == "__main__":
    main() 