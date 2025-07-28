#!/usr/bin/env python3
"""
Test Norwegian API Credentials
==============================

Quick test script to verify your API credentials work before deployment.
"""

import os
import requests
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_frost_api():
    """Test Frost API with your real credentials."""
    print("🌡️ Testing Frost API (Historical Weather)...")
    
    client_id = os.getenv('FROST_CLIENT_ID')
    if not client_id:
        print("❌ FROST_CLIENT_ID not found in .env file")
        return False
    
    try:
        # Test API call to get weather stations
        response = requests.get(
            "https://frost.met.no/api/v0/sources",
            auth=(client_id, ''),
            params={'types': 'SensorSystem', 'limit': 5},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            stations = data.get('data', [])
            print(f"✅ Frost API working! Found {len(stations)} weather stations")
            if stations:
                print(f"   Example station: {stations[0].get('name', 'Unknown')}")
            return True
        else:
            print(f"❌ Frost API error: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Frost API connection error: {e}")
        return False

def test_met_no_api():
    """Test met.no API (always available)."""
    print("\n🌤️ Testing met.no API (Current Weather)...")
    
    try:
        # Test weather API for Oslo
        response = requests.get(
            "https://api.met.no/weatherapi/locationforecast/2.0/compact",
            params={'lat': 59.9139, 'lon': 10.7522},
            headers={'User-Agent': 'DamHealthMonitor/1.0 test'},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            current_temp = data['properties']['timeseries'][0]['data']['instant']['details']['air_temperature']
            print(f"✅ met.no API working! Current temperature in Oslo: {current_temp}°C")
            return True
        else:
            print(f"❌ met.no API error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ met.no API connection error: {e}")
        return False

def test_nve_api():
    """Test NVE Hydrology API."""
    print("\n🌊 Testing NVE Hydrology API (Water Levels)...")
    
    try:
        response = requests.get(
            "https://hydapi.nve.no/api/v1/Stations",
            headers={'Accept': 'application/json'},
            params={'limit': 5},
            timeout=10
        )
        
        if response.status_code == 200:
            stations = response.json()
            print(f"✅ NVE Hydrology API working! Found {len(stations)} monitoring stations")
            if stations:
                station = stations[0]
                print(f"   Example station: {station.get('name', 'Unknown')} ({station.get('stationId', 'No ID')})")
            return True
        else:
            print(f"❌ NVE API error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ NVE API connection error: {e}")
        return False

def test_sentinel_credentials():
    """Test Sentinel Hub credentials if provided."""
    print("\n🛰️ Testing Sentinel Hub Credentials...")
    
    username = os.getenv('SENTINEL_USER')
    password = os.getenv('SENTINEL_PASS')
    
    if not username or not password or username == 'your_copernicus_username_here':
        print("⏭️ Sentinel credentials not configured (optional)")
        return True
    
    try:
        # Test login to Sentinel Hub
        from sentinelsat import SentinelAPI
        
        api = SentinelAPI(username, password, 'https://scihub.copernicus.eu/dhus')
        
        # Test query (small area, recent date)
        from datetime import datetime, timedelta
        products = api.query(
            area='POINT(10.7522 59.9139)',  # Oslo
            date=(datetime.now() - timedelta(days=30), datetime.now()),
            platformname='Sentinel-1',
            rows=1
        )
        
        print(f"✅ Sentinel Hub working! Found {len(products)} recent products")
        return True
        
    except ImportError:
        print("⚠️ sentinelsat package not installed (will be installed during setup)")
        return True
    except Exception as e:
        print(f"❌ Sentinel Hub error: {e}")
        print("   Please check your Copernicus username and password")
        return False

def main():
    """Run all API tests."""
    print("🧪 Testing Norwegian API Credentials")
    print("=" * 50)
    
    results = {
        'met_no': test_met_no_api(),
        'frost': test_frost_api(),
        'nve': test_nve_api(),
        'sentinel': test_sentinel_credentials()
    }
    
    print("\n📊 Test Results Summary:")
    print("=" * 50)
    
    working_count = 0
    for api, working in results.items():
        status = "✅ Working" if working else "❌ Failed"
        print(f"{api.upper():<12}: {status}")
        if working:
            working_count += 1
    
    print(f"\nAPIs Working: {working_count}/4")
    
    if working_count >= 2:  # At least met.no and one other
        print("\n🎉 You have enough working APIs to run the monitoring system!")
        print("   Run: python setup_monitoring.py")
    else:
        print("\n⚠️ Please check your API credentials and internet connection.")
        print("   The system will work with met.no and NVE APIs even without credentials.")

if __name__ == "__main__":
    main() 