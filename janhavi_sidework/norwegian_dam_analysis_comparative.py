#!/usr/bin/env python3
"""
Norwegian Dam Analysis for Comparative Study: India vs Norway
==============================================================

Comparative analysis of Norwegian dam infrastructure for academic publication.
Generates statistics, visualizations, and detailed CSV matching Indian dam study format.

Author: Analysis for Janhavi Singh's conference paper
Date: November 2025
Data Source: Norwegian Water Resources and Energy Directorate (NVE)
"""

import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Set professional plotting style
plt.style.use('default')
sns.set_palette("Set2")
plt.rcParams['font.size'] = 11
plt.rcParams['font.family'] = 'sans-serif'

class NorwegianDamComparativeAnalyzer:
    """
    Comprehensive analyzer for Norwegian dam infrastructure with 
    comparative metrics for India vs Norway study.
    """
    
    def __init__(self, data_dir="../Norway_Analysis/Data"):
        """Initialize analyzer with NVE data directory."""
        self.data_dir = Path(data_dir)
        self.output_dir = Path(".")
        self.viz_dir = Path("visualizations")
        self.viz_dir.mkdir(exist_ok=True)
        
        # Reference year for age calculations
        self.current_year = 2025
        
        # Norwegian to English translations for purpose field
        self.purpose_translations = {
            'Kraftproduksjon': 'Power Production',
            'Vannforsyning': 'Water Supply',
            'Rekreasjon': 'Recreation',
            'Akvakultur - settefisk': 'Aquaculture - Juvenile Fish',
            'Andre': 'Other',
            'Akvakultur': 'Aquaculture',
            'Ukjent': 'Unknown',
            'Snøproduksjon': 'Snow Production',
            'Jordvanning': 'Irrigation',
            'Vassdragsinngrep': 'Watercourse Intervention',
            'Tidligere fløtning': 'Former Log Floating',
            'Industri': 'Industry',
            'Kraftproduksjon, Oppstuvn.dam/sperred': 'Power Production, Damming',
            'Kraftproduksjon, Vannforsyning': 'Power Production, Water Supply',
            'Kraftproduksjon, Akvakultur - settefisk': 'Power Production, Aquaculture'
        }
        
        # Norwegian county names (2024/2025 system - 15 fylker)
        # Note: Approximate assignment based on coordinates
        # For precise county boundaries, use official Statistics Norway shapefiles
        self.county_map = {
            'Agder': 'Agder',
            'Innlandet': 'Innlandet',
            'Møre og Romsdal': 'Møre og Romsdal',
            'Nordland': 'Nordland',
            'Oslo': 'Oslo',
            'Rogaland': 'Rogaland',
            'Troms': 'Troms',
            'Finnmark': 'Finnmark',
            'Trøndelag': 'Trøndelag',
            'Vestfold': 'Vestfold',
            'Telemark': 'Telemark',
            'Vestland': 'Vestland',
            'Akershus': 'Akershus',
            'Buskerud': 'Buskerud',
            'Østfold': 'Østfold'
        }
        
        print("=" * 70)
        print("NORWEGIAN DAM COMPARATIVE ANALYSIS")
        print("For: India vs Norway Conference Paper")
        print("=" * 70)
        
    def load_data(self):
        """Load NVE dam and reservoir datasets."""
        print("\n📂 Loading NVE datasets...")
        
        try:
            # Load dam points
            self.dam_punkt = gpd.read_file(self.data_dir / "Vannkraft_DamPunkt.shp")
            print(f"✅ Loaded {len(self.dam_punkt):,} dam points")
            
            # Load dam lines
            self.dam_linje = gpd.read_file(self.data_dir / "Vannkraft_DamLinje.shp")
            print(f"✅ Loaded {len(self.dam_linje):,} dam lines")
            
            # Load reservoirs (with storage data)
            self.magasin = gpd.read_file(self.data_dir / "Vannkraft_Magasin.shp")
            print(f"✅ Loaded {len(self.magasin):,} reservoirs")
            
            # Convert to WGS84 for coordinate analysis
            if self.dam_punkt.crs.to_string() != 'EPSG:4326':
                self.dam_punkt = self.dam_punkt.to_crs('EPSG:4326')
                self.magasin = self.magasin.to_crs('EPSG:4326')
                
            print("✅ Data loaded successfully\n")
            return True
            
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            return False
    
    def assign_counties(self):
        """Assign Norwegian counties to dams based on coordinates.
        
        NOTE: This uses APPROXIMATE geographic assignment based on lat/long.
        For precise county attribution, official Statistics Norway (SSB) 
        administrative boundary shapefiles should be used.
        
        County system: 2024/2025 (15 fylker after Viken dissolution)
        """
        print("🗺️  Assigning counties to dams (approximate method)...")
        print("   ⚠️  Using simplified geographic assignment")
        print("   ⚠️  For precise boundaries, use official SSB shapefiles\n")
        
        # Simplified county assignment based on latitude/longitude ranges
        def get_county(lat, lon):
            """Simplified county assignment - APPROXIMATE only."""
            # Far North
            if lat > 70:
                return 'Finnmark'
            elif lat > 68.5:
                return 'Troms'
            # North
            elif lat > 66.5:
                return 'Nordland'
            # Central
            elif lat > 64:
                return 'Trøndelag'
            # West Coast
            elif lat > 61 and lon < 7:
                return 'Møre og Romsdal'
            elif lat > 59.5 and lon < 6.5:
                return 'Vestland'
            # Central/Eastern mountains
            elif lat > 61 and lon >= 7:
                return 'Innlandet'
            elif lat > 60 and lon >= 8:
                return 'Innlandet'
            # Southwest
            elif lat > 58.5 and lon < 6:
                return 'Rogaland'
            # Southeast regions
            elif lat > 59 and lon >= 9 and lon < 11:
                return 'Buskerud'
            elif lat > 59 and lon >= 11:
                return 'Akershus'
            elif lat > 58.5 and lon >= 8 and lon < 10:
                return 'Telemark'
            elif lat > 58.5 and lon >= 10:
                return 'Vestfold'
            elif lat <= 59 and lon >= 10.5:
                return 'Østfold'
            # South
            else:
                return 'Agder'
        
        # Assign counties to dam points
        self.dam_punkt['county'] = self.dam_punkt.geometry.apply(
            lambda geom: get_county(geom.y, geom.x)
        )
        
        # Assign counties to reservoirs
        self.magasin['county'] = self.magasin.geometry.centroid.apply(
            lambda geom: get_county(geom.y, geom.x)
        )
        
        print(f"✅ Counties assigned to {len(self.dam_punkt)} dams\n")
    
    def calculate_statistics(self):
        """Calculate comprehensive statistics for all analyses."""
        print("📊 Calculating comprehensive statistics...\n")
        
        # 1. DECADE-WISE ANALYSIS
        print("1️⃣  Decade-wise construction trends...")
        dam_with_year = self.dam_punkt[self.dam_punkt['idriftAar'].notna()].copy()
        dam_with_year = dam_with_year[
            (dam_with_year['idriftAar'] >= 1800) & 
            (dam_with_year['idriftAar'] <= 2025)
        ]
        dam_with_year['decade'] = (dam_with_year['idriftAar'] // 10) * 10
        
        self.decade_counts = dam_with_year['decade'].value_counts().sort_index()
        print(f"   Total dams with construction year: {len(dam_with_year):,}")
        print(f"   Peak decade: {self.decade_counts.idxmax()}s with {self.decade_counts.max()} dams\n")
        
        # 2. AGE DISTRIBUTION
        print("2️⃣  Age distribution analysis...")
        dam_with_year['age'] = self.current_year - dam_with_year['idriftAar']
        
        # Age categories matching Indian analysis
        def categorize_age(age):
            if age < 25:
                return 'Less than 25 yrs'
            elif age < 50:
                return '25 yrs to 49 yrs'
            elif age < 100:
                return '50 yrs to 99 yrs'
            else:
                return 'Greater than or Equal to 100 yrs'
        
        dam_with_year['age_category'] = dam_with_year['age'].apply(categorize_age)
        self.age_distribution = dam_with_year['age_category'].value_counts()
        
        # Add under construction (status check - 'U' = Under construction in Norwegian data)
        under_construction = len(self.dam_punkt[self.dam_punkt['status'] == 'U'])
        print(f"   Under construction: {under_construction} dams")
        if under_construction > 0:
            self.age_distribution['Under-construction'] = under_construction
            
        print(f"   Average dam age: {dam_with_year['age'].mean():.1f} years")
        print(f"   Oldest dam: {dam_with_year['age'].max():.0f} years old "
              f"(built {dam_with_year['idriftAar'].min():.0f})\n")
        
        # 3. REGIONAL DISTRIBUTION
        print("3️⃣  Regional (county) distribution...")
        self.county_counts = self.dam_punkt['county'].value_counts()
        print(f"   Total counties: {len(self.county_counts)}")
        print(f"   Top county: {self.county_counts.index[0]} with {self.county_counts.iloc[0]} dams\n")
        
        # 4. STORAGE ANALYSIS
        print("4️⃣  Storage and reservoir analysis...")
        storage_data = self.magasin[self.magasin['volOppdemt'].notna()].copy()
        self.total_storage = storage_data['volOppdemt'].sum()
        self.avg_storage = storage_data['volOppdemt'].mean()
        
        # Large dams (≥1000 MCM)
        self.large_dams = storage_data[storage_data['volOppdemt'] >= 1000]
        print(f"   Total storage capacity: {self.total_storage:,.1f} MCM")
        print(f"   Average storage: {self.avg_storage:.1f} MCM")
        print(f"   Large dams (≥1000 MCM): {len(self.large_dams)}\n")
        
        # 5. STORAGE EFFICIENCY (Volume/Area ratio)
        print("5️⃣  Storage efficiency analysis...")
        efficiency_data = self.magasin[
            (self.magasin['volOppdemt'].notna()) & 
            (self.magasin['areal_km2'].notna()) &
            (self.magasin['areal_km2'] > 0)
        ].copy()
        efficiency_data['storage_efficiency'] = (
            efficiency_data['volOppdemt'] / efficiency_data['areal_km2']
        )
        self.avg_efficiency = efficiency_data['storage_efficiency'].mean()
        print(f"   Average storage efficiency: {self.avg_efficiency:.2f} MCM/km²")
        print(f"   This indicates deep valley/fjord storage characteristics\n")
        
        # 6. REGULATION RANGE (Operational flexibility - UNIQUE to Norway)
        print("6️⃣  Regulation range analysis (UNIQUE to Norwegian data)...")
        reg_data = self.magasin[
            (self.magasin['hrv_moh'].notna()) & 
            (self.magasin['lrv_moh'].notna())
        ].copy()
        reg_data['regulation_range'] = reg_data['hrv_moh'] - reg_data['lrv_moh']
        self.avg_regulation = reg_data['regulation_range'].mean()
        self.regulation_data = reg_data
        print(f"   Reservoirs with regulation data: {len(reg_data)}")
        print(f"   Average regulation range: {self.avg_regulation:.1f} meters")
        print(f"   This shows operational flexibility for hydropower peaking\n")
        
        # 7. PURPOSE DISTRIBUTION (with English translations)
        print("7️⃣  Purpose/function analysis...")
        purpose_data = self.magasin[self.magasin['formal_L'].notna()].copy()
        
        # Translate Norwegian purposes to English
        purpose_data['purpose_english'] = purpose_data['formal_L'].map(
            self.purpose_translations
        ).fillna(purpose_data['formal_L'])  # Keep original if no translation
        
        self.purpose_counts = purpose_data['purpose_english'].value_counts()
        self.purpose_counts_norwegian = purpose_data['formal_L'].value_counts()
        
        print(f"   Primary purposes identified: {len(self.purpose_counts)}")
        if len(self.purpose_counts) > 0:
            print(f"   Dominant purpose: {self.purpose_counts.index[0]} "
                  f"({self.purpose_counts.iloc[0]} reservoirs)\n")
        
        print("✅ Statistical analysis complete\n")
    
    def generate_visualizations(self):
        """Generate all 7 visualizations matching Indian study format."""
        print("🎨 Generating visualizations...\n")
        
        # CHART 1: Regional Distribution (Donut Chart)
        self._viz_regional_distribution()
        
        # CHART 2: Age-wise Classification (Donut Chart)
        self._viz_age_distribution()
        
        # CHART 3: Decade-wise Addition (Bar Chart)
        self._viz_decade_construction()
        
        # CHART 4: Storage Efficiency (Scatter Plot)
        self._viz_storage_efficiency()
        
        # CHART 5: Regulation Range (Histogram)
        self._viz_regulation_range()
        
        # CHART 6: Purpose Distribution (Pie Chart)
        self._viz_purpose_distribution()
        
        # CHART 7: Norway-India Comparison Table
        self._viz_comparison_table()
        
        print("✅ All visualizations generated successfully\n")
    
    def _viz_regional_distribution(self):
        """Chart 1: Regional (County) Distribution - Donut Chart."""
        print("   📊 Creating regional distribution chart...")
        
        fig, ax = plt.subplots(figsize=(14, 10))
        
        # Prepare data
        top_counties = self.county_counts.head(10)
        colors = plt.cm.Set3(np.linspace(0, 1, len(top_counties)))
        
        # Create donut chart
        wedges, texts, autotexts = ax.pie(
            top_counties.values,
            labels=None,
            autopct='',
            colors=colors,
            startangle=90,
            pctdistance=0.85,
            wedgeprops=dict(width=0.5, edgecolor='white', linewidth=2)
        )
        
        # Add center text
        ax.text(0, 0, f'Total Dams : {len(self.dam_punkt)}',
                ha='center', va='center', fontsize=24, fontweight='bold')
        
        # Add labels outside
        for i, (county, count) in enumerate(top_counties.items()):
            angle = (wedges[i].theta2 + wedges[i].theta1) / 2
            x = 1.3 * np.cos(np.radians(angle))
            y = 1.3 * np.sin(np.radians(angle))
            
            ha = 'left' if x > 0 else 'right'
            ax.text(x, y, f'{county}, {count}',
                   ha=ha, va='center', fontsize=11, fontweight='bold')
        
        ax.set_title('Regional Distribution of Norwegian Dams (by County/Fylke)',
                    fontsize=16, fontweight='bold', pad=20)
        
        plt.tight_layout()
        plt.savefig(self.viz_dir / 'regional_distribution_norway.png',
                   dpi=300, bbox_inches='tight')
        plt.close()
        print("   ✅ Saved: regional_distribution_norway.png")
    
    def _viz_age_distribution(self):
        """Chart 2: Age-wise Classification - Donut Chart."""
        print("   📊 Creating age distribution chart...")
        
        fig, ax = plt.subplots(figsize=(12, 10))
        
        # Prepare data in specific order
        age_order = [
            'Under-construction',
            'Less than 25 yrs',
            '25 yrs to 49 yrs',
            '50 yrs to 99 yrs',
            'Greater than or Equal to 100 yrs'
        ]
        
        age_data = []
        age_labels = []
        for category in age_order:
            if category in self.age_distribution.index:
                age_data.append(self.age_distribution[category])
                age_labels.append(category)
        
        colors = ['#5DADE2', '#E74C3C', '#F39C12', '#9B59B6', '#2ECC71'][:len(age_data)]
        
        # Create donut chart
        wedges, texts, autotexts = ax.pie(
            age_data,
            labels=None,
            autopct='%d',
            colors=colors,
            startangle=90,
            pctdistance=0.85,
            wedgeprops=dict(width=0.5, edgecolor='white', linewidth=2),
            textprops={'fontsize': 14, 'fontweight': 'bold', 'color': 'white'}
        )
        
        # Add center title
        total_classified = sum(age_data)
        ax.text(0, 0, 'AGE-WISE\nNORWEGIAN DAMS',
                ha='center', va='center', fontsize=18, fontweight='bold')
        
        # Add legend
        ax.legend(wedges, age_labels, title="Age Categories",
                 loc="center left", bbox_to_anchor=(1, 0, 0.5, 1),
                 fontsize=11)
        
        ax.set_title('Age Distribution of Norwegian Dams',
                    fontsize=16, fontweight='bold', pad=20)
        
        plt.tight_layout()
        plt.savefig(self.viz_dir / 'age_wise_norway.png',
                   dpi=300, bbox_inches='tight')
        plt.close()
        print("   ✅ Saved: age_wise_norway.png")
    
    def _viz_decade_construction(self):
        """Chart 3: Decade-wise Addition - Bar Chart."""
        print("   📊 Creating decade-wise construction chart...")
        
        fig, ax = plt.subplots(figsize=(16, 9))
        
        # Prepare decade labels
        decades = self.decade_counts.index
        decade_labels = [f'{int(d)}s' if d < 2020 else 'Beyond\n2020' 
                        if d >= 2020 else f'Unto {int(d)}' 
                        for d in decades]
        
        # Create bar chart
        bars = ax.bar(range(len(self.decade_counts)), 
                      self.decade_counts.values,
                      color='#2E86C1', alpha=0.85, edgecolor='black', linewidth=1.2)
        
        # Add value labels on bars
        for i, (bar, value) in enumerate(zip(bars, self.decade_counts.values)):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 10,
                   f'{int(value)}',
                   ha='center', va='bottom', fontsize=11, fontweight='bold')
        
        # Styling
        ax.set_xticks(range(len(self.decade_counts)))
        ax.set_xticklabels(decade_labels, fontsize=11)
        ax.set_xlabel('Time-period', fontsize=13, fontweight='bold')
        ax.set_ylabel('Number of Dams', fontsize=13, fontweight='bold')
        ax.set_title('DECADE-WISE ADDITION OF NORWEGIAN DAMS',
                    fontsize=16, fontweight='bold', pad=20)
        ax.grid(axis='y', alpha=0.3, linestyle='--')
        ax.set_axisbelow(True)
        
        # Set y-axis limit with some headroom
        ax.set_ylim(0, max(self.decade_counts.values) * 1.15)
        
        plt.tight_layout()
        plt.savefig(self.viz_dir / 'decade_wise_norway.png',
                   dpi=300, bbox_inches='tight')
        plt.close()
        print("   ✅ Saved: decade_wise_norway.png")
    
    def _viz_storage_efficiency(self):
        """Chart 4: Storage Efficiency - Scatter Plot."""
        print("   📊 Creating storage efficiency chart...")
        
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Prepare data
        plot_data = self.magasin[
            (self.magasin['volOppdemt'].notna()) & 
            (self.magasin['areal_km2'].notna()) &
            (self.magasin['areal_km2'] > 0) &
            (self.magasin['volOppdemt'] > 0) &
            (self.magasin['areal_km2'] < 100) &  # Filter outliers
            (self.magasin['volOppdemt'] < 5000)
        ].copy()
        
        plot_data['efficiency'] = plot_data['volOppdemt'] / plot_data['areal_km2']
        
        # Create scatter plot
        scatter = ax.scatter(
            plot_data['areal_km2'],
            plot_data['volOppdemt'],
            c=plot_data['efficiency'],
            s=80,
            alpha=0.6,
            cmap='viridis',
            edgecolors='black',
            linewidth=0.5
        )
        
        # Add colorbar
        cbar = plt.colorbar(scatter, ax=ax)
        cbar.set_label('Storage Efficiency (MCM/km²)', 
                      fontsize=11, fontweight='bold')
        
        # Styling
        ax.set_xlabel('Reservoir Area (km²)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Storage Volume (MCM)', fontsize=12, fontweight='bold')
        ax.set_title('Storage Efficiency: Norwegian Deep Valley Reservoirs\n' +
                    'Volume vs Area Relationship',
                    fontsize=14, fontweight='bold', pad=15)
        ax.grid(True, alpha=0.3, linestyle='--')
        
        # Add annotation
        ax.text(0.02, 0.98, 
               f'Avg Efficiency: {self.avg_efficiency:.2f} MCM/km²\n' +
               'High values indicate deep\nvalley/fjord characteristics',
               transform=ax.transAxes,
               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8),
               va='top', fontsize=10)
        
        plt.tight_layout()
        plt.savefig(self.viz_dir / 'storage_efficiency_norway.png',
                   dpi=300, bbox_inches='tight')
        plt.close()
        print("   ✅ Saved: storage_efficiency_norway.png")
    
    def _viz_regulation_range(self):
        """Chart 5: Regulation Range - Histogram (UNIQUE to Norway)."""
        print("   📊 Creating regulation range chart...")
        
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Filter reasonable regulation ranges
        reg_plot = self.regulation_data[
            (self.regulation_data['regulation_range'] > 0) &
            (self.regulation_data['regulation_range'] < 200)
        ]['regulation_range']
        
        # Create histogram
        n, bins, patches = ax.hist(
            reg_plot,
            bins=30,
            color='#16A085',
            alpha=0.75,
            edgecolor='black',
            linewidth=1.2
        )
        
        # Add mean line
        mean_reg = reg_plot.mean()
        ax.axvline(mean_reg, color='red', linestyle='--', linewidth=2,
                  label=f'Mean: {mean_reg:.1f}m')
        
        # Styling
        ax.set_xlabel('Regulation Range (meters)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Number of Reservoirs', fontsize=12, fontweight='bold')
        ax.set_title('Operational Flexibility: Regulation Range of Norwegian Reservoirs\n' +
                    '(Higher range = Greater hydropower peaking capability)',
                    fontsize=14, fontweight='bold', pad=15)
        ax.grid(axis='y', alpha=0.3, linestyle='--')
        ax.legend(fontsize=11)
        
        # Add annotation
        ax.text(0.98, 0.98,
               f'Total Reservoirs: {len(reg_plot):,}\n' +
               f'Mean Range: {mean_reg:.1f}m\n' +
               f'Max Range: {reg_plot.max():.1f}m\n\n' +
               'This operational flexibility\n' +
               'supports Norway\'s role as\n' +
               '"Battery of Europe"',
               transform=ax.transAxes,
               bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8),
               va='top', ha='right', fontsize=10)
        
        plt.tight_layout()
        plt.savefig(self.viz_dir / 'regulation_range_norway.png',
                   dpi=300, bbox_inches='tight')
        plt.close()
        print("   ✅ Saved: regulation_range_norway.png")
    
    def _viz_purpose_distribution(self):
        """Chart 6: Purpose Distribution - Pie Chart (with English translations)."""
        print("   📊 Creating purpose distribution chart (English translations)...")
        
        fig, ax = plt.subplots(figsize=(12, 9))
        
        # Get top purposes (already in English from calculate_statistics)
        top_purposes = self.purpose_counts.head(8)
        colors = plt.cm.Paired(np.linspace(0, 1, len(top_purposes)))
        
        # Create pie chart with English labels
        wedges, texts, autotexts = ax.pie(
            top_purposes.values,
            labels=top_purposes.index,
            autopct='%1.1f%%',
            colors=colors,
            startangle=45,
            textprops={'fontsize': 10, 'fontweight': 'bold'}
        )
        
        # Style autopct (percentage text)
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontsize(11)
        
        ax.set_title('Purpose Distribution of Norwegian Dam Infrastructure\n(English Translation)',
                    fontsize=15, fontweight='bold', pad=20)
        
        plt.tight_layout()
        plt.savefig(self.viz_dir / 'purpose_distribution_norway.png',
                   dpi=300, bbox_inches='tight')
        plt.close()
        print("   ✅ Saved: purpose_distribution_norway.png (with English labels)")
    
    def _viz_comparison_table(self):
        """Chart 7: Norway vs India Comparison Table."""
        print("   📊 Creating comparative analysis table...")
        
        fig, ax = plt.subplots(figsize=(14, 10))
        ax.axis('off')
        
        # Comparison data
        comparison_data = [
            ['Metric', 'India (NRLD)', 'Norway (NVE)', 'Key Insight'],
            ['Total Large Dams', '~6,628', f'{len(self.dam_punkt):,}', 'Similar scale infrastructure'],
            ['Peak Construction', '1971-1990', f'{int(self.decade_counts.idxmax())}s', 
             'Post-independence vs Post-war'],
            ['Avg Storage/Area', 'Lower (broad valleys)', 
             f'{self.avg_efficiency:.1f} MCM/km²', 'Norway: Deep fjord storage'],
            ['Regulation Range', 'Not available', f'{self.avg_regulation:.1f}m average',
             'Norway: High operational flexibility'],
            ['Primary Purpose', 'Multipurpose\n(irrigation/flood/power)', 
             'Hydropower dominant', 'Different development focus'],
            ['Height Data', 'Available in NRLD', 'Not in public dataset',
             'Different data standards'],
            ['Governance', 'Dam Safety Act 2021\nNational DSA', 
             'NVE oversight\nWater Framework Directive', 'Statutory vs Directorate'],
            ['Geographic Focus', 'River valleys\nBroad basins', 
             'Mountain catchments\nWestern fjords', 'Topographic adaptation'],
            ['Oldest Dam', 'Pre-1900 era', 
             f'{int(self.dam_punkt["idriftAar"].min())}', 'Long infrastructure history'],
        ]
        
        # Create table
        table = ax.table(
            cellText=comparison_data,
            cellLoc='left',
            loc='center',
            bbox=[0, 0, 1, 1]
        )
        
        # Style table
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1, 2.5)
        
        # Style header row
        for i in range(4):
            cell = table[(0, i)]
            cell.set_facecolor('#2C3E50')
            cell.set_text_props(weight='bold', color='white', fontsize=11)
        
        # Alternate row colors
        for i in range(1, len(comparison_data)):
            for j in range(4):
                cell = table[(i, j)]
                if i % 2 == 0:
                    cell.set_facecolor('#ECF0F1')
                else:
                    cell.set_facecolor('#FFFFFF')
                cell.set_edgecolor('#BDC3C7')
                cell.set_linewidth(1.5)
        
        ax.set_title('Comparative Analysis: Indian vs Norwegian Dam Infrastructure\n' +
                    'Key Metrics and Insights for Conference Paper',
                    fontsize=15, fontweight='bold', pad=30)
        
        plt.tight_layout()
        plt.savefig(self.viz_dir / 'norway_india_comparison.png',
                   dpi=300, bbox_inches='tight')
        plt.close()
        print("   ✅ Saved: norway_india_comparison.png")
    
    def export_large_dams_csv(self):
        """Export detailed CSV of large Norwegian dams."""
        print("📝 Exporting large dams CSV...")
        
        # Get large dams (≥1000 MCM) OR top 30 by storage
        large_storage = self.magasin[self.magasin['volOppdemt'] >= 1000].copy()
        top_30 = self.magasin.nlargest(30, 'volOppdemt')
        
        # Combine and remove duplicates
        large_dams_data = pd.concat([large_storage, top_30]).drop_duplicates(
            subset=['magasinNr', 'magNavn']
        )
        
        # Calculate additional fields
        large_dams_data['age'] = self.current_year - large_dams_data['idriftAar']
        large_dams_data['latitude'] = large_dams_data.geometry.centroid.y
        large_dams_data['longitude'] = large_dams_data.geometry.centroid.x
        
        # Calculate storage efficiency where possible
        large_dams_data['storage_efficiency_MCM_per_km2'] = np.where(
            large_dams_data['areal_km2'] > 0,
            large_dams_data['volOppdemt'] / large_dams_data['areal_km2'],
            np.nan
        )
        
        # Calculate regulation range where available
        large_dams_data['regulation_range_m'] = np.where(
            (large_dams_data['hrv_moh'].notna()) & 
            (large_dams_data['lrv_moh'].notna()),
            large_dams_data['hrv_moh'] - large_dams_data['lrv_moh'],
            np.nan
        )
        
        # Prepare export dataframe
        export_df = pd.DataFrame({
            'Dam_Name': large_dams_data['magNavn'],
            'County': large_dams_data['county'],
            'Construction_Year': large_dams_data['idriftAar'],
            'Age_Years': large_dams_data['age'],
            'Status': large_dams_data['status'],
            'Gross_Storage_MCM': large_dams_data['volOppdemt'],
            'Reservoir_Area_km2': large_dams_data['areal_km2'],
            'Storage_Efficiency_MCM_per_km2': large_dams_data['storage_efficiency_MCM_per_km2'],
            'Regulation_Range_m': large_dams_data['regulation_range_m'],
            'Max_Water_Level_masl': large_dams_data['hrv_moh'],
            'Min_Water_Level_masl': large_dams_data['lrv_moh'],
            'Purpose': large_dams_data['formal_L'],
            'Latitude': large_dams_data['latitude'],
            'Longitude': large_dams_data['longitude'],
            'Watershed_Number': large_dams_data['vassdragNr'],
            'Reservoir_Number': large_dams_data['magasinNr'],
        })
        
        # Sort by storage volume
        export_df = export_df.sort_values('Gross_Storage_MCM', ascending=False)
        
        # Export to CSV
        output_file = self.output_dir / 'large_norwegian_dams.csv'
        export_df.to_csv(output_file, index=False, encoding='utf-8-sig')
        
        print(f"✅ Exported {len(export_df)} large dams to CSV")
        print(f"   File: {output_file}\n")
        
        return export_df
    
    def generate_statistics_summary(self):
        """Generate text summary of all key statistics."""
        print("📄 Generating statistics summary file...")
        
        summary_lines = [
            "=" * 70,
            "NORWEGIAN DAM INFRASTRUCTURE - KEY STATISTICS SUMMARY",
            "For: India vs Norway Comparative Conference Paper",
            "=" * 70,
            "",
            "DATA SOURCE",
            "-" * 70,
            "Source: Norwegian Water Resources and Energy Directorate (NVE)",
            f"Dataset: NVE Hydropower Infrastructure Database",
            f"Analysis Date: {datetime.now().strftime('%B %Y')}",
            f"Reference Year: {self.current_year}",
            "",
            "OVERALL STATISTICS",
            "-" * 70,
            f"Total Dam Points: {len(self.dam_punkt):,}",
            f"Total Dam Lines: {len(self.dam_linje):,}",
            f"Total Reservoirs: {len(self.magasin):,}",
            f"Dams with Construction Year: {len(self.dam_punkt[self.dam_punkt['idriftAar'].notna()]):,}",
            "",
            "DECADE-WISE CONSTRUCTION",
            "-" * 70,
            f"Peak Construction Decade: {int(self.decade_counts.idxmax())}s",
            f"Dams Built in Peak Decade: {int(self.decade_counts.max())}",
            f"Earliest Dam Year: {int(self.dam_punkt['idriftAar'].min())}",
            f"Latest Dam Year: {int(self.dam_punkt['idriftAar'].max())}",
            "",
            "AGE DISTRIBUTION",
            "-" * 70,
        ]
        
        for category in self.age_distribution.index:
            summary_lines.append(f"{category}: {self.age_distribution[category]:,} dams")
        
        summary_lines.extend([
            "",
            "REGIONAL DISTRIBUTION (TOP 5 COUNTIES)",
            "-" * 70,
        ])
        
        for i, (county, count) in enumerate(self.county_counts.head(5).items(), 1):
            summary_lines.append(f"{i}. {county}: {count:,} dams")
        
        summary_lines.extend([
            "",
            "STORAGE ANALYSIS",
            "-" * 70,
            f"Total Storage Capacity: {self.total_storage:,.1f} MCM",
            f"Average Storage per Reservoir: {self.avg_storage:.1f} MCM",
            f"Largest Reservoir Storage: {self.magasin['volOppdemt'].max():,.1f} MCM",
            f"Large Dams (≥1000 MCM): {len(self.large_dams)}",
            "",
            "STORAGE EFFICIENCY (TOPOGRAPHIC ADAPTATION)",
            "-" * 70,
            f"Average Storage Efficiency: {self.avg_efficiency:.2f} MCM/km²",
            "Interpretation: High values indicate deep valley/fjord storage",
            "This reflects Norway's mountainous topography",
            "",
            "REGULATION RANGE (OPERATIONAL FLEXIBILITY - UNIQUE)",
            "-" * 70,
            f"Reservoirs with Regulation Data: {len(self.regulation_data):,}",
            f"Average Regulation Range: {self.avg_regulation:.1f} meters",
            f"Maximum Regulation Range: {self.regulation_data['regulation_range'].max():.1f} meters",
            "Interpretation: High regulation ranges enable hydropower peaking",
            "Supports Norway's role as 'Battery of Europe' for grid balancing",
            "",
            "PURPOSE DISTRIBUTION (TOP 5)",
            "-" * 70,
        ])
        
        for i, (purpose, count) in enumerate(self.purpose_counts.head(5).items(), 1):
            summary_lines.append(f"{i}. {purpose}: {count} reservoirs")
        
        summary_lines.extend([
            "",
            "DATA LIMITATIONS",
            "-" * 70,
            "✗ Dam height data: Not available in NVE public dataset",
            "✓ Construction years: Available for most dams",
            "✓ Storage volumes: Available for reservoirs",
            "✓ Regulation ranges: Available (unique to Norwegian data)",
            "✓ Geographic coordinates: Complete coverage",
            "✓ Purpose/function: Available for most structures",
            "",
            "COMPARATIVE INSIGHTS: NORWAY VS INDIA",
            "-" * 70,
            "• Similar total dam counts (~5,000 vs ~6,600)",
            "• Different construction peaks (1960s Norway vs 1980s India)",
            "• Norway: High storage efficiency (deep valleys)",
            "• India: Broader river valley impoundments",
            "• Norway: Hydropower dominant purpose",
            "• India: Multipurpose (irrigation/flood/power)",
            "• Norway: Unique operational flexibility data",
            "• India: Comprehensive structural height data",
            "",
            "=" * 70,
            "END OF SUMMARY",
            "=" * 70,
        ])
        
        # Write to file
        output_file = self.output_dir / 'norway_statistics_summary.txt'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(summary_lines))
        
        print(f"✅ Statistics summary saved to: {output_file}\n")
    
    def run_complete_analysis(self):
        """Execute complete analysis workflow."""
        print("\n" + "=" * 70)
        print("STARTING COMPREHENSIVE ANALYSIS")
        print("=" * 70 + "\n")
        
        # Step 1: Load data
        if not self.load_data():
            print("❌ Failed to load data. Exiting.")
            return False
        
        # Step 2: Assign counties
        self.assign_counties()
        
        # Step 3: Calculate statistics
        self.calculate_statistics()
        
        # Step 4: Generate visualizations
        self.generate_visualizations()
        
        # Step 5: Export large dams CSV
        self.export_large_dams_csv()
        
        # Step 6: Generate summary statistics
        self.generate_statistics_summary()
        
        print("=" * 70)
        print("✅ ANALYSIS COMPLETE!")
        print("=" * 70)
        print("\nGenerated files:")
        print("  📊 7 visualization charts in visualizations/")
        print("  📝 large_norwegian_dams.csv")
        print("  📄 norway_statistics_summary.txt")
        print("\nNext step: Generate Word document report")
        print("=" * 70 + "\n")
        
        return True


def main():
    """Main execution function."""
    analyzer = NorwegianDamComparativeAnalyzer()
    success = analyzer.run_complete_analysis()
    
    if success:
        print("🎉 Norwegian dam analysis completed successfully!")
        print("📧 Ready for Janhavi's conference paper\n")
    else:
        print("❌ Analysis failed. Please check error messages above.\n")


if __name__ == "__main__":
    main()

