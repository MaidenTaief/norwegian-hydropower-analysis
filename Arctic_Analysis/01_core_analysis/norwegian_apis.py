"""
Norwegian APIs stub for Arctic Risk Analyzer
"""

import asyncio
from typing import Optional, Dict
import logging

logger = logging.getLogger(__name__)

class FrostAPI:
    """Stub for FrostAPI to allow the script to run without actual API access"""
    
    def __init__(self, client_id: str):
        self.client_id = client_id
        logger.warning("FrostAPI stub initialized - no real API calls will be made")
    
    async def find_nearest_station(self, latitude: float, longitude: float, 
                                  max_distance_km: float = 50) -> Optional[str]:
        """Stub method that returns a mock station ID"""
        # Return a realistic Norwegian weather station ID format
        return f"SN{int(latitude*100):05d}"
    
    async def get_station_data(self, station_id: str, start_date: str, 
                              end_date: str, elements: str = "mean(air_temperature P1D)") -> Optional[Dict]:
        """Stub method that returns mock weather station data"""
        return {
            "data": [],
            "source": "Frost_API_Stub",
            "station_id": station_id
        }
    
    async def get_historical_weather(self, latitude: float, longitude: float,
                                   start_date: str = "2010-01-01", end_date: str = "2023-12-31",
                                   elements: str = "mean(air_temperature P1D)") -> Optional[Dict]:
        """Stub method that returns mock historical weather data"""
        return {
            "data": [],
            "source": "Frost_API_Historical_Stub",
            "location": {"lat": latitude, "lon": longitude},
            "elements": elements
        }
    
    async def get_historical_freeze_thaw_cycles(self, latitude: float, longitude: float, 
                                               start_year: int = 2010, end_year: int = 2023) -> Optional[int]:
        """Stub method that returns an estimated freeze-thaw cycle count"""
        # Simple estimation based on latitude - further north = more cycles
        if latitude > 70:
            return 80  # Far Arctic
        elif latitude > 68:
            return 60  # High Arctic  
        else:
            return 40  # Arctic Circle 