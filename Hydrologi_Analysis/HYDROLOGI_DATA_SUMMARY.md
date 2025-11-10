# Hydrologi Measurement Station Data Summary

**Generated:** 2025-08-17 22:56:39

## Dataset Overview

- **Source file:** Hydrologi_MaleserieMalestasjon.shp
- **Total stations:** 25,609
- **Columns:** 23
- **Geographic coverage:** Norwegian hydrological measurement stations

## Column Information

| Column | Data Type | Non-null Count | Description |
|--------|-----------|----------------|-------------|
| objType | object | 25,609 | Station type |
| stSamletID | object | 25,609 | Data field (description to be determined) |
| stID | object | 25,609 | Data field (description to be determined) |
| stNavn | object | 25,609 | Station name |
| gruppe | float64 | 25,557 | Data field (description to be determined) |
| stParaKode | int64 | 25,609 | Data field (description to be determined) |
| stParam | object | 25,609 | Data field (description to be determined) |
| stStatus | int64 | 25,609 | Data field (description to be determined) |
| sanntid | object | 6,045 | Data field (description to be determined) |
| obsSted | object | 19,383 | Data field (description to be determined) |
| versjonNr | int64 | 25,609 | Data field (description to be determined) |
| flomserie | float64 | 545 | Data field (description to be determined) |
| flomserieP | float64 | 545 | Data field (description to be determined) |
| feltNr | float64 | 10,814 | Data field (description to be determined) |
| vassdragNr | object | 25,568 | Watercourse |
| hierarki | object | 25,564 | Data field (description to be determined) |
| hydrOmr | int64 | 25,609 | Data field (description to be determined) |
| serieFra | int64 | 25,609 | Data field (description to be determined) |
| serieTil | int64 | 25,609 | Data field (description to be determined) |
| uttakDato | object | 25,609 | Data field (description to be determined) |
| ekspType | object | 25,609 | Station type |
| longitude | float64 | 25,609 | Longitude coordinate |
| latitude | float64 | 25,609 | Latitude coordinate |

## Data Quality

| Column | Missing Values | Missing % |
|--------|----------------|----------|
| objType | 0 | 0.0% |
| stSamletID | 0 | 0.0% |
| stID | 0 | 0.0% |
| stNavn | 0 | 0.0% |
| gruppe | 52 | 0.2% |
| stParaKode | 0 | 0.0% |
| stParam | 0 | 0.0% |
| stStatus | 0 | 0.0% |
| sanntid | 19,564 | 76.4% |
| obsSted | 6,226 | 24.3% |
| versjonNr | 0 | 0.0% |
| flomserie | 25,064 | 97.9% |
| flomserieP | 25,064 | 97.9% |
| feltNr | 14,795 | 57.8% |
| vassdragNr | 41 | 0.2% |
| hierarki | 45 | 0.2% |
| hydrOmr | 0 | 0.0% |
| serieFra | 0 | 0.0% |
| serieTil | 0 | 0.0% |
| uttakDato | 0 | 0.0% |
| ekspType | 0 | 0.0% |
| longitude | 0 | 0.0% |
| latitude | 0 | 0.0% |

## Geographic Coverage

- **Longitude range:** -661108.000000 to 6734218.000000
- **Latitude range:** 31524.000000 to 8794015.000000

## Sample Data

```
               objType    stSamletID       stID                stNavn  gruppe  stParaKode     stParam  stStatus sanntid                 obsSted  versjonNr  flomserie  flomserieP  feltNr vassdragNr                    hierarki  hydrOmr  serieFra  serieTil   uttakDato                  ekspType  longitude   latitude
0  HydrologiskTidserie  021200061000   212.61.0             Altafjord     1.0        1000   Vannstand         0    None   Elv - naturlig profil          1        NaN         NaN     NaN     212.52  Altavassdraget/Altafjorden       22  19800101  19900101  2025-08-17  NVEs nedlastningsløsning   816341.0  7786428.0
1  HydrologiskTidserie  023600011000   236.11.0                Gednje     1.0        1000   Vannstand         1       J                 Magasin          1        NaN         NaN     NaN      236.C        Kongsfjordvassdraget       22  20100920         0  2025-08-17  NVEs nedlastningsløsning  1020926.0  7885579.0
2  HydrologiskTidserie  001600232020  16.232.20       Vm 5 Olmostjern     1.0        1000   Vannstand         0    None   Elv - naturlig profil          2        NaN         NaN     NaN    016.H5Z   Grosetåe/Skiensvassdraget        5  19700915  19980420  2025-08-17  NVEs nedlastningsløsning   124643.0  6652383.0
3  HydrologiskTidserie  003800006000     38.6.0  Rødneelv ved Sandeid     2.0        1050      Tilsig         0    None   Elv - naturlig profil          1        NaN         NaN     NaN     038.3C                 Øvstabøelva        9  19821101         0  2025-08-17  NVEs nedlastningsløsning   -13714.0  6639017.0
4  HydrologiskTidserie  006100014000    61.14.0     Dale II kraftverk     8.0        1001  Vannføring         1    None  Turbin/rør i kraftverk          0        NaN         NaN     NaN      061.A         Bergsdalsvassdraget       10  19630101         0  2025-08-17  NVEs nedlastningsløsning    -1694.0  6751332.0
```

## Usage

This CSV file can be used for:
- Hydrological station analysis
- Geographic mapping of measurement networks
- Integration with weather and climate data
- Statistical analysis of measurement station distribution
