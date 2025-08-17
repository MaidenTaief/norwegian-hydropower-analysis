#!/usr/bin/env python3
"""
Indian Dam Analysis System - Enhanced Version
=============================================

Enhanced analysis of Indian dams using the Global Dam Watch (GDW) database.
This enhanced version provides comprehensive visualizations and statistical insights
similar to the Norwegian hydropower analysis.

Features:
- Comprehensive analysis of 7,097+ Indian dams
- Spatial visualizations with enhanced mapping
- Construction timeline analysis with historical context
- Reservoir capacity and area analysis
- Hydropower generation analysis
- Regional distribution analysis
- Statistical summaries and reporting
- Organized output structure with archiving
"""

import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path
import shutil
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Set up plotting style
plt.style.use('default')
sns.set_palette("Set2")
plt.rcParams['figure.figsize'] = (15, 10)
plt.rcParams['font.size'] = 10

class IndianDamAnalyzerEnhanced:
    """
    Enhanced analyzer for Indian dam data from the Global Dam Watch database.
    Provides comprehensive analysis with organized output structure.
    """
    
    def __init__(self, data_dir="../25988293/GDW_v1_0_shp/GDW_v1_0_shp"):
        self.data_dir = Path(data_dir)
        
        # New organized results directory
        self.results_dir = Path("results/gdw_full")
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        # Archive directory for old images
        self.archive_dir = Path("old_visualizations")
        self.archive_dir.mkdir(exist_ok=True)
        
        # Load data
        self.load_gdw_data()
        
    def load_gdw_data(self):
        """Load GDW barriers data and filter for India."""
        print("🔄 Loading GDW database and filtering for Indian dams...")
        
        try:
            # Load the global database
            gdw_file = self.data_dir / "GDW_barriers_v1_0.shp"
            if not gdw_file.exists():
                print(f"❌ GDW file not found at {gdw_file}")
                return False
                
            # Load global dam data
            self.global_dams_gdf = gpd.read_file(gdw_file)
            print(f"✅ Loaded global database with {len(self.global_dams_gdf)} dams")
            
            # Filter for India
            self.indian_dams_gdf = self.global_dams_gdf[
                self.global_dams_gdf['COUNTRY'] == 'India'
            ].copy()
            
            print(f"✅ Filtered {len(self.indian_dams_gdf)} Indian dams")
            
            # Ensure coordinate system is WGS84
            if self.indian_dams_gdf.crs.to_string() != 'EPSG:4326':
                self.indian_dams_gdf = self.indian_dams_gdf.to_crs('EPSG:4326')
                
            return True
            
        except Exception as e:
            print(f"❌ Error loading GDW data: {e}")
            return False
    
    def create_construction_timeline_analysis(self):
        """Create comprehensive construction timeline analyses."""
        print("\n📈 Creating construction timeline analyses...")
        
        # Clean construction year data
        timeline_data = self.indian_dams_gdf[
            (self.indian_dams_gdf['YEAR_DAM'] >= 1800) & 
            (self.indian_dams_gdf['YEAR_DAM'] <= 2025)
        ].copy()
        
        if len(timeline_data) == 0:
            print("⚠️ No valid construction year data found")
            return
        
        # 1) Construction by decade
        timeline_data['decade'] = (timeline_data['YEAR_DAM'] // 10) * 10
        decade_counts = timeline_data['decade'].value_counts().sort_index()
        
        fig, ax = plt.subplots(figsize=(12, 7))
        bars = ax.bar(decade_counts.index, decade_counts.values, width=8, 
                     alpha=0.75, color='darkblue', edgecolor='black')
        ax.set_title('Indian Dam Construction by Decade', fontweight='bold', fontsize=14)
        ax.set_xlabel('Decade')
        ax.set_ylabel('Number of Dams Built')
        ax.grid(True, alpha=0.3, axis='y')
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            if height > 0:
                ax.text(bar.get_x() + bar.get_width()/2., height + 1, 
                       f'{int(height)}', ha='center', va='bottom', fontsize=9)
        
        plt.tight_layout()
        plt.savefig(self.results_dir / "construction_by_decade.png", dpi=300, bbox_inches='tight')
        plt.close(fig)
        
        # 2) Cumulative construction over time
        years = sorted(timeline_data['YEAR_DAM'].unique())
        cumulative = [len(timeline_data[timeline_data['YEAR_DAM'] <= y]) for y in years]
        
        fig, ax = plt.subplots(figsize=(12, 7))
        ax.plot(years, cumulative, linewidth=3, color='darkgreen', marker='o', markersize=4)
        ax.set_title('Cumulative Indian Dam Construction Over Time', fontweight='bold', fontsize=14)
        ax.set_xlabel('Year')
        ax.set_ylabel('Total Number of Dams')
        ax.grid(True, alpha=0.3)
        
        # Add historical context annotations
        if 1947 in years:
            independence_idx = years.index(1947)
            ax.annotate('Indian Independence\n(1947)', 
                       xy=(1947, cumulative[independence_idx]),
                       xytext=(0.2, 0.3), textcoords='axes fraction',
                       arrowprops=dict(arrowstyle='->', color='red'),
                       fontsize=10, color='red', fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(self.results_dir / "cumulative_construction.png", dpi=300, bbox_inches='tight')
        plt.close(fig)
        
        # 3) Historical periods analysis
        historical_periods = {
            'British Era (1800-1947)': (1800, 1947),
            'Early Independence (1947-1970)': (1947, 1970),
            'Green Revolution (1970-1990)': (1970, 1990),
            'Economic Liberalization (1990-2010)': (1990, 2010),
            'Modern Era (2010-2025)': (2010, 2025)
        }
        
        period_stats = []
        for period_name, (start, end) in historical_periods.items():
            count = len(timeline_data[(timeline_data['YEAR_DAM'] >= start) & 
                                    (timeline_data['YEAR_DAM'] < end)])
            period_stats.append({'Period': period_name, 'Count': count})
        
        period_df = pd.DataFrame(period_stats)
        
        fig, ax = plt.subplots(figsize=(12, 7))
        colors = ['lightcoral', 'lightblue', 'lightgreen', 'orange', 'purple']
        bars = ax.bar(range(len(period_df)), period_df['Count'], 
                     color=colors[:len(period_df)], alpha=0.8, edgecolor='black')
        
        ax.set_title("Indian Dam Construction by Historical Period", fontweight='bold', fontsize=14)
        ax.set_xticks(range(len(period_df)))
        ax.set_xticklabels([p.replace(' ', '\n') for p in period_df['Period']], 
                          rotation=0, fontsize=9)
        ax.set_ylabel('Number of Dams')
        ax.grid(True, alpha=0.3, axis='y')
        
        # Add value labels
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 5, 
                   f'{int(height)}', ha='center', va='bottom', 
                   fontsize=10, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(self.results_dir / "construction_by_historical_period.png", 
                   dpi=300, bbox_inches='tight')
        plt.close(fig)
    
    def create_spatial_visualizations(self):
        """Create comprehensive spatial visualizations."""
        print("\n🗺️ Creating spatial visualizations...")
        
        # 1) Geographic distribution of all Indian dams
        fig, ax = plt.subplots(figsize=(12, 8))
        self.indian_dams_gdf.plot(ax=ax, markersize=8, alpha=0.6, color='red')
        ax.set_title('Geographic Distribution of Indian Dams\nComplete GDW Dataset', 
                    fontweight='bold', fontsize=14)
        ax.set_xlabel('Longitude')
        ax.set_ylabel('Latitude')
        ax.grid(True, alpha=0.3)
        
        # Add statistics box
        stats_text = (f"Total Indian Dams: {len(self.indian_dams_gdf):,}\n"
                     f"Coverage: Pan-India\n"
                     f"Data Source: Global Dam Watch")
        ax.text(0.02, 0.98, stats_text, transform=ax.transAxes,
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.9),
                va='top', fontsize=10, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(self.results_dir / "spatial_distribution_overview.png", 
                   dpi=300, bbox_inches='tight')
        plt.close(fig)
        
        # 2) Dams by construction era (colored by decade)
        timeline_data = self.indian_dams_gdf[
            (self.indian_dams_gdf['YEAR_DAM'] >= 1900) & 
            (self.indian_dams_gdf['YEAR_DAM'] <= 2020)
        ].copy()
        
        if len(timeline_data) > 0:
            fig, ax = plt.subplots(figsize=(12, 8))
            scatter = ax.scatter(timeline_data.geometry.x, timeline_data.geometry.y,
                               c=timeline_data['YEAR_DAM'], s=25, alpha=0.7,
                               cmap='viridis', edgecolors='black', linewidth=0.2)
            
            ax.set_title('Indian Dams by Construction Year\nColor-coded by Era', 
                        fontweight='bold', fontsize=14)
            ax.set_xlabel('Longitude')
            ax.set_ylabel('Latitude')
            ax.grid(True, alpha=0.3)
            
            cbar = plt.colorbar(scatter, ax=ax)
            cbar.set_label('Construction Year', fontsize=10)
            
            plt.tight_layout()
            plt.savefig(self.results_dir / "spatial_dams_by_construction_year.png", 
                       dpi=300, bbox_inches='tight')
            plt.close(fig)
        
        # 3) Dam height categories
        height_data = self.indian_dams_gdf[self.indian_dams_gdf['DAM_HGT_M'] > 0].copy()
        
        if len(height_data) > 0:
            def categorize_height(height):
                if height < 15:
                    return 'Small (<15m)'
                elif height < 30:
                    return 'Medium (15-30m)'
                elif height < 60:
                    return 'Large (30-60m)'
                else:
                    return 'Major (>60m)'
            
            height_data['height_category'] = height_data['DAM_HGT_M'].apply(categorize_height)
            
            fig, ax = plt.subplots(figsize=(12, 8))
            
            colors = {'Small (<15m)': 'lightblue', 'Medium (15-30m)': 'blue', 
                     'Large (30-60m)': 'darkblue', 'Major (>60m)': 'red'}
            
            for category, color in colors.items():
                data = height_data[height_data['height_category'] == category]
                if len(data) > 0:
                    ax.scatter(data.geometry.x, data.geometry.y, 
                             c=color, s=20, alpha=0.7, label=category,
                             edgecolors='black', linewidth=0.2)
            
            ax.set_title('Indian Dams by Height Category', fontweight='bold', fontsize=14)
            ax.set_xlabel('Longitude')
            ax.set_ylabel('Latitude')
            ax.grid(True, alpha=0.3)
            ax.legend(loc='upper right')
            
            plt.tight_layout()
            plt.savefig(self.results_dir / "spatial_dams_by_height_category.png", 
                       dpi=300, bbox_inches='tight')
            plt.close(fig)
    
    def create_reservoir_analysis(self):
        """Create reservoir capacity and area analyses."""
        print("\n💧 Creating reservoir analyses...")
        
        # Clean reservoir data
        reservoir_data = self.indian_dams_gdf[
            (self.indian_dams_gdf['AREA_SKM'] > 0) & 
            (self.indian_dams_gdf['AREA_SKM'] < 1000)  # Remove extreme outliers
        ].copy()
        
        capacity_data = self.indian_dams_gdf[
            (self.indian_dams_gdf['CAP_MCM'] > 0) & 
            (self.indian_dams_gdf['CAP_MCM'] < 10000)  # Remove extreme outliers
        ].copy()
        
        # 1) Reservoir area distribution
        if len(reservoir_data) > 0:
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.hist(reservoir_data['AREA_SKM'], bins=50, alpha=0.7, 
                   color='skyblue', edgecolor='black')
            ax.set_title('Indian Reservoir Area Distribution', fontweight='bold')
            ax.set_xlabel('Reservoir Area (km²)')
            ax.set_ylabel('Number of Reservoirs')
            ax.grid(True, alpha=0.3)
            
            mean_area = reservoir_data['AREA_SKM'].mean()
            median_area = reservoir_data['AREA_SKM'].median()
            ax.axvline(mean_area, color='red', linestyle='--', 
                      label=f'Mean: {mean_area:.2f} km²')
            ax.axvline(median_area, color='orange', linestyle='--', 
                      label=f'Median: {median_area:.2f} km²')
            ax.legend()
            
            plt.tight_layout()
            plt.savefig(self.results_dir / "reservoir_area_distribution.png", 
                       dpi=300, bbox_inches='tight')
            plt.close(fig)
        
        # 2) Reservoir capacity distribution
        if len(capacity_data) > 0:
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.hist(capacity_data['CAP_MCM'], bins=50, alpha=0.7, 
                   color='lightgreen', edgecolor='black')
            ax.set_title('Indian Reservoir Capacity Distribution', fontweight='bold')
            ax.set_xlabel('Reservoir Capacity (Million m³)')
            ax.set_ylabel('Number of Reservoirs')
            ax.grid(True, alpha=0.3)
            
            mean_cap = capacity_data['CAP_MCM'].mean()
            median_cap = capacity_data['CAP_MCM'].median()
            ax.axvline(mean_cap, color='red', linestyle='--', 
                      label=f'Mean: {mean_cap:.1f} MCM')
            ax.axvline(median_cap, color='orange', linestyle='--', 
                      label=f'Median: {median_cap:.1f} MCM')
            ax.legend()
            
            plt.tight_layout()
            plt.savefig(self.results_dir / "reservoir_capacity_distribution.png", 
                       dpi=300, bbox_inches='tight')
            plt.close(fig)
        
        # 3) Top 10 largest reservoirs by area
        if len(reservoir_data) > 0:
            top_reservoirs = reservoir_data.nlargest(10, 'AREA_SKM')[
                ['DAM_NAME', 'AREA_SKM']
            ].dropna()
            
            if len(top_reservoirs) > 0:
                fig, ax = plt.subplots(figsize=(10, 6))
                bars = ax.barh(range(len(top_reservoirs)), top_reservoirs['AREA_SKM'],
                              color='steelblue', alpha=0.8)
                ax.set_yticks(range(len(top_reservoirs)))
                ax.set_yticklabels(top_reservoirs['DAM_NAME'], fontsize=9)
                ax.set_xlabel('Reservoir Area (km²)')
                ax.set_title('Top 10 Largest Indian Reservoirs by Area', fontweight='bold')
                ax.grid(True, alpha=0.3, axis='x')
                
                # Add value labels
                for i, bar in enumerate(bars):
                    width = bar.get_width()
                    ax.text(width + 2, bar.get_y() + bar.get_height()/2, 
                           f'{width:.1f}', ha='left', va='center', fontsize=9)
                
                plt.tight_layout()
                plt.savefig(self.results_dir / "top10_reservoirs_by_area.png", 
                           dpi=300, bbox_inches='tight')
                plt.close(fig)
    
    def create_hydropower_analysis(self):
        """Create hydropower generation analysis."""
        print("\n⚡ Creating hydropower analyses...")
        
        # Clean power data
        power_data = self.indian_dams_gdf[
            (self.indian_dams_gdf['POWER_MW'] > 0) & 
            (self.indian_dams_gdf['POWER_MW'] < 5000)  # Remove extreme outliers
        ].copy()
        
        if len(power_data) == 0:
            print("⚠️ No valid hydropower data found")
            return
        
        # 1) Power generation distribution
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.hist(power_data['POWER_MW'], bins=40, alpha=0.7, 
               color='orange', edgecolor='black')
        ax.set_title('Indian Hydropower Generation Distribution', fontweight='bold')
        ax.set_xlabel('Power Generation (MW)')
        ax.set_ylabel('Number of Dams')
        ax.grid(True, alpha=0.3)
        
        mean_power = power_data['POWER_MW'].mean()
        median_power = power_data['POWER_MW'].median()
        ax.axvline(mean_power, color='red', linestyle='--', 
                  label=f'Mean: {mean_power:.1f} MW')
        ax.axvline(median_power, color='orange', linestyle='--', 
                  label=f'Median: {median_power:.1f} MW')
        ax.legend()
        
        plt.tight_layout()
        plt.savefig(self.results_dir / "hydropower_distribution.png", 
                   dpi=300, bbox_inches='tight')
        plt.close(fig)
        
        # 2) Top 10 largest hydropower facilities
        top_power = power_data.nlargest(10, 'POWER_MW')[
            ['DAM_NAME', 'POWER_MW']
        ].dropna()
        
        if len(top_power) > 0:
            fig, ax = plt.subplots(figsize=(10, 6))
            bars = ax.barh(range(len(top_power)), top_power['POWER_MW'],
                          color='darkgreen', alpha=0.8)
            ax.set_yticks(range(len(top_power)))
            ax.set_yticklabels(top_power['DAM_NAME'], fontsize=9)
            ax.set_xlabel('Power Generation (MW)')
            ax.set_title('Top 10 Indian Hydropower Facilities', fontweight='bold')
            ax.grid(True, alpha=0.3, axis='x')
            
            # Add value labels
            for i, bar in enumerate(bars):
                width = bar.get_width()
                ax.text(width + 10, bar.get_y() + bar.get_height()/2, 
                       f'{width:.0f}', ha='left', va='center', fontsize=9)
            
            plt.tight_layout()
            plt.savefig(self.results_dir / "top10_hydropower_facilities.png", 
                       dpi=300, bbox_inches='tight')
            plt.close(fig)
    
    def create_statistical_summary(self):
        """Create comprehensive statistical summary."""
        print("\n📊 Creating statistical summary...")
        
        # Calculate comprehensive statistics
        total_dams = len(self.indian_dams_gdf)
        dams_with_year = len(self.indian_dams_gdf.dropna(subset=['YEAR_DAM']))
        dams_with_height = len(self.indian_dams_gdf[self.indian_dams_gdf['DAM_HGT_M'] > 0])
        dams_with_area = len(self.indian_dams_gdf[self.indian_dams_gdf['AREA_SKM'] > 0])
        dams_with_capacity = len(self.indian_dams_gdf[self.indian_dams_gdf['CAP_MCM'] > 0])
        dams_with_power = len(self.indian_dams_gdf[self.indian_dams_gdf['POWER_MW'] > 0])
        
        stats_summary = {
            'Dataset Overview': {
                'Total Indian Dams': total_dams,
                'Data Source': 'Global Dam Watch (GDW)',
                'Geographic Coverage': 'Pan-India',
                'Data Completeness': 'Variable by attribute'
            },
            'Construction Timeline': {
                'Dams with Construction Year': dams_with_year,
                'Coverage Percentage': f"{(dams_with_year/total_dams)*100:.1f}%",
                'Oldest Dam Year': int(self.indian_dams_gdf['YEAR_DAM'].min()) if dams_with_year > 0 else 'N/A',
                'Newest Dam Year': int(self.indian_dams_gdf['YEAR_DAM'].max()) if dams_with_year > 0 else 'N/A',
                'Average Construction Year': f"{self.indian_dams_gdf['YEAR_DAM'].mean():.0f}" if dams_with_year > 0 else 'N/A'
            },
            'Physical Characteristics': {
                'Dams with Height Data': dams_with_height,
                'Average Height (m)': f"{self.indian_dams_gdf[self.indian_dams_gdf['DAM_HGT_M'] > 0]['DAM_HGT_M'].mean():.2f}" if dams_with_height > 0 else 'N/A',
                'Maximum Height (m)': f"{self.indian_dams_gdf['DAM_HGT_M'].max():.2f}" if dams_with_height > 0 else 'N/A',
                'Dams with Area Data': dams_with_area,
                'Total Reservoir Area (km²)': f"{self.indian_dams_gdf[self.indian_dams_gdf['AREA_SKM'] > 0]['AREA_SKM'].sum():.2f}" if dams_with_area > 0 else 'N/A'
            },
            'Capacity and Power': {
                'Dams with Capacity Data': dams_with_capacity,
                'Total Capacity (MCM)': f"{self.indian_dams_gdf[self.indian_dams_gdf['CAP_MCM'] > 0]['CAP_MCM'].sum():.1f}" if dams_with_capacity > 0 else 'N/A',
                'Dams with Power Data': dams_with_power,
                'Total Power Generation (MW)': f"{self.indian_dams_gdf[self.indian_dams_gdf['POWER_MW'] > 0]['POWER_MW'].sum():.1f}" if dams_with_power > 0 else 'N/A'
            }
        }
        
        # Print summary
        print("\n" + "="*60)
        print("COMPREHENSIVE INDIAN DAM ANALYSIS - GDW FULL DATASET")
        print("="*60)
        
        for category, stats in stats_summary.items():
            print(f"\n{category}:")
            print("-" * len(category))
            for key, value in stats.items():
                print(f"  {key}: {value}")
        
        # Save summary to file
        with open(self.results_dir / "statistical_summary_gdw_full.txt", "w") as f:
            f.write("Indian Dam Infrastructure Analysis - GDW Full Dataset\n")
            f.write("="*60 + "\n\n")
            
            for category, stats in stats_summary.items():
                f.write(f"{category}:\n")
                f.write("-" * len(category) + "\n")
                for key, value in stats.items():
                    f.write(f"  {key}: {value}\n")
                f.write("\n")
        
        print("✅ Saved statistical summary to file")
    
    def run_complete_analysis(self):
        """Run the complete Indian dam analysis for GDW full dataset."""
        print("🚀 Starting Indian Dam Analysis - Enhanced GDW Full Dataset")
        print("=" * 60)
        
        # Create all enhanced visualizations
        self.create_construction_timeline_analysis()
        self.create_spatial_visualizations()
        self.create_reservoir_analysis()
        self.create_hydropower_analysis()
        self.create_statistical_summary()
        
        print("\n🎉 GDW Full Dataset Analysis completed successfully!")
        print(f"📁 Results saved in: {self.results_dir}")
        print(f"📊 Total dams analyzed: {len(self.indian_dams_gdf):,}")
        print("🗂️ Generated visualizations:")
        print("   • Construction timeline analyses")
        print("   • Spatial distribution maps")
        print("   • Reservoir capacity analyses")
        print("   • Hydropower generation analyses")
        print("   • Comprehensive statistical summary")

def main():
    """Run the complete enhanced Indian dam analysis."""
    analyzer = IndianDamAnalyzerEnhanced()
    analyzer.run_complete_analysis()

if __name__ == "__main__":
    main()
