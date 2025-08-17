#!/usr/bin/env python3
"""
Norwegian Hydropower Data Analysis
=================================

Main analysis script for Norwegian hydropower infrastructure data.
Provides comprehensive visualizations and statistical insights for
dam lines, dam points, and reservoir data from the NVE.

This script generates all the charts documented in ANALYSIS_REPORT.md
"""

import pandas as pd
import geopandas as gpd
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

class NorwegianHydropowerAnalyzer:
    """
    Advanced analyzer for Norwegian hydropower data with enhanced visualizations.
    """
    
    def __init__(self, data_dir="Data"):
        self.data_dir = Path(data_dir)

        # New results directory for fresh images
        self.results_dir = Path("results")
        self.results_dir.mkdir(exist_ok=True)

        # Archive directory for old images
        self.archive_dir = Path("old_visualizations")
        self.archive_dir.mkdir(exist_ok=True)
        
        # Load data
        self.load_all_data()
        # Archive any previously generated images (from legacy "output" or root)
        self._archive_previous_outputs()

    def _archive_previous_outputs(self):
        """Move existing generated images to a timestamped archive folder.

        This preserves old results and avoids overwriting, as requested.
        """
        legacy_output = Path("output")
        candidates: list[Path] = []

        if legacy_output.exists() and legacy_output.is_dir():
            for p in legacy_output.glob("**/*"):
                if p.is_file() and p.suffix.lower() in {".png", ".jpg", ".jpeg", ".kml", ".txt"}:
                    candidates.append(p)

        # Also consider any prior images saved beside this script (defensive)
        for p in Path.cwd().glob("*.png"):
            candidates.append(p)

        if not candidates:
            return

        ts_folder = self.archive_dir / datetime.now().strftime("%Y%m%d_%H%M%S")
        ts_folder.mkdir(parents=True, exist_ok=True)

        for src in candidates:
            # Maintain relative structure from legacy_output if applicable
            try:
                rel = src.relative_to(legacy_output) if src.is_relative_to(legacy_output) else src.name
            except AttributeError:
                # Python <3.9 compat: manual check
                try:
                    rel = src.relative_to(legacy_output)
                except Exception:
                    rel = src.name

            dest = ts_folder / (rel if isinstance(rel, str) else rel.as_posix())
            dest.parent.mkdir(parents=True, exist_ok=True)
            try:
                shutil.move(str(src), str(dest))
            except Exception:
                # If move fails for any reason, copy as fallback
                shutil.copy2(str(src), str(dest))
    
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
        """Create reservoir analyses as separate, well-labeled figures."""
        print("\n📊 Creating reservoir analyses (separate figures)...")

        # Clean data - remove zero and extreme outliers
        reservoir_data = self.magasin_gdf.copy()

        # Filter out unrealistic values
        area_data = reservoir_data[
            (reservoir_data['areal_km2'] > 0) &
            (reservoir_data['areal_km2'] < 200)
        ]['areal_km2']

        volume_data = reservoir_data[
            (reservoir_data['volOppdemt'] > 0) &
            (reservoir_data['volOppdemt'] < 1000)
        ]['volOppdemt'].dropna()

        # 1) Reservoir Areas Distribution
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.hist(area_data, bins=50, alpha=0.7, color='skyblue', edgecolor='black')
        ax.set_title('Reservoir Areas Distribution (Excluding Extreme Outliers)', fontweight='bold')
        ax.set_xlabel('Area (km²)')
        ax.set_ylabel('Number of Reservoirs')
        ax.grid(True, alpha=0.3)
        mean_area = area_data.mean()
        median_area = area_data.median()
        ax.axvline(mean_area, color='red', linestyle='--', label=f'Mean: {mean_area:.2f} km²')
        ax.axvline(median_area, color='orange', linestyle='--', label=f'Median: {median_area:.2f} km²')
        ax.legend()
        plt.tight_layout()
        plt.savefig(self.results_dir / "reservoir_areas_distribution.png", dpi=300, bbox_inches='tight')
        plt.close(fig)

        # 2) Reservoir Areas (Log Y)
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.hist(area_data, bins=50, alpha=0.7, color='lightgreen', edgecolor='black')
        ax.set_yscale('log')
        ax.set_title('Reservoir Areas (Log Scale)', fontweight='bold')
        ax.set_xlabel('Area (km²)')
        ax.set_ylabel('Number of Reservoirs (log)')
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(self.results_dir / "reservoir_areas_log.png", dpi=300, bbox_inches='tight')
        plt.close(fig)

        # 3) Reservoir Volumes Distribution
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.hist(volume_data, bins=40, alpha=0.7, color='lightcoral', edgecolor='black')
        ax.set_title('Reservoir Volumes Distribution (Excluding Extreme Outliers)', fontweight='bold')
        ax.set_xlabel('Volume (million m³)')
        ax.set_ylabel('Number of Reservoirs')
        ax.grid(True, alpha=0.3)
        mean_vol = volume_data.mean()
        median_vol = volume_data.median()
        ax.axvline(mean_vol, color='red', linestyle='--', label=f'Mean: {mean_vol:.1f} million m³')
        ax.axvline(median_vol, color='orange', linestyle='--', label=f'Median: {median_vol:.1f} million m³')
        ax.legend()
        plt.tight_layout()
        plt.savefig(self.results_dir / "reservoir_volumes_distribution.png", dpi=300, bbox_inches='tight')
        plt.close(fig)

        # 4) Size Categories Pie
        def categorize_reservoir_size(area: float) -> str:
            if area < 0.5:
                return 'Small (<0.5 km²)'
            if area < 5:
                return 'Medium (0.5-5 km²)'
            if area < 20:
                return 'Large (5-20 km²)'
            return 'Very Large (>20 km²)'

        size_categories = area_data.apply(categorize_reservoir_size)
        size_counts = size_categories.value_counts()
        fig, ax = plt.subplots(figsize=(8, 8))
        colors = ['lightblue', 'lightgreen', 'orange', 'red']
        ax.pie(size_counts.values, labels=size_counts.index, autopct='%1.1f%%', colors=colors, startangle=90)
        ax.set_title('Reservoir Size Categories (By Area)', fontweight='bold')
        plt.tight_layout()
        plt.savefig(self.results_dir / "reservoir_size_categories.png", dpi=300, bbox_inches='tight')
        plt.close(fig)

        # 5) Volume vs Area Scatter
        area_vol_data = reservoir_data[
            (reservoir_data['areal_km2'] > 0) &
            (reservoir_data['areal_km2'] < 100) &
            (reservoir_data['volOppdemt'] > 0) &
            (reservoir_data['volOppdemt'] < 500)
        ].dropna(subset=['areal_km2', 'volOppdemt'])

        if len(area_vol_data) > 0:
            fig, ax = plt.subplots(figsize=(10, 6))
            scatter = ax.scatter(
                area_vol_data['areal_km2'],
                area_vol_data['volOppdemt'],
                alpha=0.6,
                c=area_vol_data['areal_km2'],
                cmap='viridis',
                s=50,
                edgecolors='black',
                linewidth=0.3,
            )
            ax.set_xlabel('Area (km²)')
            ax.set_ylabel('Volume (million m³)')
            ax.set_title('Reservoir Volume vs Area', fontweight='bold')
            ax.grid(True, alpha=0.3)
            plt.colorbar(scatter, ax=ax, label='Area (km²)')
            correlation = area_vol_data['areal_km2'].corr(area_vol_data['volOppdemt'])
            ax.text(0.02, 0.98, f'Correlation: {correlation:.3f}', transform=ax.transAxes,
                    va='top', bbox=dict(boxstyle='round', facecolor='wheat'))
            plt.tight_layout()
            plt.savefig(self.results_dir / "reservoir_area_vs_volume.png", dpi=300, bbox_inches='tight')
            plt.close(fig)

        # 6) Top 10 Largest Reservoirs
        top_reservoirs = reservoir_data.nlargest(10, 'areal_km2')[['magNavn', 'areal_km2']].dropna()
        if len(top_reservoirs) > 0:
            fig, ax = plt.subplots(figsize=(10, 6))
            bars = ax.barh(range(len(top_reservoirs)), top_reservoirs['areal_km2'], color='steelblue', alpha=0.8)
            ax.set_yticks(range(len(top_reservoirs)))
            ax.set_yticklabels(top_reservoirs['magNavn'], fontsize=9)
            ax.set_xlabel('Area (km²)')
            ax.set_title('Top 10 Largest Reservoirs by Area', fontweight='bold')
            ax.grid(True, alpha=0.3, axis='x')
            for bar in bars:
                width = bar.get_width()
                ax.text(width + 0.5, bar.get_y() + bar.get_height()/2, f'{width:.1f}', ha='left', va='center', fontsize=9)
            plt.tight_layout()
            plt.savefig(self.results_dir / "top10_reservoirs_by_area.png", dpi=300, bbox_inches='tight')
            plt.close(fig)
    
    def create_dam_construction_timeline(self):
        """Create dam construction analyses as separate figures and fix annotation placement."""
        print("\n📈 Creating dam construction analyses (separate figures)...")

        # Combine dam data
        dam_data = pd.concat([
            self.dam_linje_gdf[['idriftAar']].assign(type='Line'),
            self.dam_punkt_gdf[['idriftAar']].assign(type='Point')
        ]).dropna()

        # Filter reasonable years
        dam_data = dam_data[(dam_data['idriftAar'] >= 1800) & (dam_data['idriftAar'] <= 2025)]

        # 1) Construction by decade
        dam_data['decade'] = (dam_data['idriftAar'] // 10) * 10
        decade_counts = dam_data['decade'].value_counts().sort_index()
        fig, ax = plt.subplots(figsize=(12, 7))
        bars = ax.bar(decade_counts.index, decade_counts.values, width=8, alpha=0.75, color='darkgreen', edgecolor='black')
        ax.set_title('Dam Construction by Decade', fontweight='bold')
        ax.set_xlabel('Decade')
        ax.set_ylabel('Number of Dams Built')
        ax.grid(True, alpha=0.3, axis='y')
        for bar in bars:
            height = bar.get_height()
            if height > 0:
                ax.text(bar.get_x() + bar.get_width()/2., height + 2, f'{int(height)}', ha='center', va='bottom', fontsize=9)
        plt.tight_layout()
        plt.savefig(self.results_dir / "construction_by_decade.png", dpi=300, bbox_inches='tight')
        plt.close(fig)

        # 2) Cumulative construction
        years = sorted(dam_data['idriftAar'].unique())
        cumulative = [len(dam_data[dam_data['idriftAar'] <= y]) for y in years]
        fig, ax = plt.subplots(figsize=(12, 7))
        ax.plot(years, cumulative, linewidth=3, color='navy', marker='o', markersize=4)
        ax.set_title('Cumulative Dam Construction', fontweight='bold')
        ax.set_xlabel('Year')
        ax.set_ylabel('Total Number of Dams')
        ax.grid(True, alpha=0.3)
        if 1950 in years:
            ax.annotate(
                'Post-WWII Boom',
                xy=(1950, cumulative[years.index(1950)]),
                xytext=(0.05, 0.9),
                textcoords='axes fraction',
                arrowprops=dict(arrowstyle='->', color='red'),
                fontsize=10,
                color='red',
                fontweight='bold',
            )
        plt.tight_layout()
        plt.savefig(self.results_dir / "cumulative_construction.png", dpi=300, bbox_inches='tight')
        plt.close(fig)

        # 3) Construction rate by 5-year period (annotation kept inside)
        dam_data['period'] = (dam_data['idriftAar'] // 5) * 5
        period_counts = dam_data['period'].value_counts().sort_index()
        construction_rate = period_counts / 5
        fig, ax = plt.subplots(figsize=(12, 7))
        ax.plot(construction_rate.index, construction_rate.values, linewidth=2.5, marker='s', markersize=6, color='darkred')
        ax.set_title('Dam Construction Rate (Dams per Year, 5-year periods)', fontweight='bold')
        ax.set_xlabel('Year')
        ax.set_ylabel('Dams per Year')
        ax.grid(True, alpha=0.3)
        if len(construction_rate) > 0:
            peak_period = construction_rate.idxmax()
            peak_rate = construction_rate.max()
            # Place annotation in the top-left inside the axes to avoid overflow
            ax.annotate(
                f'Peak: {peak_rate:.1f} dams/year\n({int(peak_period)}s)',
                xy=(peak_period, peak_rate),
                xytext=(0.02, 0.95),
                textcoords='axes fraction',
                ha='left', va='top',
                arrowprops=dict(arrowstyle='->', color='red'),
                fontsize=10, color='red', fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.6),
            )
        plt.tight_layout()
        plt.savefig(self.results_dir / "construction_rate_5yr.png", dpi=300, bbox_inches='tight')
        plt.close(fig)

        # 4) Historical context analysis
        historical_periods = {
            'Early Development (1800-1900)': (1800, 1900),
            'Industrial Growth (1900-1945)': (1900, 1945),
            'Post-War Boom (1945-1980)': (1945, 1980),
            'Modern Era (1980-2025)': (1980, 2025),
        }
        period_stats = []
        for period_name, (start, end) in historical_periods.items():
            count = len(dam_data[(dam_data['idriftAar'] >= start) & (dam_data['idriftAar'] < end)])
            period_stats.append({'Period': period_name, 'Count': count})
        period_df = pd.DataFrame(period_stats)
        fig, ax = plt.subplots(figsize=(12, 7))
        bars = ax.bar(range(len(period_df)), period_df['Count'], color=['lightblue', 'lightgreen', 'orange', 'lightcoral'], alpha=0.85, edgecolor='black')
        ax.set_title("Dam Construction by Historical Period", fontweight='bold')
        ax.set_xticks(range(len(period_df)))
        ax.set_xticklabels([p.replace(' ', '\n') for p in period_df['Period']], rotation=0, fontsize=9)
        ax.set_ylabel('Number of Dams')
        ax.grid(True, alpha=0.3, axis='y')
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 5, f'{int(height)}', ha='center', va='bottom', fontsize=10, fontweight='bold')
        plt.tight_layout()
        plt.savefig(self.results_dir / "construction_by_historical_period.png", dpi=300, bbox_inches='tight')
        plt.close(fig)
    
    def create_enhanced_spatial_visualization(self):
        """Create spatial visualizations as separate images."""
        print("\n🗺️  Creating spatial visualizations (separate figures)...")

        # Convert to WGS84 for better visualization
        dam_linje_wgs84 = self.dam_linje_gdf.to_crs('EPSG:4326')
        dam_punkt_wgs84 = self.dam_punkt_gdf.to_crs('EPSG:4326')
        magasin_wgs84 = self.magasin_gdf.to_crs('EPSG:4326')

        # 1) Dam Lines with reservoirs background
        fig, ax = plt.subplots(figsize=(12, 8))
        magasin_wgs84.plot(ax=ax, color='lightblue', alpha=0.3, edgecolor='none')
        dam_linje_wgs84.plot(ax=ax, color='red', linewidth=1.2, alpha=0.85)
        ax.set_title('Norwegian Dam Lines (Enhanced Visibility)', fontweight='bold')
        ax.set_xlabel('Longitude')
        ax.set_ylabel('Latitude')
        ax.grid(True, alpha=0.3)
        ax.text(0.02, 0.98, f'Total Dam Lines: {len(dam_linje_wgs84)}', transform=ax.transAxes,
                bbox=dict(boxstyle='round', facecolor='white'), va='top', fontsize=10, fontweight='bold')
        plt.tight_layout()
        plt.savefig(self.results_dir / "spatial_dam_lines.png", dpi=300, bbox_inches='tight')
        plt.close(fig)

        # 2) Dam Points sized/colored by year
        current_year = 2024
        dam_punkt_clean = dam_punkt_wgs84.dropna(subset=['idriftAar'])
        dam_punkt_clean = dam_punkt_clean[dam_punkt_clean['idriftAar'] > 1800]
        ages = current_year - dam_punkt_clean['idriftAar']
        sizes = 100 - (ages / ages.max()) * 80  # 20-100
        fig, ax = plt.subplots(figsize=(12, 8))
        magasin_wgs84.plot(ax=ax, color='lightblue', alpha=0.2, edgecolor='none')
        sc = ax.scatter(dam_punkt_clean.geometry.x, dam_punkt_clean.geometry.y,
                        c=dam_punkt_clean['idriftAar'], s=sizes, alpha=0.7,
                        cmap='plasma', edgecolors='black', linewidth=0.3)
        ax.set_title('Dam Points (Size by Era, Color by Year)', fontweight='bold')
        ax.set_xlabel('Longitude')
        ax.set_ylabel('Latitude')
        ax.grid(True, alpha=0.3)
        cbar = plt.colorbar(sc, ax=ax)
        cbar.set_label('Construction Year', fontsize=10)
        plt.tight_layout()
        plt.savefig(self.results_dir / "spatial_dam_points_by_year.png", dpi=300, bbox_inches='tight')
        plt.close(fig)

        # 3) Reservoir size categories map
        def get_reservoir_color(area: float) -> str:
            if area < 0.5:
                return 'lightblue'
            if area < 5:
                return 'blue'
            if area < 20:
                return 'darkblue'
            return 'navy'

        magasin_clean = magasin_wgs84[magasin_wgs84['areal_km2'] > 0]
        colors = magasin_clean['areal_km2'].apply(get_reservoir_color)
        fig, ax = plt.subplots(figsize=(12, 8))
        magasin_clean.plot(ax=ax, color=colors, alpha=0.75, edgecolor='white', linewidth=0.5)
        ax.set_title('Reservoir Size Categories (Color-Coded by Area)', fontweight='bold')
        ax.set_xlabel('Longitude')
        ax.set_ylabel('Latitude')
        ax.grid(True, alpha=0.3)
        legend_elements = [
            plt.Rectangle((0,0),1,1, facecolor='lightblue', label='Small (<0.5 km²)'),
            plt.Rectangle((0,0),1,1, facecolor='blue', label='Medium (0.5-5 km²)'),
            plt.Rectangle((0,0),1,1, facecolor='darkblue', label='Large (5-20 km²)'),
            plt.Rectangle((0,0),1,1, facecolor='navy', label='Very Large (>20 km²)')
        ]
        ax.legend(handles=legend_elements, loc='upper right')
        plt.tight_layout()
        plt.savefig(self.results_dir / "spatial_reservoir_size_categories.png", dpi=300, bbox_inches='tight')
        plt.close(fig)

        # 4) Complete infrastructure overview
        fig, ax = plt.subplots(figsize=(12, 8))
        magasin_wgs84.plot(ax=ax, color='lightblue', alpha=0.4, edgecolor='none')
        dam_punkt_wgs84.plot(ax=ax, color='red', markersize=5, alpha=0.6, label='Dam Points')
        dam_linje_wgs84.plot(ax=ax, color='darkred', linewidth=1.8, alpha=0.8, label='Dam Lines')
        ax.set_title('Complete Infrastructure Overview', fontweight='bold')
        ax.set_xlabel('Longitude')
        ax.set_ylabel('Latitude')
        ax.grid(True, alpha=0.3)
        ax.legend()
        stats_text = (
            f"Infrastructure Summary:\n"
            f"• Dam Lines: {len(dam_linje_wgs84):,}\n"
            f"• Dam Points: {len(dam_punkt_wgs84):,}\n"
            f"• Reservoirs: {len(magasin_wgs84):,}\n"
            f"• Total Features: {len(dam_linje_wgs84) + len(dam_punkt_wgs84) + len(magasin_wgs84):,}"
        )
        ax.text(0.02, 0.02, stats_text, transform=ax.transAxes, bbox=dict(boxstyle='round', facecolor='white', alpha=0.9),
                fontsize=10, fontweight='bold', va='bottom')
        plt.tight_layout()
        plt.savefig(self.results_dir / "spatial_complete_overview.png", dpi=300, bbox_inches='tight')
        plt.close(fig)
    
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
        with open(self.results_dir / "statistical_summary.txt", "w") as f:
            f.write("Norwegian Hydropower Infrastructure - Statistical Summary\n")
            f.write("="*60 + "\n\n")
            
            for category, stats in stats_summary.items():
                f.write(f"{category}:\n")
                f.write("-" * len(category) + "\n")
                for key, value in stats.items():
                    f.write(f"  {key}: {value}\n")
                f.write("\n")
        
        print("✅ Saved statistical summary to file")
    
    def run_complete_analysis(self):
        """Run the complete Norwegian hydropower analysis."""
        print("🚀 Starting Norwegian Hydropower Analysis")
        print("=" * 60)
        
        # Create all enhanced visualizations
        self.create_enhanced_reservoir_analysis()
        self.create_dam_construction_timeline()
        self.create_enhanced_spatial_visualization()
        self.create_statistical_summary()
        
        print("\n🎉 Analysis completed successfully!")
        print("New images saved in 'Norway_Analysis/results/'.")
        print("Previous images archived under 'Norway_Analysis/old_visualizations/'.")
        print("See ANALYSIS_REPORT.md for detailed explanations of all charts.")


def main():
    """Run the complete analysis."""
    analyzer = NorwegianHydropowerAnalyzer()
    analyzer.run_complete_analysis()


if __name__ == "__main__":
    main() 