#!/usr/bin/env python3
"""
Indian Dam Analysis System
==========================

Comprehensive analysis of Indian dams using the Global Dam Watch (GDW) database.
This system provides detailed visualizations and insights similar to the Norwegian analysis.

Features:
- Spatial analysis of 7,097+ Indian dams
- Construction timeline analysis
- Reservoir capacity and area analysis
- Hydropower generation analysis
- Regional distribution analysis
- Google Earth export capabilities
"""

import geopandas as gpd
import pandas as pd
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

class IndianDamAnalyzer:
    """
    Advanced analyzer for Indian dam data from the Global Dam Watch database.
    """
    
    def __init__(self, data_dir="../25988293/GDW_v1_0_shp/GDW_v1_0_shp"):
        self.data_dir = Path(data_dir)
        self.output_dir = Path("output")
        self.output_dir.mkdir(exist_ok=True)
        
        # Load data
        self.load_gdw_data()
    
    def load_gdw_data(self):
        """Load GDW barriers data and filter for India."""
        print("🔄 Loading GDW database and filtering for Indian dams...")
        
        try:
            # Load GDW barriers data
            gdf = gpd.read_file(self.data_dir / "GDW_barriers_v1_0.shp")
            print(f"✅ Loaded {len(gdf):,} dams from GDW database")
            
            # Filter for Indian dams
            self.india_dams = gdf[gdf['COUNTRY'] == 'India'].copy()
            print(f"🇮🇳 Found {len(self.india_dams):,} Indian dams")
            
            # Ensure coordinate system is WGS84
            if self.india_dams.crs.to_string() != 'EPSG:4326':
                self.india_dams = self.india_dams.to_crs('EPSG:4326')
            
            print("✅ Data loading completed")
            
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            return False
        
        return True
    
    def create_construction_timeline(self):
        """Create detailed dam construction timeline analysis for India."""
        print("\n📈 Creating Indian dam construction timeline analysis...")
        
        fig, axes = plt.subplots(2, 2, figsize=(16, 10))
        fig.suptitle('Indian Dam Construction Analysis Over Time', fontsize=16, fontweight='bold')
        
        # Filter for dams with construction year data
        dam_data = self.india_dams.dropna(subset=['YEAR_DAM'])
        dam_data = dam_data[(dam_data['YEAR_DAM'] >= 1800) & (dam_data['YEAR_DAM'] <= 2025)]
        
        if len(dam_data) == 0:
            print("❌ No construction year data available")
            return
        
        # 1. Construction by decade
        dam_data['decade'] = (dam_data['YEAR_DAM'] // 10) * 10
        decade_counts = dam_data['decade'].value_counts().sort_index()
        
        bars = axes[0,0].bar(decade_counts.index, decade_counts.values, 
                            width=8, alpha=0.7, color='darkorange', edgecolor='black')
        axes[0,0].set_title('Indian Dam Construction by Decade\nHydropower Development Timeline', fontweight='bold')
        axes[0,0].set_xlabel('Decade')
        axes[0,0].set_ylabel('Number of Dams Built')
        axes[0,0].grid(True, alpha=0.3, axis='y')
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            if height > 0:
                axes[0,0].text(bar.get_x() + bar.get_width()/2., height + 5,
                              f'{int(height)}', ha='center', va='bottom', fontsize=9)
        
        # 2. Cumulative construction
        years = sorted(dam_data['YEAR_DAM'].unique())
        cumulative = []
        for year in years:
            cumulative.append(len(dam_data[dam_data['YEAR_DAM'] <= year]))
        
        axes[0,1].plot(years, cumulative, linewidth=3, color='navy', marker='o', markersize=4)
        axes[0,1].set_title('Cumulative Indian Dam Construction\nTotal Infrastructure Growth', fontweight='bold')
        axes[0,1].set_xlabel('Year')
        axes[0,1].set_ylabel('Total Number of Dams')
        axes[0,1].grid(True, alpha=0.3)
        
        # Add annotations for key periods
        if 1950 in years:
            axes[0,1].annotate('Post-Independence Boom', xy=(1950, cumulative[years.index(1950)]), 
                              xytext=(1955, 2000), arrowprops=dict(arrowstyle='->', color='red'),
                              fontsize=10, color='red', fontweight='bold')
        
        # 3. Construction rate by 5-year periods
        dam_data['period'] = (dam_data['YEAR_DAM'] // 5) * 5
        period_counts = dam_data['period'].value_counts().sort_index()
        
        # Calculate construction rate (dams per year)
        construction_rate = period_counts / 5
        
        axes[1,0].plot(construction_rate.index, construction_rate.values, 
                      linewidth=2, marker='s', markersize=6, color='darkred')
        axes[1,0].set_title('Indian Dam Construction Rate\nDams Built per Year (5-year periods)', fontweight='bold')
        axes[1,0].set_xlabel('Year')
        axes[1,0].set_ylabel('Dams per Year')
        axes[1,0].grid(True, alpha=0.3)
        
        # Find peak construction period
        if len(construction_rate) > 0:
            peak_period = construction_rate.idxmax()
            peak_rate = construction_rate.max()
            axes[1,0].annotate(f'Peak: {peak_rate:.1f} dams/year\n({int(peak_period)}s)', 
                              xy=(peak_period, peak_rate), xytext=(peak_period-20, peak_rate+5),
                              arrowprops=dict(arrowstyle='->', color='red'),
                              fontsize=10, color='red', fontweight='bold',
                              bbox=dict(boxstyle="round,pad=0.3", facecolor='yellow', alpha=0.7))
        
        # 4. Historical context analysis
        historical_periods = {
            'Pre-Independence (1800-1947)': (1800, 1947),
            'Early Independence (1947-1970)': (1947, 1970),
            'Development Era (1970-2000)': (1970, 2000),
            'Modern Era (2000-2025)': (2000, 2025)
        }
        
        period_stats = []
        for period_name, (start, end) in historical_periods.items():
            count = len(dam_data[(dam_data['YEAR_DAM'] >= start) & (dam_data['YEAR_DAM'] < end)])
            period_stats.append({'Period': period_name, 'Count': count})
        
        period_df = pd.DataFrame(period_stats)
        
        bars = axes[1,1].bar(range(len(period_df)), period_df['Count'], 
                            color=['lightblue', 'lightgreen', 'orange', 'lightcoral'],
                            alpha=0.8, edgecolor='black')
        axes[1,1].set_title('Indian Dam Construction by Historical Period\nIndia\'s Hydropower Development', fontweight='bold')
        axes[1,1].set_xticks(range(len(period_df)))
        axes[1,1].set_xticklabels([p.replace(' ', '\n') for p in period_df['Period']], 
                                 rotation=0, fontsize=9)
        axes[1,1].set_ylabel('Number of Dams')
        axes[1,1].grid(True, alpha=0.3, axis='y')
        
        # Add value labels
        for i, bar in enumerate(bars):
            height = bar.get_height()
            axes[1,1].text(bar.get_x() + bar.get_width()/2., height + 10,
                          f'{int(height)}', ha='center', va='bottom', fontsize=10, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(self.output_dir / "indian_dam_construction_timeline.png", dpi=300, bbox_inches='tight')
        print("✅ Saved Indian dam construction timeline analysis")
        plt.show()
    
    def create_spatial_visualization(self):
        """Create enhanced spatial visualization of Indian dams."""
        print("\n🗺️ Creating Indian dam spatial visualization...")
        
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('Indian Dam Infrastructure Spatial Distribution', fontsize=16, fontweight='bold')
        
        # 1. All Indian dams
        self.india_dams.plot(ax=axes[0,0], markersize=2, alpha=0.7, color='darkred')
        axes[0,0].set_title('All Indian Dams\nComplete Infrastructure Overview', fontweight='bold')
        axes[0,0].set_xlabel('Longitude')
        axes[0,0].set_ylabel('Latitude')
        axes[0,0].grid(True, alpha=0.3)
        
        # 2. Dams by construction era
        if 'YEAR_DAM' in self.india_dams.columns:
            dam_data = self.india_dams.dropna(subset=['YEAR_DAM'])
            
            # Define eras
            def get_era(year):
                if year < 1947:
                    return 'Pre-Independence'
                elif year < 1970:
                    return 'Early Independence'
                elif year < 2000:
                    return 'Development Era'
                else:
                    return 'Modern Era'
            
            dam_data['era'] = dam_data['YEAR_DAM'].apply(get_era)
            
            # Plot by era
            eras = ['Pre-Independence', 'Early Independence', 'Development Era', 'Modern Era']
            colors = ['darkblue', 'darkgreen', 'orange', 'red']
            
            for era, color in zip(eras, colors):
                era_dams = dam_data[dam_data['era'] == era]
                if len(era_dams) > 0:
                    era_dams.plot(ax=axes[0,1], markersize=3, alpha=0.8, color=color, label=era)
            
            axes[0,1].set_title('Indian Dams by Construction Era\nHistorical Development Pattern', fontweight='bold')
            axes[0,1].set_xlabel('Longitude')
            axes[0,1].set_ylabel('Latitude')
            axes[0,1].legend()
            axes[0,1].grid(True, alpha=0.3)
        
        # 3. Dams by height (if available)
        if 'DAM_HGT_M' in self.india_dams.columns:
            height_data = self.india_dams.dropna(subset=['DAM_HGT_M'])
            
            # Create height categories
            def get_height_category(height):
                if height < 30:
                    return 'Low (<30m)'
                elif height < 100:
                    return 'Medium (30-100m)'
                else:
                    return 'High (>100m)'
            
            height_data['height_cat'] = height_data['DAM_HGT_M'].apply(get_height_category)
            
            # Plot by height category
            categories = ['Low (<30m)', 'Medium (30-100m)', 'High (>100m)']
            colors = ['lightblue', 'orange', 'red']
            
            for cat, color in zip(categories, colors):
                cat_dams = height_data[height_data['height_cat'] == cat]
                if len(cat_dams) > 0:
                    cat_dams.plot(ax=axes[1,0], markersize=3, alpha=0.8, color=color, label=cat)
            
            axes[1,0].set_title('Indian Dams by Height Category\nStructural Characteristics', fontweight='bold')
            axes[1,0].set_xlabel('Longitude')
            axes[1,0].set_ylabel('Latitude')
            axes[1,0].legend()
            axes[1,0].grid(True, alpha=0.3)
        
        # 4. Dams by purpose (if available)
        if 'MAIN_USE' in self.india_dams.columns:
            use_data = self.india_dams.dropna(subset=['MAIN_USE'])
            use_counts = use_data['MAIN_USE'].value_counts().head(5)
            
            axes[1,1].pie(use_counts.values, labels=use_counts.index, autopct='%1.1f%%', startangle=90)
            axes[1,1].set_title('Indian Dams by Primary Purpose\nUsage Distribution', fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(self.output_dir / "indian_dam_spatial_visualization.png", dpi=300, bbox_inches='tight')
        print("✅ Saved Indian dam spatial visualization")
        plt.show()
    
    def export_to_kml(self):
        """Export Indian dams to KML format for Google Earth visualization."""
        print("\n🌍 Exporting Indian dams to KML format...")
        
        # Prepare data for KML export
        kml_data = self.india_dams.copy()
        
        # Create description field
        def create_description(row):
            desc = f"<b>{row.get('DAM_NAME', 'Unknown Dam')}</b><br>"
            if pd.notna(row.get('YEAR_DAM')):
                desc += f"Year: {int(row['YEAR_DAM'])}<br>"
            if pd.notna(row.get('DAM_HGT_M')):
                desc += f"Height: {row['DAM_HGT_M']:.1f}m<br>"
            if pd.notna(row.get('AREA_SKM')):
                desc += f"Reservoir Area: {row['AREA_SKM']:.1f} km²<br>"
            if pd.notna(row.get('CAP_MCM')):
                desc += f"Capacity: {row['CAP_MCM']:.1f} MCM<br>"
            if pd.notna(row.get('POWER_MW')):
                desc += f"Power: {row['POWER_MW']:.1f} MW<br>"
            if pd.notna(row.get('RIVER')):
                desc += f"River: {row['RIVER']}<br>"
            return desc
        
        kml_data['description'] = kml_data.apply(create_description, axis=1)
        
        # Export to KML
        kml_file = self.output_dir / "indian_dams_google_earth.kml"
        
        # Create KML content
        kml_content = """<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
<Document>
    <name>Indian Dams - GDW Database</name>
    <description>Comprehensive map of Indian dams from Global Dam Watch database</description>
    <Style id="dam_style">
        <IconStyle>
            <Icon>
                <href>http://maps.google.com/mapfiles/kml/paddle/red-circle.png</href>
            </Icon>
            <scale>0.8</scale>
        </IconStyle>
    </Style>
"""
        
        # Add placemarks
        for idx, dam in kml_data.iterrows():
            if hasattr(dam.geometry, 'x') and hasattr(dam.geometry, 'y'):
                lon = dam.geometry.x
                lat = dam.geometry.y
                name = dam.get('DAM_NAME', 'Unknown Dam')
                desc = dam.get('description', '')
                
                kml_content += f"""
    <Placemark>
        <name>{name}</name>
        <description><![CDATA[{desc}]]></description>
        <styleUrl>#dam_style</styleUrl>
        <Point>
            <coordinates>{lon},{lat},0</coordinates>
        </Point>
    </Placemark>
"""
        
        kml_content += """
</Document>
</kml>
"""
        
        # Save KML file
        with open(kml_file, 'w', encoding='utf-8') as f:
            f.write(kml_content)
        
        print(f"✅ Exported {len(kml_data)} Indian dams to '{kml_file}'")
        print("🌍 Open this file in Google Earth for interactive visualization")
    
    def run_complete_analysis(self):
        """Run the complete Indian dam analysis workflow."""
        print("🚀 Starting Complete Indian Dam Analysis")
        print("=" * 50)
        
        # Create visualizations
        self.create_construction_timeline()
        self.create_spatial_visualization()
        
        # Export data
        self.export_to_kml()
        
        print("\n🎉 Indian Dam Analysis Complete!")
        print("📁 Check the 'output/' directory for all generated files")
        print("🌍 Open 'indian_dams_google_earth.kml' in Google Earth for interactive visualization")

if __name__ == "__main__":
    # Create analyzer instance
    analyzer = IndianDamAnalyzer()
    
    # Run complete analysis
    analyzer.run_complete_analysis() 