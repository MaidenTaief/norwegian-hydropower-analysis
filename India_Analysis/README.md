# Indian Dam Analysis System

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![GeoPandas](https://img.shields.io/badge/GeoPandas-Enabled-orange)](https://geopandas.org)

A comprehensive Python toolkit for analyzing Indian dam infrastructure data from the Global Dam Watch (GDW) database. This project provides a complete workflow for loading, processing, analyzing, and visualizing Indian dam data with international comparison capabilities.

## 🌊 Overview

This toolkit processes Indian dam data from the Global Dam Watch database and transforms it into various formats suitable for analysis, visualization, and integration with other systems. The project handles comprehensive dam infrastructure data with 72 different attributes per dam.

## 📊 Sample Results

### Indian Dam Construction Timeline
![Construction Timeline](output/indian_dam_construction_timeline.png)

*Historical development of Indian hydropower infrastructure from colonial era to modern times, showing the post-independence construction boom.*

### Indian Dam Spatial Visualization
![Spatial Analysis](output/indian_dam_spatial_visualization.png)

*Geographic distribution of 7,097 Indian dams across the country with enhanced visibility and categorization.*

### Google Earth Integration
- **Interactive KML File**: `output/indian_dams_google_earth.kml`
- **7,097 Indian Dams**: Complete interactive map
- **Rich Descriptions**: Dam details, construction year, height, capacity, power generation

> 📁 **More Charts**: See the full collection of generated visualizations in the [`output/`](output/) directory and detailed explanations in [`INDIAN_ANALYSIS_REPORT.md`](INDIAN_ANALYSIS_REPORT.md).

## Data Files

The analysis uses the Global Dam Watch (GDW) database:

- **GDW_barriers_v1_0.shp**: Main dam database with 41,145 dams worldwide
- **GDW_reservoirs_v1_0.shp**: Reservoir data (optional)
- **Indian Filter**: 7,097 Indian dams extracted from global database

## Prerequisites

To run the code and analysis, you need a Python environment with the following libraries installed:

```bash
pip install -r requirements.txt
```

### Required Libraries:
- **pandas**: For general data manipulation and analysis
- **geopandas**: For working with geospatial data, including reading .shp files and handling geometries
- **matplotlib** and **seaborn**: For plotting and visualization
- **shapely**: For geometric operations
- **fiona**: For reading/writing spatial data formats
- **pyproj**: For coordinate reference system transformations

## Workflow Steps

### 1. Data Loading and Filtering
The initial step involves loading the GDW barriers data and filtering for Indian dams.

**Input Files**: GDW_barriers_v1_0.shp  
**Process**: Load global database and filter for COUNTRY = 'India'  
**Output**: 7,097 Indian dams with 72 attributes each

### 2. Understanding Data Content
After loading, inspect the content to understand available attributes.

**Key Columns Analyzed**:
- DAM_NAME: Dam names
- YEAR_DAM: Construction year
- DAM_HGT_M: Dam height in meters
- AREA_SKM: Reservoir area in square kilometers
- CAP_MCM: Reservoir capacity in million cubic meters
- POWER_MW: Hydropower capacity in megawatts
- RIVER: Associated river
- MAIN_USE: Primary purpose

### 3. Spatial Data Exploration
Load the geographic location and shape data from shapefiles.

**Input Files**: GDW_barriers_v1_0.shp  
**Process**: Use geopandas to read .shp files into GeoDataFrames  
**Output**: GeoDataFrames with both attributes and geometry

### 4. Temporal Analysis
Analyze construction patterns over time.

**Process**: Group dams by construction year and decade  
**Output**: Historical development patterns and trends

### 5. Spatial Analysis
Analyze geographic distribution and patterns.

**Process**: Map dam locations and categorize by various attributes  
**Output**: Geographic distribution maps and regional analysis

### 6. Export for Visualization
Export to KML format for Google Earth visualization.

**Process**: Convert to KML format with rich descriptions  
**Output Files**: indian_dams_google_earth.kml

## Usage

### Quick Start

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the analysis**:
   ```bash
   python indian_dam_analysis.py
   ```

3. **Check outputs**:
   All generated files will be saved in the `output/` directory.

4. **View analysis report**:
   See `INDIAN_ANALYSIS_REPORT.md` for detailed explanations of all charts and insights.

5. **Open in Google Earth**:
   Open `output/indian_dams_google_earth.kml` in Google Earth for interactive visualization.

### Programmatic Usage

```python
from indian_dam_analysis import IndianDamAnalyzer

# Create analyzer instance
analyzer = IndianDamAnalyzer()

# Run complete workflow
analyzer.run_complete_analysis()

# Or run individual steps
analyzer.create_construction_timeline()
analyzer.create_spatial_visualization()
analyzer.export_to_kml()
```

## Output Files

The analysis generates the following output files in the `output/` directory:

### Visualization Files
- `indian_dam_construction_timeline.png` - Historical construction analysis
- `indian_dam_spatial_visualization.png` - Geographic distribution maps

### Google Earth Files
- `indian_dams_google_earth.kml` - Interactive map for Google Earth

### Report
- `INDIAN_ANALYSIS_REPORT.md` - Comprehensive analysis report

## Data Source

The data is provided by the Global Dam Watch (GDW) database and contains comprehensive information about global dam infrastructure, with 7,097 Indian dams extracted for this analysis.

## Key Statistics

### Indian Dam Infrastructure
- **Total Dams**: 7,097 dams
- **Geographic Coverage**: Pan-India distribution
- **Data Quality**: High-quality global standard data
- **Attribute Richness**: 72 different attributes per dam

### Sample Indian Dams
| Dam Name | Year | Height (m) | Reservoir Area (km²) | Purpose |
|----------|------|------------|---------------------|---------|
| Pong Dam | 1974 | 133 | 189.3 | Multipurpose |
| Rana Pratap Sagar | 1968 | 54 | 171.1 | Irrigation |
| Gandhi Sagar | 1960 | 62 | 522.4 | Hydropower |
| Rihand | 1962 | 91 | 397.9 | Power |
| Bansagar Dam | 2006 | 67 | 383.4 | Multipurpose |

## Comparison with Norwegian Analysis

This Indian analysis complements the Norwegian hydropower analysis:

### Similarities
- **Comprehensive Coverage**: Both cover complete national infrastructure
- **Temporal Analysis**: Both include construction timeline analysis
- **Spatial Visualization**: Both provide geographic distribution mapping
- **Google Earth Export**: Both include interactive KML exports

### Differences
- **Data Source**: Norway (NVE national data) vs India (GDW global data)
- **Scale**: India (7,097 dams) vs Norway (4,953 dams)
- **Standardization**: GDW provides international comparison capabilities
- **Attribute Richness**: GDW offers more comprehensive attribute data

## Next Steps

Following these data preparation steps, you can proceed with:

1. **Further Analysis**: Analyze characteristics of dams based on attribute data
2. **Spatial Analysis**: Perform spatial analysis using the geometry data
3. **External Integration**: Integrate external data (weather, population, etc.) based on location
4. **Interactive Visualizations**: Create interactive visualizations and dashboards
5. **Machine Learning**: Apply ML techniques for pattern recognition and prediction
6. **International Comparison**: Compare with other countries using GDW data

## Troubleshooting

### Common Issues

1. **Missing dependencies**: Install all required packages using `pip install -r requirements.txt`
2. **Large file sizes**: GDW database can be large; ensure sufficient disk space
3. **CRS issues**: The script automatically handles coordinate reference system transformations
4. **Memory issues**: For large datasets, consider processing in chunks

### Error Messages

- **"Data not loaded"**: Check GDW database file paths
- **"No Indian dams found"**: Verify COUNTRY column contains 'India'
- **"geopandas not available"**: Install with `pip install geopandas`

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Global Dam Watch (GDW)**: For providing comprehensive global dam data
- **GeoPandas Community**: For excellent geospatial data processing tools
- **Python Community**: For robust data analysis and visualization libraries

---

*This analysis provides insights into one of the world's most comprehensive dam systems, offering valuable data for energy planning, environmental management, and infrastructure development decisions.* 