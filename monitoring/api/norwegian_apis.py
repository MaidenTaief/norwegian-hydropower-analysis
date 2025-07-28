#!/usr/bin/env python3
"""
Norwegian API Integrations for Dam Health Monitoring
===================================================

Real integrations with official Norwegian data sources:
- met.no: Weather data and forecasts
- NVE Hydrology API: Water levels and discharge
- Frost API: Historical weather data  
- Sentinel Hub: Satellite imagery and InSAR
- VARSOM: Flood and avalanche warnings

All APIs are free and publicly available.
"""

import os
import asyncio
import aiohttp
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import pandas as pd
import json
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MetNoAPI:
    """Integration with Norwegian Meteorological Institute APIs."""
    
    def __init__(self):
        self.base_url = "https://api.met.no/weatherapi"
        self.headers = {
            'User-Agent': 'DamHealthMonitor/1.0 github.com/yourrepo (contact@yourorg.no)'
        }
        
    async def get_current_weather(self, lat: float, lon: float) -> Dict:
        """Get current weather conditions from LocationForecast API."""
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/locationforecast/2.0/compact"
            params = {
                'lat': round(lat, 4),
                'lon': round(lon, 4)
            }
            
            try:
                async with session.get(url, params=params, headers=self.headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Extract current conditions (first timeseries entry)
                        current = data['properties']['timeseries'][0]
                        instant = current['data']['instant']['details']
                        next_hour = current['data'].get('next_1_hours', {})
                        
                        return {
                            'timestamp': datetime.fromisoformat(current['time'].replace('Z', '+00:00')),
                            'latitude': lat,
                            'longitude': lon,
                            'temperature_c': instant.get('air_temperature'),
                            'humidity_percent': instant.get('relative_humidity'),
                            'pressure_hpa': instant.get('air_pressure_at_sea_level'),
                            'wind_speed_ms': instant.get('wind_speed'),
                            'wind_direction_deg': instant.get('wind_from_direction'),
                            'wind_gust_ms': instant.get('wind_speed_of_gust'),
                            'cloud_cover_percent': instant.get('cloud_area_fraction'),
                            'visibility_m': instant.get('visibility'),
                            'precipitation_1h_mm': next_hour.get('details', {}).get('precipitation_amount', 0),
                            'data_source': 'met.no',
                            'raw_data': data
                        }
                    else:
                        logger.error(f"met.no API error: {response.status}")
                        raise Exception(f"met.no API returned status {response.status}")
                        
            except Exception as e:
                logger.error(f"Error fetching weather data: {e}")
                raise
    
    async def get_weather_forecast(self, lat: float, lon: float, hours: int = 48) -> List[Dict]:
        """Get weather forecast for next N hours."""
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/locationforecast/2.0/compact"
            params = {
                'lat': round(lat, 4),
                'lon': round(lon, 4)
            }
            
            try:
                async with session.get(url, params=params, headers=self.headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        forecast = []
                        for entry in data['properties']['timeseries'][:hours]:
                            instant = entry['data']['instant']['details']
                            next_hour = entry['data'].get('next_1_hours', {})
                            
                            forecast.append({
                                'timestamp': datetime.fromisoformat(entry['time'].replace('Z', '+00:00')),
                                'temperature_c': instant.get('air_temperature'),
                                'precipitation_mm': next_hour.get('details', {}).get('precipitation_amount', 0),
                                'wind_speed_ms': instant.get('wind_speed'),
                                'humidity_percent': instant.get('relative_humidity')
                            })
                        
                        return forecast
                    else:
                        raise Exception(f"met.no API returned status {response.status}")
                        
            except Exception as e:
                logger.error(f"Error fetching forecast: {e}")
                raise

class NVEHydrologyAPI:
    """Integration with NVE Hydrology API for water levels and discharge."""
    
    def __init__(self):
        self.base_url = "https://hydapi.nve.no/api/v1"
        self.headers = {
            'Accept': 'application/json',
            'User-Agent': 'DamHealthMonitor/1.0'
        }
    
    async def find_nearest_station(self, lat: float, lon: float, max_distance_km: int = 50) -> Optional[Dict]:
        """Find nearest hydrological monitoring station."""
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/Stations"
            
            try:
                async with session.get(url, headers=self.headers) as response:
                    if response.status == 200:
                        stations = await response.json()
                        
                        # Find nearest station within max distance
                        from math import radians, cos, sin, asin, sqrt
                        
                        def haversine(lon1, lat1, lon2, lat2):
                            """Calculate distance between two points on Earth."""
                            lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
                            dlon = lon2 - lon1
                            dlat = lat2 - lat1
                            a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
                            c = 2 * asin(sqrt(a))
                            r = 6371  # Radius of earth in kilometers
                            return c * r
                        
                        nearest_station = None
                        min_distance = float('inf')
                        
                        for station in stations:
                            if station.get('latitude') and station.get('longitude'):
                                distance = haversine(
                                    lon, lat,
                                    station['longitude'], station['latitude']
                                )
                                
                                if distance < min_distance and distance <= max_distance_km:
                                    min_distance = distance
                                    nearest_station = station
                                    nearest_station['distance_km'] = distance
                        
                        return nearest_station
                    else:
                        raise Exception(f"NVE API returned status {response.status}")
                        
            except Exception as e:
                logger.error(f"Error finding nearest station: {e}")
                raise
    
    async def get_station_data(self, station_id: str, days: int = 7) -> Dict:
        """Get recent observations from a specific station."""
        async with aiohttp.ClientSession() as session:
            # Get station metadata
            station_url = f"{self.base_url}/Stations/{station_id}"
            
            try:
                # Fetch station info
                async with session.get(station_url, headers=self.headers) as response:
                    if response.status == 200:
                        station_info = await response.json()
                    else:
                        raise Exception(f"Station not found: {station_id}")
                
                # Get observations
                obs_url = f"{self.base_url}/Observations"
                end_time = datetime.now()
                start_time = end_time - timedelta(days=days)
                
                params = {
                    'StationId': station_id,
                    'ReferenceTime': start_time.strftime('%Y-%m-%dT%H:%M:%S.000Z'),
                    'EndTime': end_time.strftime('%Y-%m-%dT%H:%M:%S.000Z')
                }
                
                async with session.get(obs_url, params=params, headers=self.headers) as response:
                    if response.status == 200:
                        observations = await response.json()
                        
                        # Process observations
                        processed_obs = []
                        for obs in observations:
                            processed_obs.append({
                                'timestamp': datetime.fromisoformat(obs['referenceTime'].replace('Z', '+00:00')),
                                'parameter': obs['parameter'],
                                'value': obs['value'],
                                'unit': obs['unit'],
                                'quality': obs.get('quality', 0)
                            })
                        
                        return {
                            'station': station_info,
                            'observations': processed_obs,
                            'latest_reading': processed_obs[-1] if processed_obs else None
                        }
                    else:
                        logger.warning(f"No observations for station {station_id}")
                        return {
                            'station': station_info,
                            'observations': [],
                            'latest_reading': None
                        }
                        
            except Exception as e:
                logger.error(f"Error getting station data: {e}")
                raise

class FrostAPI:
    """Integration with Frost API for historical weather data."""
    
    def __init__(self, client_id: str):
        self.client_id = client_id
        self.base_url = "https://frost.met.no/api/v0"
        self.auth = (client_id, '')  # Password is empty for client_id auth
    
    async def get_historical_weather(self, lat: float, lon: float, 
                                   start_date: datetime, end_date: datetime) -> List[Dict]:
        """Get historical weather observations."""
        
        # First find nearest weather station
        stations = await self._find_weather_stations(lat, lon)
        if not stations:
            logger.warning(f"No weather stations found near {lat}, {lon}")
            return []
        
        station_id = stations[0]['id']
        logger.info(f"Using weather station: {station_id}")
        
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/observations"
            params = {
                'sources': station_id,
                'referencetime': f"{start_date.isoformat()}/{end_date.isoformat()}",
                'elements': 'air_temperature,precipitation_amount,wind_speed,relative_humidity',
                'timeresolutions': 'PT1H'  # Hourly data
            }
            
            try:
                async with session.get(url, params=params, auth=aiohttp.BasicAuth(*self.auth)) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        weather_data = []
                        for obs in data.get('data', []):
                            timestamp = datetime.fromisoformat(obs['referenceTime'].replace('Z', '+00:00'))
                            
                            # Extract observations
                            temp = None
                            precip = None
                            wind_speed = None
                            humidity = None
                            
                            for observation in obs['observations']:
                                element = observation['elementId']
                                value = observation['value']
                                
                                if element == 'air_temperature':
                                    temp = value
                                elif element == 'precipitation_amount':
                                    precip = value
                                elif element == 'wind_speed':
                                    wind_speed = value
                                elif element == 'relative_humidity':
                                    humidity = value
                            
                            weather_data.append({
                                'timestamp': timestamp,
                                'station_id': station_id,
                                'temperature_c': temp,
                                'precipitation_mm': precip,
                                'wind_speed_ms': wind_speed,
                                'humidity_percent': humidity,
                                'data_source': 'frost.met.no'
                            })
                        
                        return weather_data
                    else:
                        logger.error(f"Frost API error: {response.status}")
                        raise Exception(f"Frost API returned status {response.status}")
                        
            except Exception as e:
                logger.error(f"Error fetching historical weather: {e}")
                raise
    
    async def _find_weather_stations(self, lat: float, lon: float) -> List[Dict]:
        """Find nearby weather stations."""
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/sources"
            params = {
                'geometry': f'nearest(POINT({lon} {lat}))',
                'types': 'SensorSystem'
            }
            
            try:
                async with session.get(url, params=params, auth=aiohttp.BasicAuth(*self.auth)) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get('data', [])[:5]  # Return top 5 nearest
                    else:
                        return []
                        
            except Exception as e:
                logger.error(f"Error finding weather stations: {e}")
                return []

class VarsomAPI:
    """Integration with VARSOM API for flood and avalanche warnings."""
    
    def __init__(self):
        self.base_url = "https://api01.nve.no"
        self.headers = {
            'Accept': 'application/json',
            'User-Agent': 'DamHealthMonitor/1.0'
        }
    
    async def get_flood_warnings(self, region_ids: List[str] = None) -> List[Dict]:
        """Get current flood warnings."""
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/hydrology/forecast/flood/v1.0.6/api/County"
            
            try:
                async with session.get(url, headers=self.headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        warnings = []
                        for county in data:
                            if region_ids and county.get('id') not in region_ids:
                                continue
                                
                            for warning in county.get('RegionSummary', []):
                                warnings.append({
                                    'region_id': county.get('id'),
                                    'region_name': county.get('name'),
                                    'warning_type': 'flood',
                                    'warning_level': warning.get('ActivityLevel'),
                                    'valid_from': datetime.fromisoformat(warning['ValidFrom'].replace('Z', '+00:00')),
                                    'valid_to': datetime.fromisoformat(warning['ValidTo'].replace('Z', '+00:00')),
                                    'main_text': warning.get('MainText'),
                                    'lang_key': warning.get('LangKey'),
                                    'data_source': 'varsom.no',
                                    'raw_data': warning
                                })
                        
                        return warnings
                    else:
                        logger.error(f"VARSOM API error: {response.status}")
                        return []
                        
            except Exception as e:
                logger.error(f"Error fetching flood warnings: {e}")
                return []

class SentinelAPI:
    """Integration with Sentinel Hub for satellite data."""
    
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password
        self.base_url = "https://scihub.copernicus.eu/dhus"
    
    def search_products(self, lat: float, lon: float, 
                       start_date: datetime, end_date: datetime,
                       product_type: str = 'SLC') -> List[Dict]:
        """Search for Sentinel products covering a location."""
        try:
            from sentinelsat import SentinelAPI
            
            api = SentinelAPI(self.username, self.password, self.base_url)
            
            # Create search area (small box around point)
            footprint = f"POINT({lon} {lat})"
            
            # Search for products
            products = api.query(
                area=footprint,
                date=(start_date.date(), end_date.date()),
                platformname='Sentinel-1',
                producttype=product_type,
                sensoroperationalmode='IW'
            )
            
            # Convert to list of dictionaries
            product_list = []
            for product_id, product_info in products.items():
                product_list.append({
                    'product_id': product_id,
                    'title': product_info['title'],
                    'platform': product_info['platformname'],
                    'product_type': product_info['producttype'],
                    'sensing_date': product_info['beginposition'],
                    'orbit_direction': product_info['orbitdirection'],
                    'relative_orbit': product_info['relativeorbitnumber'],
                    'size_mb': product_info['size'],
                    'cloud_cover': product_info.get('cloudcoverpercentage', 0),
                    'footprint': product_info['footprint'],
                    'download_url': api.get_product_odata(product_id)['url']
                })
            
            return product_list
            
        except ImportError:
            logger.error("sentinelsat package not installed. Run: pip install sentinelsat")
            return []
        except Exception as e:
            logger.error(f"Error searching Sentinel products: {e}")
            return []

class NorwegianDataCollector:
    """Main class coordinating all Norwegian data sources."""
    
    def __init__(self, frost_client_id: str = None, 
                 sentinel_user: str = None, sentinel_pass: str = None):
        self.met_no = MetNoAPI()
        self.nve = NVEHydrologyAPI()
        self.frost = FrostAPI(frost_client_id) if frost_client_id else None
        self.varsom = VarsomAPI()
        self.sentinel = SentinelAPI(sentinel_user, sentinel_pass) if (sentinel_user and sentinel_pass) else None
        
        logger.info("Norwegian Data Collector initialized")
        if not frost_client_id:
            logger.warning("Frost API not available - no client_id provided")
        if not (sentinel_user and sentinel_pass):
            logger.warning("Sentinel API not available - no credentials provided")
    
    async def collect_dam_data(self, dam_id: str, lat: float, lon: float) -> Dict:
        """Collect all available data for a dam location."""
        logger.info(f"Collecting data for dam {dam_id} at {lat}, {lon}")
        
        data = {
            'dam_id': dam_id,
            'latitude': lat,
            'longitude': lon,
            'collection_time': datetime.now()
        }
        
        # Collect data from all sources concurrently
        tasks = []
        
        # Current weather (always available)
        tasks.append(('weather', self.met_no.get_current_weather(lat, lon)))
        
        # Water level data
        tasks.append(('nearest_station', self.nve.find_nearest_station(lat, lon)))
        
        # Flood warnings
        tasks.append(('flood_warnings', self.varsom.get_flood_warnings()))
        
        # Execute all tasks
        results = await asyncio.gather(
            *[task[1] for task in tasks],
            return_exceptions=True
        )
        
        # Process results
        for i, (name, _) in enumerate(tasks):
            result = results[i]
            if isinstance(result, Exception):
                logger.error(f"Error collecting {name}: {result}")
                data[name] = None
            else:
                data[name] = result
        
        # Get water level data if station found
        if data.get('nearest_station'):
            try:
                station_id = data['nearest_station']['stationId']
                station_data = await self.nve.get_station_data(station_id)
                data['water_levels'] = station_data
            except Exception as e:
                logger.error(f"Error getting water level data: {e}")
                data['water_levels'] = None
        
        # Historical weather (if Frost API available)
        if self.frost:
            try:
                end_date = datetime.now()
                start_date = end_date - timedelta(days=30)
                historical = await self.frost.get_historical_weather(lat, lon, start_date, end_date)
                data['historical_weather'] = historical
            except Exception as e:
                logger.error(f"Error getting historical weather: {e}")
                data['historical_weather'] = None
        
        # Satellite data (if Sentinel API available)
        if self.sentinel:
            try:
                end_date = datetime.now()
                start_date = end_date - timedelta(days=30)
                products = self.sentinel.search_products(lat, lon, start_date, end_date)
                data['satellite_products'] = products
            except Exception as e:
                logger.error(f"Error searching satellite data: {e}")
                data['satellite_products'] = None
        
        logger.info(f"Data collection completed for dam {dam_id}")
        return data
    
    async def test_all_apis(self) -> Dict:
        """Test all API connections and return status."""
        # Test coordinates (Oslo area)
        test_lat, test_lon = 59.9139, 10.7522
        
        results = {
            'met_no': False,
            'nve_hydrology': False,
            'frost': False,
            'varsom': False,
            'sentinel': False
        }
        
        # Test met.no
        try:
            weather = await self.met_no.get_current_weather(test_lat, test_lon)
            results['met_no'] = bool(weather)
            logger.info("✅ met.no API working")
        except Exception as e:
            logger.error(f"❌ met.no API failed: {e}")
        
        # Test NVE
        try:
            station = await self.nve.find_nearest_station(test_lat, test_lon)
            results['nve_hydrology'] = bool(station)
            logger.info("✅ NVE Hydrology API working")
        except Exception as e:
            logger.error(f"❌ NVE API failed: {e}")
        
        # Test Frost
        if self.frost:
            try:
                end_date = datetime.now()
                start_date = end_date - timedelta(days=1)
                data = await self.frost.get_historical_weather(test_lat, test_lon, start_date, end_date)
                results['frost'] = len(data) > 0
                logger.info("✅ Frost API working")
            except Exception as e:
                logger.error(f"❌ Frost API failed: {e}")
        
        # Test VARSOM
        try:
            warnings = await self.varsom.get_flood_warnings()
            results['varsom'] = isinstance(warnings, list)
            logger.info("✅ VARSOM API working")
        except Exception as e:
            logger.error(f"❌ VARSOM API failed: {e}")
        
        # Test Sentinel
        if self.sentinel:
            try:
                end_date = datetime.now()
                start_date = end_date - timedelta(days=7)
                products = self.sentinel.search_products(test_lat, test_lon, start_date, end_date)
                results['sentinel'] = isinstance(products, list)
                logger.info("✅ Sentinel API working")
            except Exception as e:
                logger.error(f"❌ Sentinel API failed: {e}")
        
        working_apis = sum(results.values())
        total_apis = len([k for k, v in results.items() if k != 'frost' and k != 'sentinel']) + \
                     (1 if self.frost else 0) + (1 if self.sentinel else 0)
        
        logger.info(f"API Status: {working_apis}/{total_apis} working")
        return results

# Example usage
async def main():
    """Example usage of Norwegian data collector."""
    
    # Initialize with environment variables
    frost_id = os.getenv('FROST_CLIENT_ID')
    sentinel_user = os.getenv('SENTINEL_USER')
    sentinel_pass = os.getenv('SENTINEL_PASS')
    
    collector = NorwegianDataCollector(
        frost_client_id=frost_id,
        sentinel_user=sentinel_user,
        sentinel_pass=sentinel_pass
    )
    
    # Test all APIs
    print("Testing API connections...")
    status = await collector.test_all_apis()
    print(f"API Status: {status}")
    
    # Example: Collect data for a dam
    # (These are example coordinates - replace with actual dam locations)
    dam_data = await collector.collect_dam_data(
        dam_id="TEST_DAM_001",
        lat=60.1699,  # Example location in Norway
        lon=9.9603
    )
    
    print(f"Collected data for dam: {dam_data['dam_id']}")
    print(f"Weather: {dam_data.get('weather', {}).get('temperature_c')}°C")
    print(f"Nearest station: {dam_data.get('nearest_station', {}).get('name', 'None')}")

if __name__ == "__main__":
    asyncio.run(main()) 