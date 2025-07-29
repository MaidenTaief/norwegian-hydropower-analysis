#!/usr/bin/env python3
"""
KML Export - Fixed Version of User's Code
=========================================

This script implements the user's KML export code with proper coordinate
transformation and fallback options to ensure it works reliably.
"""

import geopandas as gpd
import pandas as pd
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

def main():
    print("🚀 Fixed KML Export Implementation")
    print("=" * 50)
    
    # First, load the geodataframes (Prerequisites for Step 5)
    print("Loading spatial data required for KML export...")
    
    try:
        # Load dam line data
        dam_linje_gdf = gpd.read_file("Data/Vannkraft_DamLinje.shp")
        print(f"✅ Loaded dam_linje_gdf: {len(dam_linje_gdf)} features")
        print(f"   Original CRS: {dam_linje_gdf.crs}")
    except Exception as e:
        print(f"❌ Error loading dam line data: {e}")
        dam_linje_gdf = None
    
    try:
        # Load reservoir data  
        magasin_gdf = gpd.read_file("Data/Vannkraft_Magasin.shp")
        print(f"✅ Loaded magasin_gdf: {len(magasin_gdf)} features")
        print(f"   Original CRS: {magasin_gdf.crs}")
    except Exception as e:
        print(f"❌ Error loading reservoir data: {e}")
        magasin_gdf = None
    
    print("\n" + "="*60)
    print("EXECUTING ENHANCED USER'S CODE:")
    print("="*60)
    
    # --- Step 5: Export for Visualization (to KML) ---
    # Requires dam_linje_gdf and magasin_gdf from Step 3

    print("\n--- Exporting to KML for Visualization ---")

    # Define output paths for KML files
    output_kml_dam_path = 'Vannkraft_DamLinje_subset.kml'
    output_kml_magasin_simplified_path = 'Vannkraft_Magasin_simplified_50m.kml' # Using the simplified version

    if dam_linje_gdf is not None:
        try:
            # Select a subset of relevant columns for dams before exporting to KML
            dam_linje_subset_kml = dam_linje_gdf[['damNr', 'damNavn', 'objType', 'formal_L', 'idriftAar', 'geometry']].copy()

            # ENHANCEMENT: Convert to WGS84 (required for KML)
            print(f"Converting dam line data to WGS84 for KML compatibility...")
            if dam_linje_subset_kml.crs != 'EPSG:4326':
                dam_linje_subset_kml = dam_linje_subset_kml.to_crs('EPSG:4326')
                print(f"   Converted from {dam_linje_gdf.crs} to EPSG:4326")

            # Export dam line data to KML
            print(f"Attempting to export dam line data to '{output_kml_dam_path}' with a subset of columns...")
            
            try:
                dam_linje_subset_kml.to_file(output_kml_dam_path, driver='KML')
                print(f"✅ Successfully exported dam line data to '{output_kml_dam_path}'.")
            except Exception as kml_error:
                print(f"⚠️  KML export failed: {kml_error}")
                # Fallback to GeoJSON
                geojson_path = output_kml_dam_path.replace('.kml', '.geojson')
                dam_linje_subset_kml.to_file(geojson_path, driver='GeoJSON')
                print(f"✅ Fallback: Exported to GeoJSON '{geojson_path}' (can be opened in Google Earth Pro)")

        except Exception as e:
            print(f"❌ Error exporting dam line data: {e}")
    else:
        print("dam_linje_gdf not available. Skipping KML export for dam lines.")


    if magasin_gdf is not None:
         # Define a tolerance for simplification (using the value that seemed to work better)
        tolerance = 50  # meters

        try:
            print(f"\nAttempting to simplify reservoir geometries with tolerance {tolerance} and export to KML...")
            # Simplify the reservoir geometries
            magasin_simplified_gdf = magasin_gdf.copy()
            magasin_simplified_gdf['geometry'] = magasin_simplified_gdf['geometry'].simplify(tolerance, preserve_topology=True)

            # Select a subset of relevant columns for reservoirs before exporting to KML
            # ENHANCEMENT: Check which columns actually exist
            available_columns = ['magasinNr', 'magNavn', 'objType', 'formal_L', 'areal_km2', 'volOppdemt', 'geometry']
            existing_columns = [col for col in available_columns if col in magasin_simplified_gdf.columns]
            print(f"   Available columns: {existing_columns}")
            
            magasin_subset_simplified_kml = magasin_simplified_gdf[existing_columns].copy()

            # ENHANCEMENT: Convert to WGS84 (required for KML)
            print(f"Converting reservoir data to WGS84 for KML compatibility...")
            if magasin_subset_simplified_kml.crs != 'EPSG:4326':
                magasin_subset_simplified_kml = magasin_subset_simplified_kml.to_crs('EPSG:4326')
                print(f"   Converted from {magasin_gdf.crs} to EPSG:4326")

            # Export the simplified reservoir data to KML
            try:
                magasin_subset_simplified_kml.to_file(output_kml_magasin_simplified_path, driver='KML')
                print(f"✅ Successfully exported simplified reservoir data to '{output_kml_magasin_simplified_path}'.")
            except Exception as kml_error:
                print(f"⚠️  KML export failed: {kml_error}")
                # Fallback to GeoJSON
                geojson_path = output_kml_magasin_simplified_path.replace('.kml', '.geojson')
                magasin_subset_simplified_kml.to_file(geojson_path, driver='GeoJSON')
                print(f"✅ Fallback: Exported to GeoJSON '{geojson_path}' (can be opened in Google Earth Pro)")

        except Exception as e:
            print(f"❌ Error exporting simplified reservoir data: {e}")
            print("You might need to adjust the simplification tolerance if the export still fails due to too many vertices.")
    else:
        print("magasin_gdf not available. Skipping KML export for reservoirs.")


    print("\n--- KML Export Complete ---")
    
    # Additional verification
    print("\n" + "="*60)
    print("VERIFICATION:")
    print("="*60)
    
    # Check if files were created
    kml_files = [output_kml_dam_path, output_kml_magasin_simplified_path]
    geojson_files = [f.replace('.kml', '.geojson') for f in kml_files]
    
    for kml_file, geojson_file in zip(kml_files, geojson_files):
        if Path(kml_file).exists():
            file_size = Path(kml_file).stat().st_size / (1024*1024)
            print(f"✅ {kml_file} created successfully ({file_size:.2f} MB)")
        elif Path(geojson_file).exists():
            file_size = Path(geojson_file).stat().st_size / (1024*1024)
            print(f"✅ {geojson_file} created successfully ({file_size:.2f} MB) [Fallback format]")
        else:
            print(f"❌ Neither {kml_file} nor {geojson_file} was created")
    
    print("\n📋 Usage Notes:")
    print("• KML files: Open directly in Google Earth")
    print("• GeoJSON files: Open in Google Earth Pro, QGIS, web applications")
    print("• Both formats contain geographic coordinates in WGS84")
    print("• Reservoir geometries are simplified to reduce file size")
    print("• Files include selected attribute data for each feature")
    
    print("\n💡 If KML export failed:")
    print("• The GeoJSON fallback files work in most applications")
    print("• To enable KML support: conda install -c conda-forge gdal")

if __name__ == "__main__":
    main() 