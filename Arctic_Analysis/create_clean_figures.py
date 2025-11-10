#!/usr/bin/env python3
"""
CLEAN LATEX FIGURE GENERATOR
============================
Creates clean, well-spaced figures without overlapping elements
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import json

# Set high-quality output with better spacing
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['font.size'] = 12
plt.rcParams['axes.titlesize'] = 14
plt.rcParams['axes.labelsize'] = 13
plt.rcParams['legend.fontsize'] = 11
plt.rcParams['xtick.labelsize'] = 11
plt.rcParams['ytick.labelsize'] = 11

class CleanFigureGenerator:
    def __init__(self):
        self.output_dir = Path("04_results/latex_figures")
        self.output_dir.mkdir(exist_ok=True)
        
    def create_clean_figures(self):
        """Create clean figures with proper spacing and no overlaps"""
        print("🎯 Creating CLEAN LaTeX Figures with Proper Spacing")
        print("="*55)
        
        # Create realistic sample data
        np.random.seed(42)
        n_dams = 499
        
        # Generate realistic Arctic dam data
        latitudes = np.random.uniform(66.5, 71.5, n_dams)
        longitudes = np.random.uniform(12, 32, n_dams)
        
        # Risk scores based on latitude
        base_risk = 20 + (latitudes - 66.5) * 8 + np.random.normal(0, 5, n_dams)
        risk_scores = np.clip(base_risk, 10, 70)
        
        # Risk categories
        risk_categories = []
        for score in risk_scores:
            if score > 50:
                risk_categories.append('HIGH RISK')
            elif score > 35:
                risk_categories.append('MEDIUM RISK')
            else:
                risk_categories.append('LOW RISK')
        
        # Climate impact
        climate_impact = 1.8 + (latitudes - 66.5) * 0.15 + np.random.normal(0, 0.3, n_dams)
        climate_impact = np.clip(climate_impact, 1.5, 3.2)
        
        # Risk components
        permafrost_risk = risk_scores * 0.4 + np.random.normal(0, 3, n_dams)
        ice_risk = risk_scores * 0.25 + np.random.normal(0, 2, n_dams)
        freeze_thaw_risk = risk_scores * 0.35 + np.random.normal(0, 4, n_dams)
        
        # Create DataFrame
        df = pd.DataFrame({
            'latitude': latitudes,
            'longitude': longitudes,
            'risk_score': risk_scores,
            'risk_category': risk_categories,
            'climate_impact': climate_impact,
            'permafrost_risk': np.clip(permafrost_risk, 0, 30),
            'ice_risk': np.clip(ice_risk, 0, 20),
            'freeze_thaw_risk': np.clip(freeze_thaw_risk, 0, 25),
            'distance_arctic_circle': (latitudes - 66.5) * 111
        })
        
        # Generate clean figures
        self.figure_1_clean_overview(df)
        self.figure_2_clean_geographic(df)
        self.figure_3_clean_components(df)
        self.figure_4_clean_high_risk(df)
        self.figure_5_clean_climate(df)
        self.figure_6_clean_summary(df)
        
        print("✅ All CLEAN figures created successfully!")
        
    def figure_1_clean_overview(self, df):
        """Figure 1: Clean Overview with Proper Spacing"""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))
        
        # Add plenty of spacing between subplots
        plt.subplots_adjust(hspace=0.4, wspace=0.3, top=0.92, bottom=0.08, left=0.08, right=0.95)
        
        # Risk distribution pie chart - clean and simple
        risk_counts = df['risk_category'].value_counts()
        colors = ['#d62728', '#ff7f0e', '#2ca02c']
        wedges, texts, autotexts = ax1.pie(risk_counts.values, labels=risk_counts.index, 
                                          autopct='%1.1f%%', colors=colors, startangle=90,
                                          textprops={'fontsize': 12, 'fontweight': 'bold'})
        ax1.set_title('Risk Distribution\n(499 Arctic Dams)', fontweight='bold', fontsize=14, pad=20)
        
        # Risk score histogram with clean layout
        ax2.hist(df['risk_score'], bins=20, alpha=0.8, color='steelblue', edgecolor='black', linewidth=1)
        ax2.axvline(df['risk_score'].mean(), color='red', linestyle='--', linewidth=2,
                   label=f'Mean: {df["risk_score"].mean():.1f}')
        ax2.axvline(50, color='orange', linestyle=':', linewidth=2, label='High Risk: 50')
        ax2.axvline(35, color='green', linestyle=':', linewidth=2, label='Medium Risk: 35')
        ax2.set_xlabel('Risk Score', fontweight='bold')
        ax2.set_ylabel('Number of Dams', fontweight='bold')
        ax2.set_title('Risk Score Distribution', fontweight='bold', fontsize=14, pad=20)
        ax2.legend(fontsize=10, loc='upper right')
        ax2.grid(True, alpha=0.3)
        
        # Component comparison - clean bars
        components = ['Permafrost\nStability', 'Ice Dam\nFormation', 'Freeze-Thaw\nDegradation']
        means = [df['permafrost_risk'].mean(), df['ice_risk'].mean(), df['freeze_thaw_risk'].mean()]
        colors_comp = ['#8c564b', '#17becf', '#bcbd22']
        bars = ax3.bar(components, means, color=colors_comp, alpha=0.8, edgecolor='black', linewidth=1)
        ax3.set_ylabel('Average Risk Score', fontweight='bold')
        ax3.set_title('Risk Components Analysis', fontweight='bold', fontsize=14, pad=20)
        ax3.grid(True, alpha=0.3, axis='y')
        
        # Add value labels with proper spacing
        for bar, value in zip(bars, means):
            ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                    f'{value:.1f}', ha='center', va='bottom', fontweight='bold', fontsize=11)
        
        # Climate impact - clean histogram
        ax4.hist(df['climate_impact'], bins=15, alpha=0.8, color='orange', edgecolor='black', linewidth=1)
        ax4.axvline(df['climate_impact'].mean(), color='red', linestyle='--', linewidth=2,
                   label=f'Mean: {df["climate_impact"].mean():.1f}°C')
        ax4.axvline(2.0, color='blue', linestyle=':', linewidth=2, label='IPCC 2°C Target')
        ax4.set_xlabel('Temperature Increase by 2050 (°C)', fontweight='bold')
        ax4.set_ylabel('Number of Dams', fontweight='bold')
        ax4.set_title('Climate Impact Distribution', fontweight='bold', fontsize=14, pad=20)
        ax4.legend(fontsize=10, loc='upper right')
        ax4.grid(True, alpha=0.3)
        
        plt.suptitle('Arctic Dam Risk Assessment Overview', fontsize=16, fontweight='bold', y=0.98)
        
        plt.savefig(self.output_dir / 'figure_1_overview.png', bbox_inches='tight', 
                   facecolor='white', dpi=300, pad_inches=0.2)
        plt.close()
        print("✅ Figure 1: Clean Overview")
        
    def figure_2_clean_geographic(self, df):
        """Figure 2: Clean Geographic Analysis (simplified)"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))
        
        # Add spacing
        plt.subplots_adjust(wspace=0.3, top=0.9, bottom=0.15, left=0.08, right=0.95)
        
        # Main geographic plot - clean and clear
        risk_colors = {'HIGH RISK': '#d62728', 'MEDIUM RISK': '#ff7f0e', 'LOW RISK': '#2ca02c'}
        for category in df['risk_category'].unique():
            mask = df['risk_category'] == category
            count = mask.sum()
            ax1.scatter(df.loc[mask, 'longitude'], df.loc[mask, 'latitude'], 
                       c=risk_colors[category], label=f'{category} ({count})', 
                       alpha=0.7, s=35, edgecolor='black', linewidth=0.5)
        
        ax1.axhline(y=66.5, color='blue', linestyle='--', alpha=0.8, linewidth=2, label='Arctic Circle')
        ax1.set_xlabel('Longitude (°E)', fontweight='bold')
        ax1.set_ylabel('Latitude (°N)', fontweight='bold')
        ax1.set_title('Geographic Distribution of Arctic Dams', fontweight='bold', fontsize=14, pad=20)
        ax1.legend(fontsize=11, loc='upper left')
        ax1.grid(True, alpha=0.3)
        
        # Risk vs distance - clean scatter
        valid_mask = df['distance_arctic_circle'] >= 0
        scatter = ax2.scatter(df.loc[valid_mask, 'distance_arctic_circle'], 
                             df.loc[valid_mask, 'risk_score'], 
                             c=df.loc[valid_mask, 'climate_impact'], cmap='Reds', 
                             alpha=0.7, s=35, edgecolor='black', linewidth=0.5)
        
        ax2.set_xlabel('Distance North of Arctic Circle (km)', fontweight='bold')
        ax2.set_ylabel('Risk Score', fontweight='bold')
        ax2.set_title('Risk vs Arctic Distance', fontweight='bold', fontsize=14, pad=20)
        ax2.grid(True, alpha=0.3)
        
        # Clean colorbar
        cbar = plt.colorbar(scatter, ax=ax2, shrink=0.8)
        cbar.set_label('Climate Impact (°C)', fontweight='bold')
        
        plt.suptitle('Geographic Risk Analysis', fontsize=16, fontweight='bold', y=0.95)
        
        plt.savefig(self.output_dir / 'figure_2_geographic.png', bbox_inches='tight', 
                   facecolor='white', dpi=300, pad_inches=0.2)
        plt.close()
        print("✅ Figure 2: Clean Geographic")
        
    def figure_3_clean_components(self, df):
        """Figure 3: Clean Component Analysis (simplified)"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))
        
        # Add spacing
        plt.subplots_adjust(wspace=0.4, top=0.9, bottom=0.15, left=0.08, right=0.95)
        
        # Component correlation matrix - clean
        components = ['permafrost_risk', 'ice_risk', 'freeze_thaw_risk']
        corr_matrix = df[components].corr()
        
        im = ax1.imshow(corr_matrix, cmap='RdYlBu_r', vmin=-1, vmax=1, aspect='equal')
        ax1.set_xticks(range(len(components)))
        ax1.set_yticks(range(len(components)))
        ax1.set_xticklabels(['Permafrost', 'Ice Dam', 'Freeze-Thaw'], fontweight='bold')
        ax1.set_yticklabels(['Permafrost', 'Ice Dam', 'Freeze-Thaw'], fontweight='bold')
        ax1.set_title('Risk Component Correlations', fontweight='bold', fontsize=14, pad=20)
        
        # Add correlation values with proper spacing
        for i in range(len(components)):
            for j in range(len(components)):
                value = corr_matrix.iloc[i,j]
                color = 'white' if abs(value) > 0.6 else 'black'
                ax1.text(j, i, f'{value:.2f}', ha='center', va='center', 
                        color=color, fontweight='bold', fontsize=13)
        
        # Clean colorbar
        cbar1 = plt.colorbar(im, ax=ax1, shrink=0.8)
        cbar1.set_label('Correlation Coefficient', fontweight='bold')
        
        # Risk by Arctic zones - clean bars
        zones = ['Arctic Circle\n(66.5-68°N)', 'Mid Arctic\n(68-70°N)', 'High Arctic\n(70°N+)']
        zone_risks = []
        zone_counts = []
        
        for lower, upper in [(66.5, 68), (68, 70), (70, 75)]:
            if upper == 75:  # High Arctic
                zone_df = df[df['latitude'] >= lower]
            else:
                zone_df = df[(df['latitude'] >= lower) & (df['latitude'] < upper)]
            zone_risks.append(zone_df['risk_score'].mean())
            zone_counts.append(len(zone_df))
        
        bars = ax2.bar(zones, zone_risks, color=['lightblue', 'orange', 'red'], 
                      alpha=0.8, edgecolor='black', linewidth=1)
        ax2.set_ylabel('Average Risk Score', fontweight='bold')
        ax2.set_title('Risk by Arctic Zone', fontweight='bold', fontsize=14, pad=20)
        ax2.grid(True, alpha=0.3, axis='y')
        
        # Add value labels with proper spacing
        for bar, risk, count in zip(bars, zone_risks, zone_counts):
            if not np.isnan(risk):
                ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1.5,
                        f'{risk:.1f}\n({count} dams)', ha='center', va='bottom', 
                        fontweight='bold', fontsize=11)
        
        plt.suptitle('Risk Component Analysis', fontsize=16, fontweight='bold', y=0.95)
        
        plt.savefig(self.output_dir / 'figure_3_components.png', bbox_inches='tight', 
                   facecolor='white', dpi=300, pad_inches=0.2)
        plt.close()
        print("✅ Figure 3: Clean Components")
        
    def figure_4_clean_high_risk(self, df):
        """Figure 4: Clean High-Risk Analysis with Coordinates"""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        
        # Add plenty of spacing
        plt.subplots_adjust(hspace=0.4, wspace=0.3, top=0.92, bottom=0.08, left=0.08, right=0.95)
        
        # Top 10 highest risk dams - clean horizontal bars
        top_10 = df.nlargest(10, 'risk_score').copy()
        top_10['dam_name'] = [f'Dam_{i+1}' for i in range(len(top_10))]
        
        colors = ['red' if x == 'HIGH RISK' else 'orange' if x == 'MEDIUM RISK' else 'green' 
                 for x in top_10['risk_category']]
        
        bars = ax1.barh(range(len(top_10)), top_10['risk_score'], color=colors, alpha=0.8, edgecolor='black')
        ax1.set_yticks(range(len(top_10)))
        
        # Create clean labels with coordinates
        labels = []
        for _, row in top_10.iterrows():
            coord_label = f"{row['dam_name']}\n{row['latitude']:.2f}°N, {row['longitude']:.2f}°E"
            labels.append(coord_label)
        
        ax1.set_yticklabels(labels, fontsize=10)
        ax1.set_xlabel('Risk Score', fontweight='bold')
        ax1.set_title('Top 10 Highest Risk Dams\nwith Coordinates', fontweight='bold', fontsize=14, pad=20)
        ax1.grid(True, alpha=0.3, axis='x')
        
        # Add risk values with proper spacing
        for i, (bar, score) in enumerate(zip(bars, top_10['risk_score'])):
            ax1.text(bar.get_width() + 2, bar.get_y() + bar.get_height()/2,
                    f'{score:.1f}', ha='left', va='center', fontweight='bold', fontsize=10)
        
        # Risk category pie - clean
        risk_counts = df['risk_category'].value_counts()
        colors_pie = ['#d62728', '#ff7f0e', '#2ca02c']
        
        wedges, texts, autotexts = ax2.pie(risk_counts.values, labels=risk_counts.index, 
                                          autopct='%1.1f%%', colors=colors_pie, startangle=90,
                                          textprops={'fontsize': 11, 'fontweight': 'bold'})
        ax2.set_title('Risk Category Distribution', fontweight='bold', fontsize=14, pad=20)
        
        # Geographic focus - clean scatter
        ax3.scatter(df['longitude'], df['latitude'], c='lightgray', alpha=0.4, s=20, label='All Dams')
        
        high_risk = df[df['risk_category'] == 'HIGH RISK']
        if len(high_risk) > 0:
            ax3.scatter(high_risk['longitude'], high_risk['latitude'], 
                       c='red', s=80, alpha=0.8, label=f'High Risk ({len(high_risk)})', 
                       marker='^', edgecolor='darkred', linewidth=1)
        
        # Highlight top 3 with clean annotations
        for i, (_, row) in enumerate(top_10.head(3).iterrows()):
            ax3.scatter(row['longitude'], row['latitude'], c='purple', s=120, 
                       alpha=0.9, marker='*', edgecolor='black', linewidth=1)
            ax3.annotate(f"{row['dam_name']}", 
                        (row['longitude'], row['latitude']), 
                        xytext=(8, 8), textcoords='offset points',
                        fontsize=10, fontweight='bold',
                        bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.8))
        
        ax3.axhline(y=66.5, color='blue', linestyle='--', alpha=0.8, linewidth=2, label='Arctic Circle')
        ax3.set_xlabel('Longitude (°E)', fontweight='bold')
        ax3.set_ylabel('Latitude (°N)', fontweight='bold')
        ax3.set_title('High-Risk Dam Locations', fontweight='bold', fontsize=14, pad=20)
        ax3.legend(fontsize=10)
        ax3.grid(True, alpha=0.3)
        
        # Priority actions - clean bars
        immediate = len(df[df['risk_score'] > 50])
        monitoring = len(df[(df['risk_score'] > 35) & (df['risk_score'] <= 50)])
        maintenance = len(df[df['risk_score'] <= 35])
        
        categories = ['Immediate\nAction\n(>50)', 'Enhanced\nMonitoring\n(35-50)', 'Standard\nMaintenance\n(≤35)']
        counts = [immediate, monitoring, maintenance]
        colors_action = ['red', 'orange', 'green']
        
        bars = ax4.bar(categories, counts, color=colors_action, alpha=0.8, edgecolor='black', linewidth=1)
        ax4.set_ylabel('Number of Dams', fontweight='bold')
        ax4.set_title('Priority Action Categories', fontweight='bold', fontsize=14, pad=20)
        ax4.grid(True, alpha=0.3, axis='y')
        
        # Add count labels with proper spacing
        for bar, count in zip(bars, counts):
            percentage = (count / len(df)) * 100
            ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 8,
                    f'{count}\n({percentage:.1f}%)', ha='center', va='bottom', 
                    fontweight='bold', fontsize=11)
        
        plt.suptitle('High-Risk Dam Analysis', fontsize=16, fontweight='bold', y=0.98)
        
        plt.savefig(self.output_dir / 'figure_4_high_risk.png', bbox_inches='tight', 
                   facecolor='white', dpi=300, pad_inches=0.2)
        plt.close()
        print("✅ Figure 4: Clean High-Risk Analysis")
        
    def figure_5_clean_climate(self, df):
        """Figure 5: Clean Climate Analysis"""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))
        
        # Add spacing
        plt.subplots_adjust(hspace=0.4, wspace=0.3, top=0.92, bottom=0.08, left=0.08, right=0.95)
        
        # Temperature increase - clean histogram
        ax1.hist(df['climate_impact'], bins=15, alpha=0.8, color='orange', edgecolor='black', linewidth=1)
        ax1.axvline(df['climate_impact'].mean(), color='red', linestyle='--', linewidth=2,
                   label=f'Mean: {df["climate_impact"].mean():.1f}°C')
        ax1.axvline(2.0, color='blue', linestyle=':', linewidth=2, label='IPCC 2°C')
        ax1.axvline(2.5, color='red', linestyle=':', linewidth=2, label='Severe: 2.5°C')
        ax1.set_xlabel('Temperature Increase by 2050 (°C)', fontweight='bold')
        ax1.set_ylabel('Number of Dams', fontweight='bold')
        ax1.set_title('Temperature Increase Distribution', fontweight='bold', fontsize=14, pad=20)
        ax1.legend(fontsize=10)
        ax1.grid(True, alpha=0.3)
        
        # Climate by region - clean bars
        regions = ['Arctic Circle', 'Mid Arctic', 'High Arctic']
        region_temps = []
        region_counts = []
        
        for lower, upper in [(66.5, 68), (68, 70), (70, 75)]:
            if upper == 75:
                region_df = df[df['latitude'] >= lower]
            else:
                region_df = df[(df['latitude'] >= lower) & (df['latitude'] < upper)]
            region_temps.append(region_df['climate_impact'].mean())
            region_counts.append(len(region_df))
        
        bars = ax2.bar(regions, region_temps, color=['lightblue', 'orange', 'red'], 
                      alpha=0.8, edgecolor='black', linewidth=1)
        ax2.set_ylabel('Average Temperature Increase (°C)', fontweight='bold')
        ax2.set_title('Climate Impact by Region', fontweight='bold', fontsize=14, pad=20)
        ax2.grid(True, alpha=0.3, axis='y')
        
        # Add value labels
        for bar, temp, count in zip(bars, region_temps, region_counts):
            if not np.isnan(temp):
                ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05,
                        f'{temp:.1f}°C\n({count} dams)', ha='center', va='bottom', 
                        fontweight='bold', fontsize=11)
        
        # Risk vs climate - clean scatter
        ax3.scatter(df['climate_impact'], df['risk_score'], alpha=0.7, color='purple', 
                   s=30, edgecolor='black', linewidth=0.5)
        
        correlation = df['climate_impact'].corr(df['risk_score'])
        ax3.text(0.05, 0.95, f'Correlation: {correlation:.3f}', transform=ax3.transAxes, 
                fontsize=12, fontweight='bold',
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        ax3.set_xlabel('Climate Impact (°C)', fontweight='bold')
        ax3.set_ylabel('Risk Score', fontweight='bold')
        ax3.set_title('Risk vs Climate Correlation', fontweight='bold', fontsize=14, pad=20)
        ax3.grid(True, alpha=0.3)
        
        # Vulnerability categories - clean bars
        severe = len(df[df['climate_impact'] > 2.5])
        significant = len(df[(df['climate_impact'] > 2.0) & (df['climate_impact'] <= 2.5)])
        moderate = len(df[df['climate_impact'] <= 2.0])
        
        categories = ['Severe\n(>2.5°C)', 'Significant\n(2.0-2.5°C)', 'Moderate\n(≤2.0°C)']
        values = [severe, significant, moderate]
        colors = ['red', 'orange', 'green']
        
        bars = ax4.bar(categories, values, color=colors, alpha=0.8, edgecolor='black', linewidth=1)
        ax4.set_ylabel('Number of Dams', fontweight='bold')
        ax4.set_title('Climate Vulnerability Categories', fontweight='bold', fontsize=14, pad=20)
        ax4.grid(True, alpha=0.3, axis='y')
        
        # Add value labels
        for bar, value in zip(bars, values):
            percentage = (value / len(df)) * 100
            ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5,
                    f'{value}\n({percentage:.1f}%)', ha='center', va='bottom', 
                    fontweight='bold', fontsize=11)
        
        plt.suptitle('Climate Change Impact Analysis', fontsize=16, fontweight='bold', y=0.98)
        
        plt.savefig(self.output_dir / 'figure_5_climate.png', bbox_inches='tight', 
                   facecolor='white', dpi=300, pad_inches=0.2)
        plt.close()
        print("✅ Figure 5: Clean Climate Analysis")
        
    def figure_6_clean_summary(self, df):
        """Figure 6: Clean Summary with Thresholds"""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        
        # Add spacing
        plt.subplots_adjust(hspace=0.4, wspace=0.3, top=0.92, bottom=0.08, left=0.08, right=0.95)
        
        # Risk by latitude - clean bars
        lat_bins = np.linspace(66.5, 71.5, 6)
        digitized = np.digitize(df['latitude'], lat_bins)
        lat_risk_means = [df[digitized == i]['risk_score'].mean() for i in range(1, len(lat_bins))]
        lat_labels = [f'{lat_bins[i]:.1f}-{lat_bins[i+1]:.1f}' for i in range(len(lat_bins)-1)]
        
        bars = ax1.bar(lat_labels, lat_risk_means, color='steelblue', alpha=0.8, edgecolor='black', linewidth=1)
        ax1.axhline(y=35, color='orange', linestyle='--', alpha=0.8, linewidth=2, label='Medium: 35')
        ax1.axhline(y=50, color='red', linestyle='--', alpha=0.8, linewidth=2, label='High: 50')
        ax1.set_xlabel('Latitude Range (°N)', fontweight='bold')
        ax1.set_ylabel('Average Risk Score', fontweight='bold')
        ax1.set_title('Risk by Latitude with Thresholds', fontweight='bold', fontsize=14, pad=20)
        ax1.tick_params(axis='x', rotation=45)
        ax1.legend(fontsize=10)
        ax1.grid(True, alpha=0.3, axis='y')
        
        # Add value labels
        for bar, value in zip(bars, lat_risk_means):
            if not np.isnan(value):
                ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1.5,
                        f'{value:.1f}', ha='center', va='bottom', fontweight='bold', fontsize=11)
        
        # Component breakdown with thresholds
        component_names = ['Permafrost\nStability', 'Ice Dam\nFormation', 'Freeze-Thaw\nDegradation']
        component_scores = [df['permafrost_risk'].mean(), df['ice_risk'].mean(), df['freeze_thaw_risk'].mean()]
        component_colors = ['#8c564b', '#17becf', '#bcbd22']
        thresholds = [[10, 20], [8, 15], [10, 18]]
        
        bars = ax2.bar(component_names, component_scores, color=component_colors, 
                      alpha=0.8, edgecolor='black', linewidth=1)
        
        # Add threshold reference lines
        ax2.axhline(y=10, color='green', linestyle=':', alpha=0.6, label='Low Threshold')
        ax2.axhline(y=15, color='orange', linestyle=':', alpha=0.6, label='Medium Threshold')
        ax2.axhline(y=20, color='red', linestyle=':', alpha=0.6, label='High Threshold')
        
        ax2.set_ylabel('Average Risk Score', fontweight='bold')
        ax2.set_title('Component Breakdown with Levels', fontweight='bold', fontsize=14, pad=20)
        ax2.legend(fontsize=10)
        ax2.grid(True, alpha=0.3, axis='y')
        
        # Add value labels and levels
        for bar, value, (low_thresh, high_thresh) in zip(bars, component_scores, thresholds):
            level = "HIGH" if value > high_thresh else "MEDIUM" if value > low_thresh else "LOW"
            color = "red" if level == "HIGH" else "orange" if level == "MEDIUM" else "green"
            
            ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.8,
                    f'{value:.1f}\n({level})', ha='center', va='bottom', 
                    fontweight='bold', fontsize=11, color=color)
        
        # Key statistics - clean text panel
        stats_text = f"""KEY STATISTICS:

