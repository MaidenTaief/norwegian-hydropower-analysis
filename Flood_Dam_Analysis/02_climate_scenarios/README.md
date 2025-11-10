# Climate Scenarios Module

## Purpose
Model climate change impacts on flood-dam interactions using IPCC projections and Norwegian climate data.

## Research Framework
Aligns with Bergen PhD requirements:
- Climate-driven hydrological modeling
- Future flood hazard projections under different scenarios
- Long-term risk assessment (past centuries to end of century)

## Analysis Components

### 1. IPCC Scenario Integration
- **SSP1-2.6**: Low emissions scenario
- **SSP2-4.5**: Intermediate scenario  
- **SSP3-7.0**: High emissions scenario
- **SSP5-8.5**: Very high emissions scenario

### 2. Norwegian Climate Projections
- Temperature increases by latitude (Arctic amplification)
- Precipitation pattern changes
- Extreme event frequency/intensity changes
- Snow/rain transitions in mountain regions

### 3. Flood Regime Changes
- Seasonal shift analysis (spring snowmelt vs autumn storms)
- Peak discharge projections
- Flood frequency curve adjustments
- Return period recalculation (100yr → 50yr under climate change)

### 4. Dam Impact Assessment
- Spillway capacity adequacy under new flood regimes
- Reservoir management challenges
- Infrastructure adaptation requirements

## Key Outputs
1. **Climate-adjusted flood maps** for 2050, 2070, 2100
2. **Risk transition matrices** (current → future flood exposure)
3. **Dam vulnerability rankings** under climate scenarios
4. **Adaptation timeline recommendations**

## Scripts to Develop
1. `ipcc_downscaler.py` - Downscale global projections to Norwegian catchments
2. `flood_frequency_adjuster.py` - Recalculate return periods under climate change
3. `scenario_comparator.py` - Multi-scenario risk assessment
4. `adaptation_prioritizer.py` - Rank dams by climate vulnerability

## PhD Application Value
- **Future risk projections**: Core requirement for Bergen position
- **Climate model integration**: Shows technical modeling skills
- **Mountain hydrology focus**: Perfectly aligned with CMT research themes
- **Practical applications**: Supports NVE collaboration goals
