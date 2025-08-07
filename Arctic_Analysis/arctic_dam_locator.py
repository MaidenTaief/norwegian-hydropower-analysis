#!/usr/bin/env python3
"""
ARCTIC DAM LOCATOR - REAL NVE DATA INTEGRATION
==============================================
Automatically identifies Norwegian dams above the Arctic Circle (66.5°N)
Uses real NVE dataset with coordinate transformation and Arctic Circle visualization
"""

import pandas as pd
import geopandas as gpd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import logging
from dataclasses import dataclass
import asyncpg

logger = logging.getLogger(__name__)

@dataclass
class ArcticDam:
    """Structure for Arctic dam information"""
    dam_nr: Optional[str]
    dam_name: str
    latitude: float
    longitude: float
    status: str
    construction_year: Optional[int]
    purpose: str
    owner: str
    county: str = None
    municipality: str = None
    arctic_distance_km: float = 0.0  # Distance north of Arctic Circle

class ArcticDamLocator:
    """
    Locates and analyzes Norwegian dams above the Arctic Circle
    Uses real NVE dataset with accurate coordinates
    """
    
    # Arctic Circle latitude
    ARCTIC_CIRCLE_LATITUDE = 66.5  # 66°33′N
    
    def __init__(self, nve_data_path: Optional[str] = None):
        """
        Initialize with path to NVE data
        
        Args:
            nve_data_path: Path to Norway_Analysis directory with NVE data
        """
        if nve_data_path is None:
            # Default to Norway_Analysis directory where the NVE data is located
            self.nve_data_path = Path(__file__).parent.parent / "Norway_Analysis"
        else:
            self.nve_data_path = Path(nve_data_path)
        
        self.dam_data = None
        self.arctic_dams = []
        
    def load_nve_dam_data(self) -> bool:
        """Load real NVE dam data with coordinates"""
        
        try:
            # Load dam point data with geometry
            dam_file = self.nve_data_path / "Vannkraft_DamPunkt_with_geometry.csv"
            
            if not dam_file.exists():
                logger.error(f"NVE dam data not found at: {dam_file}")
                return False
            
            logger.info(f"📂 Loading NVE dam data from: {dam_file}")
            
            # Read the CSV data
            dam_df = pd.read_csv(dam_file)
            
            # Convert to GeoDataFrame
            self.dam_data = gpd.GeoDataFrame(
                dam_df, 
                geometry=gpd.GeoSeries.from_wkt(dam_df['geometry_wkt'])
            )
            
            # Set CRS - NVE data is typically in UTM 33N (EPSG:25833)
            self.dam_data.crs = 'EPSG:25833'
            
            # Convert to WGS84 (lat/lon)
            if self.dam_data.crs.to_string() != 'EPSG:4326':
                self.dam_data = self.dam_data.to_crs('EPSG:4326')
                logger.info("✅ Converted coordinates to WGS84 (lat/lon)")
            
            # Extract latitude and longitude
            self.dam_data['latitude'] = self.dam_data.geometry.y
            self.dam_data['longitude'] = self.dam_data.geometry.x
            
            # Clean and filter data
            self.dam_data = self.dam_data.dropna(subset=['latitude', 'longitude'])
            
            # Filter for Norwegian territory (basic bounds check)
            norway_bounds = {
                'lat_min': 57.0, 'lat_max': 81.0,  # Including Svalbard
                'lon_min': 4.0, 'lon_max': 32.0
            }
            
            self.dam_data = self.dam_data[
                (self.dam_data['latitude'] >= norway_bounds['lat_min']) &
                (self.dam_data['latitude'] <= norway_bounds['lat_max']) &
                (self.dam_data['longitude'] >= norway_bounds['lon_min']) &
                (self.dam_data['longitude'] <= norway_bounds['lon_max'])
            ]
            
            logger.info(f"✅ Loaded {len(self.dam_data)} Norwegian dams with valid coordinates")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to load NVE dam data: {e}")
            return False
    
    def identify_arctic_dams(self) -> List[ArcticDam]:
        """Identify all dams above the Arctic Circle"""
        
        if self.dam_data is None:
            logger.error("No dam data loaded. Call load_nve_dam_data() first.")
            return []
        
        # Filter dams above Arctic Circle
        arctic_dam_data = self.dam_data[
            self.dam_data['latitude'] > self.ARCTIC_CIRCLE_LATITUDE
        ].copy()
        
        logger.info(f"❄️ Found {len(arctic_dam_data)} dams above Arctic Circle ({self.ARCTIC_CIRCLE_LATITUDE}°N)")
        
        # Convert to ArcticDam objects
        self.arctic_dams = []
        
        for _, dam in arctic_dam_data.iterrows():
            # Calculate distance north of Arctic Circle
            arctic_distance = self._calculate_arctic_distance(dam['latitude'])
            
            arctic_dam = ArcticDam(
                dam_nr=str(dam.get('damNr', '')).strip() if pd.notna(dam.get('damNr')) else None,
                dam_name=str(dam.get('damNavn', 'Unnamed Dam')).strip(),
                latitude=float(dam['latitude']),
                longitude=float(dam['longitude']),
                status=str(dam.get('status', 'Unknown')),
                construction_year=int(dam['idriftAar']) if pd.notna(dam.get('idriftAar')) else None,
                purpose=str(dam.get('formal_L', 'Unknown')),
                owner=str(dam.get('ansvarlig', 'Unknown')),
                arctic_distance_km=arctic_distance
            )
            
            self.arctic_dams.append(arctic_dam)
        
        # Sort by distance from Arctic Circle (most northern first)
        self.arctic_dams.sort(key=lambda d: d.latitude, reverse=True)
        
        return self.arctic_dams
    
    def _calculate_arctic_distance(self, latitude: float) -> float:
        """Calculate distance north of Arctic Circle in kilometers"""
        
        # Rough conversion: 1 degree latitude ≈ 111 km
        degrees_north = latitude - self.ARCTIC_CIRCLE_LATITUDE
        distance_km = degrees_north * 111.32  # More precise conversion
        
        return max(0, distance_km)
    
    def get_arctic_statistics(self) -> Dict:
        """Get comprehensive statistics about Arctic dams"""
        
        if not self.arctic_dams:
            return {"error": "No Arctic dams identified"}
        
        # Basic statistics
        latitudes = [dam.latitude for dam in self.arctic_dams]
        construction_years = [dam.construction_year for dam in self.arctic_dams if dam.construction_year]
        
        # Group by purpose
        purpose_counts = {}
        for dam in self.arctic_dams:
            purpose = dam.purpose
            purpose_counts[purpose] = purpose_counts.get(purpose, 0) + 1
        
        # Group by decade
        decade_counts = {}
        for year in construction_years:
            decade = (year // 10) * 10
            decade_counts[decade] = decade_counts.get(decade, 0) + 1
        
        # Arctic regions (rough classification)
        regions = {
            "Far Arctic (>70°N)": len([d for d in self.arctic_dams if d.latitude > 70]),
            "High Arctic (68-70°N)": len([d for d in self.arctic_dams if 68 <= d.latitude <= 70]),
            "Arctic Circle (66.5-68°N)": len([d for d in self.arctic_dams if 66.5 <= d.latitude < 68])
        }
        
        statistics = {
            "total_arctic_dams": len(self.arctic_dams),
            "northernmost_dam": {
                "name": self.arctic_dams[0].dam_name,
                "latitude": self.arctic_dams[0].latitude,
                "longitude": self.arctic_dams[0].longitude
            },
            "southernmost_arctic_dam": {
                "name": self.arctic_dams[-1].dam_name,
                "latitude": self.arctic_dams[-1].latitude,
                "longitude": self.arctic_dams[-1].longitude
            },
            "latitude_range": {
                "min": min(latitudes),
                "max": max(latitudes),
                "mean": np.mean(latitudes),
                "std": np.std(latitudes)
            },
            "construction_period": {
                "earliest": min(construction_years) if construction_years else None,
                "latest": max(construction_years) if construction_years else None,
                "mean_year": np.mean(construction_years) if construction_years else None
            },
            "by_purpose": purpose_counts,
            "by_decade": decade_counts,
            "by_arctic_region": regions,
            "arctic_circle_latitude": self.ARCTIC_CIRCLE_LATITUDE
        }
        
        return statistics
    
    def create_arctic_visualization(self, save_path: Optional[str] = None) -> str:
        """Create comprehensive Arctic Circle visualization"""
        
        if self.dam_data is None:
            raise ValueError("No dam data loaded")
        
        # Create figure
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 10))
        fig.suptitle('Norwegian Dams - Arctic Circle Analysis', fontsize=16, fontweight='bold')
        
        # Left plot: All Norwegian dams with Arctic Circle
        self._plot_norway_with_arctic_circle(ax1)
        
        # Right plot: Arctic dams detail
        self._plot_arctic_dams_detail(ax2)
        
        # Save the plot
        if save_path is None:
            save_path = Path("arctic_dams_analysis.png")
        else:
            save_path = Path(save_path)
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()
        
        logger.info(f"✅ Arctic visualization saved to: {save_path}")
        
        return str(save_path)
    
    def _plot_norway_with_arctic_circle(self, ax):
        """Plot all Norwegian dams with Arctic Circle line"""
        
        # Plot all dams
        non_arctic = self.dam_data[self.dam_data['latitude'] <= self.ARCTIC_CIRCLE_LATITUDE]
        arctic = self.dam_data[self.dam_data['latitude'] > self.ARCTIC_CIRCLE_LATITUDE]
        
        # Plot non-Arctic dams
        ax.scatter(non_arctic['longitude'], non_arctic['latitude'], 
                  c='blue', s=15, alpha=0.6, label=f'Non-Arctic Dams ({len(non_arctic)})')
        
        # Plot Arctic dams
        ax.scatter(arctic['longitude'], arctic['latitude'], 
                  c='red', s=25, alpha=0.8, label=f'Arctic Dams ({len(arctic)})')
        
        # Draw Arctic Circle line
        lon_range = np.linspace(self.dam_data['longitude'].min() - 1, 
                               self.dam_data['longitude'].max() + 1, 100)
        arctic_circle_line = np.full_like(lon_range, self.ARCTIC_CIRCLE_LATITUDE)
        
        ax.plot(lon_range, arctic_circle_line, 'r--', linewidth=3, 
               label=f'Arctic Circle ({self.ARCTIC_CIRCLE_LATITUDE}°N)')
        
        # Styling
        ax.set_xlim(4, 32)  # Norway longitude range
        ax.set_ylim(57, 72)  # Norway latitude range
        ax.set_xlabel('Longitude (°E)')
        ax.set_ylabel('Latitude (°N)')
        ax.set_title('All Norwegian Dams\nArctic Circle Division')
        ax.grid(True, alpha=0.3)
        ax.legend()
        
        # Add annotations for key Arctic regions
        ax.annotate('Svalbard Region', xy=(15, 79), xytext=(20, 77),
                   arrowprops=dict(arrowstyle='->', color='gray'),
                   fontsize=10, ha='center')
        
        ax.annotate('Norwegian Arctic\nMainland', xy=(25, 70), xytext=(28, 68),
                   arrowprops=dict(arrowstyle='->', color='gray'),
                   fontsize=10, ha='center')
    
    def _plot_arctic_dams_detail(self, ax):
        """Plot detailed view of Arctic dams"""
        
        if not self.arctic_dams:
            ax.text(0.5, 0.5, 'No Arctic dams found', ha='center', va='center', transform=ax.transAxes)
            return
        
        # Get Arctic dam coordinates
        arctic_lats = [dam.latitude for dam in self.arctic_dams]
        arctic_lons = [dam.longitude for dam in self.arctic_dams]
        
        # Color by distance from Arctic Circle
        distances = [dam.arctic_distance_km for dam in self.arctic_dams]
        
        # Create scatter plot with color scale
        scatter = ax.scatter(arctic_lons, arctic_lats, c=distances, 
                           s=50, cmap='Reds', alpha=0.8, edgecolors='black')
        
        # Add colorbar
        cbar = plt.colorbar(scatter, ax=ax)
        cbar.set_label('Distance North of Arctic Circle (km)')
        
        # Draw Arctic Circle line
        lon_range = np.linspace(min(arctic_lons) - 2, max(arctic_lons) + 2, 100)
        arctic_circle_line = np.full_like(lon_range, self.ARCTIC_CIRCLE_LATITUDE)
        ax.plot(lon_range, arctic_circle_line, 'g--', linewidth=2, 
               label=f'Arctic Circle ({self.ARCTIC_CIRCLE_LATITUDE}°N)')
        
        # Annotate northernmost dams
        for i, dam in enumerate(self.arctic_dams[:5]):  # Top 5 northernmost
            ax.annotate(dam.dam_name if dam.dam_name != 'Unnamed Dam' else f'Dam {i+1}',
                       xy=(dam.longitude, dam.latitude),
                       xytext=(5, 5), textcoords='offset points',
                       fontsize=8, ha='left', bbox=dict(boxstyle='round,pad=0.3', 
                                                       facecolor='yellow', alpha=0.7))
        
        # Styling
        ax.set_xlabel('Longitude (°E)')
        ax.set_ylabel('Latitude (°N)')
        ax.set_title('Arctic Dams Detail View\nColor: Distance from Arctic Circle')
        ax.grid(True, alpha=0.3)
        ax.legend()
        
        # Set appropriate bounds for Arctic region
        if arctic_lats and arctic_lons:
            lat_margin = (max(arctic_lats) - min(arctic_lats)) * 0.1
            lon_margin = (max(arctic_lons) - min(arctic_lons)) * 0.1
            
            ax.set_xlim(min(arctic_lons) - lon_margin, max(arctic_lons) + lon_margin)
            ax.set_ylim(min(arctic_lats) - lat_margin, max(arctic_lats) + lat_margin)
    
    def export_arctic_dams_data(self, export_path: Optional[str] = None) -> str:
        """Export Arctic dams data to CSV"""
        
        if not self.arctic_dams:
            raise ValueError("No Arctic dams to export")
        
        # Convert to DataFrame
        export_data = []
        for dam in self.arctic_dams:
            export_data.append({
                'dam_nr': dam.dam_nr,
                'dam_name': dam.dam_name,
                'latitude': dam.latitude,
                'longitude': dam.longitude,
                'status': dam.status,
                'construction_year': dam.construction_year,
                'purpose': dam.purpose,
                'owner': dam.owner,
                'arctic_distance_km': dam.arctic_distance_km,
                'arctic_region': self._classify_arctic_region(dam.latitude)
            })
        
        df = pd.DataFrame(export_data)
        
        if export_path is None:
            export_path = "norwegian_arctic_dams.csv"
        
        df.to_csv(export_path, index=False)
        logger.info(f"✅ Arctic dams data exported to: {export_path}")
        
        return export_path
    
    def _classify_arctic_region(self, latitude: float) -> str:
        """Classify Arctic region based on latitude"""
        if latitude > 70:
            return "Far Arctic"
        elif latitude > 68:
            return "High Arctic"
        else:
            return "Arctic Circle"
    
    def get_arctic_dams_for_analysis(self) -> List[Dict]:
        """Get Arctic dams formatted for risk analysis"""
        
        return [
            {
                "dam_id": i + 1,  # Sequential ID for analysis
                "dam_nr": dam.dam_nr,
                "name": dam.dam_name,
                "latitude": dam.latitude,
                "longitude": dam.longitude,
                "construction_year": dam.construction_year,
                "arctic_distance_km": dam.arctic_distance_km,
                "arctic_region": self._classify_arctic_region(dam.latitude)
            }
            for i, dam in enumerate(self.arctic_dams)
        ]

