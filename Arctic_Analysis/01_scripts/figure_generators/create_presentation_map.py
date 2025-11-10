#!/usr/bin/env python3
"""
Create Presentation Map for Arctic Dam Distribution
==================================================
Shows all of Norway with 499 Arctic dams clearly marked by region
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

def create_norway_arctic_dams_map():
    """Create comprehensive Norway map showing Arctic dam distribution"""
    
    # Load Arctic dams data
    print("📂 Loading Arctic dams data...")
    arctic_dams = pd.read_csv("04_results/norwegian_arctic_dams.csv")
    print(f"✅ Loaded {len(arctic_dams)} Arctic dams")
    
    # Create figure
    fig, ax = plt.subplots(1, 1, figsize=(16, 12))
    
    # Define Arctic regions with colors
    region_colors = {
        'Far Arctic': '#8B0000',      # Dark red
        'High Arctic': '#DC143C',     # Crimson  
        'Arctic Circle': '#FF6347'    # Tomato
    }
    
    # Plot Arctic Circle line
    lon_range = np.linspace(4, 32, 100)
    arctic_circle_line = np.full_like(lon_range, 66.5)
    ax.plot(lon_range, arctic_circle_line, 'b--', linewidth=3, 
           label='Arctic Circle (66.5°N)', alpha=0.8)
    
    # Plot Arctic dams by region
    for region, color in region_colors.items():
        region_dams = arctic_dams[arctic_dams['arctic_region'] == region]
        if len(region_dams) > 0:
            ax.scatter(region_dams['longitude'], region_dams['latitude'], 
                      c=color, s=60, alpha=0.8, 
                      label=f'{region} ({len(region_dams)} dams)', 
                      edgecolors='white', linewidth=0.5, zorder=5)
            print(f"✅ Plotted {len(region_dams)} dams in {region}")
    
    # Set map bounds to show all of Norway
    ax.set_xlim(4, 32)
    ax.set_ylim(57, 72)
    
    # Styling
    ax.set_xlabel('Longitude (°E)', fontsize=14, fontweight='bold')
    ax.set_ylabel('Latitude (°N)', fontsize=14, fontweight='bold')
    ax.set_title('Norwegian Arctic Dam Distribution\n499 Dams Above 66.5°N Arctic Circle', 
                fontsize=18, fontweight='bold', pad=20)
    
    # Add grid
    ax.grid(True, alpha=0.3, linestyle='-', linewidth=0.5)
    
    # Legend
    legend = ax.legend(loc='upper right', fontsize=12, framealpha=0.9, 
                      fancybox=True, shadow=True)
    legend.get_frame().set_facecolor('white')
    
    # Add geographic annotations
    ax.annotate('FINNMARK\n(Northernmost Mainland)', xy=(27, 70), fontsize=11,
               ha='center', va='center', fontweight='bold',
               bbox=dict(boxstyle='round,pad=0.3', facecolor='lightgreen', alpha=0.7))
    
    ax.annotate('TROMS', xy=(18, 69), fontsize=11,
               ha='center', va='center', fontweight='bold',
               bbox=dict(boxstyle='round,pad=0.3', facecolor='lightyellow', alpha=0.7))
    
    ax.annotate('NORDLAND', xy=(14, 67), fontsize=11,
               ha='center', va='center', fontweight='bold',
               bbox=dict(boxstyle='round,pad=0.3', facecolor='lightcoral', alpha=0.7))
    
    # Add statistics box
    stats_text = """ARCTIC DAM STATISTICS

Total Arctic Dams: 499
• Far Arctic (>70°N): 79 dams (15.8%)
• High Arctic (68-70°N): 268 dams (53.7%)  
• Arctic Circle (66.5-68°N): 152 dams (30.5%)

Purposes:
• Hydropower: 346 dams (69.3%)
• Water Supply: 67 dams (13.4%)
• Other: 86 dams (17.2%)"""
    
    ax.text(0.02, 0.02, stats_text, transform=ax.transAxes, fontsize=10,
           verticalalignment='bottom', horizontalalignment='left',
           bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.9),
           fontfamily='monospace')
    
    # Add data source
    ax.text(0.98, 0.02, 'Data Source: NVE (Norwegian Water Resources and Energy Directorate)', 
           transform=ax.transAxes, fontsize=9, ha='right', va='bottom',
           style='italic', alpha=0.7)
    
    plt.tight_layout()
    
    # Save the figure
    output_path = "04_results/norway_arctic_dams_presentation_map.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"✅ Presentation map saved to: {output_path}")
    
    # Also save high-res version
    output_path_hires = "04_results/norway_arctic_dams_presentation_map_hires.png"
    plt.savefig(output_path_hires, dpi=600, bbox_inches='tight', facecolor='white')
    print(f"✅ High-res map saved to: {output_path_hires}")
    
    plt.close()
    
    return output_path

def create_distribution_charts():
    """Create simplified distribution charts"""
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
    
    # Arctic region distribution
    regions = ['Arctic Circle\n(66.5-68°N)', 'High Arctic\n(68-70°N)', 'Far Arctic\n(>70°N)']
    counts = [152, 268, 79]
    percentages = [30.5, 53.7, 15.8]
    colors = ['#FF6347', '#DC143C', '#8B0000']
    
    bars = ax1.bar(regions, counts, color=colors, alpha=0.8, edgecolor='white', linewidth=2)
    ax1.set_title('Arctic Dam Distribution by Region', fontsize=16, fontweight='bold', pad=20)
    ax1.set_ylabel('Number of Dams', fontsize=14, fontweight='bold')
    
    # Add count labels on bars
    for bar, count, pct in zip(bars, counts, percentages):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + 5,
                f'{count}\n({pct}%)', ha='center', va='bottom', 
                fontsize=12, fontweight='bold')
    
    ax1.set_ylim(0, max(counts) * 1.2)
    ax1.grid(axis='y', alpha=0.3)
    
    # Purpose distribution
    purposes = ['Hydropower', 'Water Supply', 'Other']
    purpose_counts = [346, 67, 86]
    purpose_pcts = [69.3, 13.4, 17.2]
    purpose_colors = ['#2E8B57', '#4682B4', '#DAA520']
    
    bars2 = ax2.bar(purposes, purpose_counts, color=purpose_colors, alpha=0.8, 
                   edgecolor='white', linewidth=2)
    ax2.set_title('Arctic Dam Distribution by Purpose', fontsize=16, fontweight='bold', pad=20)
    ax2.set_ylabel('Number of Dams', fontsize=14, fontweight='bold')
    
    # Add count labels on bars
    for bar, count, pct in zip(bars2, purpose_counts, purpose_pcts):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + 5,
                f'{count}\n({pct}%)', ha='center', va='bottom', 
                fontsize=12, fontweight='bold')
    
    ax2.set_ylim(0, max(purpose_counts) * 1.2)
    ax2.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    
    # Save the chart
    output_path = "04_results/arctic_dam_distribution_charts.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"✅ Distribution charts saved to: {output_path}")
    
    plt.close()
    
    return output_path

if __name__ == "__main__":
    print("🗺️  Creating Norway Arctic Dams Presentation Map...")
    map_path = create_norway_arctic_dams_map()
    
    print("\n📊 Creating Distribution Charts...")
    chart_path = create_distribution_charts()
    
    print(f"\n✅ All visualizations created successfully!")
    print(f"📁 Files saved in: Arctic_Analysis/04_results/")