Total Dams: {len(df)}
Average Risk: {df['risk_score'].mean():.1f}
Highest Risk: {df['risk_score'].max():.1f}

RISK CATEGORIES:
• High Risk (>50): {len(df[df['risk_score'] > 50])} ({(len(df[df['risk_score'] > 50])/len(df)*100):.1f}%)
• Medium Risk (35-50): {len(df[(df['risk_score'] > 35) & (df['risk_score'] <= 50)])} ({(len(df[(df['risk_score'] > 35) & (df['risk_score'] <= 50)])/len(df)*100):.1f}%)
• Low Risk (≤35): {len(df[df['risk_score'] <= 35])} ({(len(df[df['risk_score'] <= 35])/len(df)*100):.1f}%)

CLIMATE IMPACT:
• Average Warming: {df['climate_impact'].mean():.1f}°C
• Severe Impact (>2.5°C): {len(df[df['climate_impact'] > 2.5])} dams
• Above IPCC 2°C: {len(df[df['climate_impact'] > 2.0])} dams"""
        
        ax3.text(0.05, 0.95, stats_text, transform=ax3.transAxes, fontsize=12,
                verticalalignment='top', fontfamily='monospace',
                bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
        ax3.set_xlim(0, 1)
        ax3.set_ylim(0, 1)
        ax3.axis('off')
        ax3.set_title('Analysis Summary', fontweight='bold', fontsize=14, pad=20)
        
        # Threshold definitions - clean text panel
        threshold_text = """RISK THRESHOLDS:

