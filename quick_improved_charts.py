#!/usr/bin/env python3
"""
Quick Improved Charts for Norwegian Hydropower Data
==================================================

This script creates focused, improved visualizations addressing
the specific issues with reservoir charts and dam line visibility.
"""

import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

def load_data():
    """Load the hydropower data."""
    print("Loading data...")
    dam_linje = gpd.read_file("Data/Vannkraft_DamLinje.shp")
    dam_punkt = gpd.read_file("Data/Vannkraft_DamPunkt.shp") 
    magasin = gpd.read_file("Data/Vannkraft_Magasin.shp")
    return dam_linje, dam_punkt, magasin

def create_improved_reservoir_charts():
    """Create much better reservoir area and volume charts."""
    print("Creating improved reservoir charts...")
    
    _, _, magasin = load_data()
    
    # Create figure
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    fig.suptitle('Norwegian Reservoirs - Improved Analysis', fontsize=16, fontweight='bold')
    
    # 1. Better Area Distribution (remove zeros and outliers)
    area_data = magasin[magasin['areal_km2'] > 0]['areal_km2']
    area_clean = area_data[area_data < area_data.quantile(0.95)]  # Remove top 5% outliers
    
    axes[0,0].hist(area_clean, bins=30, alpha=0.8, color='steelblue', edgecolor='black')
    axes[0,0].set_title('Reservoir Areas (Cleaned Data)\nExcluding Zeros & Extreme Outliers', fontweight='bold')
    axes[0,0].set_xlabel('Area (km²)')
    axes[0,0].set_ylabel('Number of Reservoirs')
    axes[0,0].grid(True, alpha=0.3)
    
    # Add statistics text
    mean_area = area_clean.mean()
    median_area = area_clean.median()
    axes[0,0].axvline(mean_area, color='red', linestyle='--', linewidth=2, label=f'Mean: {mean_area:.2f} km²')
    axes[0,0].axvline(median_area, color='orange', linestyle='--', linewidth=2, label=f'Median: {median_area:.2f} km²')
    axes[0,0].legend()
    
    # 2. Logarithmic View for Better Distribution
    axes[0,1].hist(area_data, bins=50, alpha=0.8, color='forestgreen', edgecolor='black')
    axes[0,1].set_yscale('log')
    axes[0,1].set_title('Reservoir Areas (Log Scale)\nBetter View of Full Distribution', fontweight='bold')
    axes[0,1].set_xlabel('Area (km²)')
    axes[0,1].set_ylabel('Number of Reservoirs (Log Scale)')
    axes[0,1].grid(True, alpha=0.3)
    
    # 3. Size Categories Pie Chart
    def categorize_size(area):
        if area <= 0:
            return 'No Data'
        elif area < 1:
            return 'Small (<1 km²)'
        elif area < 10:
            return 'Medium (1-10 km²)'
        elif area < 50:
            return 'Large (10-50 km²)'
        else:
            return 'Very Large (>50 km²)'
    
    categories = magasin['areal_km2'].apply(categorize_size)
    cat_counts = categories.value_counts()
    
    colors = ['lightgray', 'lightblue', 'steelblue', 'darkblue', 'navy']
    wedges, texts, autotexts = axes[0,2].pie(cat_counts.values, labels=cat_counts.index, 
                                            autopct='%1.1f%%', colors=colors[:len(cat_counts)],
                                            startangle=90)
    axes[0,2].set_title('Reservoir Size Distribution\nby Category', fontweight='bold')
    
    # 4. Better Volume Analysis
    volume_data = magasin[magasin['volOppdemt'] > 0]['volOppdemt'].dropna()
    volume_clean = volume_data[volume_data < volume_data.quantile(0.98)]  # Remove top 2% outliers
    
    axes[1,0].hist(volume_clean, bins=25, alpha=0.8, color='darkorange', edgecolor='black')
    axes[1,0].set_title('Reservoir Volumes (Cleaned)\nExcluding Extreme Outliers', fontweight='bold')
    axes[1,0].set_xlabel('Volume (million m³)')
    axes[1,0].set_ylabel('Number of Reservoirs')
    axes[1,0].grid(True, alpha=0.3)
    
    # Add statistics
    mean_vol = volume_clean.mean()
    median_vol = volume_clean.median()
    axes[1,0].axvline(mean_vol, color='red', linestyle='--', linewidth=2, label=f'Mean: {mean_vol:.1f}')
    axes[1,0].axvline(median_vol, color='orange', linestyle='--', linewidth=2, label=f'Median: {median_vol:.1f}')
    axes[1,0].legend()
    
    # 5. Top 15 Largest Reservoirs Bar Chart
    top_reservoirs = magasin.nlargest(15, 'areal_km2')[['magNavn', 'areal_km2']].dropna()
    
    bars = axes[1,1].barh(range(len(top_reservoirs)), top_reservoirs['areal_km2'], 
                         color='teal', alpha=0.8, edgecolor='black')
    axes[1,1].set_yticks(range(len(top_reservoirs)))
    axes[1,1].set_yticklabels(top_reservoirs['magNavn'], fontsize=9)
    axes[1,1].set_xlabel('Area (km²)')
    axes[1,1].set_title('Top 15 Largest Reservoirs\nby Area', fontweight='bold')
    axes[1,1].grid(True, alpha=0.3, axis='x')
    
    # Add value labels
    for i, bar in enumerate(bars):
        width = bar.get_width()
        axes[1,1].text(width + 2, bar.get_y() + bar.get_height()/2, 
                      f'{width:.1f}', ha='left', va='center', fontsize=8, fontweight='bold')
    
    # 6. Volume vs Area Relationship
    combined_data = magasin[(magasin['areal_km2'] > 0) & (magasin['volOppdemt'] > 0)].dropna(subset=['areal_km2', 'volOppdemt'])
    # Remove extreme outliers for better visualization
    combined_clean = combined_data[
        (combined_data['areal_km2'] < combined_data['areal_km2'].quantile(0.95)) &
        (combined_data['volOppdemt'] < combined_data['volOppdemt'].quantile(0.95))
    ]
    
    if len(combined_clean) > 0:
        scatter = axes[1,2].scatter(combined_clean['areal_km2'], combined_clean['volOppdemt'], 
                                   alpha=0.7, c=combined_clean['areal_km2'], cmap='viridis', 
                                   s=60, edgecolor='black', linewidth=0.5)
        axes[1,2].set_xlabel('Area (km²)')
        axes[1,2].set_ylabel('Volume (million m³)')
        axes[1,2].set_title('Volume vs Area Relationship\n(Outliers Removed)', fontweight='bold')
        axes[1,2].grid(True, alpha=0.3)
        
        # Add trend line
        z = np.polyfit(combined_clean['areal_km2'], combined_clean['volOppdemt'], 1)
        p = np.poly1d(z)
        axes[1,2].plot(combined_clean['areal_km2'], p(combined_clean['areal_km2']), 
                      "r--", alpha=0.8, linewidth=2, label='Trend Line')
        
        # Add correlation
        correlation = combined_clean['areal_km2'].corr(combined_clean['volOppdemt'])
        axes[1,2].text(0.05, 0.95, f'Correlation: {correlation:.3f}', 
                      transform=axes[1,2].transAxes, 
                      bbox=dict(boxstyle="round", facecolor='yellow', alpha=0.8),
                      fontsize=11, fontweight='bold')
        axes[1,2].legend()
    
    plt.tight_layout()
    plt.savefig("output/improved_reservoir_analysis.png", dpi=300, bbox_inches='tight')
    print("✅ Saved improved reservoir analysis")
    plt.show()

