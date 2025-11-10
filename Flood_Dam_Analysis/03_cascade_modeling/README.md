# Cascade Risk Modeling Module

## Purpose
Model dam failure cascade scenarios and their downstream impacts, addressing the critical "lives affected vs risk" component.

## Research Question
How do climate-driven floods create cascade failure risks in Norwegian dam networks, and what are the implications for mountain communities?

## Modeling Framework

### 1. Network Topology
- **Dam connectivity**: Map upstream/downstream dam relationships
- **River network analysis**: Use NetworkX to model flow paths
- **Critical path identification**: Find dams whose failure would trigger cascades

### 2. Failure Scenarios
- **Overtopping failure**: Climate-driven flood exceeds spillway capacity
- **Structural failure**: Combined climate stress + aging infrastructure
- **Cascade propagation**: One failure triggers downstream failures

### 3. Impact Assessment
- **Flood wave modeling**: Dam break flood routing
- **Population exposure**: Census data + flood zone intersection
- **Infrastructure impact**: Roads, bridges, settlements at risk
- **Economic consequences**: Damage estimation

### 4. Early Warning Systems
- **Structural Health Monitoring (SHM)**: Sensor placement optimization
- **Real-time risk assessment**: Dynamic failure probability calculation
- **Emergency response planning**: Evacuation route optimization

## Key Components

### Population Risk Analysis
```python
# For each dam failure scenario:
- Map flood inundation extent
- Intersect with population census data
- Calculate exposure by age groups, vulnerability
- Estimate evacuation time requirements
```

### Economic Impact Modeling
```python
# Infrastructure damage assessment:
- Building damage by flood depth
- Transportation network disruption
- Agricultural land flooding
- Tourism/recreation impacts
```

### SHM System Design
```python
# Sensor network optimization:
- Accelerometers for structural monitoring
- Piezometers for pore pressure
- Weather stations for climate inputs
- Communication network resilience
```

## Scripts to Develop
1. `dam_network_builder.py` - Create dam connectivity network
2. `cascade_simulator.py` - Monte Carlo cascade failure modeling
3. `population_risk_calculator.py` - Lives at risk assessment
4. `shm_optimizer.py` - Optimal sensor placement design
5. `emergency_planner.py` - Evacuation route optimization

## PhD Research Value
- **Extreme events focus**: Core CMT research theme
- **Resilience strategies**: Another core CMT theme
- **Applied relevance**: Direct benefit to Norwegian communities
- **Interdisciplinary approach**: Combines engineering, social science, emergency management
- **Innovation potential**: SHM system design for Arctic conditions

## Real-World Applications
- **NVE collaboration**: Improved dam safety protocols
- **Municipal planning**: Flood risk zoning
- **Emergency services**: Better preparedness
- **Insurance sector**: Risk-based pricing