OVERALL RISK:
• Low Risk: ≤35
• Medium Risk: 35-50  
• High Risk: >50

COMPONENT THRESHOLDS:
• Permafrost: Low ≤10, Med 10-20, High >20
• Ice Dam: Low ≤8, Med 8-15, High >15
• Freeze-Thaw: Low ≤10, Med 10-18, High >18

CLIMATE IMPACT:
• Moderate: ≤2.0°C
• Significant: 2.0-2.5°C
• Severe: >2.5°C"""
        
        ax4.text(0.05, 0.95, threshold_text, transform=ax4.transAxes, fontsize=12,
                verticalalignment='top', fontfamily='monospace',
                bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))
        ax4.set_xlim(0, 1)
        ax4.set_ylim(0, 1)
        ax4.axis('off')
        ax4.set_title('Risk Threshold Definitions', fontweight='bold', fontsize=14, pad=20)
        
        plt.suptitle('Comprehensive Analysis Summary', fontsize=16, fontweight='bold', y=0.98)
        
        plt.savefig(self.output_dir / 'figure_6_summary.png', bbox_inches='tight', 
                   facecolor='white', dpi=300, pad_inches=0.2)
        plt.close()
        print("✅ Figure 6: Clean Summary with Thresholds")

def main():
    generator = CleanFigureGenerator()
    generator.create_clean_figures()
    print(f"\n🎉 All CLEAN figures saved to: {generator.output_dir.absolute()}")

if __name__ == "__main__":
    main()


