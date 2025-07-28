#!/usr/bin/env python3
"""
Norwegian Dam Health Monitoring API
==================================
Simplified FastAPI backend with real Norwegian data integration.
"""

import os
import asyncio
import asyncpg
from datetime import datetime
from typing import List, Dict, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import aiohttp

# Database connection pool
db_pool: asyncpg.Pool = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifecycle."""
    global db_pool
    
    # Startup
    print("🚀 Starting Norwegian Dam Health Monitoring API")
    
    try:
        # Initialize database connection
        db_pool = await asyncpg.create_pool(
            host=os.getenv('DB_HOST', 'localhost'),
            port=int(os.getenv('DB_PORT', '5432')),
            user=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('POSTGRES_PASSWORD', 'dam_monitor_2024'),
            database=os.getenv('DB_NAME', 'dam_monitoring'),
            min_size=5,
            max_size=20
        )
        print("✅ Database connection established")
        
    except Exception as e:
        print(f"❌ Startup failed: {e}")
        raise
    
    yield
    
    # Shutdown
    if db_pool:
        await db_pool.close()
        print("✅ Database connections closed")

# Create FastAPI app
app = FastAPI(
    title="Norwegian Dam Health Monitoring API",
    description="Real-time dam monitoring with Norwegian government data",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class DamInfo(BaseModel):
    dam_id: str
    dam_name: str
    latitude: float
    longitude: float
    construction_year: Optional[int] = None
    region: Optional[str] = None

class WeatherData(BaseModel):
    temperature_c: Optional[float] = None
    precipitation_mm: Optional[float] = None
    timestamp: datetime

# Dependency to get DB connection
async def get_db():
    """Dependency to get database connection."""
    async with db_pool.acquire() as connection:
        yield connection

# API Endpoints
@app.get("/")
async def root():
    return {
        "message": "Norwegian Dam Health Monitoring System",
        "version": "1.0.0",
        "data_sources": [
            "met.no - Real-time weather",
            "Your Frost API - Historical weather", 
            "Your Sentinel Hub - Satellite data",
            "NVE - Water levels"
        ],
        "endpoints": {
            "health": "/health",
            "dams": "/api/v1/dams",
            "weather": "/api/v1/weather/{dam_id}"
        }
    }

@app.get("/health")
async def health_check():
    """API health check endpoint."""
    try:
        # Test database connection
        async with db_pool.acquire() as conn:
            await conn.fetchval("SELECT 1")
        
        # Test met.no API
        response = requests.get(
            "https://api.met.no/weatherapi/locationforecast/2.0/compact",
            params={'lat': 59.9139, 'lon': 10.7522},
            headers={'User-Agent': 'DamHealthMonitor/1.0'},
            timeout=5
        )
        
        return {
            "status": "healthy",
            "timestamp": datetime.now(),
            "database": "connected",
            "met_no_api": "working" if response.status_code == 200 else "limited",
            "api_credentials": {
                "frost": "configured" if os.getenv('FROST_CLIENT_ID') else "missing",
                "sentinel": "configured" if os.getenv('SENTINEL_USER') else "missing"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")

@app.get("/api/v1/dams", response_model=List[DamInfo])
async def get_all_dams(db: asyncpg.Connection = Depends(get_db)):
    """Get all dams."""
    query = """
    SELECT dam_id, dam_name, latitude, longitude, construction_year, region
    FROM dams 
    ORDER BY dam_name
    LIMIT 100
    """
    rows = await db.fetch(query)
    return [DamInfo(**dict(row)) for row in rows]

@app.get("/api/v1/weather/{dam_id}")
async def get_dam_weather(dam_id: str, db: asyncpg.Connection = Depends(get_db)):
    """Get current weather for a dam using real met.no API."""
    
    # Get dam coordinates
    dam_info = await db.fetchrow("""
        SELECT latitude, longitude FROM dams WHERE dam_id = $1
    """, dam_id)
    
    if not dam_info:
        raise HTTPException(status_code=404, detail=f"Dam {dam_id} not found")
    
    # Get weather from met.no API
    try:
        async with aiohttp.ClientSession() as session:
            url = "https://api.met.no/weatherapi/locationforecast/2.0/compact"
            params = {
                'lat': float(dam_info['latitude']),
                'lon': float(dam_info['longitude'])
            }
            headers = {'User-Agent': 'DamHealthMonitor/1.0'}
            
            async with session.get(url, params=params, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Extract current weather
                    current = data['properties']['timeseries'][0]
                    instant = current['data']['instant']['details']
                    next_hour = current['data'].get('next_1_hours', {})
                    
                    weather = WeatherData(
                        temperature_c=instant.get('air_temperature'),
                        precipitation_mm=next_hour.get('details', {}).get('precipitation_amount', 0),
                        timestamp=datetime.now()
                    )
                    
                    # Store in database
                    await db.execute("""
                        INSERT INTO weather_data (time, dam_id, temperature_c, precipitation_mm)
                        VALUES ($1, $2, $3, $4)
                    """, weather.timestamp, dam_id, weather.temperature_c, weather.precipitation_mm)
                    
                    return {
                        "dam_id": dam_id,
                        "location": {"lat": dam_info['latitude'], "lon": dam_info['longitude']},
                        "weather": weather,
                        "data_source": "met.no (Norwegian Meteorological Institute)"
                    }
                else:
                    raise HTTPException(status_code=503, detail="Weather service unavailable")
                    
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Weather API error: {str(e)}")

@app.get("/api/v1/status")
async def system_status():
    """Get system status with Norwegian API connectivity."""
    
    frost_id = os.getenv('FROST_CLIENT_ID')
    sentinel_user = os.getenv('SENTINEL_USER') 
    
    status = {
        "system": "Norwegian Dam Health Monitoring",
        "api_credentials": {
            "frost_api": {
                "configured": bool(frost_id),
                "client_id": frost_id[:10] + "..." if frost_id else None,
                "status": "ready" if frost_id else "not_configured"
            },
            "sentinel_hub": {
                "configured": bool(sentinel_user),
                "username": sentinel_user if sentinel_user else None,
                "status": "ready" if sentinel_user else "not_configured"
            }
        },
        "data_sources": {
            "met_no": "✅ Real-time weather (always available)",
            "nve_hydrology": "✅ Water levels (public API)", 
            "frost": "✅ Historical weather (your credentials)" if frost_id else "⏭️ Not configured",
            "sentinel": "✅ Satellite data (your credentials)" if sentinel_user else "⏭️ Not configured"
        }
    }
    
    return status

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
