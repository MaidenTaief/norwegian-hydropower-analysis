#!/usr/bin/env python3
"""
ARCTIC WEATHER DATA PROCESSOR
==============================
Real Norwegian Arctic weather data integration from Seklima
Processes CSV data from Norwegian Centre for Climate Services
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class ArcticWeatherProcessor:
    """
    Processes real Arctic weather data from Seklima CSV
    Provides accurate weather conditions for Arctic dam risk analysis
    """
    
    def __init__(self, csv_path: str = "Arctic_table.csv"):
        """Initialize with path to Arctic weather CSV"""
        self.csv_path = Path(csv_path)
        self.weather_data = None
        self.stations = {}
        self.load_weather_data()
    
    def load_weather_data(self):
        """Load and parse the Arctic weather CSV data"""
        try:
            # Read CSV with semicolon separator, skip footer lines with metadata
            self.weather_data = pd.read_csv(
                self.csv_path, 
                sep=';',
                encoding='utf-8',
                skipfooter=1,  # Skip the metadata footer line
                engine='python'  # Required for skipfooter
            )
            
            # Clean column names (original columns from CSV)
            expected_cols = [
                'Name', 'Station', 'Time(norwegian mean time)', 
                'Maximum air temperature (season)', 'Mean air temperature (season)',
                'Mean air temperature, deviation from the 1991-2020 normal (season)',
                'Precipitation (season)', 
                'Mean air temperature, deviation from the 1991-2020 normal (summer or winter half-year)'
            ]
            
            # Rename columns to simpler names
            column_mapping = {
                'Name': 'name',
                'Station': 'station_id', 
                'Time(norwegian mean time)': 'time',
                'Maximum air temperature (season)': 'max_temp',
                'Mean air temperature (season)': 'mean_temp',
                'Mean air temperature, deviation from the 1991-2020 normal (season)': 'temp_anomaly',
                'Precipitation (season)': 'precipitation',
                'Mean air temperature, deviation from the 1991-2020 normal (summer or winter half-year)': 'half_year_anomaly'
            }
            
            self.weather_data = self.weather_data.rename(columns=column_mapping)
            
            # Convert time to proper datetime with flexible parsing
            self.weather_data['time'] = pd.to_datetime(
                self.weather_data['time'], 
                format='mixed',  # Let pandas figure out the format
                errors='coerce'  # Convert invalid dates to NaT
            )
            
            # Remove rows with invalid dates (like the footer)
            self.weather_data = self.weather_data.dropna(subset=['time'])
            
            # Convert numeric columns, handling missing values
            numeric_cols = ['max_temp', 'mean_temp', 'temp_anomaly', 'precipitation']
            for col in numeric_cols:
                self.weather_data[col] = pd.to_numeric(
                    self.weather_data[col], 
                    errors='coerce'
                )
            
            # Create station lookup
            unique_stations = self.weather_data[['name', 'station_id']].drop_duplicates()
            for _, row in unique_stations.iterrows():
                self.stations[row['station_id']] = row['name']
            
            logger.info(f"✅ Loaded Arctic weather data: {len(self.weather_data)} records from {len(self.stations)} stations")
            logger.info(f"📅 Data range: {self.weather_data['time'].min()} to {self.weather_data['time'].max()}")
            
        except Exception as e:
            logger.error(f"❌ Error loading Arctic weather data: {e}")
            self.weather_data = pd.DataFrame()
    
    def get_station_coordinates(self) -> Dict[str, Tuple[float, float]]:
        """Return approximate coordinates for Arctic weather stations"""
        # Known coordinates for the major Arctic stations
        coordinates = {
            'SN90450': (69.679, 18.940),  # Tromsø
            'SN94280': (70.680, 23.668),  # Hammerfest
            'SN98550': (70.373, 31.103),  # Vardø
            'SN99710': (74.518, 19.012),  # Bjørnøya
            'SN93140': (69.976, 23.371),  # Alta
            'SN99370': (69.725, 29.891),  # Kirkenes
            'SN95350': (70.069, 24.967),  # Banak
            'SN84701': (68.439, 17.427),  # Narvik
            'SN82310': (67.267, 14.365),  # Bodø
        }
        return coordinates
    
    def find_nearest_station(self, latitude: float, longitude: float) -> Optional[str]:
        """Find the nearest weather station to given coordinates"""
        coordinates = self.get_station_coordinates()
        min_distance = float('inf')
        nearest_station = None
        
        for station_id, (lat, lon) in coordinates.items():
            # Simple distance calculation (Euclidean)
            distance = np.sqrt((latitude - lat)**2 + (longitude - lon)**2)
            if distance < min_distance:
                min_distance = distance
                nearest_station = station_id
        
        return nearest_station
    
    def get_weather_for_location(self, latitude: float, longitude: float, 
                               year: int = 2023) -> Dict:
        """Get weather data for a specific location and year"""
        
        # Find nearest station
        station_id = self.find_nearest_station(latitude, longitude)
        if not station_id:
            logger.warning(f"No nearby weather station found for {latitude:.3f}°N, {longitude:.3f}°E")
            return self._get_fallback_weather(latitude)
        
        # Get station data for the specified year
        station_data = self.weather_data[
            (self.weather_data['station_id'] == station_id) &
            (self.weather_data['time'].dt.year == year)
        ].copy()
        
        if station_data.empty:
            # Try most recent year available
            station_data = self.weather_data[
                self.weather_data['station_id'] == station_id
            ].copy()
            if not station_data.empty:
                latest_year = station_data['time'].dt.year.max()
                station_data = station_data[station_data['time'].dt.year == latest_year]
        
        if station_data.empty:
            logger.warning(f"No weather data found for station {station_id}")
            return self._get_fallback_weather(latitude)
        
        # Calculate annual statistics
        mean_temp = station_data['mean_temp'].mean()
        max_temp = station_data['max_temp'].max()
        min_temp = station_data['mean_temp'].min()
        total_precip = station_data['precipitation'].sum()
        temp_anomaly = station_data['temp_anomaly'].mean()
        
        # Estimate additional parameters for dam analysis
        winter_temp = station_data[
            station_data['time'].dt.month.isin([12, 1, 2, 3])
        ]['mean_temp'].mean()
        
        summer_temp = station_data[
            station_data['time'].dt.month.isin([6, 7, 8, 9])
        ]['mean_temp'].mean()
        
        # Estimate snow depth based on temperature and precipitation
        winter_precip = station_data[
            station_data['time'].dt.month.isin([12, 1, 2, 3])
        ]['precipitation'].sum()
        
        snow_depth = max(0, winter_precip * 0.01) if winter_temp < 0 else 0
        
        return {
            'air_temperature': mean_temp,
            'winter_temperature': winter_temp if not np.isnan(winter_temp) else mean_temp - 10,
            'summer_temperature': summer_temp if not np.isnan(summer_temp) else mean_temp + 15,
            'max_temperature': max_temp,
            'min_temperature': min_temp,
            'annual_precipitation': total_precip if not np.isnan(total_precip) else 500,
            'snow_depth': snow_depth,
            'temperature_anomaly': temp_anomaly if not np.isnan(temp_anomaly) else 0,
            'wind_speed': 5.0,  # Estimate - not in dataset
            'station_name': self.stations.get(station_id, f"Station {station_id}"),
            'station_id': station_id,
            'data_year': year,
            'source': 'Seklima_Real_Data'
        }
    
    def _get_fallback_weather(self, latitude: float) -> Dict:
        """Fallback weather data if no station data available"""
        # Simple latitude-based estimates for extreme cases
        base_temp = -5 - (latitude - 66.5) * 0.5  # Colder further north
        
        return {
            'air_temperature': base_temp,
            'winter_temperature': base_temp - 10,
            'summer_temperature': base_temp + 15,
            'max_temperature': base_temp + 20,
            'min_temperature': base_temp - 15,
            'annual_precipitation': 400,
            'snow_depth': max(0, -base_temp * 0.1),
            'temperature_anomaly': 1.0,  # Assume warming trend
            'wind_speed': 6.0,
            'station_name': 'Estimated',
            'station_id': 'FALLBACK',
            'data_year': 2023,
            'source': 'Climate_Model_Fallback'
        }
    
    def get_historical_freeze_thaw_cycles(self, latitude: float, longitude: float) -> int:
        """Calculate freeze-thaw cycles from real temperature data"""
        station_id = self.find_nearest_station(latitude, longitude)
        if not station_id:
            return self._estimate_freeze_thaw_cycles(latitude)
        
        # Get multi-year data for the station
        station_data = self.weather_data[
            self.weather_data['station_id'] == station_id
        ].copy()
        
        if station_data.empty:
            return self._estimate_freeze_thaw_cycles(latitude)
        
        # Count seasonal temperature transitions
        # Look for transitions across 0°C between seasons
        cycles = 0
        
        # Group by year and count freeze-thaw transitions
        for year in station_data['time'].dt.year.unique():
            year_data = station_data[station_data['time'].dt.year == year]
            year_data = year_data.sort_values('time')
            
            temps = year_data['mean_temp'].dropna()
            
            # Count zero-crossings (freeze-thaw cycles)
            for i in range(1, len(temps)):
                if (temps.iloc[i-1] < 0 and temps.iloc[i] > 0) or \
                   (temps.iloc[i-1] > 0 and temps.iloc[i] < 0):
                    cycles += 1
        
        # Average over the years and multiply by seasonal factor
        num_years = len(station_data['time'].dt.year.unique())
        avg_cycles_per_year = cycles / max(num_years, 1)
        
        # Scale to estimate daily cycles (rough approximation)
        annual_freeze_thaw_cycles = int(avg_cycles_per_year * 15)  # Seasonal to daily scaling
        
        return max(annual_freeze_thaw_cycles, self._estimate_freeze_thaw_cycles(latitude))
    
    def _estimate_freeze_thaw_cycles(self, latitude: float) -> int:
        """Fallback estimation based on latitude"""
        if latitude > 74:
            return 80  # Far Arctic (Svalbard)
        elif latitude > 70:
            return 60  # High Arctic
        elif latitude > 68:
            return 45  # Mid Arctic
        else:
            return 30  # Arctic Circle
    
    def get_climate_trends(self, latitude: float, longitude: float) -> Dict:
        """Get climate change trends from temperature anomaly data"""
        station_id = self.find_nearest_station(latitude, longitude)
        if not station_id:
            return {'warming_trend': 1.5, 'trend_confidence': 'low'}
        
        station_data = self.weather_data[
            self.weather_data['station_id'] == station_id
        ].copy()
        
        if station_data.empty:
            return {'warming_trend': 1.5, 'trend_confidence': 'low'}
        
        # Calculate warming trend from temperature anomalies
        recent_anomalies = station_data[
            station_data['time'].dt.year >= 2015
        ]['temp_anomaly'].mean()
        
        early_anomalies = station_data[
            station_data['time'].dt.year <= 2010
        ]['temp_anomaly'].mean()
        
        if not np.isnan(recent_anomalies) and not np.isnan(early_anomalies):
            warming_trend = recent_anomalies - early_anomalies
            confidence = 'high'
        else:
            warming_trend = station_data['temp_anomaly'].mean()
            if not np.isnan(warming_trend):
                confidence = 'medium'
            else:
                warming_trend = 1.5
                confidence = 'low'
        
        return {
            'warming_trend': max(warming_trend, 0.5),  # At least some warming
            'trend_confidence': confidence,
            'station_data_years': len(station_data['time'].dt.year.unique())
        }

# Integration function for the main analyzer
async def get_real_arctic_weather_data(latitude: float, longitude: float) -> Dict:
    """
    Get real Arctic weather data for risk analysis
    Replaces the dummy FrostAPI calls
    """
    processor = ArcticWeatherProcessor()
    weather_data = processor.get_weather_for_location(latitude, longitude)
    
    # Format for compatibility with existing analyzer
    return {
        'air_temperature': weather_data['air_temperature'],
        'snow_depth': weather_data['snow_depth'],
        'wind_speed': weather_data['wind_speed'],
        'source': weather_data['source'],
        'station_name': weather_data['station_name'],
        'winter_temperature': weather_data['winter_temperature'],
        'summer_temperature': weather_data['summer_temperature'],
        'temperature_anomaly': weather_data['temperature_anomaly'],
        'precipitation': weather_data['annual_precipitation']
    }

if __name__ == "__main__":
    # Test the processor
    processor = ArcticWeatherProcessor()
    
    print("🔬 TESTING ARCTIC WEATHER PROCESSOR")
    print("="*50)
    
    # Test coordinates for Tromsø area
    test_lat, test_lon = 69.6, 18.9
    
    weather = processor.get_weather_for_location(test_lat, test_lon)
    print(f"\n📍 Weather for {test_lat}°N, {test_lon}°E:")
    print(f"   🌡️  Air temperature: {weather['air_temperature']:.1f}°C")
    print(f"   ❄️  Winter temperature: {weather['winter_temperature']:.1f}°C")
    print(f"   ☀️  Summer temperature: {weather['summer_temperature']:.1f}°C")
    print(f"   🌨️  Snow depth: {weather['snow_depth']:.1f}m")
    print(f"   📈 Temperature anomaly: {weather['temperature_anomaly']:.1f}°C")
    print(f"   📊 Station: {weather['station_name']} ({weather['station_id']})")
    print(f"   🔗 Source: {weather['source']}")
    
    # Test freeze-thaw cycles
    cycles = processor.get_historical_freeze_thaw_cycles(test_lat, test_lon)
    print(f"   ❄️🌡️ Freeze-thaw cycles: {cycles} per year")
    
    print("\n✅ Arctic weather processor ready!") 