#!/usr/bin/env python3
"""
ARCTIC DAM ANALYSIS RESULTS VISUALIZER
======================================
Creates comprehensive visualizations and reports from Arctic dam risk analysis
Multiple plots and summaries for easy user understanding
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

# Set up matplotlib for better plots
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

logger = logging.getLogger(__name__)

class ArcticResultsVisualizer:
    """
    Comprehensive visualizer for Arctic dam risk analysis results
    Creates multiple plots and reports for user understanding
    """
    
    def __init__(self, results_dir: str = "results"):
        self.results_dir = Path(results_dir)
        self.results_dir.mkdir(exist_ok=True)
        self.analysis_results = []
        self.summary_stats = {}
        
    def load_analysis_results(self, results_file: Optional[str] = None) -> bool:
        """Load analysis results from JSON file or run new analysis"""
        try:
            # Try specified file first, then default location
            if results_file and Path(results_file).exists():
                file_path = Path(results_file)
            else:
                file_path = self.results_dir / 'complete_arctic_analysis.json'
            
            if file_path.exists():
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    self.analysis_results = data.get('dam_results', [])
                    self.summary_stats = data.get('summary_stats', {})
                logger.info(f"✅ Loaded {len(self.analysis_results)} dam analysis results from {file_path}")
                return True
            else:
                logger.warning(f"No results file found at {file_path}")
                return False
        except Exception as e:
            logger.error(f"Error loading results: {e}")
            return False
    
    def create_comprehensive_visualizations(self):
        """Create all visualization plots for Arctic dam analysis"""
        if not self.analysis_results:
            logger.error("No analysis results loaded")
            return
        
        print("📊 CREATING COMPREHENSIVE ARCTIC DAM VISUALIZATIONS")
        print("="*60)
        
        # Convert results to DataFrame for easier analysis
        df = self._results_to_dataframe()
        
        # Create individual visualization plots
        self._create_risk_distribution_plot(df)
        self._create_geographic_risk_map(df)
        self._create_climate_impact_analysis(df)
        self._create_permafrost_analysis(df)
        self._create_station_coverage_plot(df)
        self._create_risk_summary_dashboard(df)
        self._create_detailed_report(df)
        
        print("✅ All visualizations created successfully!")
        print(f"📁 Results saved in: {self.results_dir.absolute()}")
    
    def _results_to_dataframe(self) -> pd.DataFrame:
        """Convert analysis results to pandas DataFrame"""
        data_rows = []
        
        for result in self.analysis_results:
            try:
                row = {
                    'dam_id': result.get('dam_id', 0),
                    'dam_name': result.get('dam_name', 'Unknown'),
                    'latitude': result.get('latitude', 0),
                    'longitude': result.get('longitude', 0),
                    'overall_risk': result.get('overall_arctic_risk', 0),
                    'permafrost_risk': result.get('permafrost_risk', {}).get('risk_score', 0),
                    'ice_dam_risk': result.get('ice_dam_risk', {}).get('risk_score', 0),
                    'freeze_thaw_risk': result.get('freeze_thaw_risk', {}).get('degradation_risk', 0),
                    'climate_temp_increase': result.get('climate_change_impact', {}).get('temperature_increase_2050', 0),
                    'air_temperature': result.get('current_conditions', {}).get('air_temperature', 0),
                    'snow_depth': result.get('current_conditions', {}).get('snow_depth', 0),
                    'permafrost_depth': result.get('current_conditions', {}).get('permafrost_depth_m', 0),
                    'data_sources': ', '.join(result.get('current_conditions', {}).get('data_sources', [])),
                    'arctic_distance': (result.get('latitude', 66.5) - 66.5) * 111.32,  # km from Arctic Circle
                    'weather_station': result.get('current_conditions', {}).get('station_name', 'Unknown')
                }
                
                # Classify Arctic regions
                lat = row['latitude']
                if lat > 74:
                    row['arctic_region'] = 'Far Arctic (Svalbard)'
                elif lat > 70:
                    row['arctic_region'] = 'High Arctic'
                elif lat > 68:
                    row['arctic_region'] = 'Mid Arctic'
                else:
                    row['arctic_region'] = 'Arctic Circle'
                
                # Risk categories
                if row['overall_risk'] > 60:
                    row['risk_category'] = 'High Risk'
                elif row['overall_risk'] > 40:
                    row['risk_category'] = 'Medium Risk'
                else:
                    row['risk_category'] = 'Low Risk'
                
                data_rows.append(row)
                
            except Exception as e:
                logger.warning(f"Error processing result: {e}")
                continue
        
        df = pd.DataFrame(data_rows)
        logger.info(f"📊 Created DataFrame with {len(df)} dam records")
        return df
    
    def _create_risk_distribution_plot(self, df: pd.DataFrame):
        """Create risk distribution analysis plots"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('🧊 ARCTIC DAM RISK DISTRIBUTION ANALYSIS', fontsize=16, fontweight='bold')
        
        # Overall risk distribution
        axes[0, 0].hist(df['overall_risk'], bins=20, alpha=0.7, color='skyblue', edgecolor='black')
        axes[0, 0].axvline(df['overall_risk'].mean(), color='red', linestyle='--', 
                          label=f'Mean: {df["overall_risk"].mean():.1f}')
        axes[0, 0].set_title('Overall Risk Score Distribution')
        axes[0, 0].set_xlabel('Risk Score')
        axes[0, 0].set_ylabel('Number of Dams')
        axes[0, 0].legend()
        axes[0, 0].grid(True, alpha=0.3)
        
        # Risk by Arctic region
        risk_by_region = df.groupby('arctic_region')['overall_risk'].mean().sort_values(ascending=False)
        axes[0, 1].bar(range(len(risk_by_region)), risk_by_region.values, 
                       color=['#ff6b6b', '#feca57', '#48dbfb', '#0abde3'])
        axes[0, 1].set_title('Average Risk by Arctic Region')
        axes[0, 1].set_ylabel('Average Risk Score')
        axes[0, 1].set_xticks(range(len(risk_by_region)))
        axes[0, 1].set_xticklabels(risk_by_region.index, rotation=45, ha='right')
        axes[0, 1].grid(True, alpha=0.3)
        
        # Risk category pie chart
        risk_counts = df['risk_category'].value_counts()
        colors = ['#ff6b6b', '#feca57', '#54a0ff']
        axes[1, 0].pie(risk_counts.values, labels=risk_counts.index, autopct='%1.1f%%', 
                       colors=colors, startangle=90)
        axes[1, 0].set_title('Dam Distribution by Risk Category')
        
        # Risk components comparison
        risk_components = ['permafrost_risk', 'ice_dam_risk', 'freeze_thaw_risk']
        component_means = [df[comp].mean() for comp in risk_components]
        axes[1, 1].bar(['Permafrost', 'Ice Dam', 'Freeze-Thaw'], component_means, 
                       color=['#8e44ad', '#3498db', '#e74c3c'])
        axes[1, 1].set_title('Average Risk by Component Type')
        axes[1, 1].set_ylabel('Average Risk Score')
        axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(self.results_dir / 'arctic_risk_distribution.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("📈 Created: Risk Distribution Analysis")
    
    def _create_geographic_risk_map(self, df: pd.DataFrame):
        """Create geographic visualization of dam risks"""
        fig, axes = plt.subplots(1, 2, figsize=(16, 8))
        fig.suptitle('🗺️ GEOGRAPHIC DISTRIBUTION OF ARCTIC DAM RISKS', fontsize=16, fontweight='bold')
        
        # Scatter plot of dam locations colored by risk
        scatter = axes[0].scatter(df['longitude'], df['latitude'], 
                                c=df['overall_risk'], s=60, alpha=0.7, 
                                cmap='RdYlBu_r', edgecolors='black', linewidth=0.5)
        axes[0].set_title('Dam Locations Colored by Overall Risk')
        axes[0].set_xlabel('Longitude (°E)')
        axes[0].set_ylabel('Latitude (°N)')
        
        # Add Arctic Circle line
        axes[0].axhline(y=66.5, color='blue', linestyle='--', alpha=0.7, 
                       label='Arctic Circle (66.5°N)')
        axes[0].legend()
        
        # Add colorbar
        cbar = plt.colorbar(scatter, ax=axes[0])
        cbar.set_label('Overall Risk Score')
        axes[0].grid(True, alpha=0.3)
        
        # Distance from Arctic Circle vs Risk
        axes[1].scatter(df['arctic_distance'], df['overall_risk'], 
                       alpha=0.6, s=50, color='coral')
        axes[1].set_title('Risk vs Distance from Arctic Circle')
        axes[1].set_xlabel('Distance North of Arctic Circle (km)')
        axes[1].set_ylabel('Overall Risk Score')
        
        # Add trend line
        z = np.polyfit(df['arctic_distance'], df['overall_risk'], 1)
        p = np.poly1d(z)
        axes[1].plot(df['arctic_distance'], p(df['arctic_distance']), "r--", alpha=0.8, 
                    label=f'Trend (slope: {z[0]:.3f})')
        axes[1].legend()
        axes[1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(self.results_dir / 'arctic_geographic_risks.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("🗺️ Created: Geographic Risk Distribution")
    
    def _create_climate_impact_analysis(self, df: pd.DataFrame):
        """Create climate change impact analysis"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('🌡️ CLIMATE CHANGE IMPACT ANALYSIS', fontsize=16, fontweight='bold')
        
        # Temperature increase by 2050
        axes[0, 0].hist(df['climate_temp_increase'], bins=15, alpha=0.7, 
                       color='orangered', edgecolor='black')
        axes[0, 0].axvline(df['climate_temp_increase'].mean(), color='darkred', 
                          linestyle='--', label=f'Mean: {df["climate_temp_increase"].mean():.1f}°C')
        axes[0, 0].set_title('Projected Temperature Increase by 2050')
        axes[0, 0].set_xlabel('Temperature Increase (°C)')
        axes[0, 0].set_ylabel('Number of Dams')
        axes[0, 0].legend()
        axes[0, 0].grid(True, alpha=0.3)
        
        # Climate impact vs current temperature
        axes[0, 1].scatter(df['air_temperature'], df['climate_temp_increase'], 
                          alpha=0.6, s=50, color='orange')
        axes[0, 1].set_title('Climate Impact vs Current Temperature')
        axes[0, 1].set_xlabel('Current Air Temperature (°C)')
        axes[0, 1].set_ylabel('Projected Temperature Increase (°C)')
        axes[0, 1].grid(True, alpha=0.3)
        
        # Climate impact by Arctic region
        climate_by_region = df.groupby('arctic_region')['climate_temp_increase'].mean().sort_values(ascending=False)
        axes[1, 0].bar(range(len(climate_by_region)), climate_by_region.values,
                      color=['#ff6b6b', '#feca57', '#48dbfb', '#0abde3'])
        axes[1, 0].set_title('Average Climate Impact by Region')
        axes[1, 0].set_ylabel('Avg Temperature Increase (°C)')
        axes[1, 0].set_xticks(range(len(climate_by_region)))
        axes[1, 0].set_xticklabels(climate_by_region.index, rotation=45, ha='right')
        axes[1, 0].grid(True, alpha=0.3)
        
        # Overall risk vs climate impact
        axes[1, 1].scatter(df['climate_temp_increase'], df['overall_risk'], 
                          alpha=0.6, s=50, color='red')
        axes[1, 1].set_title('Overall Risk vs Climate Impact')
        axes[1, 1].set_xlabel('Projected Temperature Increase (°C)')
        axes[1, 1].set_ylabel('Overall Risk Score')
        
        # Add correlation coefficient
        correlation = df['climate_temp_increase'].corr(df['overall_risk'])
        axes[1, 1].text(0.05, 0.95, f'Correlation: {correlation:.3f}', 
                        transform=axes[1, 1].transAxes, bbox=dict(boxstyle="round", facecolor='wheat'))
        axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(self.results_dir / 'arctic_climate_impact.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("🌡️ Created: Climate Impact Analysis")
    
    def _create_permafrost_analysis(self, df: pd.DataFrame):
        """Create permafrost-specific analysis"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('❄️ PERMAFROST ANALYSIS', fontsize=16, fontweight='bold')
        
        # Permafrost depth distribution
        axes[0, 0].hist(df['permafrost_depth'], bins=20, alpha=0.7, 
                       color='lightblue', edgecolor='black')
        axes[0, 0].set_title('Permafrost Depth Distribution')
        axes[0, 0].set_xlabel('Permafrost Depth (m)')
        axes[0, 0].set_ylabel('Number of Dams')
        axes[0, 0].grid(True, alpha=0.3)
        
        # Permafrost depth vs latitude
        axes[0, 1].scatter(df['latitude'], df['permafrost_depth'], 
                          alpha=0.6, s=50, color='blue')
        axes[0, 1].set_title('Permafrost Depth vs Latitude')
        axes[0, 1].set_xlabel('Latitude (°N)')
        axes[0, 1].set_ylabel('Permafrost Depth (m)')
        axes[0, 1].grid(True, alpha=0.3)
        
        # Permafrost risk vs depth
        axes[1, 0].scatter(df['permafrost_depth'], df['permafrost_risk'], 
                          alpha=0.6, s=50, color='purple')
        axes[1, 0].set_title('Permafrost Risk vs Depth')
        axes[1, 0].set_xlabel('Permafrost Depth (m)')
        axes[1, 0].set_ylabel('Permafrost Risk Score')
        axes[1, 0].grid(True, alpha=0.3)
        
        # Snow depth vs permafrost depth
        axes[1, 1].scatter(df['snow_depth'], df['permafrost_depth'], 
                          alpha=0.6, s=50, color='cyan')
        axes[1, 1].set_title('Snow Depth vs Permafrost Depth')
        axes[1, 1].set_xlabel('Snow Depth (m)')
        axes[1, 1].set_ylabel('Permafrost Depth (m)')
        axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(self.results_dir / 'arctic_permafrost_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("❄️ Created: Permafrost Analysis")
    
    def _create_station_coverage_plot(self, df: pd.DataFrame):
        """Create weather station coverage analysis"""
        fig, axes = plt.subplots(1, 2, figsize=(16, 8))
        fig.suptitle('📡 WEATHER STATION COVERAGE ANALYSIS', fontsize=16, fontweight='bold')
        
        # Station usage frequency
        station_counts = df['weather_station'].value_counts()
        axes[0].bar(range(len(station_counts)), station_counts.values, 
                   color='lightgreen', edgecolor='black')
        axes[0].set_title('Dams per Weather Station')
        axes[0].set_xlabel('Weather Stations')
        axes[0].set_ylabel('Number of Dams Served')
        axes[0].set_xticks(range(len(station_counts)))
        axes[0].set_xticklabels(station_counts.index, rotation=45, ha='right')
        axes[0].grid(True, alpha=0.3)
        
        # Data source distribution
        data_source_counts = df['data_sources'].str.contains('Seklima_Real_Data').value_counts()
        # Ensure labels match the data
        if len(data_source_counts) == 2:
            labels = ['Fallback Data', 'Real Seklima Data'] if False in data_source_counts.index else ['Real Seklima Data', 'Fallback Data']
        else:
            labels = ['Real Seklima Data'] if True in data_source_counts.index else ['Fallback Data']
        
        colors = ['#2ecc71', '#e74c3c'][:len(data_source_counts)]
        axes[1].pie(data_source_counts.values, labels=labels[:len(data_source_counts)], autopct='%1.1f%%', 
                   colors=colors, startangle=90)
        axes[1].set_title('Data Source Quality Distribution')
        
        plt.tight_layout()
        plt.savefig(self.results_dir / 'arctic_station_coverage.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("📡 Created: Weather Station Coverage")
    
    def _create_risk_summary_dashboard(self, df: pd.DataFrame):
        """Create comprehensive risk summary dashboard"""
        fig = plt.figure(figsize=(20, 12))
        fig.suptitle('🎯 ARCTIC DAM RISK ASSESSMENT DASHBOARD', fontsize=20, fontweight='bold')
        
        # Create a complex subplot layout
        gs = fig.add_gridspec(3, 4, hspace=0.3, wspace=0.3)
        
        # Top summary statistics
        ax1 = fig.add_subplot(gs[0, :2])
        summary_stats = [
            f"Total Dams Analyzed: {len(df)}",
            f"High Risk Dams: {len(df[df['risk_category'] == 'High Risk'])}",
            f"Average Risk Score: {df['overall_risk'].mean():.1f}",
            f"Max Risk Score: {df['overall_risk'].max():.1f}",
            f"Real Data Coverage: {(df['data_sources'].str.contains('Seklima').sum() / len(df) * 100):.1f}%"
        ]
        
        for i, stat in enumerate(summary_stats):
            ax1.text(0.1, 0.8 - i*0.15, stat, fontsize=14, fontweight='bold', 
                    transform=ax1.transAxes)
        ax1.set_title('📊 SUMMARY STATISTICS', fontsize=16, fontweight='bold')
        ax1.axis('off')
        
        # Risk distribution
        ax2 = fig.add_subplot(gs[0, 2:])
        risk_counts = df['risk_category'].value_counts()
        colors = ['#e74c3c', '#f39c12', '#27ae60']
        wedges, texts, autotexts = ax2.pie(risk_counts.values, labels=risk_counts.index, 
                                          autopct='%1.1f%%', colors=colors, startangle=90)
        ax2.set_title('Risk Category Distribution')
        
        # Geographic distribution
        ax3 = fig.add_subplot(gs[1, :2])
        scatter = ax3.scatter(df['longitude'], df['latitude'], 
                             c=df['overall_risk'], s=40, alpha=0.7, 
                             cmap='RdYlBu_r', edgecolors='black', linewidth=0.3)
        ax3.axhline(y=66.5, color='blue', linestyle='--', alpha=0.7)
        ax3.set_title('Geographic Risk Distribution')
        ax3.set_xlabel('Longitude')
        ax3.set_ylabel('Latitude')
        
        # Top 10 highest risk dams
        ax4 = fig.add_subplot(gs[1, 2:])
        top_risk_dams = df.nlargest(10, 'overall_risk')
        y_pos = range(len(top_risk_dams))
        ax4.barh(y_pos, top_risk_dams['overall_risk'], color='red', alpha=0.7)
        ax4.set_yticks(y_pos)
        ax4.set_yticklabels([name[:20] + '...' if len(name) > 20 else name 
                            for name in top_risk_dams['dam_name']], fontsize=8)
        ax4.set_title('Top 10 Highest Risk Dams')
        ax4.set_xlabel('Risk Score')
        
        # Climate impact by region
        ax5 = fig.add_subplot(gs[2, :2])
        climate_by_region = df.groupby('arctic_region')['climate_temp_increase'].mean()
        ax5.bar(range(len(climate_by_region)), climate_by_region.values,
               color=['#ff6b6b', '#feca57', '#48dbfb', '#0abde3'])
        ax5.set_title('Climate Impact by Arctic Region')
        ax5.set_ylabel('Avg Temp Increase (°C)')
        ax5.set_xticks(range(len(climate_by_region)))
        ax5.set_xticklabels(climate_by_region.index, rotation=45, ha='right')
        
        # Risk components comparison
        ax6 = fig.add_subplot(gs[2, 2:])
        components = ['permafrost_risk', 'ice_dam_risk', 'freeze_thaw_risk']
        component_means = [df[comp].mean() for comp in components]
        component_names = ['Permafrost', 'Ice Dam', 'Freeze-Thaw']
        bars = ax6.bar(component_names, component_means, 
                      color=['#8e44ad', '#3498db', '#e74c3c'])
        ax6.set_title('Average Risk by Component')
        ax6.set_ylabel('Average Risk Score')
        
        # Add value labels on bars
        for bar, value in zip(bars, component_means):
            ax6.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                    f'{value:.1f}', ha='center', va='bottom', fontweight='bold')
        
        plt.savefig(self.results_dir / 'arctic_risk_dashboard.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("🎯 Created: Comprehensive Risk Dashboard")
    
    def _create_detailed_report(self, df: pd.DataFrame):
        """Create detailed text report"""
        report_path = self.results_dir / 'arctic_dam_analysis_report.md'
        
        with open(report_path, 'w') as f:
            f.write("# ARCTIC DAM RISK ANALYSIS REPORT\n")
            f.write("## Comprehensive Assessment of Norwegian Arctic Dams\n\n")
            f.write(f"**Analysis Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("## EXECUTIVE SUMMARY\n\n")
            f.write(f"- **Total Dams Analyzed:** {len(df)}\n")
            f.write(f"- **High Risk Dams:** {len(df[df['risk_category'] == 'High Risk'])}\n")
            f.write(f"- **Medium Risk Dams:** {len(df[df['risk_category'] == 'Medium Risk'])}\n")
            f.write(f"- **Low Risk Dams:** {len(df[df['risk_category'] == 'Low Risk'])}\n")
            f.write(f"- **Average Overall Risk:** {df['overall_risk'].mean():.1f}\n")
            f.write(f"- **Real Data Coverage:** {(df['data_sources'].str.contains('Seklima').sum() / len(df) * 100):.1f}%\n\n")
            
            f.write("## KEY FINDINGS\n\n")
            f.write("### Geographic Distribution\n")
            f.write(f"- Northernmost dam: {df.loc[df['latitude'].idxmax(), 'dam_name']} at {df['latitude'].max():.2f}°N\n")
            f.write(f"- Southernmost dam: {df.loc[df['latitude'].idxmin(), 'dam_name']} at {df['latitude'].min():.2f}°N\n")
            f.write(f"- Average distance from Arctic Circle: {df['arctic_distance'].mean():.0f} km\n\n")
            
            f.write("### Risk Analysis\n")
            highest_risk = df.loc[df['overall_risk'].idxmax()]
            f.write(f"- Highest risk dam: **{highest_risk['dam_name']}** (Risk: {highest_risk['overall_risk']:.1f})\n")
            f.write(f"- Average permafrost risk: {df['permafrost_risk'].mean():.1f}\n")
            f.write(f"- Average ice dam risk: {df['ice_dam_risk'].mean():.1f}\n")
            f.write(f"- Average freeze-thaw risk: {df['freeze_thaw_risk'].mean():.1f}\n\n")
            
            f.write("### Climate Change Impact\n")
            f.write(f"- Average temperature increase by 2050: {df['climate_temp_increase'].mean():.1f}°C\n")
            f.write(f"- Maximum projected warming: {df['climate_temp_increase'].max():.1f}°C\n")
            f.write(f"- Dams with >2°C warming: {len(df[df['climate_temp_increase'] > 2])}\n\n")
            
            f.write("### Data Quality\n")
            f.write(f"- Dams with real Seklima weather data: {df['data_sources'].str.contains('Seklima').sum()}\n")
            f.write("- Primary weather stations used:\n")
            for station, count in df['weather_station'].value_counts().head(5).items():
                f.write(f"  - {station}: {count} dams\n")
            f.write("\n")
            
            f.write("## HIGH RISK DAMS REQUIRING ATTENTION\n\n")
            high_risk_dams = df[df['risk_category'] == 'High Risk'].sort_values('overall_risk', ascending=False)
            if len(high_risk_dams) > 0:
                for _, dam in high_risk_dams.iterrows():
                    f.write(f"- **{dam['dam_name']}** (ID: {dam['dam_id']})\n")
                    f.write(f"  - Location: {dam['latitude']:.2f}°N, {dam['longitude']:.2f}°E\n")
                    f.write(f"  - Overall Risk: {dam['overall_risk']:.1f}\n")
                    f.write(f"  - Primary Concerns: ")
                    concerns = []
                    if dam['permafrost_risk'] > 50:
                        concerns.append("Permafrost instability")
                    if dam['ice_dam_risk'] > 50:
                        concerns.append("Ice dam formation")
                    if dam['freeze_thaw_risk'] > 50:
                        concerns.append("Freeze-thaw damage")
                    f.write(", ".join(concerns) if concerns else "General Arctic conditions")
                    f.write("\n\n")
            else:
                f.write("No dams classified as high risk in current analysis.\n\n")
            
            f.write("## RECOMMENDATIONS\n\n")
            f.write("1. **Immediate Attention Required:**\n")
            f.write("   - Focus on dams with risk scores > 60\n")
            f.write("   - Prioritize Far Arctic and High Arctic locations\n\n")
            
            f.write("2. **Climate Adaptation Planning:**\n")
            f.write("   - Develop adaptation strategies for dams with >2°C projected warming\n")
            f.write("   - Consider increased spillway capacity for extreme precipitation\n\n")
            
            f.write("3. **Monitoring Enhancement:**\n")
            f.write("   - Install real-time monitoring for high-risk dams\n")
            f.write("   - Regular permafrost stability assessments\n\n")
            
            f.write("---\n")
            f.write("*Report generated by Arctic Dam Risk Analyzer with real Seklima weather data*\n")
        
        print("📝 Created: Detailed Analysis Report")

def create_all_visualizations():
    """Main function to create all visualizations from analysis results"""
    visualizer = ArcticResultsVisualizer()
    
    # Try to load existing results or run new analysis
    if not visualizer.load_analysis_results():
        print("⚠️  No existing results found. Please run the analysis first.")
        print("   Run: python arctic_risk_analyzer_improved.py")
        return False
    
    # Create all visualizations
    visualizer.create_comprehensive_visualizations()
    return True

if __name__ == "__main__":
    create_all_visualizations() 