def create_better_spatial_visualization():
    """Create spatial visualization with much better dam line visibility."""
    print("Creating better spatial visualization...")
    
    dam_linje, dam_punkt, magasin = load_data()
    
    # Convert to WGS84 for better plotting
    dam_linje_wgs84 = dam_linje.to_crs('EPSG:4326')
    dam_punkt_wgs84 = dam_punkt.to_crs('EPSG:4326')
    magasin_wgs84 = magasin.to_crs('EPSG:4326')
    
    fig, axes = plt.subplots(2, 2, figsize=(16, 14))
    fig.suptitle('Norwegian Hydropower Infrastructure - Enhanced Visibility', 
                fontsize=16, fontweight='bold')
    
    # 1. Dam Lines ONLY with high contrast
    axes[0,0].set_facecolor('white')
    dam_linje_wgs84.plot(ax=axes[0,0], color='darkred', linewidth=2, alpha=0.9)
    axes[0,0].set_title(f'Dam Lines Only\n{len(dam_linje_wgs84):,} Infrastructure Lines', fontweight='bold')
    axes[0,0].set_xlabel('Longitude')
    axes[0,0].set_ylabel('Latitude')
    axes[0,0].grid(True, alpha=0.3)
    
    # 2. Dam Points with size and color coding
    dam_punkt_clean = dam_punkt_wgs84.dropna(subset=['idriftAar'])
    dam_punkt_clean = dam_punkt_clean[dam_punkt_clean['idriftAar'] > 1800]
    
    # Create size based on construction year (newer = larger)
    current_year = 2024
    years_old = current_year - dam_punkt_clean['idriftAar']
    sizes = 120 - (years_old / years_old.max()) * 80  # Size range: 40-120
    
    scatter = axes[0,1].scatter(dam_punkt_clean.geometry.x, dam_punkt_clean.geometry.y,
                               c=dam_punkt_clean['idriftAar'], s=sizes, alpha=0.8, 
                               cmap='plasma', edgecolors='black', linewidth=0.8)
    axes[0,1].set_title(f'Dam Points by Construction Era\n{len(dam_punkt_clean):,} Dated Structures', fontweight='bold')
    axes[0,1].set_xlabel('Longitude')
    axes[0,1].set_ylabel('Latitude')
    axes[0,1].grid(True, alpha=0.3)
    
    # Add colorbar
    cbar = plt.colorbar(scatter, ax=axes[0,1])
    cbar.set_label('Construction Year', fontsize=10)
    
    # 3. Reservoirs by size with clear categories
    reservoir_clean = magasin_wgs84[magasin_wgs84['areal_km2'] > 0]
    
    # Define clear size categories with distinct colors
    def get_color_and_size(area):
        if area < 1:
            return 'lightblue', 20
        elif area < 5:
            return 'blue', 40
        elif area < 20:
            return 'darkblue', 60
        elif area < 100:
            return 'navy', 80
        else:
            return 'black', 100
    
    colors_sizes = reservoir_clean['areal_km2'].apply(get_color_and_size)
    colors = [cs[0] for cs in colors_sizes]
    sizes = [cs[1] for cs in colors_sizes]
    
    # Plot reservoirs as points for better visibility
    axes[1,0].scatter(reservoir_clean.geometry.centroid.x, reservoir_clean.geometry.centroid.y,
                     c=colors, s=sizes, alpha=0.7, edgecolors='black', linewidth=0.5)
    axes[1,0].set_title(f'Reservoir Locations by Size\n{len(reservoir_clean):,} Water Bodies', fontweight='bold')
    axes[1,0].set_xlabel('Longitude')
    axes[1,0].set_ylabel('Latitude')
    axes[1,0].grid(True, alpha=0.3)
    
    # Add legend
    legend_elements = [
        plt.scatter([], [], c='lightblue', s=20, label='<1 km²', edgecolors='black'),
        plt.scatter([], [], c='blue', s=40, label='1-5 km²', edgecolors='black'),
        plt.scatter([], [], c='darkblue', s=60, label='5-20 km²', edgecolors='black'),
        plt.scatter([], [], c='navy', s=80, label='20-100 km²', edgecolors='black'),
        plt.scatter([], [], c='black', s=100, label='>100 km²', edgecolors='black')
    ]
    axes[1,0].legend(handles=legend_elements, loc='upper right', title='Reservoir Size')
    
    # 4. Combined view with optimized colors and layers
    # Plot reservoirs as light background
    magasin_wgs84.plot(ax=axes[1,1], color='lightcyan', alpha=0.5, edgecolor='white', linewidth=0.2)
    
    # Plot dam lines with high contrast
    dam_linje_wgs84.plot(ax=axes[1,1], color='red', linewidth=1.5, alpha=0.9, label='Dam Lines')
    
    # Plot major dam points
    major_dams = dam_punkt_wgs84.sample(min(500, len(dam_punkt_wgs84)))  # Sample for visibility
    major_dams.plot(ax=axes[1,1], color='darkred', markersize=15, alpha=0.8, label='Dam Points (Sample)')
    
    axes[1,1].set_title('Complete Infrastructure Overview\nOptimized Layer Visibility', fontweight='bold')
    axes[1,1].set_xlabel('Longitude')
    axes[1,1].set_ylabel('Latitude')
    axes[1,1].grid(True, alpha=0.3)
    axes[1,1].legend(loc='upper right')
    
    # Add comprehensive statistics
    stats_text = f"""Norway Hydropower Infrastructure:
    
    🔸 Dam Lines: {len(dam_linje_wgs84):,} linear structures
    🔸 Dam Points: {len(dam_punkt_wgs84):,} point locations
    🔸 Reservoirs: {len(magasin_wgs84):,} water bodies
    🔸 Total Area: {magasin_wgs84['areal_km2'].sum():.0f} km²
    🔸 Avg Construction: {dam_linje_wgs84['idriftAar'].mean():.0f}"""
    
    axes[1,1].text(0.02, 0.02, stats_text, transform=axes[1,1].transAxes, 
                  bbox=dict(boxstyle="round,pad=0.5", facecolor='white', alpha=0.9),
                  fontsize=9, fontweight='bold', verticalalignment='bottom')
    
    plt.tight_layout()
    plt.savefig("output/improved_spatial_visualization.png", dpi=300, bbox_inches='tight')
    print("✅ Saved improved spatial visualization")
    plt.show()

def main():
    """Run the improved analysis."""
    print("🚀 Creating Improved Norwegian Hydropower Visualizations")
    print("=" * 60)
    
    # Ensure output directory exists
    Path("output").mkdir(exist_ok=True)
    
    # Create improved charts
    create_improved_reservoir_charts()
    create_better_spatial_visualization()
    
    print("\n🎉 Improved visualizations completed!")
    print("Generated files:")
    print("  • improved_reservoir_analysis.png")
    print("  • improved_spatial_visualization.png")

if __name__ == "__main__":
    main() 