#!/usr/bin/env python3
"""
KML Export Script for Norwegian Hydropower Data
==============================================

This script specifically handles KML export with fallback options
for visualization in Google Earth and other KML-compatible applications.
"""

import geopandas as gpd
import pandas as pd
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

def check_kml_support():
    """
    Check if KML driver is available in the current geopandas installation.
    """
    try:
        import fiona
        available_drivers = fiona.supported_drivers
        return 'KML' in available_drivers
    except:
        return False

def export_to_kml_with_fallback(gdf, output_path, data_type="data"):
    """
    Export GeoDataFrame to KML with fallback options.
    
    Parameters:
    -----------
    gdf : GeoDataFrame
        The data to export
    output_path : str
        Path for the KML file
    data_type : str
        Description of data type for error messages
    """
    try:
        print(f"Attempting to export {data_type} to '{output_path}'...")
        
        # Ensure we're in WGS84 for KML
        if gdf.crs != 'EPSG:4326':
            print(f"Converting {data_type} from {gdf.crs} to WGS84...")
            gdf_wgs84 = gdf.to_crs('EPSG:4326')
        else:
            gdf_wgs84 = gdf.copy()
        
        # Try KML export
        gdf_wgs84.to_file(output_path, driver='KML')
        print(f"✅ Successfully exported {data_type} to '{output_path}'.")
        return True
        
    except Exception as e:
        print(f"❌ Error exporting {data_type} to KML: {e}")
        
        # Fallback to GeoJSON
        geojson_path = output_path.replace('.kml', '.geojson')
        try:
            gdf_wgs84.to_file(geojson_path, driver='GeoJSON')
            print(f"✅ Fallback: Exported {data_type} to GeoJSON: '{geojson_path}'")
            print("   Note: GeoJSON can be opened in Google Earth Pro")
            return False
        except Exception as e2:
            print(f"❌ Fallback also failed: {e2}")
            return False

def main():
    """
    Main function to export Norwegian hydropower data to KML.
    """
    print("🚀 Norwegian Hydropower Data - KML Export")
    print("=" * 50)
    
    # Check KML support
    kml_supported = check_kml_support()
    print(f"KML Driver Support: {'✅ Available' if kml_supported else '❌ Not Available'}")
    
    if not kml_supported:
        print("⚠️  KML driver not available. Will use GeoJSON fallback.")
        print("   Install GDAL with KML support for native KML export.")
    
    print()
    
    # Load the spatial data
    data_dir = Path("Data")
    
    # Initialize variables
    dam_linje_gdf = None
    magasin_gdf = None
    
    # Load dam line data
    try:
        print("Loading dam line spatial data...")
        dam_linje_gdf = gpd.read_file(data_dir / "Vannkraft_DamLinje.shp")
        print(f"✅ Loaded {len(dam_linje_gdf)} dam line features")
    except Exception as e:
        print(f"❌ Error loading dam line data: {e}")
    
    # Load reservoir data
    try:
        print("Loading reservoir spatial data...")
        magasin_gdf = gpd.read_file(data_dir / "Vannkraft_Magasin.shp")
        print(f"✅ Loaded {len(magasin_gdf)} reservoir features")
    except Exception as e:
        print(f"❌ Error loading reservoir data: {e}")
    
    print()
    
    # --- Step 5: Export for Visualization (to KML) ---
    print("--- Exporting to KML for Visualization ---")
    
    # Define output paths for KML files
    output_kml_dam_path = 'output/Vannkraft_DamLinje_subset.kml'
    output_kml_magasin_simplified_path = 'output/Vannkraft_Magasin_simplified_50m.kml'
    
    # Ensure output directory exists
    Path('output').mkdir(exist_ok=True)
    
    # Export dam line data
    if dam_linje_gdf is not None:
        try:
            # Select a subset of relevant columns for dams before exporting to KML
            dam_linje_subset_kml = dam_linje_gdf[['damNr', 'damNavn', 'objType', 'formal_L', 'idriftAar', 'geometry']].copy()
            
            # Clean data - remove rows with null geometries
            dam_linje_subset_kml = dam_linje_subset_kml.dropna(subset=['geometry'])
            
            print(f"Preparing {len(dam_linje_subset_kml)} dam line features for export...")
            export_to_kml_with_fallback(dam_linje_subset_kml, output_kml_dam_path, "dam line data")
            
        except Exception as e:
            print(f"❌ Error preparing dam line data for KML: {e}")
    else:
        print("❌ dam_linje_gdf not available. Skipping KML export for dam lines.")
    
    print()
    
    # Export reservoir data
    if magasin_gdf is not None:
        # Define a tolerance for simplification
        tolerance = 50  # meters
        
        try:
            print(f"Attempting to simplify reservoir geometries with tolerance {tolerance}...")
            
            # Simplify the reservoir geometries
            magasin_simplified_gdf = magasin_gdf.copy()
            magasin_simplified_gdf['geometry'] = magasin_simplified_gdf['geometry'].simplify(
                tolerance, preserve_topology=True
            )
            
            # Select a subset of relevant columns for reservoirs before exporting to KML
            available_columns = ['magasinNr', 'magNavn', 'objType', 'formal_L', 'areal_km2', 'volOppdemt', 'geometry']
            existing_columns = [col for col in available_columns if col in magasin_simplified_gdf.columns]
            
            magasin_subset_simplified_kml = magasin_simplified_gdf[existing_columns].copy()
            
            # Clean data - remove rows with null geometries
            magasin_subset_simplified_kml = magasin_subset_simplified_kml.dropna(subset=['geometry'])
            
            # Remove empty geometries
            magasin_subset_simplified_kml = magasin_subset_simplified_kml[
                ~magasin_subset_simplified_kml.geometry.is_empty
            ]
            
            print(f"Preparing {len(magasin_subset_simplified_kml)} simplified reservoir features for export...")
            export_to_kml_with_fallback(
                magasin_subset_simplified_kml, 
                output_kml_magasin_simplified_path, 
                "simplified reservoir data"
            )
            
        except Exception as e:
            print(f"❌ Error preparing reservoir data for KML: {e}")
            print("💡 You might need to adjust the simplification tolerance if export fails due to complex geometries.")
    else:
        print("❌ magasin_gdf not available. Skipping KML export for reservoirs.")
    
    print()
    print("--- KML Export Complete ---")
    
    # Additional information
    print("\n📋 Additional Information:")
    print("• KML files can be opened directly in Google Earth")
    print("• GeoJSON files can be opened in Google Earth Pro, QGIS, and web applications")
    print("• Both formats preserve geographic coordinates and attribute data")
    
    if not kml_supported:
        print("\n💡 To enable native KML export:")
        print("   conda install -c conda-forge gdal")
        print("   or")
        print("   pip install gdal")

if __name__ == "__main__":
    main() 