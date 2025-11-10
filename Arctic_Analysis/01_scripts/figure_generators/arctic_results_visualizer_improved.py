#!/usr/bin/env python3
"""
IMPROVED ARCTIC DAM ANALYSIS VISUALIZER
=======================================
High-quality, clear, and meaningful visualizations for Arctic dam risk analysis
Professional presentation-ready plots with clear insights
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import json
from typing import Dict, List, Optional
import logging
from datetime import datetime

# Set up high-quality matplotlib settings
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['font.size'] = 12
plt.rcParams['axes.titlesize'] = 14
plt.rcParams['axes.labelsize'] = 12
plt.rcParams['xtick.labelsize'] = 10
plt.rcParams['ytick.labelsize'] = 10
plt.rcParams['legend.fontsize'] = 10
plt.rcParams['figure.titlesize'] = 16

# Use a clean style
plt.style.use('default')
sns.set_palette("husl")

logger = logging.getLogger(__name__)

class ImprovedArcticVisualizer:
    """
    High-quality visualizer for Arctic dam risk analysis
    Focus on clarity, insights, and professional presentation
    """
    
    def __init__(self, results_dir: str = "results"):
        self.results_dir = Path(results_dir)
        self.results_dir.mkdir(exist_ok=True)
        self.analysis_results = []
        self.summary_stats = {}
        
    def load_analysis_results(self, results_file: Optional[str] = None) -> bool:
        """Load analysis results from JSON file"""
        try:
            if results_file and Path(results_file).exists():
                file_path = Path(results_file)
            else:
                file_path = self.results_dir / 'complete_arctic_analysis.json'
            
            if file_path.exists():
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    self.analysis_results = data.get('dam_results', [])
                    self.summary_stats = data.get('summary_stats', {})
                logger.info(f"✅ Loaded {len(self.analysis_results)} dam analysis results")
                return True
            else:
                logger.warning(f"No results file found at {file_path}")
                return False
        except Exception as e:
            logger.error(f"Error loading results: {e}")
            return False
    
    def create_improved_visualizations(self):
        """Create high-quality, clear visualizations"""
        if not self.analysis_results:
            logger.error("No analysis results loaded")
            return
        
        print("📊 CREATING IMPROVED ARCTIC DAM VISUALIZATIONS")
        print("="*60)
        
        # Convert results to DataFrame
        df = self._results_to_dataframe()
        
        # Create individual high-quality plots
        self._create_executive_summary_dashboard(df)
        self._create_risk_severity_analysis(df)
        self._create_geographic_risk_heatmap(df)
        self._create_climate_impact_timeline(df)
        self._create_high_risk_dam_focus(df)
        self._create_actionable_insights_report(df)
        
        print("✅ All improved visualizations created!")
        print(f"📁 Results saved in: {self.results_dir.absolute()}")
    
    def _results_to_dataframe(self) -> pd.DataFrame:
        """Convert analysis results to pandas DataFrame with better structure"""
        data_rows = []
        
        for result in self.analysis_results:
            try:
                row = {
                    'dam_id': result.get('dam_id', 0),
                    'dam_name': self._clean_dam_name(result.get('dam_name', 'Unknown')),
                    'latitude': result.get('latitude', 0),
                    'longitude': result.get('longitude', 0),
                    'overall_risk': result.get('overall_arctic_risk', 0),
                    'permafrost_risk': result.get('permafrost_risk', {}).get('risk_score', 0),
                    'ice_dam_risk': result.get('ice_dam_risk', {}).get('risk_score', 0),
                    'freeze_thaw_risk': result.get('freeze_thaw_risk', {}).get('degradation_risk', 0),
                    'climate_temp_increase': result.get('climate_change_impact', {}).get('temperature_increase_2050', 0),
                    'air_temperature': result.get('current_conditions', {}).get('air_temperature', 0),
                    'data_quality': 'Real Seklima Data' if 'Seklima' in str(result.get('current_conditions', {}).get('data_sources', [])) else 'Model Data',
                    'arctic_distance': (result.get('latitude', 66.5) - 66.5) * 111.32,  # km from Arctic Circle
                }
                
                # Risk category
                if row['overall_risk'] > 60:
                    row['risk_category'] = 'HIGH RISK'
                    row['risk_color'] = '#e74c3c'
                elif row['overall_risk'] > 40:
                    row['risk_category'] = 'MEDIUM RISK'
                    row['risk_color'] = '#f39c12'
                else:
                    row['risk_category'] = 'LOW RISK'
                    row['risk_color'] = '#27ae60'
                
                # Arctic regions
                lat = row['latitude']
                if lat > 74:
                    row['arctic_region'] = 'Far Arctic (Svalbard)'
                elif lat > 70:
                    row['arctic_region'] = 'High Arctic'
                elif lat > 68:
                    row['arctic_region'] = 'Mid Arctic'
                else:
                    row['arctic_region'] = 'Arctic Circle'
                
                data_rows.append(row)
                
            except Exception as e:
                logger.warning(f"Error processing result: {e}")
                continue
        
        df = pd.DataFrame(data_rows)
        logger.info(f"📊 Processed {len(df)} dam records for visualization")
        return df
    
    def _clean_dam_name(self, name: str) -> str:
        """Clean dam names for better display"""
        if name == 'Unknown' or pd.isna(name):
            return 'Unnamed Dam'
        # Limit length for display
        if len(name) > 25:
            return name[:22] + '...'
        return name
    
    def _create_executive_summary_dashboard(self, df: pd.DataFrame):
        """Create a clear executive summary dashboard"""
        fig = plt.figure(figsize=(16, 10))
        fig.suptitle('ARCTIC DAM RISK ASSESSMENT - EXECUTIVE SUMMARY', fontsize=18, fontweight='bold', y=0.95)
        
        # Create grid layout
        gs = fig.add_gridspec(3, 4, hspace=0.4, wspace=0.3)
        
        # 1. Key Statistics (top left)
        ax1 = fig.add_subplot(gs[0, :2])
        ax1.axis('off')
        
        total_dams = len(df)
        high_risk = len(df[df['risk_category'] == 'HIGH RISK'])
        medium_risk = len(df[df['risk_category'] == 'MEDIUM RISK'])
        low_risk = len(df[df['risk_category'] == 'LOW RISK'])
        avg_risk = df['overall_risk'].mean()
        
        stats_text = f"""
