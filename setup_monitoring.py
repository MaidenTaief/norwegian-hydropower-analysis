#!/usr/bin/env python3
"""
Norwegian Dam Health Monitoring System - Complete Setup
======================================================

This script sets up the complete dam health monitoring system with
real Norwegian data integration. It guides you through:

1. API credentials setup
2. Database initialization  
3. Data import from your existing NVE files
4. System deployment with Docker
5. Verification and testing

Usage:
    python setup_monitoring.py
"""

import os
import sys
import subprocess
import asyncio
import asyncpg
from pathlib import Path
import shutil
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
import requests
import time

console = Console()

class MonitoringSystemSetup:
    """Complete setup manager for the monitoring system."""
    
    def __init__(self):
        self.project_root = Path.cwd()
        self.monitoring_dir = self.project_root / "monitoring"
        self.data_dir = self.project_root / "Data"
        self.env_file = self.project_root / ".env"
        
        self.required_apis = {
            'FROST_CLIENT_ID': {
                'name': 'Frost API (met.no)',
                'url': 'https://frost.met.no/auth/requestCredentials.html',
                'description': 'Historical weather data from Norwegian Meteorological Institute',
                'required': False
            },
            'SENTINEL_USER': {
                'name': 'Sentinel Hub (Copernicus)',
                'url': 'https://scihub.copernicus.eu/dhus/#/self-registration',
                'description': 'Satellite imagery and InSAR data',
                'required': False
            }
        }
    
    def display_welcome(self):
        """Display welcome message and system overview."""
        console.print(Panel.fit(
            "🏗️ Norwegian Dam Health Monitoring System Setup\n\n"
            "This setup will create a complete real-time monitoring system for your Norwegian dams.\n"
            "It integrates with your existing NVE data analysis and adds:\n\n"
            "✅ Real-time weather monitoring (met.no)\n"
            "✅ Water level data (NVE Hydrology API)\n"
            "✅ Satellite monitoring (Sentinel Hub)\n"
            "✅ Health scoring and alerts\n"
            "✅ Professional dashboards (Grafana)\n"
            "✅ REST API for integration\n\n"
            "🔐 All data sources are official Norwegian government APIs\n"
            "🆓 All APIs are free (some require registration)\n"
            "⚡ No changes to your existing analysis code",
            title="Welcome", 
            border_style="green"
        ))
    
    def check_prerequisites(self):
        """Check system prerequisites."""
        console.print("\n📋 Checking prerequisites...")
        
        # Check Docker
        try:
            result = subprocess.run(['docker', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                console.print("✅ Docker installed")
            else:
                console.print("❌ Docker not found")
                return False
        except FileNotFoundError:
            console.print("❌ Docker not found - please install Docker first")
            return False
        
        # Check Docker Compose
        try:
            result = subprocess.run(['docker-compose', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                console.print("✅ Docker Compose installed")
            else:
                console.print("❌ Docker Compose not found")
                return False
        except FileNotFoundError:
            console.print("❌ Docker Compose not found - please install Docker Compose")
            return False
        
        # Check existing NVE data
        required_files = [
            'Vannkraft_DamPunkt.shp',
            'Vannkraft_DamLinje.shp',
            'Vannkraft_Magasin.shp'
        ]
        
        missing_files = []
        for file in required_files:
            if not (self.data_dir / file).exists():
                missing_files.append(file)
        
        if missing_files:
            console.print(f"❌ Missing NVE data files: {missing_files}")
            console.print(f"Please ensure your NVE shapefiles are in {self.data_dir}")
            return False
        else:
            console.print("✅ NVE data files found")
        
        return True
    
    def setup_api_credentials(self):
        """Guide user through API credential setup."""
        console.print("\n🔑 API Credentials Setup")
        console.print("Some Norwegian data sources require free registration...")
        
        credentials = {}
        
        # Read existing .env if it exists
        if self.env_file.exists():
            with open(self.env_file, 'r') as f:
                for line in f:
                    if '=' in line and not line.startswith('#'):
                        key, value = line.strip().split('=', 1)
                        credentials[key] = value
        
        for key, info in self.required_apis.items():
            console.print(f"\n📡 {info['name']}")
            console.print(f"   Purpose: {info['description']}")
            console.print(f"   Register at: {info['url']}")
            
            current_value = credentials.get(key, '')
            if current_value:
                console.print(f"   Current value: {current_value[:10]}...")
                if Confirm.ask(f"Keep existing {key}?"):
                    continue
            
            if info['required']:
                while True:
                    value = Prompt.ask(f"Enter {key}")
                    if value.strip():
                        credentials[key] = value.strip()
                        break
                    console.print("This credential is required.")
            else:
                value = Prompt.ask(f"Enter {key} (optional, press Enter to skip)", default="")
                if value.strip():
                    credentials[key] = value.strip()
        
        # Database password
        db_password = credentials.get('POSTGRES_PASSWORD', 'dam_monitor_2024')
        if Confirm.ask("Change database password?", default=False):
            db_password = Prompt.ask("Enter database password", default=db_password)
        credentials['POSTGRES_PASSWORD'] = db_password
        
        # Grafana password
        grafana_password = credentials.get('GRAFANA_PASSWORD', 'admin')
        if Confirm.ask("Change Grafana admin password?", default=False):
            grafana_password = Prompt.ask("Enter Grafana password", default=grafana_password)
        credentials['GRAFANA_PASSWORD'] = grafana_password
        
        # Save to .env file
        self.save_env_file(credentials)
        console.print("✅ Credentials saved to .env file")
    
    def save_env_file(self, credentials):
        """Save credentials to .env file."""
        env_content = """# Norwegian Dam Health Monitoring System - Configuration
# Generated by setup script

# =============================================================================
# DATABASE CONFIGURATION
# =============================================================================
POSTGRES_PASSWORD={postgres_password}
GRAFANA_PASSWORD={grafana_password}

# =============================================================================
# NORWEGIAN API CREDENTIALS
# =============================================================================
""".format(
            postgres_password=credentials.get('POSTGRES_PASSWORD', 'dam_monitor_2024'),
            grafana_password=credentials.get('GRAFANA_PASSWORD', 'admin')
        )
        
        for key, info in self.required_apis.items():
            value = credentials.get(key, '')
            env_content += f"\n# {info['name']}\n"
            env_content += f"# Register at: {info['url']}\n"
            env_content += f"{key}={value}\n"
        
        env_content += """
# =============================================================================
# SYSTEM CONFIGURATION
# =============================================================================
DEBUG=false
COLLECTION_INTERVAL_MINUTES=60
BATCH_SIZE=10
DATA_PATH=./data/postgres

# =============================================================================
# OPTIONAL INTEGRATIONS
# =============================================================================
# SMTP_HOST=
# SMTP_PORT=587
# SMTP_USER=
# SMTP_PASS=
# ALERT_EMAIL_FROM=alerts@dammonitoring.no
# SLACK_WEBHOOK_URL=
"""
        
        with open(self.env_file, 'w') as f:
            f.write(env_content)
    
    def create_directory_structure(self):
        """Create required directory structure."""
        console.print("\n📁 Creating directory structure...")
        
        directories = [
            "monitoring/data/postgres",
            "monitoring/logs",
            "monitoring/grafana/dashboards",
            "monitoring/grafana/datasources"
        ]
        
        for dir_path in directories:
            full_path = self.project_root / dir_path
            full_path.mkdir(parents=True, exist_ok=True)
            console.print(f"✅ Created {dir_path}")
    
    def test_api_connections(self):
        """Test API connections before deployment."""
        console.print("\n🔌 Testing API connections...")
        
        # Test met.no (always available)
        try:
            response = requests.get(
                "https://api.met.no/weatherapi/locationforecast/2.0/compact",
                params={'lat': 59.9139, 'lon': 10.7522},
                headers={'User-Agent': 'DamHealthMonitor/1.0 setup'},
                timeout=10
            )
            if response.status_code == 200:
                console.print("✅ met.no API - Weather data")
            else:
                console.print("⚠️ met.no API - Limited access")
        except Exception as e:
            console.print(f"❌ met.no API - {e}")
        
        # Test NVE Hydrology API
        try:
            response = requests.get(
                "https://hydapi.nve.no/api/v1/Stations",
                headers={'Accept': 'application/json'},
                timeout=10
            )
            if response.status_code == 200:
                console.print("✅ NVE Hydrology API - Water levels")
            else:
                console.print("⚠️ NVE Hydrology API - Limited access")
        except Exception as e:
            console.print(f"❌ NVE Hydrology API - {e}")
        
        # Test Frost API if credentials provided
        frost_id = os.getenv('FROST_CLIENT_ID')
        if frost_id:
            try:
                response = requests.get(
                    "https://frost.met.no/api/v0/sources",
                    auth=(frost_id, ''),
                    params={'types': 'SensorSystem'},
                    timeout=10
                )
                if response.status_code == 200:
                    console.print("✅ Frost API - Historical weather")
                else:
                    console.print("⚠️ Frost API - Check credentials")
            except Exception as e:
                console.print(f"❌ Frost API - {e}")
        else:
            console.print("⏭️ Frost API - No credentials (optional)")
    
    def deploy_system(self):
        """Deploy the monitoring system with Docker."""
        console.print("\n🚀 Deploying monitoring system...")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            
            # Change to monitoring directory
            os.chdir(self.monitoring_dir)
            
            # Build and start services
            task1 = progress.add_task("Building Docker images...", total=None)
            result = subprocess.run(['docker-compose', 'build'], capture_output=True, text=True)
            if result.returncode != 0:
                console.print(f"❌ Docker build failed: {result.stderr}")
                return False
            progress.update(task1, completed=True)
            
            task2 = progress.add_task("Starting services...", total=None)
            result = subprocess.run(['docker-compose', 'up', '-d'], capture_output=True, text=True)
            if result.returncode != 0:
                console.print(f"❌ Docker deployment failed: {result.stderr}")
                return False
            progress.update(task2, completed=True)
            
            # Wait for services to be ready
            task3 = progress.add_task("Waiting for services to start...", total=None)
            time.sleep(30)  # Give services time to initialize
            progress.update(task3, completed=True)
        
        console.print("✅ System deployed successfully")
        return True
    
    async def import_nve_data(self):
        """Import existing NVE data."""
        console.print("\n📊 Importing your existing NVE dam data...")
        
        # Change back to project root for data import
        os.chdir(self.project_root)
        
        # Wait for database to be ready
        max_attempts = 10
        for attempt in range(max_attempts):
            try:
                conn = await asyncpg.connect(
                    "postgresql://postgres:dam_monitor_2024@localhost:5432/dam_monitoring"
                )
                await conn.close()
                break
            except Exception:
                if attempt < max_attempts - 1:
                    console.print(f"Waiting for database... (attempt {attempt + 1}/{max_attempts})")
                    await asyncio.sleep(10)
                else:
                    console.print("❌ Database not ready after waiting")
                    return False
        
        # Run the import script
        try:
            result = subprocess.run([
                sys.executable, 'import_existing_data.py', 
                '--data-dir', str(self.data_dir)
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                console.print("✅ NVE data imported successfully")
                console.print(result.stdout)
                return True
            else:
                console.print("❌ Data import failed")
                console.print(result.stderr)
                return False
                
        except Exception as e:
            console.print(f"❌ Import error: {e}")
            return False
    
    def verify_deployment(self):
        """Verify the deployment is working."""
        console.print("\n🔍 Verifying deployment...")
        
        services = {
            'API': 'http://localhost:8000/health',
            'Grafana': 'http://localhost:3000/api/health',
            'Database': 'postgresql://postgres:dam_monitor_2024@localhost:5432/dam_monitoring'
        }
        
        # Test API
        try:
            response = requests.get(services['API'], timeout=10)
            if response.status_code == 200:
                console.print("✅ API service running")
            else:
                console.print("⚠️ API service issues")
        except Exception as e:
            console.print(f"❌ API service - {e}")
        
        # Test Grafana
        try:
            response = requests.get(services['Grafana'], timeout=10)
            if response.status_code == 200:
                console.print("✅ Grafana service running")
            else:
                console.print("⚠️ Grafana service issues")
        except Exception as e:
            console.print(f"❌ Grafana service - {e}")
        
        # Test Database
        try:
            asyncio.run(self._test_database())
            console.print("✅ Database service running")
        except Exception as e:
            console.print(f"❌ Database service - {e}")
    
    async def _test_database(self):
        """Test database connection."""
        conn = await asyncpg.connect(
            "postgresql://postgres:dam_monitor_2024@localhost:5432/dam_monitoring"
        )
        result = await conn.fetchval("SELECT COUNT(*) FROM dams")
        await conn.close()
        return result
    
    def display_completion_info(self):
        """Display completion information and next steps."""
        console.print("\n🎉 Setup completed successfully!")
        
        # Create info table
        table = Table(title="🔗 Access Information")
        table.add_column("Service", style="cyan")
        table.add_column("URL", style="magenta")
        table.add_column("Credentials", style="green")
        
        table.add_row("API Documentation", "http://localhost:8000/docs", "No login required")
        table.add_row("Grafana Dashboards", "http://localhost:3000", "admin / (your password)")
        table.add_row("API Health Check", "http://localhost:8000/health", "No login required")
        
        console.print(table)
        
        console.print(Panel.fit(
            "📊 Your existing analysis code remains unchanged!\n"
            "The monitoring system runs alongside your current project.\n\n"
            "🔄 Next Steps:\n"
            "1. Visit Grafana to view real-time dashboards\n"
            "2. Check API docs for integration options\n"
            "3. Monitor logs: docker-compose logs -f\n"
            "4. Stop system: docker-compose down\n\n"
            "📈 Sample API Queries:\n"
            "• All dams: curl http://localhost:8000/api/v1/dams\n"
            "• Risk matrix: curl http://localhost:8000/api/v1/analysis/risk-matrix\n"
            "• Dam health: curl http://localhost:8000/api/v1/dams/{dam_id}/health",
            title="🚀 System Ready!",
            border_style="green"
        ))

async def main():
    """Main setup function."""
    setup = MonitoringSystemSetup()
    
    # Welcome and prerequisites
    setup.display_welcome()
    
    if not setup.check_prerequisites():
        console.print("\n❌ Prerequisites not met. Please install required software and try again.")
        return
    
    if not Confirm.ask("\nContinue with setup?"):
        console.print("Setup cancelled.")
        return
    
    # Setup process
    setup.setup_api_credentials()
    setup.create_directory_structure()
    setup.test_api_connections()
    
    if not Confirm.ask("\nProceed with system deployment?"):
        console.print("Setup cancelled before deployment.")
        return
    
    # Deploy system
    if not setup.deploy_system():
        console.print("❌ Deployment failed. Check Docker logs for details.")
        return
    
    # Import data
    if not await setup.import_nve_data():
        console.print("⚠️ Data import had issues, but system is running.")
    
    # Verify and complete
    setup.verify_deployment()
    setup.display_completion_info()

if __name__ == "__main__":
    asyncio.run(main()) 