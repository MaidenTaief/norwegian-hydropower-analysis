#!/usr/bin/env python3
"""
Example Usage of Norwegian Hydropower Data Analyzer
==================================================

This script demonstrates various ways to use the NorwegianHydropowerAnalyzer
class for different analysis scenarios.
"""

from norwegian_hydropower_analysis import NorwegianHydropowerAnalyzer
import pandas as pd
import geopandas as gpd

def example_basic_workflow():
    """
    Example 1: Basic complete workflow
    """
    print("Example 1: Basic Complete Workflow")
    print("=" * 40)
    
    # Create analyzer and run complete workflow
    analyzer = NorwegianHydropowerAnalyzer()
    success = analyzer.run_complete_workflow()
    
    if success:
        print("✓ Basic workflow completed successfully!")
    else:
        print("❌ Basic workflow failed!")

def example_step_by_step():
    """
    Example 2: Step-by-step workflow with custom processing
    """
    print("\nExample 2: Step-by-Step Workflow")
    print("=" * 40)
    
    analyzer = NorwegianHydropowerAnalyzer()
    
    # Step 1: Load data
    print("Loading .dbf files...")
    if analyzer.load_dbf_files():
        print("✓ Data loaded successfully")
        
        # Step 2: Explore data
        print("\nExploring data content...")
        analyzer.explore_data_content()
        
        # Step 3: Load spatial data
        print("\nLoading spatial data...")
        if analyzer.load_spatial_data():
            print("✓ Spatial data loaded successfully")
            
            # Custom analysis: Filter by construction year
            if 'idriftAar' in analyzer.dam_linje_gdf.columns:
                print("\nCustom Analysis: Dams built after 1980")
                recent_dams = analyzer.dam_linje_gdf[
                    analyzer.dam_linje_gdf['idriftAar'] > 1980
                ]
                print(f"Found {len(recent_dams)} dams built after 1980")
                
                # Save filtered data
                recent_dams.to_csv(analyzer.output_dir / "recent_dams_after_1980.csv", index=False)
                print("✓ Saved filtered data to recent_dams_after_1980.csv")
            
            # Step 4: Combine attributes and geometry
            print("\nCombining attributes and geometry...")
            analyzer.combine_attributes_geometry()
            
            # Step 5: Export for visualization
            print("\nExporting for visualization...")
            analyzer.export_for_visualization()
            
            # Create visualizations
            print("\nCreating visualizations...")
            analyzer.create_visualizations()
            
            # Generate report
            print("\nGenerating summary report...")
            analyzer.generate_summary_report()
            
            print("✓ Step-by-step workflow completed!")
        else:
            print("❌ Failed to load spatial data")
    else:
        print("❌ Failed to load .dbf files")

def example_custom_analysis():
    """
    Example 3: Custom analysis focusing on specific aspects
    """
    print("\nExample 3: Custom Analysis")
    print("=" * 40)
    
    analyzer = NorwegianHydropowerAnalyzer()
    
    # Load data
    if not analyzer.load_dbf_files():
        print("❌ Failed to load data")
        return
    
    if not analyzer.load_spatial_data():
        print("❌ Failed to load spatial data")
        return
    
    # Custom analysis 1: Reservoir size analysis
    print("Analyzing reservoir sizes...")
    if 'areal_km2' in analyzer.magasin_gdf.columns:
        large_reservoirs = analyzer.magasin_gdf[
            analyzer.magasin_gdf['areal_km2'] > 10
        ]
        print(f"Found {len(large_reservoirs)} reservoirs larger than 10 km²")
        
        # Save large reservoirs
        large_reservoirs.to_csv(analyzer.output_dir / "large_reservoirs.csv", index=False)
        print("✓ Saved large reservoirs data")
    
    # Custom analysis 2: Dam purpose analysis
    print("\nAnalyzing dam purposes...")
    if 'formal_L' in analyzer.dam_linje_gdf.columns:
        purpose_counts = analyzer.dam_linje_gdf['formal_L'].value_counts()
        print("Dam purposes:")
        for purpose, count in purpose_counts.items():
            print(f"  {purpose}: {count}")
        
        # Save purpose analysis
        purpose_counts.to_csv(analyzer.output_dir / "dam_purposes.csv")
        print("✓ Saved dam purposes analysis")
    
    # Custom analysis 3: Spatial distribution
    print("\nAnalyzing spatial distribution...")
    bounds = analyzer.magasin_gdf.total_bounds
    print(f"Reservoir extent: {bounds}")
    
    # Calculate center point
    center_lon = (bounds[0] + bounds[2]) / 2
    center_lat = (bounds[1] + bounds[3]) / 2
    print(f"Center point: {center_lon:.4f}, {center_lat:.4f}")
    
    # Save spatial summary
    spatial_summary = pd.DataFrame({
        'metric': ['min_lon', 'min_lat', 'max_lon', 'max_lat', 'center_lon', 'center_lat'],
        'value': [bounds[0], bounds[1], bounds[2], bounds[3], center_lon, center_lat]
    })
    spatial_summary.to_csv(analyzer.output_dir / "spatial_summary.csv", index=False)
    print("✓ Saved spatial summary")

def example_data_export():
    """
    Example 4: Custom data export formats
    """
    print("\nExample 4: Custom Data Export")
    print("=" * 40)
    
    analyzer = NorwegianHydropowerAnalyzer()
    
    # Load data
    if not analyzer.load_dbf_files() or not analyzer.load_spatial_data():
        print("❌ Failed to load data")
        return
    
    # Export 1: JSON format
    print("Exporting to JSON format...")
    if analyzer.dam_linje_df is not None:
        analyzer.dam_linje_df.to_json(
            analyzer.output_dir / "dam_linje.json", 
            orient='records', 
            indent=2
        )
        print("✓ Exported dam lines to JSON")
    
    # Export 2: Excel format with multiple sheets
    print("Exporting to Excel format...")
    with pd.ExcelWriter(analyzer.output_dir / "norwegian_hydropower_data.xlsx") as writer:
        if analyzer.dam_linje_df is not None:
            analyzer.dam_linje_df.to_excel(writer, sheet_name='Dam_Lines', index=False)
        if analyzer.dam_punkt_df is not None:
            analyzer.dam_punkt_df.to_excel(writer, sheet_name='Dam_Points', index=False)
        if analyzer.magasin_df is not None:
            analyzer.magasin_df.to_excel(writer, sheet_name='Reservoirs', index=False)
    print("✓ Exported all data to Excel")
    
    # Export 3: GeoJSON format
    print("Exporting to GeoJSON format...")
    if analyzer.dam_linje_gdf is not None:
        analyzer.dam_linje_gdf.to_file(
            analyzer.output_dir / "dam_linje.geojson", 
            driver='GeoJSON'
        )
        print("✓ Exported dam lines to GeoJSON")
    
    if analyzer.magasin_gdf is not None:
        analyzer.magasin_gdf.to_file(
            analyzer.output_dir / "magasin.geojson", 
            driver='GeoJSON'
        )
        print("✓ Exported reservoirs to GeoJSON")

def main():
    """
    Run all examples
    """
    print("Norwegian Hydropower Data Analysis - Examples")
    print("=" * 50)
    
    # Run examples
    example_basic_workflow()
    example_step_by_step()
    example_custom_analysis()
    example_data_export()
    
    print("\n🎉 All examples completed!")
    print("Check the 'output' directory for generated files.")

if __name__ == "__main__":
    main() 