#!/usr/bin/env python3
"""
Advanced Norwegian Hydropower Data Analysis
==========================================

This script provides enhanced visualizations and meaningful analysis
of Norwegian hydropower infrastructure data with improved charts
and statistical insights.
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

class AdvancedHydropowerAnalyzer:
    """
    Advanced analyzer for Norwegian hydropower data with enhanced visualizations.
    """
    
    def __init__(self, data_dir="Data"):
        self.data_dir = Path(data_dir)
        self.output_dir = Path("output")
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
            
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            return False
        
        return True
    
    def create_enhanced_reservoir_analysis(self):
        """Create enhanced reservoir area and volume analysis."""
        print("\n📊 Creating enhanced reservoir analysis...")
        
        fig, axes = plt.subplots(2, 3, figsize=(20, 12))
        fig.suptitle('Norwegian Reservoir Analysis - Enhanced View', fontsize=16, fontweight='bold')
        
        # Clean data - remove zero and extreme outliers
        reservoir_data = self.magasin_gdf.copy()
        
        # Filter out unrealistic values
        area_data = reservoir_data[
            (reservoir_data['areal_km2'] > 0) & 
            (reservoir_data['areal_km2'] < 200)  # Remove extreme outliers
        ]['areal_km2']
        
        volume_data = reservoir_data[
            (reservoir_data['volOppdemt'] > 0) & 
            (reservoir_data['volOppdemt'] < 1000)  # Remove extreme outliers
        ]['volOppdemt'].dropna()
        
        # 1. Reservoir Areas - Better Distribution
        axes[0,0].hist(area_data, bins=50, alpha=0.7, color='skyblue', edgecolor='black')
        axes[0,0].set_title('Reservoir Areas Distribution\n(Excluding Extreme Outliers)', fontweight='bold')
        axes[0,0].set_xlabel('Area (km²)')
        axes[0,0].set_ylabel('Number of Reservoirs')
        axes[0,0].grid(True, alpha=0.3)
        
        # Add statistics
        mean_area = area_data.mean()
        median_area = area_data.median()
        axes[0,0].axvline(mean_area, color='red', linestyle='--', label=f'Mean: {mean_area:.2f} km²')
        axes[0,0].axvline(median_area, color='orange', linestyle='--', label=f'Median: {median_area:.2f} km²')
        axes[0,0].legend()
        
        # 2. Log Scale for Better View
        axes[0,1].hist(area_data, bins=50, alpha=0.7, color='lightgreen', edgecolor='black')
        axes[0,1].set_yscale('log')
        axes[0,1].set_title('Reservoir Areas (Log Scale)\nBetter View of Distribution', fontweight='bold')
        axes[0,1].set_xlabel('Area (km²)')
        axes[0,1].set_ylabel('Number of Reservoirs (Log Scale)')
        axes[0,1].grid(True, alpha=0.3)
        
        # 3. Reservoir Volume Distribution
        axes[0,2].hist(volume_data, bins=40, alpha=0.7, color='lightcoral', edgecolor='black')
        axes[0,2].set_title('Reservoir Volumes Distribution\n(Excluding Extreme Outliers)', fontweight='bold')
        axes[0,2].set_xlabel('Volume (million m³)')
        axes[0,2].set_ylabel('Number of Reservoirs')
        axes[0,2].grid(True, alpha=0.3)
        
        # Add statistics
        mean_vol = volume_data.mean()
        median_vol = volume_data.median()
        axes[0,2].axvline(mean_vol, color='red', linestyle='--', label=f'Mean: {mean_vol:.1f} million m³')
        axes[0,2].axvline(median_vol, color='orange', linestyle='--', label=f'Median: {median_vol:.1f} million m³')
        axes[0,2].legend()
        
        # 4. Size Categories Analysis
        # Create size categories
        def categorize_reservoir_size(area):
            if area < 0.5:
                return 'Small (<0.5 km²)'
            elif area < 5:
                return 'Medium (0.5-5 km²)'
            elif area < 20:
                return 'Large (5-20 km²)'
            else:
                return 'Very Large (>20 km²)'
        
        size_categories = area_data.apply(categorize_reservoir_size)
        size_counts = size_categories.value_counts()
        
        colors = ['lightblue', 'lightgreen', 'orange', 'red']
        wedges, texts, autotexts = axes[1,0].pie(size_counts.values, labels=size_counts.index, 
                                                autopct='%1.1f%%', colors=colors, startangle=90)
        axes[1,0].set_title('Reservoir Size Categories\nDistribution by Area', fontweight='bold')
        
        # 5. Volume vs Area Scatter Plot
        # Get matching data for scatter plot
        area_vol_data = reservoir_data[
            (reservoir_data['areal_km2'] > 0) & 
            (reservoir_data['areal_km2'] < 100) &
            (reservoir_data['volOppdemt'] > 0) & 
            (reservoir_data['volOppdemt'] < 500)
        ].dropna(subset=['areal_km2', 'volOppdemt'])
        
        if len(area_vol_data) > 0:
            scatter = axes[1,1].scatter(area_vol_data['areal_km2'], area_vol_data['volOppdemt'], 
                                      alpha=0.6, c=area_vol_data['areal_km2'], cmap='viridis', s=50)
            axes[1,1].set_xlabel('Area (km²)')
            axes[1,1].set_ylabel('Volume (million m³)')
            axes[1,1].set_title('Reservoir Volume vs Area\nRelationship Analysis', fontweight='bold')
            axes[1,1].grid(True, alpha=0.3)
            plt.colorbar(scatter, ax=axes[1,1], label='Area (km²)')
            
            # Add correlation
            correlation = area_vol_data['areal_km2'].corr(area_vol_data['volOppdemt'])
            axes[1,1].text(0.05, 0.95, f'Correlation: {correlation:.3f}', 
                          transform=axes[1,1].transAxes, bbox=dict(boxstyle="round", facecolor='wheat'))
        
        # 6. Top 10 Largest Reservoirs
        top_reservoirs = reservoir_data.nlargest(10, 'areal_km2')[['magNavn', 'areal_km2']].dropna()
        
        if len(top_reservoirs) > 0:
            bars = axes[1,2].barh(range(len(top_reservoirs)), top_reservoirs['areal_km2'], 
                                 color='steelblue', alpha=0.7)
            axes[1,2].set_yticks(range(len(top_reservoirs)))
            axes[1,2].set_yticklabels(top_reservoirs['magNavn'], fontsize=8)
            axes[1,2].set_xlabel('Area (km²)')
            axes[1,2].set_title('Top 10 Largest Reservoirs\nby Area', fontweight='bold')
            axes[1,2].grid(True, alpha=0.3, axis='x')
            
            # Add value labels on bars
            for i, bar in enumerate(bars):
                width = bar.get_width()
                axes[1,2].text(width + 1, bar.get_y() + bar.get_height()/2, 
                              f'{width:.1f}', ha='left', va='center', fontsize=8)
        
        plt.tight_layout()
        plt.savefig(self.output_dir / "enhanced_reservoir_analysis.png", dpi=300, bbox_inches='tight')
        print("✅ Saved enhanced reservoir analysis")
        plt.show()
    
    def create_dam_construction_timeline(self):
        """Create detailed dam construction timeline analysis."""
        print("\n📈 Creating dam construction timeline analysis...")
        
        fig, axes = plt.subplots(2, 2, figsize=(16, 10))
        fig.suptitle('Norwegian Dam Construction Analysis Over Time', fontsize=16, fontweight='bold')
        
        # Combine dam data
        dam_data = pd.concat([
            self.dam_linje_gdf[['idriftAar']].assign(type='Line'),
            self.dam_punkt_gdf[['idriftAar']].assign(type='Point')
        ]).dropna()
        
        # Filter reasonable years
        dam_data = dam_data[(dam_data['idriftAar'] >= 1800) & (dam_data['idriftAar'] <= 2025)]
        
        # 1. Construction by decade
        dam_data['decade'] = (dam_data['idriftAar'] // 10) * 10
        decade_counts = dam_data['decade'].value_counts().sort_index()
        
        bars = axes[0,0].bar(decade_counts.index, decade_counts.values, 
                            width=8, alpha=0.7, color='darkgreen', edgecolor='black')
        axes[0,0].set_title('Dam Construction by Decade\nHydropower Development Timeline', fontweight='bold')
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
        years = sorted(dam_data['idriftAar'].unique())
        cumulative = []
        for year in years:
            cumulative.append(len(dam_data[dam_data['idriftAar'] <= year]))
        
        axes[0,1].plot(years, cumulative, linewidth=3, color='navy', marker='o', markersize=4)
        axes[0,1].set_title('Cumulative Dam Construction\nTotal Infrastructure Growth', fontweight='bold')
        axes[0,1].set_xlabel('Year')
        axes[0,1].set_ylabel('Total Number of Dams')
        axes[0,1].grid(True, alpha=0.3)
        
        # Add annotations for key periods
        axes[0,1].annotate('Post-WWII Boom', xy=(1950, cumulative[years.index(1950) if 1950 in years else -1]), 
                          xytext=(1955, 2000), arrowprops=dict(arrowstyle='->', color='red'),
                          fontsize=10, color='red', fontweight='bold')
        
        # 3. Construction rate by 5-year periods
        dam_data['period'] = (dam_data['idriftAar'] // 5) * 5
        period_counts = dam_data['period'].value_counts().sort_index()
        
        # Calculate construction rate (dams per year)
        construction_rate = period_counts / 5
        
        axes[1,0].plot(construction_rate.index, construction_rate.values, 
                      linewidth=2, marker='s', markersize=6, color='darkred')
        axes[1,0].set_title('Dam Construction Rate\nDams Built per Year (5-year periods)', fontweight='bold')
        axes[1,0].set_xlabel('Year')
        axes[1,0].set_ylabel('Dams per Year')
        axes[1,0].grid(True, alpha=0.3)
        
        # Find peak construction period
        peak_period = construction_rate.idxmax()
        peak_rate = construction_rate.max()
        axes[1,0].annotate(f'Peak: {peak_rate:.1f} dams/year\n({int(peak_period)}s)', 
                          xy=(peak_period, peak_rate), xytext=(peak_period-20, peak_rate+5),
                          arrowprops=dict(arrowstyle='->', color='red'),
                          fontsize=10, color='red', fontweight='bold',
                          bbox=dict(boxstyle="round,pad=0.3", facecolor='yellow', alpha=0.7))
        
        # 4. Historical context analysis
        historical_periods = {
            'Early Development (1800-1900)': (1800, 1900),
            'Industrial Growth (1900-1945)': (1900, 1945),
            'Post-War Boom (1945-1980)': (1945, 1980),
            'Modern Era (1980-2025)': (1980, 2025)
        }
        
        period_stats = []
        for period_name, (start, end) in historical_periods.items():
            count = len(dam_data[(dam_data['idriftAar'] >= start) & (dam_data['idriftAar'] < end)])
            period_stats.append({'Period': period_name, 'Count': count})
        
        period_df = pd.DataFrame(period_stats)
        
        bars = axes[1,1].bar(range(len(period_df)), period_df['Count'], 
                            color=['lightblue', 'lightgreen', 'orange', 'lightcoral'],
                            alpha=0.8, edgecolor='black')
        axes[1,1].set_title('Dam Construction by Historical Period\nNorway\'s Hydropower Development', fontweight='bold')
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
        plt.savefig(self.output_dir / "dam_construction_timeline.png", dpi=300, bbox_inches='tight')
        print("✅ Saved dam construction timeline analysis")
        plt.show()
    
    def create_enhanced_spatial_visualization(self):
        """Create enhanced spatial visualization with better visibility."""
        print("\n🗺️  Creating enhanced spatial visualization...")
        
        fig, axes = plt.subplots(2, 2, figsize=(20, 16))
        fig.suptitle('Norwegian Hydropower Infrastructure - Enhanced Spatial View', 
                    fontsize=16, fontweight='bold')
        
        # Convert to WGS84 for better visualization
        dam_linje_wgs84 = self.dam_linje_gdf.to_crs('EPSG:4326')
        dam_punkt_wgs84 = self.dam_punkt_gdf.to_crs('EPSG:4326')
        magasin_wgs84 = self.magasin_gdf.to_crs('EPSG:4326')
        
        # 1. Dam Lines with Better Styling
        magasin_wgs84.plot(ax=axes[0,0], color='lightblue', alpha=0.3, edgecolor='none')
        dam_linje_wgs84.plot(ax=axes[0,0], color='red', linewidth=1.5, alpha=0.8)
        axes[0,0].set_title('Norwegian Dam Lines\nEnhanced Visibility', fontweight='bold')
        axes[0,0].set_xlabel('Longitude')
        axes[0,0].set_ylabel('Latitude')
        axes[0,0].grid(True, alpha=0.3)
        
        # Add statistics
        axes[0,0].text(0.02, 0.98, f'Total Dam Lines: {len(dam_linje_wgs84)}', 
                      transform=axes[0,0].transAxes, bbox=dict(boxstyle="round", facecolor='white'),
                      verticalalignment='top', fontsize=10, fontweight='bold')
        
        # 2. Dam Points with Size Based on Construction Year
        # Create size based on age (older = smaller points)
        current_year = 2024
        dam_punkt_clean = dam_punkt_wgs84.dropna(subset=['idriftAar'])
        dam_punkt_clean = dam_punkt_clean[dam_punkt_clean['idriftAar'] > 1800]
        
        ages = current_year - dam_punkt_clean['idriftAar']
        # Normalize sizes (newer dams = larger points)
        sizes = 100 - (ages / ages.max()) * 80  # Size range: 20-100
        
        magasin_wgs84.plot(ax=axes[0,1], color='lightblue', alpha=0.2, edgecolor='none')
        scatter = axes[0,1].scatter(dam_punkt_clean.geometry.x, dam_punkt_clean.geometry.y,
                                   c=dam_punkt_clean['idriftAar'], s=sizes, alpha=0.7, 
                                   cmap='plasma', edgecolors='black', linewidth=0.5)
        
        axes[0,1].set_title('Norwegian Dam Points\nSized by Era, Colored by Construction Year', fontweight='bold')
        axes[0,1].set_xlabel('Longitude')
        axes[0,1].set_ylabel('Latitude')
        axes[0,1].grid(True, alpha=0.3)
        
        # Add colorbar
        cbar = plt.colorbar(scatter, ax=axes[0,1])
        cbar.set_label('Construction Year', fontsize=10)
        
        # 3. Reservoir Size Distribution Map
        # Color reservoirs by size category
        def get_reservoir_color(area):
            if area < 0.5:
                return 'lightblue'
            elif area < 5:
                return 'blue'
            elif area < 20:
                return 'darkblue'
            else:
                return 'navy'
        
        magasin_clean = magasin_wgs84[magasin_wgs84['areal_km2'] > 0]
        colors = magasin_clean['areal_km2'].apply(get_reservoir_color)
        
        magasin_clean.plot(ax=axes[1,0], color=colors, alpha=0.7, edgecolor='white', linewidth=0.5)
        axes[1,0].set_title('Reservoir Size Categories\nColor-Coded by Area', fontweight='bold')
        axes[1,0].set_xlabel('Longitude')
        axes[1,0].set_ylabel('Latitude')
        axes[1,0].grid(True, alpha=0.3)
        
        # Add legend
        legend_elements = [
            plt.Rectangle((0,0),1,1, facecolor='lightblue', label='Small (<0.5 km²)'),
            plt.Rectangle((0,0),1,1, facecolor='blue', label='Medium (0.5-5 km²)'),
            plt.Rectangle((0,0),1,1, facecolor='darkblue', label='Large (5-20 km²)'),
            plt.Rectangle((0,0),1,1, facecolor='navy', label='Very Large (>20 km²)')
        ]
        axes[1,0].legend(handles=legend_elements, loc='upper right')
        
        # 4. Combined Infrastructure Density Map
        # Create a density heatmap
        from matplotlib.colors import LinearSegmentedColormap
        
        # Plot base reservoirs
        magasin_wgs84.plot(ax=axes[1,1], color='lightblue', alpha=0.4, edgecolor='none')
        
        # Plot dam points with density coloring
        dam_punkt_wgs84.plot(ax=axes[1,1], color='red', markersize=8, alpha=0.6, label='Dam Points')
        
        # Plot dam lines with varying thickness
        dam_linje_wgs84.plot(ax=axes[1,1], color='darkred', linewidth=2, alpha=0.8, label='Dam Lines')
        
        axes[1,1].set_title('Complete Infrastructure Overview\nDams, Points, and Reservoirs', fontweight='bold')
        axes[1,1].set_xlabel('Longitude')
        axes[1,1].set_ylabel('Latitude')
        axes[1,1].grid(True, alpha=0.3)
        axes[1,1].legend()
        
        # Add summary statistics
        stats_text = f"""Infrastructure Summary:
        • Dam Lines: {len(dam_linje_wgs84):,}
        • Dam Points: {len(dam_punkt_wgs84):,}
        • Reservoirs: {len(magasin_wgs84):,}
        • Total Features: {len(dam_linje_wgs84) + len(dam_punkt_wgs84) + len(magasin_wgs84):,}"""
        
        axes[1,1].text(0.02, 0.02, stats_text, transform=axes[1,1].transAxes, 
                      bbox=dict(boxstyle="round", facecolor='white', alpha=0.9),
                      fontsize=10, fontweight='bold', verticalalignment='bottom')
        
        plt.tight_layout()
        plt.savefig(self.output_dir / "enhanced_spatial_visualization.png", dpi=300, bbox_inches='tight')
        print("✅ Saved enhanced spatial visualization")
        plt.show()
    
    def create_statistical_summary(self):
        """Create comprehensive statistical summary."""
        print("\n📈 Creating statistical summary...")
        
        # Calculate comprehensive statistics
        stats_summary = {
            'Dam Lines': {
                'Total Count': len(self.dam_linje_gdf),
                'With Construction Year': len(self.dam_linje_gdf.dropna(subset=['idriftAar'])),
                'Oldest Dam': int(self.dam_linje_gdf['idriftAar'].min()) if not self.dam_linje_gdf['idriftAar'].isna().all() else 'N/A',
                'Newest Dam': int(self.dam_linje_gdf['idriftAar'].max()) if not self.dam_linje_gdf['idriftAar'].isna().all() else 'N/A',
                'Average Construction Year': f"{self.dam_linje_gdf['idriftAar'].mean():.0f}" if not self.dam_linje_gdf['idriftAar'].isna().all() else 'N/A'
            },
            'Dam Points': {
                'Total Count': len(self.dam_punkt_gdf),
                'With Construction Year': len(self.dam_punkt_gdf.dropna(subset=['idriftAar'])),
                'Oldest Dam': int(self.dam_punkt_gdf['idriftAar'].min()) if not self.dam_punkt_gdf['idriftAar'].isna().all() else 'N/A',
                'Newest Dam': int(self.dam_punkt_gdf['idriftAar'].max()) if not self.dam_punkt_gdf['idriftAar'].isna().all() else 'N/A',
                'Average Construction Year': f"{self.dam_punkt_gdf['idriftAar'].mean():.0f}" if not self.dam_punkt_gdf['idriftAar'].isna().all() else 'N/A'
            },
            'Reservoirs': {
                'Total Count': len(self.magasin_gdf),
                'With Area Data': len(self.magasin_gdf.dropna(subset=['areal_km2'])),
                'With Volume Data': len(self.magasin_gdf.dropna(subset=['volOppdemt'])),
                'Total Area (km²)': f"{self.magasin_gdf['areal_km2'].sum():.2f}",
                'Average Area (km²)': f"{self.magasin_gdf['areal_km2'].mean():.2f}",
                'Largest Reservoir (km²)': f"{self.magasin_gdf['areal_km2'].max():.2f}",
                'Total Volume (million m³)': f"{self.magasin_gdf['volOppdemt'].sum():.1f}",
                'Average Volume (million m³)': f"{self.magasin_gdf['volOppdemt'].mean():.1f}"
            }
        }
        
        # Print summary
        print("\n" + "="*60)
        print("COMPREHENSIVE STATISTICAL SUMMARY")
        print("="*60)
        
        for category, stats in stats_summary.items():
            print(f"\n{category}:")
            print("-" * len(category))
            for key, value in stats.items():
                print(f"  {key}: {value}")
        
        # Save summary to file
        with open(self.output_dir / "statistical_summary.txt", "w") as f:
            f.write("Norwegian Hydropower Infrastructure - Statistical Summary\n")
            f.write("="*60 + "\n\n")
            
            for category, stats in stats_summary.items():
                f.write(f"{category}:\n")
                f.write("-" * len(category) + "\n")
                for key, value in stats.items():
                    f.write(f"  {key}: {value}\n")
                f.write("\n")
        
        print("✅ Saved statistical summary to file")
    
    def run_advanced_analysis(self):
        """Run the complete advanced analysis."""
        print("🚀 Starting Advanced Norwegian Hydropower Analysis")
        print("=" * 60)
        
        # Create all enhanced visualizations
        self.create_enhanced_reservoir_analysis()
        self.create_dam_construction_timeline()
        self.create_enhanced_spatial_visualization()
        self.create_statistical_summary()
        
        print("\n🎉 Advanced analysis completed successfully!")
        print("Check the 'output' directory for all generated files.")


def main():
    """Run the advanced analysis."""
    analyzer = AdvancedHydropowerAnalyzer()
    analyzer.run_advanced_analysis()


if __name__ == "__main__":
    main() 