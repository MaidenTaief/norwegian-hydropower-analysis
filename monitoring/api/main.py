#!/usr/bin/env python3
"""
Norwegian Dam Health Monitoring - FastAPI Backend
================================================

Complete REST API for real-time Norwegian dam health monitoring
- Live data from Norwegian government APIs
- TimescaleDB integration for time-series data
- Health scoring with ML integration
- Real-time alerts and notifications
- Professional monitoring dashboard support

API Documentation: http://localhost:8000/docs
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import asyncpg
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
import os
import json
import logging
from pathlib import Path
import uvicorn
from pydantic import BaseModel, Field
from contextlib import asynccontextmanager

# Import our Norwegian APIs
from api.norwegian_apis import HealthMonitoringAPI

# Import failure analysis components
from api.failure_endpoints import failure_router
from api.failure_analysis import integrate_failure_analysis

# Import ML risk prediction components
from api.ml_risk_prediction import DamRiskPredictor

# Import SHM technology components
from api.shm_technologies import IntegratedSHMSystem, create_shm_tables

# Import Arctic risk analysis components
from api.arctic_risk_analyzer import ArcticRiskAnalyzer, create_arctic_tables

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pydantic models for API responses
class DamInfo(BaseModel):
    dam_id: int
    nve_dam_nr: Optional[str]
    dam_name: Optional[str]
    municipality: Optional[str]
    county: Optional[str]
    owner: Optional[str]
    construction_year: Optional[int]
    dam_height_m: Optional[float]
    status: str
    risk_level: str
    latitude: Optional[float]
    longitude: Optional[float]

class HealthScore(BaseModel):
    dam_id: int
    dam_name: Optional[str]
    timestamp: datetime
    overall_score: float
    structural_score: Optional[float]
    operational_score: Optional[float]
    environmental_score: Optional[float]
    safety_score: Optional[float]
    confidence_level: Optional[float]

class WeatherReading(BaseModel):
    dam_id: int
    timestamp: datetime
    temperature_c: Optional[float]
    precipitation_mm: Optional[float]
    wind_speed_ms: Optional[float]
    wind_direction: Optional[float]
    humidity_percent: Optional[float]
    pressure_hpa: Optional[float]
    snow_depth_cm: Optional[float]
    data_source: str

class Alert(BaseModel):
    alert_id: int
    dam_id: int
    dam_name: Optional[str]
    alert_type: str
    severity: str
    title: str
    description: Optional[str]
    created_at: datetime
    status: str
    hours_active: Optional[float]

class SensorReading(BaseModel):
    sensor_id: int
    dam_id: int
    sensor_type: str
    timestamp: datetime
    value: float
    unit: str
    quality_score: Optional[float]

class DamOverview(BaseModel):
    dam_id: int
    dam_name: Optional[str]
    municipality: Optional[str]
    county: Optional[str]
    risk_level: str
    health_score: Optional[float]
    last_health_update: Optional[datetime]
    active_alerts: int
    inspection_status: str

class MonitoringStats(BaseModel):
    total_dams: int
    active_dams: int
    critical_alerts: int
    average_health_score: float
    data_points_last_24h: int
    last_update: datetime

# New Pydantic models for advanced features

class MLRiskPrediction(BaseModel):
    dam_id: int
    risk_score: float
    risk_level: str
    failure_probability: float
    most_likely_failure_type: Optional[str]
    predictions: Dict[str, float]
    recommended_actions: List[str]
    confidence: float

class ArcticRiskAssessment(BaseModel):
    dam_id: int
    latitude: float
    is_arctic: bool
    overall_arctic_risk: float
    permafrost_risk: Dict[str, Any]
    ice_dam_risk: Dict[str, Any]
    freeze_thaw_risk: Dict[str, Any]
    climate_change_impact: Dict[str, Any]
    mitigation_measures: List[str]

class SHMAssessment(BaseModel):
    dam_id: int
    timestamp: str
    fem_analysis: Dict[str, Any]
    fiber_optic_analysis: Dict[str, Any]
    drone_inspection: Dict[str, Any]
    integrated_health_score: float
    recommendations: List[str]

class MLModelPerformance(BaseModel):
    model_name: str
    r2_score: float
    mae: float
    mse: float
    training_date: Optional[str]

# Global variables
db_pool = None
monitoring_api = None
monitoring_task = None
ml_predictor = None
arctic_analyzer = None
shm_system = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    await startup_event()
    yield
    # Shutdown
    await shutdown_event()

# Initialize FastAPI app
app = FastAPI(
    title="Norwegian Dam Health Monitoring API",
    description="Real-time monitoring system for Norwegian hydropower infrastructure",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include failure analysis router
app.include_router(failure_router)

async def startup_event():
    """Initialize database connection and monitoring APIs"""
    global db_pool, monitoring_api, monitoring_task
    
    try:
        # Database connection
        DATABASE_URL = (
            f"postgresql://dam_monitor_app:"
            f"{os.getenv('POSTGRES_PASSWORD', 'dam_monitor_2024')}"
            f"@timescaledb:5432/postgres"
        )
        
        db_pool = await asyncpg.create_pool(
            DATABASE_URL,
            min_size=5,
            max_size=20,
            command_timeout=60
        )
        
        logger.info("✅ Database connection established")
        
        # Initialize Norwegian APIs
        frost_client_id = os.getenv('FROST_CLIENT_ID')
        sentinel_user = os.getenv('SENTINEL_USER')
        sentinel_pass = os.getenv('SENTINEL_PASS')
        
        if all([frost_client_id, sentinel_user, sentinel_pass]):
            monitoring_api = HealthMonitoringAPI(frost_client_id, sentinel_user, sentinel_pass)
            logger.info("✅ Norwegian APIs initialized")
            
            # Start background monitoring task
            monitoring_task = asyncio.create_task(background_monitoring())
            logger.info("✅ Background monitoring started")
        else:
            logger.warning("⚠️ Some API credentials missing - monitoring limited")
        
        # Initialize failure analysis system
        try:
            failure_result = await integrate_failure_analysis(db_pool)
            if failure_result['status'] == 'success':
                logger.info("✅ Failure analysis system initialized")
            else:
                logger.warning(f"⚠️ Failure analysis initialization issue: {failure_result.get('error', 'Unknown')}")
        except Exception as e:
            logger.warning(f"⚠️ Failure analysis initialization failed: {e}")
        
        # Initialize ML risk prediction system
        try:
            global ml_predictor
            ml_predictor = DamRiskPredictor(db_pool)
            logger.info("✅ ML risk prediction system initialized")
        except Exception as e:
            logger.warning(f"⚠️ ML system initialization failed: {e}")
        
        # Initialize Arctic risk analysis system
        try:
            global arctic_analyzer
            arctic_analyzer = ArcticRiskAnalyzer(db_pool)
            await create_arctic_tables(db_pool)
            logger.info("✅ Arctic risk analysis system initialized")
        except Exception as e:
            logger.warning(f"⚠️ Arctic analysis initialization failed: {e}")
        
        # Initialize SHM technology system
        try:
            global shm_system
            shm_system = IntegratedSHMSystem(dam_id=1)  # Default dam for system operations
            await create_shm_tables(db_pool)
            logger.info("✅ SHM technology system initialized")
        except Exception as e:
            logger.warning(f"⚠️ SHM system initialization failed: {e}")
            
    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
        raise

async def shutdown_event():
    """Cleanup on shutdown"""
    global db_pool, monitoring_api, monitoring_task
    
    if monitoring_task:
        monitoring_task.cancel()
        try:
            await monitoring_task
        except asyncio.CancelledError:
            pass
    
    if monitoring_api:
        await monitoring_api.close_all()
    
    if db_pool:
        await db_pool.close()
    
    logger.info("✅ Shutdown complete")

async def get_db():
    """Database dependency"""
    if not db_pool:
        raise HTTPException(status_code=500, detail="Database not available")
    return db_pool

# ==================================================================================
# HEALTH CHECK ENDPOINTS
# ==================================================================================

@app.get("/health")
async def health_check():
    """System health check"""
    try:
        # Check database
        async with db_pool.acquire() as conn:
            await conn.execute("SELECT 1")
        
        # Check APIs status
        api_status = {
            "database": "✅ Connected",
            "monitoring_apis": "✅ Active" if monitoring_api else "⚠️ Limited",
            "background_monitoring": "✅ Running" if monitoring_task and not monitoring_task.done() else "❌ Stopped",
            "ml_prediction": "✅ Active" if ml_predictor else "❌ Not initialized",
            "arctic_analysis": "✅ Active" if arctic_analyzer else "❌ Not initialized",
            "shm_technology": "✅ Active" if shm_system else "❌ Not initialized"
        }
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "services": api_status
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")

@app.get("/stats", response_model=MonitoringStats)
async def get_monitoring_stats(db: asyncpg.Pool = Depends(get_db)):
    """Get overall monitoring statistics"""
    try:
        async with db.acquire() as conn:
            # Total and active dams
            total_dams = await conn.fetchval("SELECT COUNT(*) FROM dams")
            active_dams = await conn.fetchval("SELECT COUNT(*) FROM dams WHERE status = 'active'")
            
            # Critical alerts
            critical_alerts = await conn.fetchval(
                "SELECT COUNT(*) FROM alerts WHERE status = 'active' AND severity = 'critical'"
            )
            
            # Average health score
            avg_health = await conn.fetchval(
                "SELECT AVG(overall_score) FROM latest_dam_health WHERE overall_score IS NOT NULL"
            )
            
            # Data points in last 24 hours
            data_points = await conn.fetchval("""
                SELECT COUNT(*) FROM (
                    SELECT COUNT(*) FROM weather_data WHERE time > NOW() - INTERVAL '24 hours'
                    UNION ALL
                    SELECT COUNT(*) FROM water_levels WHERE time > NOW() - INTERVAL '24 hours'
                    UNION ALL
                    SELECT COUNT(*) FROM sensor_readings WHERE time > NOW() - INTERVAL '24 hours'
                ) as combined
            """)
            
            return MonitoringStats(
                total_dams=total_dams or 0,
                active_dams=active_dams or 0,
                critical_alerts=critical_alerts or 0,
                average_health_score=round(avg_health or 0, 2),
                data_points_last_24h=data_points or 0,
                last_update=datetime.now()
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching stats: {str(e)}")

# ==================================================================================
# DAM INFORMATION ENDPOINTS
# ==================================================================================

@app.get("/dams", response_model=List[DamInfo])
async def get_dams(
    limit: int = Query(100, le=1000),
    offset: int = Query(0, ge=0),
    municipality: Optional[str] = None,
    county: Optional[str] = None,
    risk_level: Optional[str] = None,
    db: asyncpg.Pool = Depends(get_db)
):
    """Get list of dams with optional filtering"""
    try:
        query = """
            SELECT dam_id, nve_dam_nr, dam_name, municipality, county, owner,
                   construction_year, dam_height_m, status, risk_level,
                   ST_Y(location::geometry) as latitude,
                   ST_X(location::geometry) as longitude
            FROM dams
            WHERE 1=1
        """
        params = []
        param_count = 0
        
        if municipality:
            param_count += 1
            query += f" AND municipality ILIKE ${param_count}"
            params.append(f"%{municipality}%")
        
        if county:
            param_count += 1
            query += f" AND county ILIKE ${param_count}"
            params.append(f"%{county}%")
        
        if risk_level:
            param_count += 1
            query += f" AND risk_level = ${param_count}"
            params.append(risk_level)
        
        query += f" ORDER BY dam_name LIMIT ${param_count + 1} OFFSET ${param_count + 2}"
        params.extend([limit, offset])
        
        async with db.acquire() as conn:
            rows = await conn.fetch(query, *params)
            return [DamInfo(**dict(row)) for row in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching dams: {str(e)}")

@app.get("/dams/{dam_id}", response_model=DamInfo)
async def get_dam_details(dam_id: int, db: asyncpg.Pool = Depends(get_db)):
    """Get detailed information for a specific dam"""
    try:
        async with db.acquire() as conn:
            row = await conn.fetchrow("""
                SELECT dam_id, nve_dam_nr, dam_name, municipality, county, owner,
                       construction_year, dam_height_m, status, risk_level,
                       ST_Y(location::geometry) as latitude,
                       ST_X(location::geometry) as longitude
                FROM dams WHERE dam_id = $1
            """, dam_id)
            
            if not row:
                raise HTTPException(status_code=404, detail="Dam not found")
            
            return DamInfo(**dict(row))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching dam details: {str(e)}")

@app.get("/dams/overview", response_model=List[DamOverview])
async def get_dams_overview(
    limit: int = Query(50, le=500),
    db: asyncpg.Pool = Depends(get_db)
):
    """Get overview of all dams with health scores and alerts"""
    try:
        async with db.acquire() as conn:
            rows = await conn.fetch("""
                SELECT * FROM dam_overview
                ORDER BY 
                    CASE 
                        WHEN health_score IS NULL THEN 1
                        ELSE 0
                    END,
                    health_score ASC,
                    active_alerts DESC
                LIMIT $1
            """, limit)
            
            return [DamOverview(**dict(row)) for row in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching dam overview: {str(e)}")

# ==================================================================================
# HEALTH MONITORING ENDPOINTS
# ==================================================================================

@app.get("/dams/{dam_id}/health", response_model=HealthScore)
async def get_dam_health(dam_id: int, db: asyncpg.Pool = Depends(get_db)):
    """Get latest health score for a dam"""
    try:
        async with db.acquire() as conn:
            row = await conn.fetchrow("""
                SELECT h.dam_id, d.dam_name, h.time as timestamp, h.overall_score,
                       h.structural_score, h.operational_score, h.environmental_score,
                       h.safety_score, h.confidence_level
                FROM latest_dam_health h
                JOIN dams d ON h.dam_id = d.dam_id
                WHERE h.dam_id = $1
            """, dam_id)
            
            if not row:
                raise HTTPException(status_code=404, detail="Health data not found for dam")
            
            return HealthScore(**dict(row))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching health data: {str(e)}")

@app.get("/dams/{dam_id}/health/history")
async def get_dam_health_history(
    dam_id: int,
    hours: int = Query(24, le=8760),  # Max 1 year
    db: asyncpg.Pool = Depends(get_db)
):
    """Get health score history for a dam"""
    try:
        async with db.acquire() as conn:
            rows = await conn.fetch("""
                SELECT time as timestamp, overall_score, structural_score,
                       operational_score, environmental_score, safety_score,
                       confidence_level, calculation_method
                FROM health_scores
                WHERE dam_id = $1 AND time > NOW() - INTERVAL '%d hours'
                ORDER BY time DESC
            """ % hours, dam_id)
            
            return [dict(row) for row in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching health history: {str(e)}")

@app.post("/dams/{dam_id}/health/calculate")
async def calculate_dam_health(dam_id: int, db: asyncpg.Pool = Depends(get_db)):
    """Manually trigger health score calculation for a dam"""
    try:
        async with db.acquire() as conn:
            # Call the database function to calculate health score
            score = await conn.fetchval("SELECT calculate_dam_health_score($1)", dam_id)
            
            if score is None:
                raise HTTPException(status_code=404, detail="Dam not found or no data available")
            
            return {"dam_id": dam_id, "health_score": float(score), "calculated_at": datetime.now()}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating health score: {str(e)}")

# ==================================================================================
# SENSOR DATA ENDPOINTS
# ==================================================================================

@app.get("/dams/{dam_id}/sensors")
async def get_dam_sensors(dam_id: int, db: asyncpg.Pool = Depends(get_db)):
    """Get all sensors for a dam"""
    try:
        async with db.acquire() as conn:
            rows = await conn.fetch("""
                SELECT sensor_id, sensor_type, sensor_name, manufacturer, model,
                       installation_date, status, 
                       ST_Y(location::geometry) as latitude,
                       ST_X(location::geometry) as longitude
                FROM sensors WHERE dam_id = $1
                ORDER BY sensor_type, sensor_name
            """, dam_id)
            
            return [dict(row) for row in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching sensors: {str(e)}")

@app.get("/dams/{dam_id}/sensor-data", response_model=List[SensorReading])
async def get_sensor_data(
    dam_id: int,
    sensor_type: Optional[str] = None,
    hours: int = Query(24, le=8760),
    db: asyncpg.Pool = Depends(get_db)
):
    """Get recent sensor readings for a dam"""
    try:
        query = """
            SELECT sr.sensor_id, s.dam_id, s.sensor_type, sr.time as timestamp,
                   sr.value, sr.unit, sr.quality_score
            FROM sensor_readings sr
            JOIN sensors s ON sr.sensor_id = s.sensor_id
            WHERE s.dam_id = $1 AND sr.time > NOW() - INTERVAL '%d hours'
        """ % hours
        
        params = [dam_id]
        
        if sensor_type:
            query += " AND s.sensor_type = $2"
            params.append(sensor_type)
        
        query += " ORDER BY sr.time DESC"
        
        async with db.acquire() as conn:
            rows = await conn.fetch(query, *params)
            return [SensorReading(**dict(row)) for row in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching sensor data: {str(e)}")

# ==================================================================================
# WEATHER DATA ENDPOINTS
# ==================================================================================

@app.get("/dams/{dam_id}/weather", response_model=List[WeatherReading])
async def get_weather_data(
    dam_id: int,
    hours: int = Query(24, le=8760),
    source: Optional[str] = None,
    db: asyncpg.Pool = Depends(get_db)
):
    """Get weather data for a dam"""
    try:
        query = """
            SELECT dam_id, time as timestamp, temperature_c, precipitation_mm,
                   wind_speed_ms, wind_direction, humidity_percent, pressure_hpa,
                   snow_depth_cm, data_source
            FROM weather_data
            WHERE dam_id = $1 AND time > NOW() - INTERVAL '%d hours'
        """ % hours
        
        params = [dam_id]
        
        if source:
            query += " AND data_source = $2"
            params.append(source)
        
        query += " ORDER BY time DESC"
        
        async with db.acquire() as conn:
            rows = await conn.fetch(query, *params)
            return [WeatherReading(**dict(row)) for row in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching weather data: {str(e)}")

@app.get("/dams/{dam_id}/weather/current")
async def get_current_weather(dam_id: int, db: asyncpg.Pool = Depends(get_db)):
    """Get most recent weather data for a dam"""
    try:
        async with db.acquire() as conn:
            row = await conn.fetchrow("""
                SELECT dam_id, time as timestamp, temperature_c, precipitation_mm,
                       wind_speed_ms, wind_direction, humidity_percent, pressure_hpa,
                       snow_depth_cm, data_source
                FROM weather_data
                WHERE dam_id = $1
                ORDER BY time DESC
                LIMIT 1
            """, dam_id)
            
            if not row:
                raise HTTPException(status_code=404, detail="No weather data available")
            
            return dict(row)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching current weather: {str(e)}")

# ==================================================================================
# ALERTS ENDPOINTS
# ==================================================================================

@app.get("/alerts", response_model=List[Alert])
async def get_alerts(
    status: str = Query("active"),
    severity: Optional[str] = None,
    limit: int = Query(50, le=500),
    db: asyncpg.Pool = Depends(get_db)
):
    """Get system alerts"""
    try:
        query = "SELECT * FROM active_alerts WHERE 1=1"
        params = []
        param_count = 0
        
        if status != "all":
            param_count += 1
            query = query.replace("active_alerts", "alerts") + f" AND status = ${param_count}"
            params.append(status)
        
        if severity:
            param_count += 1
            query += f" AND severity = ${param_count}"
            params.append(severity)
        
        query += f" ORDER BY created_at DESC LIMIT ${param_count + 1}"
        params.append(limit)
        
        async with db.acquire() as conn:
            rows = await conn.fetch(query, *params)
            return [Alert(**dict(row)) for row in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching alerts: {str(e)}")

@app.get("/dams/{dam_id}/alerts", response_model=List[Alert])
async def get_dam_alerts(
    dam_id: int,
    status: str = Query("active"),
    db: asyncpg.Pool = Depends(get_db)
):
    """Get alerts for a specific dam"""
    try:
        async with db.acquire() as conn:
            rows = await conn.fetch("""
                SELECT a.alert_id, a.dam_id, d.dam_name, a.alert_type, a.severity,
                       a.title, a.description, a.created_at, a.status,
                       EXTRACT(HOURS FROM NOW() - a.created_at) as hours_active
                FROM alerts a
                JOIN dams d ON a.dam_id = d.dam_id
                WHERE a.dam_id = $1 AND ($2 = 'all' OR a.status = $2)
                ORDER BY a.created_at DESC
            """, dam_id, status)
            
            return [Alert(**dict(row)) for row in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching dam alerts: {str(e)}")

# ==================================================================================
# DATA COLLECTION ENDPOINTS
# ==================================================================================

@app.post("/dams/{dam_id}/collect-data")
async def trigger_data_collection(
    dam_id: int,
    background_tasks: BackgroundTasks,
    db: asyncpg.Pool = Depends(get_db)
):
    """Manually trigger data collection for a specific dam"""
    if not monitoring_api:
        raise HTTPException(status_code=503, detail="Monitoring APIs not available")
    
    try:
        # Get dam coordinates
        async with db.acquire() as conn:
            row = await conn.fetchrow("""
                SELECT ST_Y(location::geometry) as lat, ST_X(location::geometry) as lon
                FROM dams WHERE dam_id = $1
            """, dam_id)
            
            if not row:
                raise HTTPException(status_code=404, detail="Dam not found")
        
        # Schedule background data collection
        background_tasks.add_task(collect_and_store_dam_data, dam_id, row['lat'], row['lon'])
        
        return {"message": f"Data collection triggered for dam {dam_id}", "status": "scheduled"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error triggering data collection: {str(e)}")

@app.post("/collect-all-data")
async def trigger_full_data_collection(background_tasks: BackgroundTasks):
    """Trigger data collection for all active dams"""
    if not monitoring_api:
        raise HTTPException(status_code=503, detail="Monitoring APIs not available")
    
    background_tasks.add_task(collect_all_dams_data)
    return {"message": "Full data collection triggered", "status": "scheduled"}

# ==================================================================================
# BACKGROUND TASKS
# ==================================================================================

async def background_monitoring():
    """Background task for continuous Norwegian dam monitoring"""
    logger.info("🔄 Starting background monitoring with real Norwegian APIs...")
    
    while True:
        try:
            if not monitoring_api:
                logger.warning("⚠️ Norwegian APIs not initialized - skipping collection cycle")
                await asyncio.sleep(300)  # Wait 5 minutes
                continue
                
            # Get sample of dams for monitoring (avoid overwhelming APIs)
            async with db_pool.acquire() as connection:
                sample_dams = await connection.fetch("""
                    SELECT dam_id, dam_name, nve_dam_nr, latitude, longitude 
                    FROM dams 
                    WHERE status = 'active' 
                        AND latitude IS NOT NULL 
                        AND longitude IS NOT NULL
                    ORDER BY RANDOM() 
                    LIMIT 25
                """)
                
                if not sample_dams:
                    logger.warning("⚠️ No dams with coordinates found for monitoring")
                    await asyncio.sleep(600)  # Wait 10 minutes
                    continue
                
                logger.info(f"📡 Collecting real-time data for {len(sample_dams)} Norwegian dams...")
                
                # Collect weather data for sample dams
                for dam in sample_dams:
                    try:
                        # Get real Norwegian weather data
                        weather_data = await monitoring_api.met_no.get_current_weather(
                            dam['latitude'], dam['longitude']
                        )
                        
                        if weather_data:
                            # Insert real weather data
                            await connection.execute("""
                                INSERT INTO weather_data 
                                (time, dam_id, temperature_c, precipitation_mm, wind_speed_ms, humidity_percent, data_source)
                                VALUES (NOW(), $1, $2, $3, $4, $5, 'met.no_live')
                            """, 
                            dam['dam_id'],
                            weather_data.temperature or 0,
                            weather_data.precipitation or 0,
                            weather_data.wind_speed or 0,
                            weather_data.humidity or 50
                            )
                            
                            logger.info(f"✅ Live weather data collected for {dam['dam_name']}")
                        
                        # Add small delay between API calls
                        await asyncio.sleep(2)
                        
                    except Exception as e:
                        logger.error(f"❌ Error collecting data for dam {dam['dam_name']}: {e}")
                
                # Update health scores based on new data
                await connection.execute("""
                    SELECT update_all_dam_health_scores()
                """)
                
                logger.info(f"✅ Monitoring cycle complete - collected live Norwegian data")
                
        except Exception as e:
            logger.error(f"❌ Background monitoring error: {e}")
        
        # Wait before next collection cycle (1 hour as configured)
        collection_interval = int(os.getenv('COLLECTION_INTERVAL_MINUTES', 30))
        logger.info(f"💤 Waiting {collection_interval} minutes until next monitoring cycle...")
        await asyncio.sleep(collection_interval * 60)

async def collect_all_dams_data():
    """Collect data for all active dams"""
    try:
        async with db_pool.acquire() as conn:
            # Get sample of active dams (limit for performance)
            batch_size = int(os.getenv('BATCH_SIZE', '10'))
            rows = await conn.fetch("""
                SELECT dam_id, ST_Y(location::geometry) as lat, ST_X(location::geometry) as lon
                FROM dams 
                WHERE status = 'active' AND location IS NOT NULL
                ORDER BY RANDOM()
                LIMIT $1
            """, batch_size)
            
            logger.info(f"Collecting data for {len(rows)} dams...")
            
            # Process dams in parallel
            tasks = []
            for row in rows:
                if row['lat'] and row['lon']:
                    task = collect_and_store_dam_data(row['dam_id'], row['lat'], row['lon'])
                    tasks.append(task)
            
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
                logger.info(f"✅ Data collection completed for {len(tasks)} dams")
                
    except Exception as e:
        logger.error(f"Error in collect_all_dams_data: {e}")

async def collect_and_store_dam_data(dam_id: int, lat: float, lon: float):
    """Collect and store data for a single dam"""
    try:
        # Collect data from all Norwegian APIs
        data = await monitoring_api.collect_dam_data(dam_id, lat, lon)
        
        # Store in database
        await monitoring_api.store_data(data, db_pool)
        
        logger.info(f"✅ Data collected and stored for dam {dam_id}")
        
    except Exception as e:
        logger.error(f"Error collecting data for dam {dam_id}: {e}")

async def update_health_scores():
    """Update health scores for all dams"""
    try:
        async with db_pool.acquire() as conn:
            updated_count = await conn.fetchval("SELECT update_all_dam_health_scores()")
            logger.info(f"✅ Updated health scores for {updated_count} dams")
    except Exception as e:
        logger.error(f"Error updating health scores: {e}")

# ==================================================================================
# RISK MATRIX ENDPOINT
# ==================================================================================

@app.get("/risk-matrix")
async def get_risk_matrix(db: asyncpg.Pool = Depends(get_db)):
    """Get risk matrix data for dashboard visualization"""
    try:
        async with db.acquire() as conn:
            # Get risk distribution
            risk_data = await conn.fetch("""
                SELECT 
                    risk_level,
                    COUNT(*) as dam_count,
                    AVG(lh.overall_score) as avg_health_score,
                    COUNT(a.alert_id) as total_alerts
                FROM dams d
                LEFT JOIN latest_dam_health lh ON d.dam_id = lh.dam_id
                LEFT JOIN alerts a ON d.dam_id = a.dam_id AND a.status = 'active'
                WHERE d.status = 'active'
                GROUP BY risk_level
                ORDER BY 
                    CASE risk_level 
                        WHEN 'low' THEN 1 
                        WHEN 'medium' THEN 2 
                        WHEN 'high' THEN 3 
                        WHEN 'critical' THEN 4 
                    END
            """)
            
            return {
                "risk_distribution": [dict(row) for row in risk_data],
                "generated_at": datetime.now().isoformat()
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating risk matrix: {str(e)}")

# ==================================================================================
# ML RISK PREDICTION ENDPOINTS
# ==================================================================================

@app.post("/ml/train-models")
async def train_ml_models(db: asyncpg.Pool = Depends(get_db)):
    """Train all ML risk prediction models"""
    try:
        if not ml_predictor:
            raise HTTPException(status_code=503, detail="ML system not initialized")
        
        scores = await ml_predictor.train_all_models()
        return {
            "status": "success",
            "model_scores": scores,
            "trained_at": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ML training failed: {str(e)}")

@app.get("/ml/predict/{dam_id}", response_model=MLRiskPrediction)
async def get_ml_risk_prediction(dam_id: int, db: asyncpg.Pool = Depends(get_db)):
    """Get ML-based risk prediction for a dam"""
    try:
        if not ml_predictor:
            raise HTTPException(status_code=503, detail="ML system not initialized")
        
        prediction = await ml_predictor.predict_dam_risk(dam_id)
        
        if 'error' in prediction:
            raise HTTPException(status_code=404, detail=prediction['error'])
        
        return MLRiskPrediction(
            dam_id=prediction['dam_id'],
            risk_score=prediction['risk_score'],
            risk_level=prediction['risk_level'],
            failure_probability=prediction['risk_score'] / 100,
            most_likely_failure_type=prediction.get('most_likely_failure_type'),
            predictions=prediction['predictions'],
            recommended_actions=prediction['recommended_actions'],
            confidence=0.85
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ML prediction failed: {str(e)}")

@app.get("/ml/model-performance")
async def get_model_performance():
    """Get ML model performance metrics"""
    try:
        if not ml_predictor or not ml_predictor.model_scores:
            return {"message": "No trained models available", "models": []}
        
        performance = []
        for model_name, scores in ml_predictor.model_scores.items():
            performance.append(MLModelPerformance(
                model_name=model_name,
                r2_score=scores.get('r2', 0),
                mae=scores.get('mae', 0),
                mse=scores.get('mse', 0),
                training_date=datetime.now().isoformat()
            ))
        
        return {"models": performance}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting model performance: {str(e)}")

# ==================================================================================
# ARCTIC RISK ANALYSIS ENDPOINTS
# ==================================================================================

@app.get("/arctic/analyze/{dam_id}", response_model=ArcticRiskAssessment)
async def analyze_arctic_risk(dam_id: int, latitude: float = Query(..., ge=-90, le=90), 
                            db: asyncpg.Pool = Depends(get_db)):
    """Analyze Arctic-specific risks for a dam"""
    try:
        if not arctic_analyzer:
            raise HTTPException(status_code=503, detail="Arctic analysis system not initialized")
        
        assessment = await arctic_analyzer.analyze_arctic_risks(dam_id, latitude)
        
        return ArcticRiskAssessment(
            dam_id=assessment['dam_id'],
            latitude=assessment['latitude'],
            is_arctic=assessment['is_arctic'],
            overall_arctic_risk=assessment['overall_arctic_risk'],
            permafrost_risk=assessment['permafrost_risk'],
            ice_dam_risk=assessment['ice_dam_risk'],
            freeze_thaw_risk=assessment['freeze_thaw_risk'],
            climate_change_impact=assessment['climate_change_impact'],
            mitigation_measures=assessment['mitigation_measures']
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Arctic analysis failed: {str(e)}")

@app.get("/arctic/regional-analysis")
async def get_regional_arctic_analysis(db: asyncpg.Pool = Depends(get_db)):
    """Get regional Arctic risk analysis for Norwegian regions"""
    try:
        if not arctic_analyzer:
            raise HTTPException(status_code=503, detail="Arctic analysis system not initialized")
        
        from api.arctic_risk_analyzer import NorwegianRegionalAnalyzer
        regional_analyzer = NorwegianRegionalAnalyzer(arctic_analyzer)
        
        analysis = await regional_analyzer.analyze_regional_risks()
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Regional analysis failed: {str(e)}")

# ==================================================================================
# SHM TECHNOLOGY ENDPOINTS
# ==================================================================================

@app.get("/shm/assess/{dam_id}", response_model=SHMAssessment)
async def run_shm_assessment(dam_id: int, height: float = Query(50), length: float = Query(200),
                           thickness: float = Query(10), water_level: float = Query(65),
                           temp_variation: float = Query(5), db: asyncpg.Pool = Depends(get_db)):
    """Run comprehensive SHM assessment for a dam"""
    try:
        if not shm_system:
            raise HTTPException(status_code=503, detail="SHM system not initialized")
        
        # Update dam ID for specific assessment
        shm_system.dam_id = dam_id
        
        dam_properties = {
            'height': height,
            'length': length,
            'thickness': thickness,
            'water_level': water_level,
            'temp_variation': temp_variation
        }
        
        assessment = await shm_system.perform_comprehensive_assessment(dam_properties)
        
        return SHMAssessment(
            dam_id=assessment['dam_id'],
            timestamp=assessment['timestamp'],
            fem_analysis=assessment['fem_analysis'],
            fiber_optic_analysis=assessment['fiber_optic_analysis'],
            drone_inspection=assessment['drone_inspection'],
            integrated_health_score=assessment['integrated_health_score'],
            recommendations=assessment['recommendations']
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"SHM assessment failed: {str(e)}")

@app.get("/shm/fiber-optic/{dam_id}")
async def get_fiber_optic_analysis(dam_id: int, water_level: float = Query(70),
                                 temp_variation: float = Query(5), db: asyncpg.Pool = Depends(get_db)):
    """Get fiber optic monitoring analysis for a dam"""
    try:
        if not shm_system:
            raise HTTPException(status_code=503, detail="SHM system not initialized")
        
        readings = shm_system.fiber_optic.simulate_fiber_measurement({
            'water_level': water_level,
            'temperature_variation': temp_variation
        })
        
        anomalies = shm_system.fiber_optic.detect_anomalies(readings)
        
        return {
            "dam_id": dam_id,
            "measurement_points": len(readings),
            "anomalies": anomalies,
            "strain_data": [{"position": r.position_m, "strain": r.strain, "temperature": r.temperature} 
                          for r in readings[::10]]  # Every 10th point for API efficiency
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fiber optic analysis failed: {str(e)}")

@app.get("/shm/drone-inspection/{dam_id}")
async def get_drone_inspection(dam_id: int, db: asyncpg.Pool = Depends(get_db)):
    """Get drone inspection results for a dam"""
    try:
        if not shm_system:
            raise HTTPException(status_code=503, detail="SHM system not initialized")
        
        results = shm_system.drone_inspection.process_drone_image(f"dam_{dam_id}_inspection.jpg")
        results['dam_id'] = dam_id
        
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Drone inspection failed: {str(e)}")

# ==================================================================================
# INTEGRATED ANALYTICS ENDPOINTS
# ==================================================================================

@app.get("/analytics/comprehensive-risk/{dam_id}")
async def get_comprehensive_risk_analysis(dam_id: int, latitude: float = Query(..., ge=-90, le=90),
                                        db: asyncpg.Pool = Depends(get_db)):
    """Get comprehensive risk analysis combining ML, Arctic, and SHM assessments"""
    try:
        results = {}
        
        # ML Risk Prediction
        if ml_predictor:
            try:
                ml_risk = await ml_predictor.predict_dam_risk(dam_id)
                results['ml_prediction'] = ml_risk
            except Exception as e:
                results['ml_prediction'] = {"error": str(e)}
        
        # Arctic Risk Analysis
        if arctic_analyzer:
            try:
                arctic_risk = await arctic_analyzer.analyze_arctic_risks(dam_id, latitude)
                results['arctic_analysis'] = arctic_risk
            except Exception as e:
                results['arctic_analysis'] = {"error": str(e)}
        
        # SHM Assessment
        if shm_system:
            try:
                shm_system.dam_id = dam_id
                shm_assessment = await shm_system.perform_comprehensive_assessment({
                    'height': 50, 'length': 200, 'thickness': 10, 
                    'water_level': 65, 'temp_variation': 5
                })
                results['shm_assessment'] = shm_assessment
            except Exception as e:
                results['shm_assessment'] = {"error": str(e)}
        
        # Calculate integrated risk score
        risk_scores = []
        if 'ml_prediction' in results and 'risk_score' in results['ml_prediction']:
            risk_scores.append(results['ml_prediction']['risk_score'])
        if 'arctic_analysis' in results and 'overall_arctic_risk' in results['arctic_analysis']:
            risk_scores.append(results['arctic_analysis']['overall_arctic_risk'])
        if 'shm_assessment' in results and 'integrated_health_score' in results['shm_assessment']:
            risk_scores.append(100 - results['shm_assessment']['integrated_health_score'])  # Convert health to risk
        
        integrated_risk = sum(risk_scores) / len(risk_scores) if risk_scores else 0
        
        results['integrated_risk_score'] = round(integrated_risk, 2)
        results['risk_level'] = (
            "CRITICAL" if integrated_risk > 80 else
            "HIGH" if integrated_risk > 60 else
            "MEDIUM" if integrated_risk > 40 else
            "LOW"
        )
        results['analysis_timestamp'] = datetime.now().isoformat()
        
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Comprehensive analysis failed: {str(e)}")

# ==================================================================================
# APPLICATION STARTUP
# ==================================================================================

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 