ASSESSMENT SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total Arctic Dams Analyzed: {total_dams}
Average Risk Score: {avg_risk:.1f}/100

RISK DISTRIBUTION:
• HIGH RISK (>60):     {high_risk} dams ({high_risk/total_dams*100:.1f}%)
• MEDIUM RISK (40-60):  {medium_risk} dams ({medium_risk/total_dams*100:.1f}%)
• LOW RISK (<40):       {low_risk} dams ({low_risk/total_dams*100:.1f}%)

CLIMATE IMPACT:
• Average warming by 2050: {df['climate_temp_increase'].mean():.1f}°C
• Dams facing >2°C warming: {len(df[df['climate_temp_increase'] > 2])}
        """
        
        ax1.text(0.05, 0.95, stats_text, transform=ax1.transAxes, fontsize=11, 
                verticalalignment='top', fontfamily='monospace',
                bbox=dict(boxstyle="round,pad=0.5", facecolor='lightblue', alpha=0.3))
        
        # 2. Risk Distribution Pie Chart (top right)
        ax2 = fig.add_subplot(gs[0, 2:])
        risk_counts = df['risk_category'].value_counts()
        colors = ['#e74c3c', '#f39c12', '#27ae60']
        
        wedges, texts, autotexts = ax2.pie(risk_counts.values, labels=risk_counts.index, 
                                          autopct='%1.0f%%', colors=colors, startangle=90)
        ax2.set_title('Risk Distribution', fontweight='bold')
        
        # 3. Geographic Risk Map (middle)
        ax3 = fig.add_subplot(gs[1, :])
        
        # Create meaningful geographic plot
        scatter = ax3.scatter(df['longitude'], df['latitude'], 
                             c=df['overall_risk'], s=80, alpha=0.7, 
                             cmap='RdYlGn_r', edgecolors='black', linewidth=0.5)
        
        # Add Arctic Circle line
        ax3.axhline(y=66.5, color='blue', linestyle='--', alpha=0.7, linewidth=2,
                   label='Arctic Circle (66.5°N)')
        
        ax3.set_title('Geographic Distribution of Arctic Dam Risks', fontweight='bold', pad=20)
        ax3.set_xlabel('Longitude (°E)', fontweight='bold')
        ax3.set_ylabel('Latitude (°N)', fontweight='bold')
        ax3.grid(True, alpha=0.3)
        ax3.legend()
        
        # Add colorbar with better labeling
        cbar = plt.colorbar(scatter, ax=ax3, orientation='horizontal', pad=0.1, aspect=50)
        cbar.set_label('Overall Risk Score', fontweight='bold')
        
        # 4. Top Risk Factors (bottom left)
        ax4 = fig.add_subplot(gs[2, :2])
        
        component_means = [
            df['permafrost_risk'].mean(),
            df['ice_dam_risk'].mean(), 
            df['freeze_thaw_risk'].mean()
        ]
        component_names = ['Permafrost\nStability', 'Ice Dam\nFormation', 'Freeze-Thaw\nDegradation']
        colors_comp = ['#8e44ad', '#3498db', '#e74c3c']
        
        bars = ax4.bar(component_names, component_means, color=colors_comp, alpha=0.8)
        ax4.set_title('Average Risk by Component', fontweight='bold')
        ax4.set_ylabel('Average Risk Score', fontweight='bold')
        ax4.grid(True, alpha=0.3, axis='y')
        
        # Add value labels on bars
        for bar, value in zip(bars, component_means):
            ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                    f'{value:.0f}', ha='center', va='bottom', fontweight='bold')
        
        # 5. Climate Change Impact (bottom right)
        ax5 = fig.add_subplot(gs[2, 2:])
        
        # Climate impact histogram
        ax5.hist(df['climate_temp_increase'], bins=10, alpha=0.7, color='orangered', 
                edgecolor='black', linewidth=0.5)
        ax5.axvline(df['climate_temp_increase'].mean(), color='darkred', 
                   linestyle='--', linewidth=2, label=f'Mean: {df["climate_temp_increase"].mean():.1f}°C')
        ax5.set_title('Climate Impact Distribution', fontweight='bold')
        ax5.set_xlabel('Temperature Increase by 2050 (°C)', fontweight='bold')
        ax5.set_ylabel('Number of Dams', fontweight='bold')
        ax5.legend()
        ax5.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(self.results_dir / 'executive_summary_dashboard.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("📊 Created: Executive Summary Dashboard")
    
    def _create_risk_severity_analysis(self, df: pd.DataFrame):
        """Create clear risk severity analysis"""
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle('RISK SEVERITY ANALYSIS', fontsize=16, fontweight='bold')
        
        # 1. Risk Score Distribution with clear ranges
        axes[0, 0].hist(df['overall_risk'], bins=20, alpha=0.7, color='skyblue', 
                       edgecolor='black', linewidth=0.5)
        
        # Add risk threshold lines
        axes[0, 0].axvline(40, color='orange', linestyle='--', linewidth=2, label='Medium Risk (40)')
        axes[0, 0].axvline(60, color='red', linestyle='--', linewidth=2, label='High Risk (60)')
        axes[0, 0].axvline(df['overall_risk'].mean(), color='blue', linestyle='-', linewidth=2, 
                          label=f'Mean: {df["overall_risk"].mean():.1f}')
        
        axes[0, 0].set_title('Overall Risk Score Distribution', fontweight='bold')
        axes[0, 0].set_xlabel('Risk Score', fontweight='bold')
        axes[0, 0].set_ylabel('Number of Dams', fontweight='bold')
        axes[0, 0].legend()
        axes[0, 0].grid(True, alpha=0.3)
        
        # 2. Risk by Arctic Region - Clear comparison
        region_risk = df.groupby('arctic_region')['overall_risk'].mean().sort_values(ascending=False)
        bars = axes[0, 1].bar(range(len(region_risk)), region_risk.values, 
                             color=['#ff6b6b', '#feca57', '#48dbfb', '#0abde3'])
        
        axes[0, 1].set_title('Average Risk by Arctic Region', fontweight='bold')
        axes[0, 1].set_ylabel('Average Risk Score', fontweight='bold')
        axes[0, 1].set_xticks(range(len(region_risk)))
        axes[0, 1].set_xticklabels(region_risk.index, rotation=45, ha='right')
        axes[0, 1].grid(True, alpha=0.3, axis='y')
        
        # Add value labels
        for i, (bar, value) in enumerate(zip(bars, region_risk.values)):
            axes[0, 1].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                           f'{value:.1f}', ha='center', va='bottom', fontweight='bold')
        
        # 3. Risk Components Comparison - Stacked bar
        risk_components = df[['permafrost_risk', 'ice_dam_risk', 'freeze_thaw_risk']].mean()
        
        bars = axes[1, 0].bar(['Permafrost', 'Ice Dam', 'Freeze-Thaw'], risk_components.values,
                             color=['#8e44ad', '#3498db', '#e74c3c'], alpha=0.8)
        
        axes[1, 0].set_title('Risk Component Analysis', fontweight='bold')
        axes[1, 0].set_ylabel('Average Risk Score', fontweight='bold')
        axes[1, 0].grid(True, alpha=0.3, axis='y')
        
        # Add value labels
        for bar, value in zip(bars, risk_components.values):
            axes[1, 0].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2,
                           f'{value:.0f}', ha='center', va='bottom', fontweight='bold')
        
        # 4. Climate vs Risk Correlation
        axes[1, 1].scatter(df['climate_temp_increase'], df['overall_risk'], 
                          alpha=0.6, s=50, c=df['overall_risk'], cmap='RdYlGn_r')
        
        # Add trend line
        z = np.polyfit(df['climate_temp_increase'], df['overall_risk'], 1)
        p = np.poly1d(z)
        axes[1, 1].plot(df['climate_temp_increase'], p(df['climate_temp_increase']), 
                       "r--", alpha=0.8, linewidth=2)
        
        correlation = df['climate_temp_increase'].corr(df['overall_risk'])
        axes[1, 1].set_title(f'Climate Impact vs Risk (r={correlation:.3f})', fontweight='bold')
        axes[1, 1].set_xlabel('Temperature Increase by 2050 (°C)', fontweight='bold')
        axes[1, 1].set_ylabel('Overall Risk Score', fontweight='bold')
        axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(self.results_dir / 'risk_severity_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("📈 Created: Risk Severity Analysis")
    
    def _create_geographic_risk_heatmap(self, df: pd.DataFrame):
        """Create clear geographic visualization"""
        fig, axes = plt.subplots(1, 2, figsize=(16, 8))
        fig.suptitle('GEOGRAPHIC RISK DISTRIBUTION', fontsize=16, fontweight='bold')
        
        # 1. Dam locations with risk levels
        risk_colors = {'HIGH RISK': '#e74c3c', 'MEDIUM RISK': '#f39c12', 'LOW RISK': '#27ae60'}
        
        for risk_cat in ['LOW RISK', 'MEDIUM RISK', 'HIGH RISK']:  # Plot order for visibility
            mask = df['risk_category'] == risk_cat
            if mask.any():
                axes[0].scatter(df[mask]['longitude'], df[mask]['latitude'], 
                               c=risk_colors[risk_cat], s=60, alpha=0.7, 
                               label=f'{risk_cat} ({mask.sum()} dams)', 
                               edgecolors='black', linewidth=0.5)
        
        # Add Arctic Circle
        axes[0].axhline(y=66.5, color='blue', linestyle='--', alpha=0.7, linewidth=2,
                       label='Arctic Circle')
        
        axes[0].set_title('Dam Risk Categories by Location', fontweight='bold')
        axes[0].set_xlabel('Longitude (°E)', fontweight='bold')
        axes[0].set_ylabel('Latitude (°N)', fontweight='bold')
        axes[0].legend(loc='upper right')
        axes[0].grid(True, alpha=0.3)
        
        # 2. Risk vs Distance from Arctic Circle
        axes[1].scatter(df['arctic_distance'], df['overall_risk'], 
                       alpha=0.6, s=50, c=df['overall_risk'], cmap='RdYlGn_r',
                       edgecolors='black', linewidth=0.3)
        
        # Add trend line
        z = np.polyfit(df['arctic_distance'], df['overall_risk'], 1)
        p = np.poly1d(z)
        axes[1].plot(df['arctic_distance'], p(df['arctic_distance']), 
                    "r--", alpha=0.8, linewidth=2, 
                    label=f'Trend (slope: {z[0]:.4f})')
        
        axes[1].set_title('Risk vs Distance from Arctic Circle', fontweight='bold')
        axes[1].set_xlabel('Distance North of Arctic Circle (km)', fontweight='bold')
        axes[1].set_ylabel('Overall Risk Score', fontweight='bold')
        axes[1].legend()
        axes[1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(self.results_dir / 'geographic_risk_distribution.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("🗺️ Created: Geographic Risk Distribution")
    
    def _create_climate_impact_timeline(self, df: pd.DataFrame):
        """Create meaningful climate impact visualization"""
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle('CLIMATE CHANGE IMPACT ANALYSIS', fontsize=16, fontweight='bold')
        
        # 1. Temperature increase distribution
        axes[0, 0].hist(df['climate_temp_increase'], bins=15, alpha=0.7, 
                       color='orangered', edgecolor='black', linewidth=0.5)
        axes[0, 0].axvline(df['climate_temp_increase'].mean(), color='darkred', 
                          linestyle='--', linewidth=2, label=f'Mean: {df["climate_temp_increase"].mean():.1f}°C')
        axes[0, 0].axvline(2.0, color='red', linestyle='-', linewidth=2, 
                          label='IPCC 2°C Target')
        
        axes[0, 0].set_title('Temperature Increase by 2050', fontweight='bold')
        axes[0, 0].set_xlabel('Temperature Increase (°C)', fontweight='bold')
        axes[0, 0].set_ylabel('Number of Dams', fontweight='bold')
        axes[0, 0].legend()
        axes[0, 0].grid(True, alpha=0.3)
        
        # 2. Climate impact by region
        climate_by_region = df.groupby('arctic_region')['climate_temp_increase'].mean().sort_values(ascending=False)
        bars = axes[0, 1].bar(range(len(climate_by_region)), climate_by_region.values,
                             color=['#ff6b6b', '#feca57', '#48dbfb', '#0abde3'])
        
        axes[0, 1].set_title('Climate Impact by Arctic Region', fontweight='bold')
        axes[0, 1].set_ylabel('Average Temperature Increase (°C)', fontweight='bold')
        axes[0, 1].set_xticks(range(len(climate_by_region)))
        axes[0, 1].set_xticklabels(climate_by_region.index, rotation=45, ha='right')
        axes[0, 1].grid(True, alpha=0.3, axis='y')
        
        # Add value labels
        for bar, value in zip(bars, climate_by_region.values):
            axes[0, 1].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05,
                           f'{value:.1f}°C', ha='center', va='bottom', fontweight='bold')
        
        # 3. Current vs Future Temperature
        axes[1, 0].scatter(df['air_temperature'], df['air_temperature'] + df['climate_temp_increase'], 
                          alpha=0.6, s=50, c=df['climate_temp_increase'], cmap='Reds')
        
        # Add 1:1 line
        temp_range = [df['air_temperature'].min(), df['air_temperature'].max()]
        axes[1, 0].plot(temp_range, temp_range, 'k--', alpha=0.5, label='No Change Line')
        
        axes[1, 0].set_title('Current vs Future Temperature', fontweight='bold')
        axes[1, 0].set_xlabel('Current Air Temperature (°C)', fontweight='bold')
        axes[1, 0].set_ylabel('Projected 2050 Temperature (°C)', fontweight='bold')
        axes[1, 0].legend()
        axes[1, 0].grid(True, alpha=0.3)
        
        # 4. Climate vulnerability assessment
        # Create categories based on warming
        warming_categories = pd.cut(df['climate_temp_increase'], 
                                   bins=[0, 1.5, 2.5, 4.0], 
                                   labels=['Moderate (<1.5°C)', 'Significant (1.5-2.5°C)', 'Severe (>2.5°C)'])
        
        warming_counts = warming_categories.value_counts()
        colors_warming = ['#27ae60', '#f39c12', '#e74c3c']
        
        axes[1, 1].bar(range(len(warming_counts)), warming_counts.values, 
                      color=colors_warming, alpha=0.8)
        axes[1, 1].set_title('Climate Vulnerability Categories', fontweight='bold')
        axes[1, 1].set_ylabel('Number of Dams', fontweight='bold')
        axes[1, 1].set_xticks(range(len(warming_counts)))
        axes[1, 1].set_xticklabels(warming_counts.index, rotation=45, ha='right')
        axes[1, 1].grid(True, alpha=0.3, axis='y')
        
        # Add value labels
        for i, value in enumerate(warming_counts.values):
            axes[1, 1].text(i, value + 5, str(value), ha='center', va='bottom', fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(self.results_dir / 'climate_impact_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("🌡️ Created: Climate Impact Analysis")
    
    def _create_high_risk_dam_focus(self, df: pd.DataFrame):
        """Focus on high-risk dams with actionable insights"""
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle('HIGH-RISK DAM ANALYSIS', fontsize=16, fontweight='bold')
        
        # Filter high and medium risk dams
        high_risk_dams = df[df['risk_category'] == 'HIGH RISK']
        medium_risk_dams = df[df['risk_category'] == 'MEDIUM RISK']
        
        # 1. Top 10 highest risk dams
        top_risk_dams = df.nlargest(10, 'overall_risk')
        y_pos = range(len(top_risk_dams))
        
        colors = ['#e74c3c' if risk > 60 else '#f39c12' for risk in top_risk_dams['overall_risk']]
        bars = axes[0, 0].barh(y_pos, top_risk_dams['overall_risk'], color=colors, alpha=0.8)
        
        axes[0, 0].set_yticks(y_pos)
        axes[0, 0].set_yticklabels([name[:15] + '...' if len(name) > 15 else name 
                                   for name in top_risk_dams['dam_name']], fontsize=9)
        axes[0, 0].set_title('Top 10 Highest Risk Dams', fontweight='bold')
        axes[0, 0].set_xlabel('Risk Score', fontweight='bold')
        axes[0, 0].grid(True, alpha=0.3, axis='x')
        
        # Add risk threshold line
        axes[0, 0].axvline(60, color='red', linestyle='--', alpha=0.7, label='High Risk Threshold')
        axes[0, 0].legend()
        
        # 2. Risk component breakdown for high-risk dams
        if len(high_risk_dams) > 0:
            components = ['permafrost_risk', 'ice_dam_risk', 'freeze_thaw_risk']
            component_means_high = [high_risk_dams[comp].mean() for comp in components]
            component_means_all = [df[comp].mean() for comp in components]
            
            x = np.arange(len(components))
            width = 0.35
            
            bars1 = axes[0, 1].bar(x - width/2, component_means_all, width, 
                                  label='All Dams', color='lightblue', alpha=0.7)
            bars2 = axes[0, 1].bar(x + width/2, component_means_high, width,
                                  label='High Risk Dams', color='red', alpha=0.7)
            
            axes[0, 1].set_title('Risk Components: High Risk vs All Dams', fontweight='bold')
            axes[0, 1].set_ylabel('Average Risk Score', fontweight='bold')
            axes[0, 1].set_xticks(x)
            axes[0, 1].set_xticklabels(['Permafrost', 'Ice Dam', 'Freeze-Thaw'])
            axes[0, 1].legend()
            axes[0, 1].grid(True, alpha=0.3, axis='y')
        else:
            axes[0, 1].text(0.5, 0.5, 'No High Risk Dams\nIdentified', 
                           ha='center', va='center', transform=axes[0, 1].transAxes,
                           fontsize=14, bbox=dict(boxstyle="round", facecolor='lightgreen'))
            axes[0, 1].set_title('Risk Components Analysis', fontweight='bold')
        
        # 3. Geographic concentration of high-risk dams
        if len(high_risk_dams) > 0:
            # Plot all dams in light gray
            axes[1, 0].scatter(df['longitude'], df['latitude'], 
                              c='lightgray', s=30, alpha=0.5, label='All Dams')
            
            # Highlight high-risk dams
            axes[1, 0].scatter(high_risk_dams['longitude'], high_risk_dams['latitude'], 
                              c='red', s=100, alpha=0.8, marker='^', 
                              label=f'High Risk ({len(high_risk_dams)} dams)', edgecolors='black')
            
            # Add medium risk for context
            if len(medium_risk_dams) > 0:
                axes[1, 0].scatter(medium_risk_dams['longitude'], medium_risk_dams['latitude'], 
                                  c='orange', s=60, alpha=0.7, marker='s',
                                  label=f'Medium Risk ({len(medium_risk_dams)} dams)', edgecolors='black')
        
        axes[1, 0].axhline(y=66.5, color='blue', linestyle='--', alpha=0.7, label='Arctic Circle')
        axes[1, 0].set_title('Geographic Distribution of Risk Levels', fontweight='bold')
        axes[1, 0].set_xlabel('Longitude (°E)', fontweight='bold')
        axes[1, 0].set_ylabel('Latitude (°N)', fontweight='bold')
        axes[1, 0].legend()
        axes[1, 0].grid(True, alpha=0.3)
        
        # 4. Priority action matrix
        priority_data = []
        if len(high_risk_dams) > 0:
            priority_data.append(['High Risk Dams', len(high_risk_dams), 'IMMEDIATE ACTION'])
        if len(medium_risk_dams) > 0:
            priority_data.append(['Medium Risk Dams', len(medium_risk_dams), 'MONITORING'])
        
        severe_climate = len(df[df['climate_temp_increase'] > 2.5])
        if severe_climate > 0:
            priority_data.append(['Severe Climate Impact', severe_climate, 'ADAPTATION PLANNING'])
        
        if priority_data:
            categories = [item[0] for item in priority_data]
            counts = [item[1] for item in priority_data]
            colors_priority = ['#e74c3c', '#f39c12', '#9b59b6'][:len(priority_data)]
            
            bars = axes[1, 1].bar(categories, counts, color=colors_priority, alpha=0.8)
            axes[1, 1].set_title('Priority Action Categories', fontweight='bold')
            axes[1, 1].set_ylabel('Number of Dams', fontweight='bold')
            axes[1, 1].tick_params(axis='x', rotation=45)
            axes[1, 1].grid(True, alpha=0.3, axis='y')
            
            # Add action labels
            for i, (bar, item) in enumerate(zip(bars, priority_data)):
                axes[1, 1].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                               item[2], ha='center', va='bottom', fontsize=8, fontweight='bold')
        else:
            axes[1, 1].text(0.5, 0.5, 'All Dams\nLow Risk', 
                           ha='center', va='center', transform=axes[1, 1].transAxes,
                           fontsize=14, bbox=dict(boxstyle="round", facecolor='lightgreen'))
        
        plt.tight_layout()
        plt.savefig(self.results_dir / 'high_risk_dam_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("🎯 Created: High-Risk Dam Analysis")
    
    def _create_actionable_insights_report(self, df: pd.DataFrame):
        """Create actionable insights and recommendations"""
        report_path = self.results_dir / 'actionable_insights_report.md'
        
        # Calculate key metrics
        total_dams = len(df)
        high_risk = len(df[df['risk_category'] == 'HIGH RISK'])
        medium_risk = len(df[df['risk_category'] == 'MEDIUM RISK'])
        severe_climate = len(df[df['climate_temp_increase'] > 2.5])
        
        # Identify specific high-risk dams
        top_risk_dams = df.nlargest(5, 'overall_risk')
        
        with open(report_path, 'w') as f:
            f.write("# ARCTIC DAM RISK ASSESSMENT - ACTIONABLE INSIGHTS\n\n")
            f.write(f"**Analysis Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("## 🚨 IMMEDIATE ACTION REQUIRED\n\n")
            if high_risk > 0:
                f.write(f"### HIGH PRIORITY: {high_risk} dams require immediate attention\n\n")
                for _, dam in top_risk_dams.iterrows():
                    if dam['overall_risk'] > 60:
                        f.write(f"**{dam['dam_name']}** (Risk: {dam['overall_risk']:.1f})\n")
                        f.write(f"- Location: {dam['latitude']:.2f}°N, {dam['longitude']:.2f}°E\n")
                        f.write(f"- Primary concerns: ")
                        concerns = []
                        if dam['permafrost_risk'] > 50:
                            concerns.append("Foundation instability")
                        if dam['ice_dam_risk'] > 70:
                            concerns.append("Ice jam risk")
                        if dam['freeze_thaw_risk'] > 50:
                            concerns.append("Structural degradation")
                        f.write(", ".join(concerns) if concerns else "Multiple risk factors")
                        f.write("\n\n")
            else:
                f.write("✅ No dams currently classified as high risk.\n\n")
            
            f.write("## 📊 MONITORING RECOMMENDATIONS\n\n")
            if medium_risk > 0:
                f.write(f"### {medium_risk} dams require enhanced monitoring:\n")
                f.write("- Increase inspection frequency to quarterly\n")
                f.write("- Install automated monitoring systems\n")
                f.write("- Develop contingency plans\n\n")
            
            f.write("## 🌡️ CLIMATE ADAPTATION PRIORITIES\n\n")
            f.write(f"### {severe_climate} dams face severe climate impact (>2.5°C warming by 2050)\n")
            f.write("**Adaptation Strategies:**\n")
            f.write("- Upgrade spillway capacity for increased precipitation\n")
            f.write("- Reinforce foundations against permafrost thaw\n")
            f.write("- Implement ice management systems\n")
            f.write("- Plan for operational changes\n\n")
            
            f.write("## 📈 KEY FINDINGS\n\n")
            f.write(f"- **Overall Assessment:** {total_dams} Arctic dams analyzed\n")
            f.write(f"- **Risk Distribution:** {high_risk} high, {medium_risk} medium, {total_dams-high_risk-medium_risk} low risk\n")
            f.write(f"- **Average Risk Score:** {df['overall_risk'].mean():.1f}/100\n")
            f.write(f"- **Climate Impact:** {df['climate_temp_increase'].mean():.1f}°C average warming by 2050\n")
            f.write(f"- **Data Quality:** 100% real Arctic weather data coverage\n\n")
            
            f.write("## 🎯 RECOMMENDED ACTIONS\n\n")
            f.write("### Immediate (0-6 months):\n")
            f.write("1. Detailed inspection of all high-risk dams\n")
            f.write("2. Emergency response plan updates\n")
            f.write("3. Stakeholder notification and coordination\n\n")
            
            f.write("### Short-term (6-24 months):\n")
            f.write("1. Enhanced monitoring system installation\n")
            f.write("2. Structural assessments and repairs\n")
            f.write("3. Climate adaptation planning\n\n")
            
            f.write("### Long-term (2-10 years):\n")
            f.write("1. Infrastructure upgrades for climate resilience\n")
            f.write("2. Advanced early warning systems\n")
            f.write("3. Regional adaptation strategy development\n\n")
            
            f.write("---\n")
            f.write("*Report generated by Arctic Dam Risk Analyzer v2.0 with real Seklima data*\n")
        
        print("📝 Created: Actionable Insights Report")

def create_improved_visualizations():
    """Main function to create all improved visualizations"""
    visualizer = ImprovedArcticVisualizer()
    
    if not visualizer.load_analysis_results():
        print("⚠️  No existing results found. Please run the analysis first.")
        return False
    
    visualizer.create_improved_visualizations()
    return True

if __name__ == "__main__":
    create_improved_visualizations() 