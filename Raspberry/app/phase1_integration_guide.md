# Phase 1: Web Application Integration Guide

## Overview

This guide explains how to integrate the Phase 1 web API with your existing `Fish_pond_system.py` monitoring system.

### Where to Run Each Step

| Step | Location | Notes |
| --- | --- | --- |
| Install PostgreSQL | Raspberry Pi (or device hosting the API) | The actual database server should live on the Pi next to the monitoring system. |
| Create DB & user | **Either:** Raspberry Pi terminal **or** Windows pgAdmin | ✅ **You can use both interchangeably!** pgAdmin on Windows connects to the Pi's PostgreSQL over the network. Both methods work perfectly and see the same database. |
| Schema setup | **Either:** Windows (pgAdmin Query Tool) **or** Raspberry Pi (psql) | ✅ **Use whichever you prefer!** Execute `phase1_database_setup.sql` against the Pi's database. Both methods work - no conflicts. |
| Database management | **Either:** Windows pgAdmin **or** Raspberry Pi terminal | ✅ **Switch freely between both!** Use pgAdmin for visual browsing, terminal for scripts. Both connect to the same database. |
| Python dependencies | Raspberry Pi | The API process runs on the Pi, so install requirements there. |
| Environment variables | Raspberry Pi | Set `DB_*`, JWT, etc., on the Pi before launching the API. |
| API server | Raspberry Pi | Run `phase1_pond_api.py` on the Pi. |
| Frontend / testing | Any machine with network access to the Pi | Use curl, browser, or future React app.

> **✅ Using Both Methods Interchangeably:** You can freely use **pgAdmin on Windows** and **terminal commands on Raspberry Pi** for all database tasks. They're just different interfaces to the same PostgreSQL database on your Pi. There are **no conflicts or issues** - changes made in one are immediately visible in the other. Use whichever is more convenient for each task!

## Architecture

```
┌─────────────────────┐
│ Fish_pond_system.py │  (Existing monitoring system)
│  - Sensor reading   │
│  - ThingSpeak sync  │
│  - Pump control     │
└──────────┬──────────┘
           │
           │ (Option 1: Direct DB write)
           ▼
┌─────────────────────┐
│  PostgreSQL DB      │  (New: Historical storage)
│  - sensor_readings  │
│  - users            │
│  - alerts           │
└──────────┬──────────┘
           │
           │ (Option 2: ThingSpeak API)
           ▼
┌─────────────────────┐
│  phase1_pond_api.py │  (New: Web API)
│  - REST endpoints   │
│  - WebSocket        │
│  - Authentication   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  React Dashboard    │  (Future: Web frontend)
│  - Real-time charts │
│  - Alerts           │
│  - Statistics       │
└─────────────────────┘
```

## Installation Steps

### 1. Install PostgreSQL (run on Raspberry Pi)

```bash
# On Raspberry Pi (Raspbian/Debian)
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib

# Start PostgreSQL service
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Create database and user
sudo -u postgres psql
```

In PostgreSQL prompt:
```sql
CREATE DATABASE pond_db;
CREATE USER km WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE pond_db TO km;
\q
```

> **Tip:** If you prefer pgAdmin on Windows, register the Raspberry Pi server (Host = Pi IP, Port = 5432, Maintenance DB = postgres, Username = postgres). Creating the database and user through pgAdmin applies the changes on the Pi even though the GUI runs on Windows.

### 2. Set Up Database Schema (connect to Raspberry Pi database)

You can run the schema from the Pi itself **or** from your Windows PC via pgAdmin. **Both methods work perfectly and can be used interchangeably** - they're just different interfaces to the same PostgreSQL database on your Raspberry Pi.

- **Option A – Raspberry Pi terminal**
  ```bash
  # Copy phase1_database_setup.sql to the Pi, then run:
  psql -U km -d pond_db -f phase1_database_setup.sql
  ```

- **Option B – Windows using pgAdmin**
  1. Open pgAdmin on Windows.
  2. Register a new server that points to the Pi's IP address (host), port `5432`, and the `postgres` superuser (or another admin).
  3. Right-click the `pond_db` database → **Query Tool**, open `phase1_database_setup.sql`, and execute it.

> **✅ Using Both Methods Interchangeably:** You can freely switch between pgAdmin (Windows) and terminal commands (Raspberry Pi) at any time. There are **no conflicts or issues** - both connect to the same database. Use whichever is more convenient:
> - **pgAdmin (Windows)**: Better for visual browsing, GUI-based queries, and exploring data
> - **Terminal (Raspberry Pi)**: Faster for scripts, automation, and command-line workflows
> 
> Both methods see the same data and changes made in one are immediately visible in the other.

### 3. Install Python Dependencies (run on Raspberry Pi)

```bash
# Install Phase 1 requirements
pip install -r phase1_requirements.txt

# Or install individually:
pip install Flask flask-cors flask-jwt-extended flask-socketio psycopg2-binary requests Werkzeug
```

### 4. Configure Environment Variables (on Raspberry Pi)

Create a `.env` file (optional, or set in system):

```bash
# Database configuration
DB_NAME=pond_db
DB_USER=km
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432

# JWT secret (CHANGE THIS!)
JWT_SECRET_KEY=your-super-secret-jwt-key-change-this

# ThingSpeak (from existing config)
THINGSPEAK_API_KEY=O0YOQQGDSJGFZH8P
THINGSPEAK_CHANNEL_ID=your_channel_id
```

### 5. Modify Existing System (Optional Integration)

You have two options for data flow:

