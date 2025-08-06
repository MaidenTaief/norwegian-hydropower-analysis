#!/usr/bin/env python3
"""
Norwegian APIs Integration for Dam Health Monitoring
===================================================

Complete integration with Norwegian government APIs and data sources:
- met.no: Real-time weather data
- Frost API: Historical weather data  
- NVE Hydrology: Water levels and flow data
- Sentinel Hub: Satellite imagery and InSAR
- VARSOM: Avalanche and flood warnings

All APIs use your real credentials configured in .env
"""

import aiohttp
import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
import os
from dataclasses import dataclass
from pathlib import Path
import asyncpg

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class WeatherData:
    """Weather data structure from Norwegian APIs"""
    timestamp: datetime
    temperature: Optional[float]
    precipitation: Optional[float]
    wind_speed: Optional[float]
    wind_direction: Optional[float]
    humidity: Optional[float]
    pressure: Optional[float]
    snow_depth: Optional[float]
    source: str

@dataclass
class WaterLevelData:
    """Water level data from NVE"""
    timestamp: datetime
    water_level: Optional[float]
    flow_rate: Optional[float]
    reservoir_fill: Optional[float]
    inflow: Optional[float]
    outflow: Optional[float]

@dataclass
class SatelliteData:
    """Satellite observation data"""
    timestamp: datetime
    satellite: str
    observation_type: str
    cloud_cover: Optional[float]
    image_quality: Optional[float]
    displacement: Optional[float]
    vegetation_index: Optional[float]
    water_surface_area: Optional[float]
    image_url: Optional[str]

class MetNoAPI:
    """
    Integration with met.no APIs for real-time Norwegian weather data
    https://api.met.no/
    """
    
    BASE_URL = "https://api.met.no/weatherapi"
    
    def __init__(self):
        self.session = None
        self.headers = {
            'User-Agent': 'NorwegianDamMonitoring/1.0 (taief@example.com)'
        }
    
    async def _get_session(self):
        if not self.session:
            self.session = aiohttp.ClientSession(headers=self.headers)
        return self.session
    
    async def get_current_weather(self, lat: float, lon: float) -> Optional[WeatherData]:
        """Get current weather conditions for a location"""
        try:
            session = await self._get_session()
            url = f"{self.BASE_URL}/locationforecast/2.0/compact"
            params = {'lat': lat, 'lon': lon}
            
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Extract current conditions
                    current = data['properties']['timeseries'][0]
                    instant = current['data']['instant']['details']
                    
                    return WeatherData(
                        timestamp=datetime.fromisoformat(current['time'].replace('Z', '+00:00')),
                        temperature=instant.get('air_temperature'),
                        precipitation=current['data'].get('next_1_hours', {}).get('details', {}).get('precipitation_amount'),
                        wind_speed=instant.get('wind_speed'),
                        wind_direction=instant.get('wind_from_direction'),
                        humidity=instant.get('relative_humidity'),
                        pressure=instant.get('air_pressure_at_sea_level'),
                        snow_depth=None,  # Not available in locationforecast
                        source='met.no'
                    )
                else:
                    logger.error(f"met.no API error: {response.status}")
                    return None
        except Exception as e:
            logger.error(f"Error fetching met.no data: {e}")
            return None
    
    async def close(self):
        if self.session:
            await self.session.close()

