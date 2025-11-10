# Arctic Dam Risk Analysis

## Quick Start

```bash
# Step 1: Extract Arctic dams
cd 01_core_analysis
python3 arctic_dam_locator.py

# Step 2: Run risk analysis  
python3 arctic_risk_analyzer_improved.py

# Step 3: Generate figures
cd ../01_scripts/figure_generators
python3 arctic_results_visualizer_improved.py
```

## Folder Structure

- `00_data/` - Weather data (Seklima, 2015-2025)
- `01_core_analysis/` - Main scripts
- `01_scripts/` - Utilities and figure generators
- `02_documentation/` - Detailed guides
- `03_latex_report/` - LaTeX paper
- `06_outputs/` - Generated results

## Data Status

✅ Real weather data: 9 Arctic stations, 1,129 records  
✅ Real dam data: 4,953 Norwegian dams (NVE)
