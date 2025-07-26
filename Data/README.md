# Data Directory

## Norwegian Hydropower Data Files

This directory should contain the Norwegian Water Resources and Energy Directorate (NVE) hydropower data files.

### Required Files

Place the following shapefile sets in this directory:

#### 1. Dam Line Data
- `Vannkraft_DamLinje.shp`
- `Vannkraft_DamLinje.shx`
- `Vannkraft_DamLinje.dbf`
- `Vannkraft_DamLinje.prj`
- `Vannkraft_DamLinje.cpg`

#### 2. Dam Point Data
- `Vannkraft_DamPunkt.shp`
- `Vannkraft_DamPunkt.shx`
- `Vannkraft_DamPunkt.dbf`
- `Vannkraft_DamPunkt.prj`
- `Vannkraft_DamPunkt.cpg`

#### 3. Reservoir Data
- `Vannkraft_Magasin.shp`
- `Vannkraft_Magasin.shx`
- `Vannkraft_Magasin.dbf`
- `Vannkraft_Magasin.prj`
- `Vannkraft_Magasin.cpg`

### Data Source

The data can be obtained from:
- **Norwegian Water Resources and Energy Directorate (NVE)**
- **Website:** https://www.nve.no/
- **Data Portal:** NVE's open data platform

### Data Description

- **Dam Lines:** Linear representations of dam structures
- **Dam Points:** Point representations of dam locations
- **Reservoirs:** Polygon representations of water reservoirs and regulated lakes

### Coordinate System

The source data uses **EPSG:25833** (UTM Zone 33N) coordinate reference system, which is automatically converted to **EPSG:4326** (WGS84) for visualization purposes.

### File Sizes

The data files are typically:
- Dam Line files: ~2-3 MB total
- Dam Point files: ~2-3 MB total  
- Reservoir files: ~80-100 MB total (large due to complex polygon geometries)

### Note

The actual data files are not included in this repository due to their size and licensing considerations. Users must obtain the data directly from NVE. 