# Integration function for Arctic risk analyzer
async def get_real_arctic_dams(nve_data_path: Optional[str] = None) -> List[Dict]:
    """
    Get real Arctic dams from NVE dataset for risk analysis
    
    Returns:
        List of Arctic dams with coordinates and metadata
    """
    
    try:
        locator = ArcticDamLocator(nve_data_path)
        
        # Load data and identify Arctic dams
        if locator.load_nve_dam_data():
            arctic_dams = locator.identify_arctic_dams()
            
            if arctic_dams:
                logger.info(f"✅ Found {len(arctic_dams)} real Arctic dams from NVE dataset")
                return locator.get_arctic_dams_for_analysis()
            else:
                logger.warning("No Arctic dams found in NVE dataset")
                return []
        else:
            logger.error("Failed to load NVE dataset")
            return []
            
    except Exception as e:
        logger.error(f"Error getting real Arctic dams: {e}")
        return []

# Example usage and testing
if __name__ == "__main__":
    # Create locator and analyze Arctic dams
    locator = ArcticDamLocator()
    
    if locator.load_nve_dam_data():
        arctic_dams = locator.identify_arctic_dams()
        
        print(f"\n❄️ NORWEGIAN ARCTIC DAMS ANALYSIS")
        print("="*50)
        
        # Get statistics
        stats = locator.get_arctic_statistics()
        
        print(f"Total Arctic dams: {stats['total_arctic_dams']}")
        print(f"Northernmost dam: {stats['northernmost_dam']['name']} at {stats['northernmost_dam']['latitude']:.2f}°N")
        print(f"Latitude range: {stats['latitude_range']['min']:.2f}°N - {stats['latitude_range']['max']:.2f}°N")
        
        print("\nBy Arctic region:")
        for region, count in stats['by_arctic_region'].items():
            print(f"  {region}: {count} dams")
        
        print("\nBy purpose:")
        for purpose, count in sorted(stats['by_purpose'].items(), key=lambda x: x[1], reverse=True):
            if count > 0:
                print(f"  {purpose}: {count} dams")
        
        # Create visualization
        locator.create_arctic_visualization()
        
        # Export data
        locator.export_arctic_dams_data()
        
        print(f"\n✅ Analysis complete! Found {len(arctic_dams)} dams above {locator.ARCTIC_CIRCLE_LATITUDE}°N")
    else:
        print("❌ Failed to load NVE dam data") 