#!/usr/bin/env python3
"""
Indian Dam Database Smart Cleaner
=================================

Comprehensive data cleaning system for Indian dam infrastructure data from GDW database.
Implements systematic quality validation and cleaning methodology suitable for research
and policy applications.

Data Quality Issues Identified:
- Names: Only 5.1% have valid names (361/7097)
- Years: Only 16.7% have valid construction years (1185/7097)
- Heights: Only 4.6% have positive height values (328/7097)
- Power: Only 0.1% have power data (8/7097)
- River/Use: <5% have meaningful metadata

Cleaning Strategy: Multi-tier approach with progressive quality standards
"""

import geopandas as gpd
import pandas as pd
import numpy as np
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

class IndianDamSmartCleaner:
    """
    Smart data cleaning system for Indian dam database with comprehensive
    quality validation and systematic cleaning methodology.
    """
    
    def __init__(self, data_dir="../25988293/GDW_v1_0_shp/GDW_v1_0_shp"):
        self.data_dir = Path(data_dir)
        self.results_dir = Path("results/cleaned_database")
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        # Quality metrics tracking
        self.quality_report = {
            'original_count': 0,
            'cleaning_steps': [],
            'final_counts': {},
            'quality_improvements': {}
        }
        
        self.load_raw_data()
    
    def load_raw_data(self):
        """Load raw GDW data and filter for India."""
        print("🔄 Loading raw GDW database...")
        
        try:
            gdw_file = self.data_dir / "GDW_barriers_v1_0.shp"
            if not gdw_file.exists():
                print(f"❌ GDW file not found at {gdw_file}")
                return False
                
            # Load global database
            self.global_dams_gdf = gpd.read_file(gdw_file)
            print(f"✅ Loaded global database: {len(self.global_dams_gdf):,} dams")
            
            # Filter for India
            self.raw_indian_dams = self.global_dams_gdf[
                self.global_dams_gdf['COUNTRY'] == 'India'
            ].copy()
            
            self.quality_report['original_count'] = len(self.raw_indian_dams)
            print(f"✅ Filtered Indian dams: {len(self.raw_indian_dams):,} dams")
            
            # Ensure WGS84 coordinate system
            if self.raw_indian_dams.crs.to_string() != 'EPSG:4326':
                self.raw_indian_dams = self.raw_indian_dams.to_crs('EPSG:4326')
                
            return True
            
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            return False
    
    def analyze_raw_data_quality(self):
        """Comprehensive analysis of raw data quality."""
        print("\n📊 Analyzing raw data quality...")
        
        analysis = {}
        total = len(self.raw_indian_dams)
        
        # Key attributes to analyze
        attributes = {
            'DAM_NAME': 'Dam names',
            'YEAR_DAM': 'Construction years',
            'DAM_HGT_M': 'Dam heights',
            'AREA_SKM': 'Reservoir areas',
            'CAP_MCM': 'Reservoir capacities',
            'POWER_MW': 'Power generation',
            'RIVER': 'River names',
            'MAIN_USE': 'Primary usage'
        }
        
        for attr, desc in attributes.items():
            if attr in self.raw_indian_dams.columns:
                analysis[attr] = self._analyze_attribute(attr, desc, total)
        
        self.raw_quality_analysis = analysis
        self._print_quality_summary(analysis, total)
        return analysis
    
    def _analyze_attribute(self, attr, desc, total):
        """Analyze quality of a specific attribute."""
        data = self.raw_indian_dams[attr]
        
        result = {
            'description': desc,
            'total': total,
            'non_null': data.notna().sum(),
            'null_count': data.isna().sum(),
            'null_percentage': (data.isna().sum() / total) * 100
        }
        
        # Specific validation rules by attribute type
        if attr == 'YEAR_DAM':
            valid_years = data[(data >= 1800) & (data <= 2025)]
            result['valid_count'] = len(valid_years)
            result['valid_percentage'] = (len(valid_years) / total) * 100
            result['validation_rule'] = 'Years between 1800-2025'
            
        elif attr in ['DAM_HGT_M', 'AREA_SKM', 'CAP_MCM', 'POWER_MW']:
            positive_values = data[data > 0]
            result['valid_count'] = len(positive_values)
            result['valid_percentage'] = (len(positive_values) / total) * 100
            result['validation_rule'] = 'Positive values only'
            
        elif attr == 'DAM_NAME':
            valid_names = data[
                (data.notna()) & 
                (data != '') & 
                (data != 'Unknown') &
                (data.astype(str).str.strip() != '')
            ]
            result['valid_count'] = len(valid_names)
            result['valid_percentage'] = (len(valid_names) / total) * 100
            result['validation_rule'] = 'Non-empty, meaningful names'
            
        else:  # RIVER, MAIN_USE
            non_empty = data[(data.notna()) & (data != '') & (data.astype(str).str.strip() != '')]
            result['valid_count'] = len(non_empty)
            result['valid_percentage'] = (len(non_empty) / total) * 100
            result['validation_rule'] = 'Non-empty text'
        
        return result
    
    def _print_quality_summary(self, analysis, total):
        """Print comprehensive quality summary."""
        print(f"\n{'='*60}")
        print("RAW DATA QUALITY ANALYSIS")
        print(f"{'='*60}")
        print(f"Total Indian dams: {total:,}")
        print()
        
        for attr, data in analysis.items():
            print(f"{data['description']} ({attr}):")
            print(f"  Non-null values: {data['non_null']:,} ({100-data['null_percentage']:.1f}%)")
            print(f"  Valid values: {data['valid_count']:,} ({data['valid_percentage']:.1f}%)")
            print(f"  Validation rule: {data['validation_rule']}")
            print()
    
    def design_cleaning_tiers(self):
        """Design multi-tier cleaning approach based on quality analysis."""
        print("🎯 Designing multi-tier cleaning approach...")
        
        # Tier 1: Research Grade (Highest Quality)
        self.tier1_criteria = {
            'name': 'Research Grade Database',
            'description': 'Highest quality data suitable for academic research and policy',
            'criteria': {
                'DAM_NAME': 'Must have valid, meaningful name',
                'YEAR_DAM': 'Must have valid construction year (1800-2025)',
                'physical_data': 'Must have at least 2 of: height, area, capacity',
                'completeness': 'High attribute completeness'
            }
        }
        
        # Tier 2: Analysis Grade (Good Quality)
        self.tier2_criteria = {
            'name': 'Analysis Grade Database',
            'description': 'Good quality data suitable for general analysis',
            'criteria': {
                'YEAR_DAM': 'Must have valid construction year (1800-2025)',
                'physical_data': 'Must have at least 1 of: height, area, capacity',
                'geographic': 'Must have valid geographic coordinates'
            }
        }
        
        # Tier 3: Basic Grade (Usable Quality)
        self.tier3_criteria = {
            'name': 'Basic Grade Database',
            'description': 'Basic quality data for overview analysis',
            'criteria': {
                'geographic': 'Must have valid geographic coordinates',
                'exists': 'Must be a real dam record (not placeholder)'
            }
        }
        
        print("✅ Designed 3-tier cleaning approach:")
        print(f"   Tier 1: {self.tier1_criteria['name']}")
        print(f"   Tier 2: {self.tier2_criteria['name']}")
        print(f"   Tier 3: {self.tier3_criteria['name']}")
    
    def apply_tier1_cleaning(self):
        """Apply Tier 1 cleaning - Research Grade."""
        print("\n🔬 Applying Tier 1 Cleaning (Research Grade)...")
        
        data = self.raw_indian_dams.copy()
        original_count = len(data)
        
        # Step 1: Valid names
        data = data[
            (data['DAM_NAME'].notna()) & 
            (data['DAM_NAME'] != '') & 
            (data['DAM_NAME'] != 'Unknown') &
            (data['DAM_NAME'].astype(str).str.strip() != '')
        ].copy()
        step1_count = len(data)
        
        # Step 2: Valid construction years
        data = data[
            (data['YEAR_DAM'] >= 1800) & 
            (data['YEAR_DAM'] <= 2025)
        ].copy()
        step2_count = len(data)
        
        # Step 3: Must have at least 2 physical attributes
        data['physical_count'] = (
            (data['DAM_HGT_M'] > 0).astype(int) +
            (data['AREA_SKM'] > 0).astype(int) +
            (data['CAP_MCM'] > 0).astype(int)
        )
        data = data[data['physical_count'] >= 2].copy()
        step3_count = len(data)
        
        # Step 4: Clean up physical values (remove extreme outliers)
        # Height: reasonable range 5-300m
        data = data[(data['DAM_HGT_M'] <= 0) | ((data['DAM_HGT_M'] >= 5) & (data['DAM_HGT_M'] <= 300))].copy()
        
        # Area: reasonable range 0.1-2000 km²
        data = data[(data['AREA_SKM'] <= 0) | ((data['AREA_SKM'] >= 0.1) & (data['AREA_SKM'] <= 2000))].copy()
        
        # Capacity: reasonable range 1-50000 MCM
        data = data[(data['CAP_MCM'] <= 0) | ((data['CAP_MCM'] >= 1) & (data['CAP_MCM'] <= 50000))].copy()
        
        step4_count = len(data)
        
        self.tier1_cleaned = data.drop(columns=['physical_count'])
        
        # Track cleaning steps
        cleaning_steps = [
            {'step': 'Valid dam names', 'remaining': step1_count, 'removed': original_count - step1_count},
            {'step': 'Valid construction years', 'remaining': step2_count, 'removed': step1_count - step2_count},
            {'step': 'Minimum 2 physical attributes', 'remaining': step3_count, 'removed': step2_count - step3_count},
            {'step': 'Remove extreme outliers', 'remaining': step4_count, 'removed': step3_count - step4_count}
        ]
        
        self.quality_report['cleaning_steps'].extend([
            f"Tier 1 Research Grade: {original_count:,} → {step4_count:,} dams"
        ])
        
        print(f"✅ Tier 1 Complete: {original_count:,} → {step4_count:,} dams ({(step4_count/original_count)*100:.1f}%)")
        for step in cleaning_steps:
            print(f"   {step['step']}: -{step['removed']:,} → {step['remaining']:,} remaining")
        
        return self.tier1_cleaned
    
    def apply_tier2_cleaning(self):
        """Apply Tier 2 cleaning - Analysis Grade."""
        print("\n📊 Applying Tier 2 Cleaning (Analysis Grade)...")
        
        data = self.raw_indian_dams.copy()
        original_count = len(data)
        
        # Step 1: Valid construction years
        data = data[
            (data['YEAR_DAM'] >= 1800) & 
            (data['YEAR_DAM'] <= 2025)
        ].copy()
        step1_count = len(data)
        
        # Step 2: Must have at least 1 physical attribute
        data['has_physical'] = (
            (data['DAM_HGT_M'] > 0) |
            (data['AREA_SKM'] > 0) |
            (data['CAP_MCM'] > 0)
        )
        data = data[data['has_physical']].copy()
        step2_count = len(data)
        
        # Step 3: Clean outliers (more lenient than Tier 1)
        # Height: 1-400m
        data = data[(data['DAM_HGT_M'] <= 0) | ((data['DAM_HGT_M'] >= 1) & (data['DAM_HGT_M'] <= 400))].copy()
        
        # Area: 0.01-3000 km²
        data = data[(data['AREA_SKM'] <= 0) | ((data['AREA_SKM'] >= 0.01) & (data['AREA_SKM'] <= 3000))].copy()
        
        # Capacity: 0.1-100000 MCM
        data = data[(data['CAP_MCM'] <= 0) | ((data['CAP_MCM'] >= 0.1) & (data['CAP_MCM'] <= 100000))].copy()
        
        step3_count = len(data)
        
        self.tier2_cleaned = data.drop(columns=['has_physical'])
        
        print(f"✅ Tier 2 Complete: {original_count:,} → {step3_count:,} dams ({(step3_count/original_count)*100:.1f}%)")
        return self.tier2_cleaned
    
    def apply_tier3_cleaning(self):
        """Apply Tier 3 cleaning - Basic Grade."""
        print("\n🗺️ Applying Tier 3 Cleaning (Basic Grade)...")
        
        data = self.raw_indian_dams.copy()
        original_count = len(data)
        
        # Step 1: Must have valid geographic coordinates
        data = data[
            (data.geometry.notna()) &
            (data.geometry.x.between(68, 98)) &  # India longitude range
            (data.geometry.y.between(6, 38))     # India latitude range
        ].copy()
        step1_count = len(data)
        
        # Step 2: Must have some meaningful data (not all placeholder)
        data['has_some_data'] = (
            (data['DAM_NAME'].notna() & (data['DAM_NAME'] != '') & (data['DAM_NAME'] != 'Unknown')) |
            ((data['YEAR_DAM'] >= 1800) & (data['YEAR_DAM'] <= 2025)) |
            (data['DAM_HGT_M'] > 0) |
            (data['AREA_SKM'] > 0) |
            (data['CAP_MCM'] > 0)
        )
        data = data[data['has_some_data']].copy()
        step2_count = len(data)
        
        self.tier3_cleaned = data.drop(columns=['has_some_data'])
        
        print(f"✅ Tier 3 Complete: {original_count:,} → {step2_count:,} dams ({(step2_count/original_count)*100:.1f}%)")
        return self.tier3_cleaned
    
    def generate_quality_summary(self):
        """Generate comprehensive quality improvement summary."""
        print("\n📈 Generating quality improvement summary...")
        
        original_total = len(self.raw_indian_dams)
        
        # Calculate final counts
        tier1_count = len(self.tier1_cleaned) if hasattr(self, 'tier1_cleaned') else 0
        tier2_count = len(self.tier2_cleaned) if hasattr(self, 'tier2_cleaned') else 0
        tier3_count = len(self.tier3_cleaned) if hasattr(self, 'tier3_cleaned') else 0
        
        self.quality_report['final_counts'] = {
            'original': original_total,
            'tier1_research': tier1_count,
            'tier2_analysis': tier2_count,
            'tier3_basic': tier3_count
        }
        
        # Calculate quality improvements for each tier
        for tier, data in [('tier1', self.tier1_cleaned), ('tier2', self.tier2_cleaned), ('tier3', self.tier3_cleaned)]:
            if len(data) > 0:
                improvements = {}
                
                # Name completeness
                valid_names = len(data[
                    (data['DAM_NAME'].notna()) & 
                    (data['DAM_NAME'] != '') & 
                    (data['DAM_NAME'] != 'Unknown')
                ])
                improvements['name_completeness'] = (valid_names / len(data)) * 100
                
                # Year validity
                valid_years = len(data[(data['YEAR_DAM'] >= 1800) & (data['YEAR_DAM'] <= 2025)])
                improvements['year_validity'] = (valid_years / len(data)) * 100
                
                # Physical data completeness
                has_height = (data['DAM_HGT_M'] > 0).sum()
                has_area = (data['AREA_SKM'] > 0).sum()
                has_capacity = (data['CAP_MCM'] > 0).sum()
                improvements['height_completeness'] = (has_height / len(data)) * 100
                improvements['area_completeness'] = (has_area / len(data)) * 100
                improvements['capacity_completeness'] = (has_capacity / len(data)) * 100
                
                self.quality_report['quality_improvements'][tier] = improvements
        
        self._print_final_summary()
    
    def _print_final_summary(self):
        """Print comprehensive final summary."""
        print(f"\n{'='*70}")
        print("COMPREHENSIVE CLEANING SUMMARY")
        print(f"{'='*70}")
        
        original = self.quality_report['final_counts']['original']
        
        print(f"Original Database: {original:,} Indian dams")
        print()
        
        print("Cleaned Database Tiers:")
        print(f"  Tier 1 (Research Grade): {self.quality_report['final_counts']['tier1_research']:,} dams ({(self.quality_report['final_counts']['tier1_research']/original)*100:.1f}%)")
        print(f"  Tier 2 (Analysis Grade): {self.quality_report['final_counts']['tier2_analysis']:,} dams ({(self.quality_report['final_counts']['tier2_analysis']/original)*100:.1f}%)")
        print(f"  Tier 3 (Basic Grade):    {self.quality_report['final_counts']['tier3_basic']:,} dams ({(self.quality_report['final_counts']['tier3_basic']/original)*100:.1f}%)")
        print()
        
        print("Quality Improvements (Tier 1 Research Grade):")
        if 'tier1' in self.quality_report['quality_improvements']:
            t1 = self.quality_report['quality_improvements']['tier1']
            print(f"  Name Completeness: {t1['name_completeness']:.1f}%")
            print(f"  Year Validity: {t1['year_validity']:.1f}%")
            print(f"  Height Data: {t1['height_completeness']:.1f}%")
            print(f"  Area Data: {t1['area_completeness']:.1f}%")
            print(f"  Capacity Data: {t1['capacity_completeness']:.1f}%")
    
    def save_cleaned_databases(self):
        """Save all cleaned database tiers."""
        print("\n💾 Saving cleaned databases...")
        
        # Save each tier
        tiers = [
            ('tier1_research_grade', self.tier1_cleaned, 'Research Grade'),
            ('tier2_analysis_grade', self.tier2_cleaned, 'Analysis Grade'),
            ('tier3_basic_grade', self.tier3_cleaned, 'Basic Grade')
        ]
        
        for filename, data, description in tiers:
            # Save as shapefile
            shp_path = self.results_dir / f"{filename}.shp"
            data.to_file(shp_path)
            
            # Save as CSV (without geometry)
            csv_path = self.results_dir / f"{filename}.csv"
            data_csv = data.drop(columns=['geometry'])
            data_csv.to_csv(csv_path, index=False)
            
            print(f"✅ Saved {description}: {len(data):,} dams")
            print(f"   Shapefile: {shp_path}")
            print(f"   CSV: {csv_path}")
        
        # Save quality report
        report_path = self.results_dir / "data_cleaning_report.txt"
        with open(report_path, 'w') as f:
            f.write("Indian Dam Database - Data Cleaning Report\n")
            f.write("=" * 50 + "\n\n")
            
            f.write(f"Original Database: {self.quality_report['final_counts']['original']:,} dams\n\n")
            
            f.write("Cleaned Database Results:\n")
            for tier, count in self.quality_report['final_counts'].items():
                if tier != 'original':
                    f.write(f"  {tier}: {count:,} dams\n")
            
            f.write("\nCleaning Methodology:\n")
            for step in self.quality_report['cleaning_steps']:
                f.write(f"  {step}\n")
        
        print(f"✅ Saved cleaning report: {report_path}")
    
    def run_complete_smart_cleaning(self):
        """Run complete smart cleaning process."""
        print("🚀 Starting Comprehensive Smart Cleaning Process")
        print("=" * 60)
        
        # Step 1: Analyze raw data quality
        self.analyze_raw_data_quality()
        
        # Step 2: Design cleaning tiers
        self.design_cleaning_tiers()
        
        # Step 3: Apply all cleaning tiers
        self.apply_tier1_cleaning()
        self.apply_tier2_cleaning()
        self.apply_tier3_cleaning()
        
        # Step 4: Generate quality summary
        self.generate_quality_summary()
        
        # Step 5: Save cleaned databases
        self.save_cleaned_databases()
        
        print("\n🎉 Smart Cleaning Process Completed Successfully!")
        print(f"📁 Results saved in: {self.results_dir}")
        print("📊 Three cleaned database tiers available:")
        print("   • Research Grade: Highest quality for academic research")
        print("   • Analysis Grade: Good quality for general analysis")
        print("   • Basic Grade: Usable quality for overview studies")

def main():
    """Run the complete smart cleaning process."""
    cleaner = IndianDamSmartCleaner()
    cleaner.run_complete_smart_cleaning()

if __name__ == "__main__":
    main()