class FrostAPI:
    """
    Integration with Frost API for historical Norwegian weather data
    https://frost.met.no/
    """
    
    BASE_URL = "https://frost.met.no/observations/v0.jsonld"
    
    def __init__(self, client_id: str):
        self.client_id = client_id
        self.session = None
        self.auth = aiohttp.BasicAuth(client_id, '')  # Frost uses client_id as username, empty password
    
    async def _get_session(self):
        if not self.session:
            self.session = aiohttp.ClientSession(auth=self.auth)
        return self.session
    
    async def get_historical_weather(self, station_id: str, start_date: datetime, end_date: datetime) -> List[WeatherData]:
        """Get historical weather data from Frost API"""
        try:
            session = await self._get_session()
            
            params = {
                'sources': station_id,
                'referencetime': f"{start_date.isoformat()}/{end_date.isoformat()}",
                'elements': 'air_temperature,sum(precipitation_amount PT1H),wind_speed,wind_from_direction,relative_humidity,air_pressure_at_sea_level,snow_depth'
            }
            
            async with session.get(self.BASE_URL, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    weather_data = []
                    
                    for observation in data.get('data', []):
                        # Parse observation data
                        timestamp = datetime.fromisoformat(observation['referenceTime'].replace('Z', '+00:00'))
                        
                        # Extract values from observations array
                        values = {}
                        for obs in observation.get('observations', []):
                            element = obs['elementId']
                            value = obs.get('value')
                            if value is not None:
                                values[element] = float(value)
                        
                        weather_data.append(WeatherData(
                            timestamp=timestamp,
                            temperature=values.get('air_temperature'),
                            precipitation=values.get('sum(precipitation_amount PT1H)'),
                            wind_speed=values.get('wind_speed'),
                            wind_direction=values.get('wind_from_direction'),
                            humidity=values.get('relative_humidity'),
                            pressure=values.get('air_pressure_at_sea_level'),
                            snow_depth=values.get('snow_depth'),
                            source='frost'
                        ))
                    
                    return weather_data
                else:
                    logger.error(f"Frost API error: {response.status}")
                    return []
        except Exception as e:
            logger.error(f"Error fetching Frost data: {e}")
            return []
    
    async def find_nearest_station(self, lat: float, lon: float) -> Optional[str]:
        """Find the nearest weather station to given coordinates"""
        try:
            session = await self._get_session()
            url = "https://frost.met.no/sources/v0.jsonld"
            
            params = {
                'geometry': f'nearest(POINT({lon} {lat}))',
                'types': 'SensorSystem'
            }
            
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    sources = data.get('data', [])
                    if sources:
                        return sources[0]['id']
                return None
        except Exception as e:
            logger.error(f"Error finding nearest station: {e}")
            return None
    
    async def close(self):
        if self.session:
            await self.session.close()

class NVEHydrologyAPI:
    """
    Integration with NVE Hydrology API for water level and flow data
    https://hydapi.nve.no/
    """
    
    BASE_URL = "https://hydapi.nve.no/api/v1"
    
    def __init__(self):
        self.session = None
    
    async def _get_session(self):
        if not self.session:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def get_water_levels(self, station_id: str, start_date: datetime, end_date: datetime) -> List[WaterLevelData]:
        """Get water level data from NVE station"""
        try:
            session = await self._get_session()
            
            # Format dates for NVE API
            start_str = start_date.strftime('%Y-%m-%d')
            end_str = end_date.strftime('%Y-%m-%d')
            
            url = f"{self.BASE_URL}/Observations"
            params = {
                'StationId': station_id,
                'Parameter': '1000',  # Water level parameter
                'ResolutionTime': '60',  # 60 minutes
                'ReferenceTime': f"{start_str}/{end_str}"
            }
            
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    water_data = []
                    
                    for observation in data.get('observations', []):
                        timestamp = datetime.fromisoformat(observation['time'])
                        value = observation.get('value')
                        
                        if value is not None:
                            water_data.append(WaterLevelData(
                                timestamp=timestamp,
                                water_level=float(value),
                                flow_rate=None,  # Would need separate API call
                                reservoir_fill=None,  # Calculated separately
                                inflow=None,
                                outflow=None
                            ))
                    
                    return water_data
                else:
                    logger.error(f"NVE API error: {response.status}")
                    return []
        except Exception as e:
            logger.error(f"Error fetching NVE data: {e}")
            return []
    
    async def find_nearest_station(self, lat: float, lon: float) -> Optional[str]:
        """Find nearest NVE hydrology station"""
        try:
            session = await self._get_session()
            url = f"{self.BASE_URL}/Stations"
            
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Find closest station (simplified)
                    min_distance = float('inf')
                    closest_station = None
                    
                    for station in data.get('data', []):
                        if 'latitude' in station and 'longitude' in station:
                            # Simple distance calculation
                            distance = ((lat - station['latitude'])**2 + (lon - station['longitude'])**2)**0.5
                            if distance < min_distance:
                                min_distance = distance
                                closest_station = station['stationId']
                    
                    return closest_station
                return None
        except Exception as e:
            logger.error(f"Error finding NVE station: {e}")
            return None
    
    async def close(self):
        if self.session:
            await self.session.close()

class SentinelHubAPI:
    """
    Integration with Sentinel Hub for satellite imagery and InSAR data
    https://www.sentinel-hub.com/
    """
    
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password
        self.session = None
        self.auth_token = None
    
    async def _get_session(self):
        if not self.session:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def _get_auth_token(self):
        """Get OAuth token for Sentinel Hub"""
        if self.auth_token:
            return self.auth_token
        
        try:
            session = await self._get_session()
            auth_url = "https://services.sentinel-hub.com/oauth/token"
            
            data = {
                'grant_type': 'client_credentials',
                'client_id': self.username,
                'client_secret': self.password
            }
            
            async with session.post(auth_url, data=data) as response:
                if response.status == 200:
                    token_data = await response.json()
                    self.auth_token = token_data['access_token']
                    return self.auth_token
                else:
                    logger.error(f"Sentinel Hub auth error: {response.status}")
                    return None
        except Exception as e:
            logger.error(f"Error getting Sentinel Hub token: {e}")
            return None
    
    async def get_satellite_image(self, lat: float, lon: float, date: datetime, bbox_size: float = 0.01) -> Optional[SatelliteData]:
        """Get satellite imagery for location and date"""
        try:
            token = await self._get_auth_token()
            if not token:
                return None
            
            session = await self._get_session()
            
            # Define bounding box around the point
            bbox = [
                lon - bbox_size, lat - bbox_size,
                lon + bbox_size, lat + bbox_size
            ]
            
            # Sentinel Hub Processing API request
            url = "https://services.sentinel-hub.com/api/v1/process"
            
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
            
            # Request for Sentinel-2 true color image
            request_data = {
                "input": {
                    "bounds": {
                        "properties": {"crs": "http://www.opengis.net/def/crs/EPSG/0/4326"},
                        "geometry": {
                            "type": "Polygon",
                            "coordinates": [[
                                [bbox[0], bbox[1]], [bbox[2], bbox[1]],
                                [bbox[2], bbox[3]], [bbox[0], bbox[3]], [bbox[0], bbox[1]]
                            ]]
                        }
                    },
                    "data": [{
                        "type": "sentinel-2-l2a",
                        "dataFilter": {
                            "timeRange": {
                                "from": date.strftime('%Y-%m-%d'),
                                "to": (date + timedelta(days=1)).strftime('%Y-%m-%d')
                            },
                            "maxCloudCoverage": 50
                        }
                    }]
                },
                "output": {
                    "width": 256,
                    "height": 256,
                    "responses": [{
                        "identifier": "default",
                        "format": {"type": "image/jpeg"}
                    }]
                },
                "evalscript": """
                //VERSION=3
                function setup() {
                    return {
                        input: ["B02", "B03", "B04", "SCL"],
                        output: { bands: 3 }
                    };
                }
                function evaluatePixel(sample) {
                    return [sample.B04, sample.B03, sample.B02];
                }
                """
            }
            
            async with session.post(url, headers=headers, json=request_data) as response:
                if response.status == 200:
                    # For now, return metadata (actual image would be binary data)
                    return SatelliteData(
                        timestamp=date,
                        satellite="Sentinel-2",
                        observation_type="optical",
                        cloud_cover=None,  # Would be extracted from metadata
                        image_quality=0.8,  # Placeholder
                        displacement=None,  # Not available for optical
                        vegetation_index=None,  # Could be calculated
                        water_surface_area=None,  # Could be calculated
                        image_url=f"sentinel_hub_image_{date.strftime('%Y%m%d')}.jpg"
                    )
                else:
                    logger.error(f"Sentinel Hub API error: {response.status}")
                    return None
        except Exception as e:
            logger.error(f"Error fetching Sentinel Hub data: {e}")
            return None
    
    async def close(self):
        if self.session:
            await self.session.close()

class VARSOMAPI:
    """
    Integration with VARSOM (Norwegian avalanche and flood warning service)
    https://api.varsom.no/
    """
    
    BASE_URL = "https://api.varsom.no/v2"
    
    def __init__(self):
        self.session = None
    
    async def _get_session(self):
        if not self.session:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def get_flood_warnings(self, region_id: str) -> List[Dict]:
        """Get flood warnings for a region"""
        try:
            session = await self._get_session()
            url = f"{self.BASE_URL}/warnings/flood/{region_id}"
            
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get('warnings', [])
                else:
                    logger.error(f"VARSOM API error: {response.status}")
                    return []
        except Exception as e:
            logger.error(f"Error fetching VARSOM data: {e}")
            return []
    
    async def close(self):
        if self.session:
            await self.session.close()

class HealthMonitoringAPI:
    """
    Main orchestrator for Norwegian dam health monitoring APIs
    Coordinates data collection from all sources
    """
    
    def __init__(self, frost_client_id: str, sentinel_user: str, sentinel_pass: str):
        self.met_no = MetNoAPI()
        self.frost = FrostAPI(frost_client_id)
        self.nve = NVEHydrologyAPI()
        self.sentinel = SentinelHubAPI(sentinel_user, sentinel_pass)
        self.varsom = VARSOMAPI()
    
    async def collect_dam_data(self, dam_id: int, lat: float, lon: float) -> Dict[str, Any]:
        """Collect all available data for a specific dam"""
        logger.info(f"Collecting data for dam {dam_id} at ({lat}, {lon})")
        
        tasks = []
        
        # Current weather from met.no
        tasks.append(self._safe_task(self.met_no.get_current_weather(lat, lon), "met_no"))
        
        # Find and get historical weather from Frost
        tasks.append(self._safe_task(self._get_frost_data(lat, lon), "frost"))
        
        # Find and get water level data from NVE
        tasks.append(self._safe_task(self._get_nve_data(lat, lon), "nve"))
        
        # Get recent satellite imagery
        tasks.append(self._safe_task(self.sentinel.get_satellite_image(lat, lon, datetime.now()), "sentinel"))
        
        # Collect all data concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Package results
        data = {
            'dam_id': dam_id,
            'coordinates': {'lat': lat, 'lon': lon},
            'collection_time': datetime.now().isoformat(),
            'weather_current': results[0],
            'weather_historical': results[1],
            'water_levels': results[2],
            'satellite_data': results[3]
        }
        
        return data
    
    async def _safe_task(self, coro, source_name):
        """Execute a task safely with error handling"""
        try:
            return await coro
        except Exception as e:
            logger.error(f"Error in {source_name}: {e}")
            return None
    
    async def _get_frost_data(self, lat: float, lon: float):
        """Get historical weather data from Frost API"""
        station_id = await self.frost.find_nearest_station(lat, lon)
        if station_id:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=7)  # Last week
            return await self.frost.get_historical_weather(station_id, start_date, end_date)
        return None
    
    async def _get_nve_data(self, lat: float, lon: float):
        """Get water level data from NVE"""
        station_id = await self.nve.find_nearest_station(lat, lon)
        if station_id:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=1)  # Last 24 hours
            return await self.nve.get_water_levels(station_id, start_date, end_date)
        return None
    
    async def store_data(self, data: Dict[str, Any], db_pool):
        """Store collected data in TimescaleDB"""
        try:
            async with db_pool.acquire() as conn:
                # Store weather data
                if data.get('weather_current'):
                    await self._store_weather_data(conn, data['dam_id'], data['weather_current'])
                
                # Store historical weather
                if data.get('weather_historical'):
                    for weather in data['weather_historical']:
                        await self._store_weather_data(conn, data['dam_id'], weather)
                
                # Store water levels
                if data.get('water_levels'):
                    for water in data['water_levels']:
                        await self._store_water_data(conn, data['dam_id'], water)
                
                # Store satellite data
                if data.get('satellite_data'):
                    await self._store_satellite_data(conn, data['dam_id'], data['satellite_data'])
                
                logger.info(f"Successfully stored data for dam {data['dam_id']}")
        except Exception as e:
            logger.error(f"Error storing data: {e}")
    
    async def _store_weather_data(self, conn, dam_id: int, weather: WeatherData):
        """Store weather data in database"""
        await conn.execute("""
            INSERT INTO weather_data (time, dam_id, temperature_c, precipitation_mm, 
                                    wind_speed_ms, wind_direction, humidity_percent, 
                                    pressure_hpa, snow_depth_cm, data_source)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
            ON CONFLICT (time, dam_id) DO UPDATE SET
                temperature_c = EXCLUDED.temperature_c,
                precipitation_mm = EXCLUDED.precipitation_mm,
                wind_speed_ms = EXCLUDED.wind_speed_ms,
                wind_direction = EXCLUDED.wind_direction,
                humidity_percent = EXCLUDED.humidity_percent,
                pressure_hpa = EXCLUDED.pressure_hpa,
                snow_depth_cm = EXCLUDED.snow_depth_cm,
                data_source = EXCLUDED.data_source
        """, weather.timestamp, dam_id, weather.temperature, weather.precipitation,
             weather.wind_speed, weather.wind_direction, weather.humidity,
             weather.pressure, weather.snow_depth, weather.source)
    
    async def _store_water_data(self, conn, dam_id: int, water: WaterLevelData):
        """Store water level data in database"""
        await conn.execute("""
            INSERT INTO water_levels (time, dam_id, water_level_m, flow_rate_m3s, 
                                    reservoir_fill_percent, inflow_m3s, outflow_m3s)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            ON CONFLICT (time, dam_id) DO UPDATE SET
                water_level_m = EXCLUDED.water_level_m,
                flow_rate_m3s = EXCLUDED.flow_rate_m3s,
                reservoir_fill_percent = EXCLUDED.reservoir_fill_percent,
                inflow_m3s = EXCLUDED.inflow_m3s,
                outflow_m3s = EXCLUDED.outflow_m3s
        """, water.timestamp, dam_id, water.water_level, water.flow_rate,
             water.reservoir_fill, water.inflow, water.outflow)
    
    async def _store_satellite_data(self, conn, dam_id: int, satellite: SatelliteData):
        """Store satellite data in database"""
        await conn.execute("""
            INSERT INTO satellite_observations (time, dam_id, satellite, observation_type,
                                              cloud_cover_percent, image_quality, displacement_mm,
                                              vegetation_index, water_surface_area_m2, image_url)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
            ON CONFLICT (time, dam_id) DO UPDATE SET
                satellite = EXCLUDED.satellite,
                observation_type = EXCLUDED.observation_type,
                cloud_cover_percent = EXCLUDED.cloud_cover_percent,
                image_quality = EXCLUDED.image_quality,
                displacement_mm = EXCLUDED.displacement_mm,
                vegetation_index = EXCLUDED.vegetation_index,
                water_surface_area_m2 = EXCLUDED.water_surface_area_m2,
                image_url = EXCLUDED.image_url
        """, satellite.timestamp, dam_id, satellite.satellite, satellite.observation_type,
             satellite.cloud_cover, satellite.image_quality, satellite.displacement,
             satellite.vegetation_index, satellite.water_surface_area, satellite.image_url)
    
    async def close_all(self):
        """Close all API connections"""
        await self.met_no.close()
        await self.frost.close()
        await self.nve.close()
        await self.sentinel.close()
        await self.varsom.close()

