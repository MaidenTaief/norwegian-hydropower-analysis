#!/usr/bin/env python3
"""
Norwegian Hydropower Data Analysis - Enhanced Version
====================================================

Enhanced analysis script for Norwegian hydropower infrastructure data.
This version includes both dam points and dam lines in KML export for
complete visualization of Norwegian hydropower infrastructure.

Features:
- Dam points (locations)
- Dam lines (actual structures) 
- Reservoirs (water bodies)
- Comprehensive KML export with all three components
"""

import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Set up plotting style
plt.style.use('default')
sns.set_palette("Set2")
plt.rcParams['figure.figsize'] = (15, 10)
plt.rcParams['font.size'] = 10

class NorwegianHydropowerAnalyzerEnhanced:
    """
    Enhanced analyzer for Norwegian hydropower data with complete KML export.
    Includes dam points, dam lines, and reservoirs in single KML file.
    """
    
    def __init__(self, data_dir="Data"):
        self.data_dir = Path(data_dir)
        self.output_dir = Path("output_enhanced")
        self.output_dir.mkdir(exist_ok=True)
        
        # Load data
        self.load_all_data()
    
    def load_all_data(self):
        """Load all hydropower data."""
        print("🔄 Loading Norwegian hydropower data...")
        
        try:
            # Load spatial data
            self.dam_linje_gdf = gpd.read_file(self.data_dir / "Vannkraft_DamLinje.shp")
            self.dam_punkt_gdf = gpd.read_file(self.data_dir / "Vannkraft_DamPunkt.shp")
            self.magasin_gdf = gpd.read_file(self.data_dir / "Vannkraft_Magasin.shp")
            
            print(f"✅ Loaded {len(self.dam_linje_gdf)} dam lines")
            print(f"✅ Loaded {len(self.dam_punkt_gdf)} dam points")  
            print(f"✅ Loaded {len(self.magasin_gdf)} reservoirs")
            
            # Ensure coordinate system is WGS84 for KML export
            if self.dam_linje_gdf.crs.to_string() != 'EPSG:4326':
                self.dam_linje_gdf = self.dam_linje_gdf.to_crs('EPSG:4326')
            if self.dam_punkt_gdf.crs.to_string() != 'EPSG:4326':
                self.dam_punkt_gdf = self.dam_punkt_gdf.to_crs('EPSG:4326')
            if self.magasin_gdf.crs.to_string() != 'EPSG:4326':
                self.magasin_gdf = self.magasin_gdf.to_crs('EPSG:4326')
            
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            return False
        
        return True
    
    def export_comprehensive_kml(self):
        """Export comprehensive KML with dam points, dam lines, and reservoirs."""
        print("\n🌍 Exporting comprehensive Norwegian hydropower KML...")
        
        # Prepare data for KML export
        kml_file = self.output_dir / "norwegian_hydropower_comprehensive.kml"
        
        # Create KML content with proper XML formatting
        kml_content = '<?xml version="1.0" encoding="UTF-8"?>\n'
        kml_content += '<kml xmlns="http://www.opengis.net/kml/2.2">\n'
        kml_content += '<Document>\n'
        kml_content += '    <name>Norwegian Hydropower Infrastructure - Complete</name>\n'
        kml_content += '    <description>Comprehensive map of Norwegian dams, dam structures, and reservoirs</description>\n'
        
        # Define styles for different components
        kml_content += '    <Style id="dam_point_style">\n'
        kml_content += '        <IconStyle>\n'
        kml_content += '            <Icon>\n'
        kml_content += '                <href>http://maps.google.com/mapfiles/kml/paddle/red-circle.png</href>\n'
        kml_content += '            </Icon>\n'
        kml_content += '            <scale>0.8</scale>\n'
        kml_content += '        </IconStyle>\n'
        kml_content += '    </Style>\n'
        
        kml_content += '    <Style id="dam_line_style">\n'
        kml_content += '        <LineStyle>\n'
        kml_content += '            <color>ff0000ff</color>\n'
        kml_content += '            <width>3</width>\n'
        kml_content += '        </LineStyle>\n'
        kml_content += '    </Style>\n'
        
        kml_content += '    <Style id="reservoir_style">\n'
        kml_content += '        <PolyStyle>\n'
        kml_content += '            <color>7f0000ff</color>\n'
        kml_content += '            <outline>1</outline>\n'
        kml_content += '        </PolyStyle>\n'
        kml_content += '    </Style>\n'
        
        # Add dam points
        print("📍 Adding dam points...")
        for idx, row in self.dam_punkt_gdf.iterrows():
            if pd.notna(row.geometry):
                coords = row.geometry.coords[0] if hasattr(row.geometry, 'coords') else (row.geometry.x, row.geometry.y)
                dam_name = row.get('damNavn', 'Unknown Dam')
                
                # Create description
                desc = f"<![CDATA[<b>{dam_name}</b><br>"
                if pd.notna(row.get('idriftAar')):
                    desc += f"Year: {int(row['idriftAar'])}<br>"
                if pd.notna(row.get('formal_L')):
                    desc += f"Purpose: {row['formal_L']}<br>"
                if pd.notna(row.get('objType')):
                    desc += f"Type: {row['objType']}<br>"
                desc += "]]>"
                
                kml_content += '    <Placemark>\n'
                kml_content += f'        <name>{dam_name}</name>\n'
                kml_content += f'        <description>{desc}</description>\n'
                kml_content += '        <styleUrl>#dam_point_style</styleUrl>\n'
                kml_content += '        <Point>\n'
                kml_content += f'            <coordinates>{coords[0]},{coords[1]},0</coordinates>\n'
                kml_content += '        </Point>\n'
                kml_content += '    </Placemark>\n'
        
        # Add dam lines
        print("🏗️ Adding dam lines...")
        for idx, row in self.dam_linje_gdf.iterrows():
            if pd.notna(row.geometry):
                dam_name = row.get('damNavn', 'Unknown Dam Structure')
                
                # Create description
                desc = f"<![CDATA[<b>{dam_name} (Structure)</b><br>"
                if pd.notna(row.get('idriftAar')):
                    desc += f"Year: {int(row['idriftAar'])}<br>"
                if pd.notna(row.get('formal_L')):
                    desc += f"Purpose: {row['formal_L']}<br>"
                if pd.notna(row.get('objType')):
                    desc += f"Type: {row['objType']}<br>"
                desc += "]]>"
                
                # Get coordinates for line geometry
                if hasattr(row.geometry, 'coords'):
                    coords_str = ' '.join([f"{coord[0]},{coord[1]},0" for coord in row.geometry.coords])
                else:
                    # For simplified geometries
                    coords_str = f"{row.geometry.x},{row.geometry.y},0"
                
                kml_content += '    <Placemark>\n'
                kml_content += f'        <name>{dam_name} (Structure)</name>\n'
                kml_content += f'        <description>{desc}</description>\n'
                kml_content += '        <styleUrl>#dam_line_style</styleUrl>\n'
                kml_content += '        <LineString>\n'
                kml_content += f'            <coordinates>{coords_str}</coordinates>\n'
                kml_content += '        </LineString>\n'
                kml_content += '    </Placemark>\n'
        
        # Add reservoirs (simplified for KML compatibility)
        print("💧 Adding reservoirs...")
        tolerance = 50  # meters for simplification
        magasin_simplified = self.magasin_gdf.copy()
        magasin_simplified['geometry'] = magasin_simplified['geometry'].simplify(tolerance, preserve_topology=True)
        
        for idx, row in magasin_simplified.iterrows():
            if pd.notna(row.geometry):
                reservoir_name = row.get('magNavn', 'Unknown Reservoir')
                
                # Create description
                desc = f"<![CDATA[<b>{reservoir_name}</b><br>"
                if pd.notna(row.get('areal_km2')):
                    desc += f"Area: {row['areal_km2']:.1f} km²<br>"
                if pd.notna(row.get('volOppdemt')):
                    desc += f"Volume: {row['volOppdemt']:.1f} million m³<br>"
                if pd.notna(row.get('formal_L')):
                    desc += f"Purpose: {row['formal_L']}<br>"
                desc += "]]>"
                
                # Get coordinates for polygon geometry
                if hasattr(row.geometry, 'exterior'):
                    coords_str = ' '.join([f"{coord[0]},{coord[1]},0" for coord in row.geometry.exterior.coords])
                else:
                    # For simplified geometries
                    coords_str = f"{row.geometry.x},{row.geometry.y},0"
                
                kml_content += '    <Placemark>\n'
                kml_content += f'        <name>{reservoir_name}</name>\n'
                kml_content += f'        <description>{desc}</description>\n'
                kml_content += '        <styleUrl>#reservoir_style</styleUrl>\n'
                kml_content += '        <Polygon>\n'
                kml_content += '            <outerBoundaryIs>\n'
                kml_content += '                <LinearRing>\n'
                kml_content += f'                    <coordinates>{coords_str}</coordinates>\n'
                kml_content += '                </LinearRing>\n'
                kml_content += '            </outerBoundaryIs>\n'
                kml_content += '        </Polygon>\n'
                kml_content += '    </Placemark>\n'
        
        kml_content += '</Document>\n'
        kml_content += '</kml>'
        
        # Save KML file
        with open(kml_file, 'w', encoding='utf-8') as f:
            f.write(kml_content)
        
        print(f"✅ Exported comprehensive Norwegian hydropower KML")
        print(f"📁 KML file: {kml_file}")
        print(f"📊 Components included:")
        print(f"   • {len(self.dam_punkt_gdf)} dam points (red circles)")
        print(f"   • {len(self.dam_linje_gdf)} dam lines (red lines)")
        print(f"   • {len(self.magasin_gdf)} reservoirs (blue polygons)")
    
    def create_enhanced_spatial_visualization(self):
        """Create enhanced spatial visualization showing all components."""
        print("\n🗺️ Creating enhanced spatial visualization...")
        
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('Norwegian Hydropower Infrastructure - Complete View', fontsize=16, fontweight='bold')
        
        # Base map setup
        for ax in axes.flat:
            ax.set_xlim(4, 32)  # Norway longitude range
            ax.set_ylim(57, 72)  # Norway latitude range
            ax.grid(True, alpha=0.3)
        
        # 1. All components together
        # Plot reservoirs first (background)
        self.magasin_gdf.plot(ax=axes[0,0], alpha=0.3, color='lightblue', edgecolor='blue', linewidth=0.5)
        # Plot dam lines
        self.dam_linje_gdf.plot(ax=axes[0,0], color='red', linewidth=1, alpha=0.8)
        # Plot dam points
        self.dam_punkt_gdf.plot(ax=axes[0,0], markersize=2, alpha=0.8, color='darkred')
        
        axes[0,0].set_title('Complete Norwegian Hydropower Infrastructure\nAll Components', fontweight='bold')
        axes[0,0].set_xlabel('Longitude')
        axes[0,0].set_ylabel('Latitude')
        
        # 2. Dam points only
        self.dam_punkt_gdf.plot(ax=axes[0,1], markersize=3, alpha=0.8, color='darkred')
        axes[0,1].set_title('Dam Points (Locations)\n4,953 dam locations', fontweight='bold')
        axes[0,1].set_xlabel('Longitude')
        axes[0,1].set_ylabel('Latitude')
        
        # 3. Dam lines only
        self.dam_linje_gdf.plot(ax=axes[1,0], color='red', linewidth=1, alpha=0.8)
        axes[1,0].set_title('Dam Lines (Structures)\n4,813 dam structures', fontweight='bold')
        axes[1,0].set_xlabel('Longitude')
        axes[1,0].set_ylabel('Latitude')
        
        # 4. Reservoirs only
        self.magasin_gdf.plot(ax=axes[1,1], alpha=0.6, color='lightblue', edgecolor='blue', linewidth=0.5)
        axes[1,1].set_title('Reservoirs (Water Bodies)\n2,997 reservoirs', fontweight='bold')
        axes[1,1].set_xlabel('Longitude')
        axes[1,1].set_ylabel('Latitude')
        
        plt.tight_layout()
        plt.savefig(self.output_dir / "norwegian_hydropower_complete_view.png", dpi=300, bbox_inches='tight')
        print("✅ Saved enhanced spatial visualization")
        plt.show()
    
    def create_statistical_summary(self):
        """Create comprehensive statistical summary."""
        print("\n📊 Creating comprehensive statistical summary...")
        
        stats_summary = {
            'Infrastructure Overview': {
                'Dam Points': len(self.dam_punkt_gdf),
                'Dam Lines': len(self.dam_linje_gdf),
                'Reservoirs': len(self.magasin_gdf),
                'Total Components': len(self.dam_punkt_gdf) + len(self.dam_linje_gdf) + len(self.magasin_gdf)
            },
            'Dam Points Analysis': {
                'With Names': len(self.dam_punkt_gdf.dropna(subset=['damNavn'])),
                'With Construction Year': len(self.dam_punkt_gdf.dropna(subset=['idriftAar'])),
                'With Purpose': len(self.dam_punkt_gdf.dropna(subset=['formal_L']))
            },
            'Dam Lines Analysis': {
                'With Names': len(self.dam_linje_gdf.dropna(subset=['damNavn'])),
                'With Construction Year': len(self.dam_linje_gdf.dropna(subset=['idriftAar'])),
                'With Purpose': len(self.dam_linje_gdf.dropna(subset=['formal_L']))
            },
            'Reservoir Analysis': {
                'With Names': len(self.magasin_gdf.dropna(subset=['magNavn'])),
                'With Area Data': len(self.magasin_gdf.dropna(subset=['areal_km2'])),
                'With Volume Data': len(self.magasin_gdf.dropna(subset=['volOppdemt'])),
                'Total Area (km²)': f"{self.magasin_gdf['areal_km2'].sum():.2f}",
                'Total Volume (million m³)': f"{self.magasin_gdf['volOppdemt'].sum():.1f}"
            }
        }
        
        # Print summary
        print("\n" + "="*60)
        print("COMPREHENSIVE NORWEGIAN HYDROPOWER SUMMARY")
        print("="*60)
        
        for category, stats in stats_summary.items():
            print(f"\n{category}:")
            print("-" * len(category))
            for key, value in stats.items():
                print(f"  {key}: {value}")
        
        # Save summary to file
        with open(self.output_dir / "comprehensive_statistical_summary.txt", "w") as f:
            f.write("Norwegian Hydropower Infrastructure - Comprehensive Statistical Summary\n")
            f.write("="*60 + "\n\n")
            
            for category, stats in stats_summary.items():
                f.write(f"{category}:\n")
                f.write("-" * len(category) + "\n")
                for key, value in stats.items():
                    f.write(f"  {key}: {value}\n")
                f.write("\n")
        
        print("✅ Saved comprehensive statistical summary to file")
    
    def run_complete_enhanced_analysis(self):
        """Run complete enhanced analysis workflow."""
        print("🚀 Starting Norwegian Hydropower Analysis - Enhanced Version")
        print("="*60)
        
        # Run all analysis components
        self.export_comprehensive_kml()
        self.create_enhanced_spatial_visualization()
        self.create_statistical_summary()
        
        print("\n" + "="*60)
        print("✅ NORWEGIAN HYDROPOWER ANALYSIS - ENHANCED VERSION COMPLETED")
        print("="*60)
        print(f"📁 Output directory: {self.output_dir}")
        print(f"📊 Infrastructure components:")
        print(f"   • {len(self.dam_punkt_gdf):,} dam points")
        print(f"   • {len(self.dam_linje_gdf):,} dam lines")
        print(f"   • {len(self.magasin_gdf):,} reservoirs")
        print(f"   • Total: {len(self.dam_punkt_gdf) + len(self.dam_linje_gdf) + len(self.magasin_gdf):,} components")
        print("\n📋 Generated files:")
        print("  • norwegian_hydropower_comprehensive.kml")
        print("  • norwegian_hydropower_complete_view.png")
        print("  • comprehensive_statistical_summary.txt")

def main():
    """Main function to run the enhanced Norwegian hydropower analysis."""
    analyzer = NorwegianHydropowerAnalyzerEnhanced()
    analyzer.run_complete_enhanced_analysis()

if __name__ == "__main__":
    main() 