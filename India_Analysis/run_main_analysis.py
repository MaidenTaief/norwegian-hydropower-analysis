#!/usr/bin/env python3
"""
Indian Dam Analysis - Main Entry Point
======================================

Simple entry point for running the main Indian dam analysis.
This script runs the comprehensive analysis focusing on cleaned,
validated data with quality comparisons.
"""

from indian_dam_comprehensive_analysis import IndianDamComprehensiveAnalyzer

def main():
    """
    Run the main Indian dam analysis.
    
    This comprehensive analysis:
    - Focuses on cleaned, validated data (PRIMARY)
    - Includes raw data comparisons (SECONDARY)
    - Generates unified results in results/comprehensive/
    - Suitable for academic research and policy applications
    """
    print("🇮🇳 Indian Dam Infrastructure Analysis")
    print("="*50)
    print("🎯 Running comprehensive analysis with cleaned database focus")
    print("📊 Quality-validated data suitable for research and policy")
    print()
    
    analyzer = IndianDamComprehensiveAnalyzer()
    analyzer.run_comprehensive_analysis()
    
    print("\n" + "="*50)
    print("✅ ANALYSIS COMPLETE")
    print("📁 Results: results/comprehensive/")
    print("🎯 Recommendation: Use these results for reliable analysis")

if __name__ == "__main__":
    main()
