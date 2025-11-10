#!/usr/bin/env python3
"""
MERGE SEKLIMA CSV FILES
=======================
Merges the two downloaded Seklima CSV files into one complete Arctic_table.csv
"""

import pandas as pd
import sys
from pathlib import Path

def merge_seklima_files(file1_path, file2_path, output_path):
    """
    Merge two Seklima CSV files with different parameters
    
    Args:
        file1_path: Path to temperature/precipitation CSV
        file2_path: Path to wind/snow CSV
        output_path: Path to save merged CSV
    """
    
    print("🔄 MERGING SEKLIMA DATA FILES")
    print("="*60)
    
    # Read both files with semicolon separator
    print(f"\n📂 Reading file 1: {file1_path}")
    df1 = pd.read_csv(file1_path, sep=';', encoding='utf-8')
    print(f"   ✅ Loaded {len(df1)} records")
    print(f"   📊 Columns: {', '.join(df1.columns)}")
    
    print(f"\n📂 Reading file 2: {file2_path}")
    df2 = pd.read_csv(file2_path, sep=';', encoding='utf-8')
    print(f"   ✅ Loaded {len(df2)} records")
    print(f"   📊 Columns: {', '.join(df2.columns)}")
    
    # Merge on common columns: Name, Station, Time
    print("\n🔗 Merging files on: Name, Station, Time(norwegian mean time)")
    
    merged_df = pd.merge(
        df1, 
        df2,
        on=['Name', 'Station', 'Time(norwegian mean time)'],
        how='outer',  # Keep all records from both files
        suffixes=('', '_dup')  # Avoid duplicate column names
    )
    
    print(f"   ✅ Merged successfully: {len(merged_df)} records")
    print(f"   📊 Total columns: {len(merged_df.columns)}")
    
    # Show merged data statistics
    print("\n📈 MERGED DATA SUMMARY:")
    print(f"   • Stations: {merged_df['Station'].nunique()} unique")
    print(f"   • Station names: {', '.join(merged_df['Name'].unique())}")
    print(f"   • Date range: {merged_df['Time(norwegian mean time)'].min()} to {merged_df['Time(norwegian mean time)'].max()}")
    print(f"   • Total records: {len(merged_df)}")
    
    # Check for missing data
    print("\n🔍 DATA QUALITY CHECK:")
    for col in merged_df.columns:
        if col not in ['Name', 'Station', 'Time(norwegian mean time)']:
            missing_pct = (merged_df[col].isna().sum() / len(merged_df)) * 100
            if missing_pct > 0:
                print(f"   ⚠️  {col}: {missing_pct:.1f}% missing")
            else:
                print(f"   ✅ {col}: Complete")
    
    # Show column list
    print("\n📋 FINAL COLUMNS IN MERGED FILE:")
    for i, col in enumerate(merged_df.columns, 1):
        print(f"   {i}. {col}")
    
    # Save merged file
    print(f"\n💾 Saving merged data to: {output_path}")
    merged_df.to_csv(output_path, sep=';', index=False, encoding='utf-8')
    print(f"   ✅ Saved successfully!")
    
    # Show sample data
    print("\n📊 SAMPLE OF MERGED DATA (First 5 rows):")
    print(merged_df.head().to_string())
    
    return merged_df

if __name__ == "__main__":
    # File paths
    downloads = Path.home() / "Downloads"
    file1 = downloads / "table.csv"
    file2 = downloads / "table (1).csv"
    output = Path(__file__).parent / "Arctic_table.csv"
    
    # Check if files exist
    if not file1.exists():
        print(f"❌ ERROR: File not found: {file1}")
        sys.exit(1)
    
    if not file2.exists():
        print(f"❌ ERROR: File not found: {file2}")
        sys.exit(1)
    
    # Merge files
    try:
        merged_df = merge_seklima_files(file1, file2, output)
        
        print("\n" + "="*60)
        print("✅ SUCCESS! Arctic_table.csv is ready!")
        print(f"📁 Location: {output}")
        print(f"📊 Total records: {len(merged_df)}")
        print(f"🎯 Ready for Arctic dam risk analysis!")
        print("="*60)
        
        print("\n🚀 NEXT STEPS:")
        print("   1. Run: python3 arctic_dam_locator.py")
        print("   2. Run: python3 arctic_risk_analyzer_improved.py")
        print("   3. Generate real visualizations!")
        
    except Exception as e:
        print(f"\n❌ ERROR during merge: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