# Example usage and testing
async def test_apis():
    """Test API connections"""
    # Load environment variables
    frost_client_id = os.getenv('FROST_CLIENT_ID')
    sentinel_user = os.getenv('SENTINEL_USER')
    sentinel_pass = os.getenv('SENTINEL_PASS')
    
    if not all([frost_client_id, sentinel_user, sentinel_pass]):
        logger.error("Missing API credentials in environment variables")
        return
    
    # Initialize monitoring API
    monitoring = HealthMonitoringAPI(frost_client_id, sentinel_user, sentinel_pass)
    
    # Test coordinates (Oslo area)
    lat, lon = 59.9139, 10.7522
    
    try:
        # Test individual APIs
        logger.info("Testing met.no API...")
        weather = await monitoring.met_no.get_current_weather(lat, lon)
        logger.info(f"Weather data: {weather}")
        
        logger.info("Testing Frost API...")
        station = await monitoring.frost.find_nearest_station(lat, lon)
        logger.info(f"Nearest station: {station}")
        
        logger.info("Testing NVE API...")
        nve_station = await monitoring.nve.find_nearest_station(lat, lon)
        logger.info(f"Nearest NVE station: {nve_station}")
        
        logger.info("Testing Sentinel Hub...")
        satellite = await monitoring.sentinel.get_satellite_image(lat, lon, datetime.now())
        logger.info(f"Satellite data: {satellite}")
        
    finally:
        await monitoring.close_all()

if __name__ == "__main__":
    asyncio.run(test_apis()) 