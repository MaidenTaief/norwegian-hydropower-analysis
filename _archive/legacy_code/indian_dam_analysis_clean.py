#!/usr/bin/env python3
"""
Indian Dam Analysis System - Clean Version
==========================================

Comprehensive analysis of Indian dams using the Global Dam Watch (GDW) database.
This CLEAN version focuses on dams with complete information including names and key attributes.

Features:
- Spatial analysis of Indian dams with complete data
- Construction timeline analysis for named dams
- Reservoir capacity and area analysis
- Hydropower generation analysis
- Regional distribution analysis
- Google Earth export capabilities
- Quality-focused filtering for better analysis
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

class IndianDamAnalyzerClean:
    """
    Advanced analyzer for Indian dam data from the Global Dam Watch database.
    CLEAN VERSION: Focuses on dams with complete information including names and key attributes.
    """
    
    def __init__(self, data_dir="../25988293/GDW_v1_0_shp/GDW_v1_0_shp"):
        self.data_dir = Path(data_dir)
        self.output_dir = Path("output_clean")
        self.output_dir.mkdir(exist_ok=True)
        
        # Load data
        self.load_gdw_data_clean()
    
    def load_gdw_data_clean(self):
        """Load GDW barriers data, filter for India, and apply quality filters."""
        print("🔄 Loading GDW database and filtering for Indian dams with complete data...")
        
        try:
            # Load GDW barriers data
            gdf = gpd.read_file(self.data_dir / "GDW_barriers_v1_0.shp")
            print(f"✅ Loaded {len(gdf):,} dams from GDW database")
            
            # Filter for Indian dams
            india_dams = gdf[gdf['COUNTRY'] == 'India'].copy()
            print(f"🇮🇳 Found {len(india_dams):,} Indian dams")
            
            # Apply quality filters for CLEAN version
            print("\n🔍 Applying quality filters for clean analysis...")
            
            # Filter 1: Must have a dam name
            if 'DAM_NAME' in india_dams.columns:
                named_dams = india_dams[india_dams['DAM_NAME'].notna() & 
                                      (india_dams['DAM_NAME'] != '') & 
                                      (india_dams['DAM_NAME'] != 'Unknown')].copy()
                print(f"📝 Dams with names: {len(named_dams):,}")
            else:
                print("⚠️ No DAM_NAME column found, using all dams")
                named_dams = india_dams.copy()
            
            # Filter 2: Must have construction year
            if 'YEAR_DAM' in named_dams.columns:
                year_dams = named_dams[named_dams['YEAR_DAM'].notna() & 
                                     (named_dams['YEAR_DAM'] >= 1800) & 
                                     (named_dams['YEAR_DAM'] <= 2025)].copy()
                print(f"📅 Dams with construction year: {len(year_dams):,}")
            else:
                print("⚠️ No YEAR_DAM column found")
                year_dams = named_dams.copy()
            
            # Filter 3: Must have at least one key attribute (height, area, capacity, or power)
            key_attributes = ['DAM_HGT_M', 'AREA_SKM', 'CAP_MCM', 'POWER_MW']
            available_attributes = [attr for attr in key_attributes if attr in year_dams.columns]
            
            if available_attributes:
                # Create a mask for dams with at least one key attribute
                has_key_data = year_dams[available_attributes].notna().any(axis=1)
                self.india_dams_clean = year_dams[has_key_data].copy()
                print(f"📊 Dams with key attributes ({', '.join(available_attributes)}): {len(self.india_dams_clean):,}")
            else:
                print("⚠️ No key attributes found")
                self.india_dams_clean = year_dams.copy()
            
            # Store original data for comparison
            self.india_dams_original = india_dams.copy()
            
            # Ensure coordinate system is WGS84
            if self.india_dams_clean.crs.to_string() != 'EPSG:4326':
                self.india_dams_clean = self.india_dams_clean.to_crs('EPSG:4326')
            
            print(f"\n✅ CLEAN DATASET: {len(self.india_dams_clean):,} high-quality Indian dams")
            print(f"📈 Data quality improvement: {len(self.india_dams_original):,} → {len(self.india_dams_clean):,} dams")
            print(f"🎯 Quality ratio: {len(self.india_dams_clean)/len(self.india_dams_original)*100:.1f}%")
            
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            return False
        
        return True
    
    def analyze_data_completeness(self):
        """Analyze the completeness of data in the clean dataset."""
        print("\n📊 Analyzing data completeness in clean dataset...")
        
        if len(self.india_dams_clean) == 0:
            print("❌ No clean data available")
            return
        
        # Key attributes to check
        key_attributes = ['DAM_NAME', 'YEAR_DAM', 'DAM_HGT_M', 'AREA_SKM', 'CAP_MCM', 'POWER_MW', 'RIVER', 'MAIN_USE']
        available_attributes = [attr for attr in key_attributes if attr in self.india_dams_clean.columns]
        
        # Calculate completeness
        completeness_data = {}
        for attr in available_attributes:
            non_null_count = self.india_dams_clean[attr].notna().sum()
            completeness_pct = (non_null_count / len(self.india_dams_clean)) * 100
            completeness_data[attr] = {
                'count': non_null_count,
                'percentage': completeness_pct
            }
        
        # Create completeness visualization
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
        fig.suptitle('Indian Dam Data Completeness Analysis - Clean Dataset', fontsize=16, fontweight='bold')
        
        # Bar chart of completeness percentages
        attributes = list(completeness_data.keys())
        percentages = [completeness_data[attr]['percentage'] for attr in attributes]
        counts = [completeness_data[attr]['count'] for attr in attributes]
        
        bars = ax1.bar(attributes, percentages, color='lightcoral', alpha=0.8, edgecolor='black')
        ax1.set_title('Data Completeness by Attribute\nPercentage of Dams with Data', fontweight='bold')
        ax1.set_ylabel('Percentage (%)')
        ax1.set_ylim(0, 100)
        ax1.grid(True, alpha=0.3, axis='y')
        
        # Add value labels on bars
        for bar, pct, count in zip(bars, percentages, counts):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + 1,
                    f'{pct:.1f}%\n({count:,})', ha='center', va='bottom', fontweight='bold')
        
        # Rotate x-axis labels for better readability
        ax1.tick_params(axis='x', rotation=45)
        
        # Pie chart showing overall data quality
        total_dams = len(self.india_dams_clean)
        dams_with_all_key_data = self.india_dams_clean[available_attributes].notna().all(axis=1).sum()
        dams_with_some_data = total_dams - dams_with_all_key_data
        
        labels = ['Complete Data', 'Partial Data']
        sizes = [dams_with_all_key_data, dams_with_some_data]
        colors = ['lightgreen', 'lightcoral']
        
        ax2.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
        ax2.set_title('Overall Data Quality Distribution\nComplete vs Partial Information', fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(self.output_dir / "indian_dam_data_completeness.png", dpi=300, bbox_inches='tight')
        print("✅ Saved data completeness analysis")
        plt.show()
        
        # Print summary
        print(f"\n📋 DATA COMPLETENESS SUMMARY:")
        print(f"   Total dams in clean dataset: {total_dams:,}")
        print(f"   Dams with complete key data: {dams_with_all_key_data:,} ({dams_with_all_key_data/total_dams*100:.1f}%)")
        print(f"   Dams with partial data: {dams_with_some_data:,} ({dams_with_some_data/total_dams*100:.1f}%)")
        
        for attr in available_attributes:
            pct = completeness_data[attr]['percentage']
            count = completeness_data[attr]['count']
            print(f"   {attr}: {count:,} dams ({pct:.1f}%)")
    
    def create_construction_timeline_clean(self):
        """Create detailed dam construction timeline analysis for clean Indian dataset."""
        print("\n📈 Creating Indian dam construction timeline analysis (clean dataset)...")
        
        fig, axes = plt.subplots(2, 2, figsize=(16, 10))
        fig.suptitle('Indian Dam Construction Analysis - Clean Dataset (Named Dams)', fontsize=16, fontweight='bold')
        
        # Filter for dams with construction year data
        dam_data = self.india_dams_clean.dropna(subset=['YEAR_DAM'])
        dam_data = dam_data[(dam_data['YEAR_DAM'] >= 1800) & (dam_data['YEAR_DAM'] <= 2025)]
        
        if len(dam_data) == 0:
            print("❌ No construction year data available")
            return
        
        # 1. Construction by decade
        dam_data['decade'] = (dam_data['YEAR_DAM'] // 10) * 10
        decade_counts = dam_data['decade'].value_counts().sort_index()
        
        bars = axes[0,0].bar(decade_counts.index, decade_counts.values, 
                            width=8, alpha=0.7, color='darkorange', edgecolor='black')
        axes[0,0].set_title('Indian Dam Construction by Decade\nNamed Dams with Complete Data', fontweight='bold')
        axes[0,0].set_xlabel('Decade')
        axes[0,0].set_ylabel('Number of Dams Built')
        axes[0,0].grid(True, alpha=0.3, axis='y')
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            if height > 0:
                axes[0,0].text(bar.get_x() + bar.get_width()/2., height + 0.5,
                              f'{int(height)}', ha='center', va='bottom', fontweight='bold')
        
        # 2. Construction timeline with dam names
        axes[0,1].scatter(dam_data['YEAR_DAM'], range(len(dam_data)), 
                         alpha=0.6, s=50, color='darkblue')
        axes[0,1].set_title('Construction Timeline\nAll Named Dams', fontweight='bold')
        axes[0,1].set_xlabel('Construction Year')
        axes[0,1].set_ylabel('Dam Index')
        axes[0,1].grid(True, alpha=0.3)
        
        # Add some notable dams as annotations
        if 'DAM_NAME' in dam_data.columns:
            notable_dams = dam_data.nlargest(5, 'YEAR_DAM')  # Most recent dams
            for idx, row in notable_dams.iterrows():
                axes[0,1].annotate(row['DAM_NAME'][:20] + '...' if len(str(row['DAM_NAME'])) > 20 else row['DAM_NAME'],
                                  (row['YEAR_DAM'], dam_data.index.get_loc(idx)),
                                  xytext=(5, 5), textcoords='offset points',
                                  fontsize=8, bbox=dict(boxstyle="round,pad=0.3", facecolor='yellow', alpha=0.7))
        
        # 3. Construction rate analysis
        year_counts = dam_data['YEAR_DAM'].value_counts().sort_index()
        axes[1,0].plot(year_counts.index, year_counts.values, 
                      linewidth=2, color='red', marker='o', markersize=4)
        axes[1,0].set_title('Annual Construction Rate\nNamed Dams', fontweight='bold')
        axes[1,0].set_xlabel('Year')
        axes[1,0].set_ylabel('Dams Built per Year')
        axes[1,0].grid(True, alpha=0.3)
        
        # Add trend line
        if len(year_counts) > 1:
            z = np.polyfit(year_counts.index, year_counts.values, 1)
            p = np.poly1d(z)
            axes[1,0].plot(year_counts.index, p(year_counts.index), 
                          "r--", alpha=0.8, linewidth=2, label=f'Trend: {z[0]:.2f} dams/year')
            axes[1,0].legend()
        
        # 4. Cumulative construction
        cumulative_dams = dam_data['YEAR_DAM'].value_counts().sort_index().cumsum()
        axes[1,1].plot(cumulative_dams.index, cumulative_dams.values, 
                      linewidth=3, color='green', marker='o', markersize=4)
        axes[1,1].set_title('Cumulative Dam Construction\nNamed Dams Over Time', fontweight='bold')
        axes[1,1].set_xlabel('Year')
        axes[1,1].set_ylabel('Total Dams Built')
        axes[1,1].grid(True, alpha=0.3)
        
        # Add milestone annotations
        milestones = [100, 500, 1000, 2000]
        for milestone in milestones:
            if cumulative_dams.max() >= milestone:
                milestone_year = cumulative_dams[cumulative_dams >= milestone].index[0]
                axes[1,1].axhline(y=milestone, color='red', linestyle='--', alpha=0.5)
                axes[1,1].annotate(f'{milestone} dams', (milestone_year, milestone),
                                  xytext=(10, 10), textcoords='offset points',
                                  bbox=dict(boxstyle="round,pad=0.3", facecolor='lightblue', alpha=0.7))
        
        plt.tight_layout()
        plt.savefig(self.output_dir / "indian_dam_construction_timeline_clean.png", dpi=300, bbox_inches='tight')
        print("✅ Saved Indian dam construction timeline (clean dataset)")
        plt.show()
    
    def create_spatial_visualization_clean(self):
        """Create enhanced spatial visualization for clean Indian dam dataset."""
        print("\n🗺️ Creating enhanced spatial visualization (clean dataset)...")
        
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('Indian Dam Spatial Analysis - Clean Dataset (Named Dams)', fontsize=16, fontweight='bold')
        
        # Base map setup
        for ax in axes.flat:
            ax.set_xlim(68, 98)  # India longitude range
            ax.set_ylim(8, 37)   # India latitude range
            ax.grid(True, alpha=0.3)
        
        # 1. All clean dams
        self.india_dams_clean.plot(ax=axes[0,0], markersize=3, alpha=0.8, color='darkred')
        axes[0,0].set_title(f'All Named Indian Dams\n{len(self.india_dams_clean):,} dams with complete data', fontweight='bold')
        axes[0,0].set_xlabel('Longitude')
        axes[0,0].set_ylabel('Latitude')
        
        # 2. Dams by construction era
        if 'YEAR_DAM' in self.india_dams_clean.columns:
            year_data = self.india_dams_clean.dropna(subset=['YEAR_DAM'])
            
            def get_era(year):
                if year < 1947:
                    return 'Pre-Independence'
                elif year < 1980:
                    return 'Post-Independence'
                elif year < 2000:
                    return 'Modern Era'
                else:
                    return 'Recent Era'
            
            year_data['era'] = year_data['YEAR_DAM'].apply(get_era)
            
            eras = ['Pre-Independence', 'Post-Independence', 'Modern Era', 'Recent Era']
            colors = ['darkblue', 'darkgreen', 'darkorange', 'darkred']
            
            for era, color in zip(eras, colors):
                era_dams = year_data[year_data['era'] == era]
                if len(era_dams) > 0:
                    era_dams.plot(ax=axes[0,1], markersize=4, alpha=0.8, color=color, label=era)
            
            axes[0,1].set_title('Indian Dams by Construction Era\nHistorical Development', fontweight='bold')
            axes[0,1].set_xlabel('Longitude')
            axes[0,1].set_ylabel('Latitude')
            axes[0,1].legend()
        
        # 3. Dams by height (if available)
        if 'DAM_HGT_M' in self.india_dams_clean.columns:
            height_data = self.india_dams_clean.dropna(subset=['DAM_HGT_M'])
            
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
        
        # 4. Dams by purpose (if available)
        if 'MAIN_USE' in self.india_dams_clean.columns:
            use_data = self.india_dams_clean.dropna(subset=['MAIN_USE'])
            use_counts = use_data['MAIN_USE'].value_counts().head(5)
            
            axes[1,1].pie(use_counts.values, labels=use_counts.index, autopct='%1.1f%%', startangle=90)
            axes[1,1].set_title('Indian Dams by Primary Purpose\nUsage Distribution', fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(self.output_dir / "indian_dam_spatial_visualization_clean.png", dpi=300, bbox_inches='tight')
        print("✅ Saved Indian dam spatial visualization (clean dataset)")
        plt.show()
    
    def export_to_kml_clean(self):
        """Export clean Indian dams to KML format for Google Earth visualization."""
        print("\n🌍 Exporting clean Indian dams to KML format...")
        
        # Prepare data for KML export
        kml_data = self.india_dams_clean.copy()
        
        # Create description field
        def create_description(row):
            desc = f"<![CDATA[<b>{row.get('DAM_NAME', 'Unknown Dam')}</b><br>"
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
            if pd.notna(row.get('MAIN_USE')):
                desc += f"Purpose: {row['MAIN_USE']}<br>"
            desc += "]]>"
            return desc
        
        kml_data['description'] = kml_data.apply(create_description, axis=1)
        
        # Export to KML
        kml_file = self.output_dir / "indian_dams_google_earth_clean.kml"
        
        # Create KML content with proper XML formatting
        kml_content = '<?xml version="1.0" encoding="UTF-8"?>\n'
        kml_content += '<kml xmlns="http://www.opengis.net/kml/2.2">\n'
        kml_content += '<Document>\n'
        kml_content += '    <name>Indian Dams - Clean Dataset (Named Dams)</name>\n'
        kml_content += '    <description>High-quality map of Indian dams with complete information from Global Dam Watch database</description>\n'
        kml_content += '    <Style id="dam_style">\n'
        kml_content += '        <IconStyle>\n'
        kml_content += '            <Icon>\n'
        kml_content += '                <href>http://maps.google.com/mapfiles/kml/paddle/red-circle.png</href>\n'
        kml_content += '            </Icon>\n'
        kml_content += '            <scale>0.8</scale>\n'
        kml_content += '        </IconStyle>\n'
        kml_content += '    </Style>\n'
        
        # Add placemarks for each dam
        for idx, row in kml_data.iterrows():
            if pd.notna(row.geometry):
                coords = row.geometry.coords[0] if hasattr(row.geometry, 'coords') else (row.geometry.x, row.geometry.y)
                dam_name = row.get('DAM_NAME', 'Unknown Dam')
                description = row['description']
                
                kml_content += '    <Placemark>\n'
                kml_content += f'        <name>{dam_name}</name>\n'
                kml_content += f'        <description>{description}</description>\n'
                kml_content += '        <styleUrl>#dam_style</styleUrl>\n'
                kml_content += '        <Point>\n'
                kml_content += f'            <coordinates>{coords[0]},{coords[1]},0</coordinates>\n'
                kml_content += '        </Point>\n'
                kml_content += '    </Placemark>\n'
        
        kml_content += '</Document>\n'
        kml_content += '</kml>'
        
        # Save KML file
        with open(kml_file, 'w', encoding='utf-8') as f:
            f.write(kml_content)
        
        print(f"✅ Exported {len(kml_data):,} clean Indian dams to KML")
        print(f"📁 KML file: {kml_file}")
    
    def create_statistical_summary_clean(self):
        """Create comprehensive statistical summary for clean dataset."""
        print("\n📊 Creating statistical summary for clean dataset...")
        
        if len(self.india_dams_clean) == 0:
            print("❌ No clean data available")
            return
        
        # Calculate statistics
        stats_summary = {
            'Dataset Overview': {
                'Total Dams (Original)': len(self.india_dams_original),
                'Total Dams (Clean)': len(self.india_dams_clean),
                'Quality Improvement': f"{len(self.india_dams_clean)/len(self.india_dams_original)*100:.1f}%",
                'Data Completeness': 'High (Named dams with key attributes)'
            },
            'Temporal Analysis': {
                'Earliest Dam': int(self.india_dams_clean['YEAR_DAM'].min()) if 'YEAR_DAM' in self.india_dams_clean.columns else 'N/A',
                'Latest Dam': int(self.india_dams_clean['YEAR_DAM'].max()) if 'YEAR_DAM' in self.india_dams_clean.columns else 'N/A',
                'Average Construction Year': int(self.india_dams_clean['YEAR_DAM'].mean()) if 'YEAR_DAM' in self.india_dams_clean.columns else 'N/A',
                'Construction Span': f"{int(self.india_dams_clean['YEAR_DAM'].max() - self.india_dams_clean['YEAR_DAM'].min())} years" if 'YEAR_DAM' in self.india_dams_clean.columns else 'N/A'
            },
            'Structural Characteristics': {
                'Average Height': f"{self.india_dams_clean['DAM_HGT_M'].mean():.1f}m" if 'DAM_HGT_M' in self.india_dams_clean.columns else 'N/A',
                'Maximum Height': f"{self.india_dams_clean['DAM_HGT_M'].max():.1f}m" if 'DAM_HGT_M' in self.india_dams_clean.columns else 'N/A',
                'Total Reservoir Area': f"{self.india_dams_clean['AREA_SKM'].sum():.1f} km²" if 'AREA_SKM' in self.india_dams_clean.columns else 'N/A',
                'Average Reservoir Area': f"{self.india_dams_clean['AREA_SKM'].mean():.1f} km²" if 'AREA_SKM' in self.india_dams_clean.columns else 'N/A',
                'Total Capacity': f"{self.india_dams_clean['CAP_MCM'].sum():.1f} MCM" if 'CAP_MCM' in self.india_dams_clean.columns else 'N/A',
                'Total Power Capacity': f"{self.india_dams_clean['POWER_MW'].sum():.1f} MW" if 'POWER_MW' in self.india_dams_clean.columns else 'N/A'
            }
        }
        
        # Print summary
        print("\n" + "="*60)
        print("CLEAN DATASET STATISTICAL SUMMARY")
        print("="*60)
        
        for category, stats in stats_summary.items():
            print(f"\n{category}:")
            print("-" * len(category))
            for key, value in stats.items():
                print(f"  {key}: {value}")
        
        # Save summary to file
        with open(self.output_dir / "statistical_summary_clean.txt", "w") as f:
            f.write("Indian Dam Infrastructure - Clean Dataset Statistical Summary\n")
            f.write("="*60 + "\n\n")
            
            for category, stats in stats_summary.items():
                f.write(f"{category}:\n")
                f.write("-" * len(category) + "\n")
                for key, value in stats.items():
                    f.write(f"  {key}: {value}\n")
                f.write("\n")
        
        print("✅ Saved statistical summary to file")
    
    def run_complete_analysis_clean(self):
        """Run complete clean analysis workflow."""
        print("🚀 Starting Indian Dam Analysis - Clean Version")
        print("="*60)
        
        # Run all analysis components
        self.analyze_data_completeness()
        self.create_construction_timeline_clean()
        self.create_spatial_visualization_clean()
        self.export_to_kml_clean()
        self.create_statistical_summary_clean()
        
        print("\n" + "="*60)
        print("✅ INDIAN DAM ANALYSIS - CLEAN VERSION COMPLETED")
        print("="*60)
        print(f"📁 Output directory: {self.output_dir}")
        print(f"📊 Clean dataset: {len(self.india_dams_clean):,} high-quality dams")
        print(f"🎯 Quality improvement: {len(self.india_dams_clean)/len(self.india_dams_original)*100:.1f}%")
        print("\n📋 Generated files:")
        print("  • indian_dam_data_completeness.png")
        print("  • indian_dam_construction_timeline_clean.png")
        print("  • indian_dam_spatial_visualization_clean.png")
        print("  • indian_dams_google_earth_clean.kml")
        print("  • statistical_summary_clean.txt")

def main():
    """Main function to run the clean Indian dam analysis."""
    analyzer = IndianDamAnalyzerClean()
    analyzer.run_complete_analysis_clean()

if __name__ == "__main__":
    main() 