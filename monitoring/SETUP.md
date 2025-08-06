# 🚀 Norwegian Dam Monitoring - Complete Setup Guide

**Step-by-step guide to get your real-time Norwegian dam monitoring system running**

## 📋 Prerequisites

Before starting, make sure you have:
- **Docker Desktop** installed and running
- **Git** for version control
- **A text editor** for configuration files
- **Norwegian API credentials** (I'll show you how to get them)

## 🔑 Step 1: Get Norwegian API Credentials

### Frost API (Free - Norwegian Weather Data)
1. Go to [frost.met.no](https://frost.met.no/)
2. Click "Register" and create an account
3. Once logged in, go to "API Access"
4. Copy your **Client ID** - this is your `FROST_CLIENT_ID`

### Sentinel Hub (Satellite Data)
1. Visit [sentinel-hub.com](https://sentinel-hub.com/)
2. Create a free account (30-day trial available)
3. Go to "Dashboard" → "User Settings"
4. Note your **Username** and **Password**

## 🛠️ Step 2: Project Setup

### Clone the Repository
```bash
git clone [your-repository-url]
cd "Norway Dam"
```

### Navigate to Monitoring Directory
```bash
cd monitoring
```

### Create Environment Configuration
Create a `.env` file with your credentials:

```bash
# Copy the template
cp .env.example .env

# Edit with your credentials
nano .env
```

Add your credentials:
```env
# Norwegian API Credentials
FROST_CLIENT_ID=your_frost_client_id_here
SENTINEL_USER=your_email@example.com
SENTINEL_PASS=your_sentinel_password

# Database Configuration
POSTGRES_PASSWORD=dam_monitor_2024
GRAFANA_PASSWORD=admin

# System Configuration
COLLECTION_INTERVAL_MINUTES=30
BATCH_SIZE=25
DEBUG=false
```

## 🚀 Step 3: Launch the System

### Start Docker Desktop
Make sure Docker Desktop is running on your machine.

### Build and Launch
```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps
```

You should see:
```
NAME                           STATUS
norwegian_dam_timescaledb      Up (healthy)
norwegian_dam_api              Up
norwegian_dam_grafana          Up
```

### Wait for Initial Setup
The system needs a few minutes to:
1. Initialize the database
2. Import Norwegian dam data
3. Start collecting live weather data

## 🔍 Step 4: Verify Everything Works

### Check API Health
```bash
curl http://localhost:8000/health
```

Should return:
```json
{
  "status": "healthy",
  "database": "connected",
  "norwegian_apis": "initialized"
}
```

### Check Database
```bash
# Connect to database
docker exec -it norwegian_dam_timescaledb psql -U postgres -d postgres

# Check dam count
SELECT COUNT(*) FROM dams;

# Check live weather data
SELECT COUNT(*) FROM weather_data WHERE data_source = 'met.no_live';

# Exit
\q
```

### Monitor Live Data Collection
```bash
# Watch the logs for live data collection
docker logs norwegian_dam_api -f
```

You should see messages like:
```
INFO:api.main:✅ Live weather data collected for BRASKEREIDFOSS
INFO:api.main:✅ Live weather data collected for BRONTJØNN
INFO:api.main:📡 Collecting real-time data for 25 Norwegian dams...
```

## 📊 Step 5: Access Your Dashboards

### Grafana Dashboard
1. Open http://localhost:3000
2. Login: `admin` / `admin`
3. Go to "Dashboards" → "Norwegian Dam Health Monitoring"

### API Documentation
1. Open http://localhost:8000/docs
2. Explore available endpoints
3. Try the `/dams` endpoint to see your Norwegian dams

### Database Access
- **Host**: localhost
- **Port**: 5432
- **Database**: postgres
- **Username**: postgres
- **Password**: dam_monitor_2024

## 🎯 Step 6: Customize Your Monitoring

### Scale Up Monitoring
Edit `monitoring/api/main.py`:
```python
# Change from 25 to 50 dams per cycle
LIMIT 50

# Change from 30 to 15 minutes
COLLECTION_INTERVAL_MINUTES=15
```

### Add More Dashboard Panels
Use these SQL queries in Grafana:

**Live Weather Table:**
```sql
SELECT 
  d.dam_name as "Dam Name",
  ROUND(w.temperature_c, 1) as "Temp °C",
  ROUND(w.precipitation_mm, 1) as "Rain mm",
  w.time as "Updated"
FROM weather_data w
JOIN dams d ON w.dam_id = d.dam_id
WHERE w.data_source = 'met.no_live'
  AND w.time > NOW() - INTERVAL '2 hours'
ORDER BY w.time DESC
```

## 🔧 Troubleshooting

### Common Issues

**API not collecting data:**
```bash
# Check logs
docker logs norwegian_dam_api

# Restart API service
docker-compose restart api
```

**Database connection issues:**
```bash
# Check database logs
docker logs norwegian_dam_timescaledb

# Restart database
docker-compose restart timescaledb
```

**Grafana can't connect:**
- Make sure Host is set to `timescaledb` (not localhost)
- Port should be `5432`
- Database: `postgres`

### Reset Everything
```bash
# Stop all services
docker-compose down

# Remove volumes (WARNING: deletes all data)
docker-compose down -v

# Restart fresh
docker-compose up -d
```

## 📈 Performance Monitoring

### Check System Performance
```bash
# View resource usage
docker stats

# Check API response times
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:8000/health
```

### Monitor Data Collection
```sql
-- Check monitoring frequency
SELECT 
    DATE_TRUNC('hour', time) as hour,
    COUNT(*) as records,
    COUNT(DISTINCT dam_id) as unique_dams
FROM weather_data
WHERE data_source = 'met.no_live'
  AND time > NOW() - INTERVAL '24 hours'
GROUP BY hour
ORDER BY hour DESC;
```

## 🎉 Success Indicators

You'll know everything is working when you see:

1. **✅ 200+ Norwegian dams** in database
2. **✅ Live weather data** being collected every 30 minutes
3. **✅ 25+ dams per monitoring cycle**
4. **✅ Grafana dashboards** showing real-time data
5. **✅ Temperature readings** from actual Norwegian locations

## 📞 Getting Help

If you run into issues:

1. **Check the logs**: `docker logs [container-name]`
2. **Verify API credentials**: Make sure they're correctly set in `.env`
3. **Check Docker**: Ensure Docker Desktop is running
4. **Review this guide**: Double-check each step

## 🎯 What's Next

Once your system is running:

1. **Create custom dashboards** with your specific monitoring needs
2. **Set up alerts** for extreme weather conditions
3. **Scale to more dams** by adjusting the monitoring parameters
4. **Integrate additional Norwegian APIs** for more data sources

---

**🇳🇴 Happy monitoring! Your Norwegian dam infrastructure is now under real-time surveillance!** 