# Database Setup Guide

This guide explains how to obtain the required databases for running the Norwegian and Indian dam analyses.

## 📊 Required Databases

### 🇳🇴 Norwegian Data (NVE)
**Source**: Norwegian Water Resources and Energy Directorate (NVE)  
**Website**: https://www.nve.no/  
**Data**: Norwegian hydropower infrastructure data

#### How to Download:
1. Visit the NVE website: https://www.nve.no/
2. Navigate to "Data og statistikk" (Data and Statistics)
3. Look for "Vannkraft" (Hydropower) data
4. Download the following files:
   - `Vannkraft_DamLinje.shp` (Dam lines)
   - `Vannkraft_DamPunkt.shp` (Dam points)
   - `Vannkraft_Magasin.shp` (Reservoirs)
   - Associated `.dbf`, `.shx`, `.prj` files

#### Setup Instructions:
```bash
# Create the data directory
mkdir -p Norway_Analysis/Data

# Place downloaded files in Norway_Analysis/Data/
# Your structure should look like:
Norway_Analysis/Data/
├── Vannkraft_DamLinje.shp
├── Vannkraft_DamLinje.dbf
├── Vannkraft_DamLinje.shx
├── Vannkraft_DamLinje.prj
├── Vannkraft_DamPunkt.shp
├── Vannkraft_DamPunkt.dbf
├── Vannkraft_DamPunkt.shx
├── Vannkraft_DamPunkt.prj
├── Vannkraft_Magasin.shp
├── Vannkraft_Magasin.dbf
├── Vannkraft_Magasin.shx
└── Vannkraft_Magasin.prj
```

### 🇮🇳 Indian Data (GDW)
**Source**: Global Dam Watch (GDW)  
**Website**: https://globaldamwatch.org/  
**Data**: Global dam infrastructure database

#### How to Download:
1. Visit the Global Dam Watch website: https://globaldamwatch.org/
2. Navigate to "Data" or "Downloads" section
3. Download the GDW v1.0 database
4. Extract the files to get:
   - `GDW_barriers_v1_0.shp` (Main dam database)
   - `GDW_reservoirs_v1_0.shp` (Reservoir data)
   - Associated files (`.dbf`, `.shx`, `.prj`, etc.)

#### Setup Instructions:
```bash
# Create the GDW directory
mkdir -p 25988293/GDW_v1_0_shp/GDW_v1_0_shp

# Place downloaded files in 25988293/GDW_v1_0_shp/GDW_v1_0_shp/
# Your structure should look like:
25988293/GDW_v1_0_shp/GDW_v1_0_shp/
├── GDW_barriers_v1_0.shp
├── GDW_barriers_v1_0.dbf
├── GDW_barriers_v1_0.shx
├── GDW_barriers_v1_0.prj
├── GDW_reservoirs_v1_0.shp
├── GDW_reservoirs_v1_0.dbf
├── GDW_reservoirs_v1_0.shx
└── GDW_reservoirs_v1_0.prj
```

## 🚀 Running the Analyses

### Norwegian Analysis
```bash
cd Norway_Analysis
pip install -r requirements.txt
python norwegian_hydropower_analysis.py
```

### Indian Analysis
```bash
cd India_Analysis
pip install -r requirements.txt
python indian_dam_analysis.py
```

## 📋 Data Requirements

### Norwegian Analysis Requirements:
- **Dam Lines**: 4,813 linear structures
- **Dam Points**: 4,953 point locations  
- **Reservoirs**: 2,997 water bodies
- **Format**: ESRI Shapefile (.shp, .dbf, .shx, .prj)

### Indian Analysis Requirements:
- **Dams**: 7,097 Indian dams (from 41,145 global dams)
- **Attributes**: 72 different attributes per dam
- **Format**: ESRI Shapefile (.shp, .dbf, .shx, .prj)

## 🔍 Verification

After downloading the databases, verify they're working:

### Test Norwegian Data:
```python
import geopandas as gpd

# Test Norwegian data
gdf = gpd.read_file("Norway_Analysis/Data/Vannkraft_DamPunkt.shp")
print(f"Norwegian dams loaded: {len(gdf)}")
```

### Test Indian Data:
```python
import geopandas as gpd

# Test Indian data
gdf = gpd.read_file("25988293/GDW_v1_0_shp/GDW_v1_0_shp/GDW_barriers_v1_0.shp")
india_dams = gdf[gdf['COUNTRY'] == 'India']
print(f"Indian dams found: {len(india_dams)}")
```

## ⚠️ Important Notes

1. **Large Files**: These databases are large (100MB+ each)
2. **Download Time**: May take several minutes depending on your connection
3. **Storage**: Ensure you have sufficient disk space
4. **Updates**: Check for newer versions of the databases periodically
5. **License**: Respect the terms of use for each data source

## 🆘 Troubleshooting

### Common Issues:
1. **"File not found"**: Ensure files are in the correct directories
2. **"Permission denied"**: Check file permissions
3. **"Invalid format"**: Ensure all associated files (.dbf, .shx, .prj) are present
4. **"Memory error"**: These are large datasets; ensure sufficient RAM

### Getting Help:
- **NVE Data**: Contact NVE directly for data access issues
- **GDW Data**: Check Global Dam Watch documentation
- **Analysis Issues**: Check the individual README files in each analysis folder

---

*This guide ensures users can properly set up the required databases to run both Norwegian and Indian dam analyses.* 