#### Option A: Direct Database Integration (Recommended)

Modify `Fish_pond_system.py` to save readings directly to PostgreSQL:

```python
# Add to Fish_pond_system.py imports
import psycopg2
from psycopg2.extras import RealDictCursor

# Add to SmartFishPondMonitor.__init__()
def __init__(self):
    # ... existing code ...
    self.db_conn = self._init_database()

def _init_database(self):
    """Initialize database connection."""
    try:
        conn = psycopg2.connect(
            dbname='pond_db',
            user='km',
            password='your_password',
            host='localhost'
        )
        logger.info("✅ Database connection established")
        return conn
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return None

# Add new method to save readings
def save_to_database(self, data, status):
    """Save sensor readings to PostgreSQL database."""
    if not self.db_conn:
        return False
    
    try:
        cur = self.db_conn.cursor()
        cur.execute("""
            INSERT INTO sensor_readings 
            (temperature, ph, ec, nitrogen, phosphorus, turbidity, 
             quality_status, quality_score, timestamp)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            data.get('temperature'),
            data.get('ph'),
            data.get('ec'),
            data.get('nitrogen'),
            data.get('phosphorus'),
            data.get('turbidity'),
            status.get('overall'),
            status.get('score'),
            datetime.now()
        ))
        self.db_conn.commit()
        cur.close()
        logger.debug("✅ Data saved to database")
        return True
    except Exception as e:
        logger.error(f"Database save error: {e}")
        return False

# Modify thingspeak_loop() to also save to database
def thingspeak_loop(self):
    while self.state['running']:
        try:
            # ... existing ThingSpeak code ...
            
            # Also save to database
            if self.has_any_valid_data(data):
                self.save_to_database(data, status)
                
        except Exception as e:
            logger.error(f"Error in thingspeak_loop: {e}")
```

#### Option B: ThingSpeak-Only (No Code Changes)

The API will automatically fall back to ThingSpeak if database is unavailable. This requires no changes to your existing system, but data will be less real-time.

### 6. Start the API Server (on Raspberry Pi)

```bash
# Run the Flask API
python phase1_pond_api.py

# Or run in background
nohup python phase1_pond_api.py > api.log 2>&1 &

# Or use gunicorn for production
gunicorn -w 4 -b 0.0.0.0:5000 phase1_pond_api:app
```

The API will be available at: `http://localhost:5000/api/`

### 7. Test the API (any machine that can reach the Pi)

```bash
# Health check
curl http://localhost:5000/api/health

# Get current readings (no auth required)
curl http://localhost:5000/api/current-readings

# Login
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# Get historical data (with auth token)
curl http://localhost:5000/api/historical/temperature?period=24h \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## API Endpoints Reference

### Authentication
- `POST /api/auth/login` - User login
- `POST /api/auth/register` - User registration

### Sensor Data
- `GET /api/current-readings` - Latest sensor readings
- `GET /api/historical/<parameter>` - Historical data (temperature, ph, ec, etc.)
- `GET /api/readings/all` - All recent readings with pagination

### Alerts
- `GET /api/alerts` - Get recent alerts
- `POST /api/alerts/<id>/acknowledge` - Acknowledge an alert

### Statistics
- `GET /api/statistics` - Statistical summary

### Configuration
- `GET /api/config` - Get system configuration
- `POST /api/config` - Update configuration

### Health
- `GET /api/health` - Health check

## WebSocket Events

Connect to: `ws://localhost:5000`

Events:
- `connect` - Client connected
- `subscribe_readings` - Subscribe to real-time updates
- `sensor_update` - Broadcasted every 10 seconds with latest readings

## Integration with Existing System

### Running Both Systems

You can run both systems simultaneously:

```bash
# Terminal 1: Existing monitoring system
python Fish_pond_system.py

# Terminal 2: Web API
python phase1_pond_api.py
```

### Systemd Service (Optional)

Create `/etc/systemd/system/pond-api.service`:

```ini
[Unit]
Description=Fish Pond Web API
After=network.target postgresql.service

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/SFP-MS
ExecStart=/usr/bin/python3 /home/pi/SFP-MS/phase1_pond_api.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable pond-api
sudo systemctl start pond-api
sudo systemctl status pond-api
```

## Next Steps (Phase 2+)

1. **Build React Dashboard** - Create frontend using the API endpoints
2. **Add ML Predictions** - Train models on historical data
3. **Multi-pond Support** - Extend database schema for multiple ponds
4. **Mobile PWA** - Progressive Web App for mobile access

## Troubleshooting

### Database Connection Issues
```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Test connection
psql -U km -d pond_db -c "SELECT 1;"

# Check firewall
sudo ufw allow 5432/tcp
```

### API Not Starting
- Check port 5000 is not in use: `sudo lsof -i :5000`
- Check logs: `tail -f api.log`
- Verify database credentials in code

### No Data in API
- Verify database has data: `SELECT COUNT(*) FROM sensor_readings;`
- Check ThingSpeak API key is correct
- Verify integration code is saving to database

## Security Notes

⚠️ **IMPORTANT**: Before deploying to production:

1. Change default admin password
2. Use proper password hashing (Werkzeug)
3. Set strong JWT_SECRET_KEY
4. Enable HTTPS (use nginx reverse proxy)
5. Restrict database access
6. Use environment variables for secrets
7. Enable rate limiting
8. Add input validation

## Support

For issues or questions:
- Check logs: `tail -f pond_monitor.log` and `tail -f api.log`
- Review database: `psql -U km -d pond_db`
- Test API endpoints with curl or Postman

