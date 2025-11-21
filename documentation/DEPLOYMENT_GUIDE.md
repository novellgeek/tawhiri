# Tawhiri Space Weather Dashboard - Deployment Guide

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Place Files in Package Structure

```
tawhiri/
  space_weather/
    __init__.py
    constants.py
    scales.py
    utils.py
    data_fetchers.py
    plotting.py
    pdf_export.py
    nz_translations.py
    app.py
```

### 3. Run the Application

```bash
# Option 1: Direct run
streamlit run tawhiri/space_weather/app.py

# Option 2: Python module
python -m tawhiri.space_weather.app

# Option 3: Custom script
python run_dashboard.py
```

---

## Deployment Options

### Option A: Standalone Streamlit Deployment

**Best for:** Simple deployments, development, testing

```bash
# Run on default port (8501)
streamlit run tawhiri/space_weather/app.py

# Run on custom port
streamlit run tawhiri/space_weather/app.py --server.port 8080

# Run with custom config
streamlit run tawhiri/space_weather/app.py --server.headless true
```

**Access:** http://localhost:8501

### Option B: Streamlit Cloud Deployment

**Best for:** Cloud-hosted, managed deployment

1. Push code to GitHub
2. Connect to Streamlit Cloud
3. Deploy automatically

**Pros:**
- Free hosting
- Automatic updates
- HTTPS included

**Cons:**
- Public by default (need authentication setup)
- Internet required

### Option C: Docker Container Deployment

**Best for:** Production, isolated environments, NZDF secure networks

**Dockerfile:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY tawhiri/ tawhiri/

# Expose port
EXPOSE 8501

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Run app
CMD ["streamlit", "run", "tawhiri/space_weather/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

**Build and Run:**
```bash
# Build
docker build -t tawhiri-spaceweather .

# Run
docker run -p 8501:8501 tawhiri-spaceweather

# Run with volume for logs
docker run -p 8501:8501 -v $(pwd)/logs:/app/logs tawhiri-spaceweather
```

### Option D: Systemd Service (Linux Server)

**Best for:** Always-on server deployment

**Service File** (`/etc/systemd/system/tawhiri-spaceweather.service`):
```ini
[Unit]
Description=Tawhiri Space Weather Dashboard
After=network.target

[Service]
Type=simple
User=spaceweather
WorkingDirectory=/opt/tawhiri
Environment="PATH=/opt/tawhiri/venv/bin"
ExecStart=/opt/tawhiri/venv/bin/streamlit run space_weather/app.py --server.port 8501
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Setup:**
```bash
# Create user
sudo useradd -r -s /bin/false spaceweather

# Install application
sudo mkdir -p /opt/tawhiri
sudo cp -r tawhiri/ /opt/tawhiri/
sudo chown -R spaceweather:spaceweather /opt/tawhiri

# Create virtual environment
cd /opt/tawhiri
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Enable and start service
sudo systemctl enable tawhiri-spaceweather
sudo systemctl start tawhiri-spaceweather

# Check status
sudo systemctl status tawhiri-spaceweather

# View logs
sudo journalctl -u tawhiri-spaceweather -f
```

---

## Configuration

### Environment Variables

```bash
# Optional configuration via environment variables
export TAWHIRI_LOG_LEVEL=INFO
export TAWHIRI_CACHE_TTL=600
export STREAMLIT_SERVER_PORT=8501
export STREAMLIT_SERVER_ADDRESS=0.0.0.0
```

### Streamlit Config

Create `.streamlit/config.toml`:

```toml
[server]
port = 8501
address = "0.0.0.0"
headless = true
enableCORS = false
enableXsrfProtection = true

[browser]
serverAddress = "spaceweather.nzdf.mil.nz"
gatherUsageStats = false

[theme]
primaryColor = "#003366"  # NZDF Blue
backgroundColor = "#0d1419"
secondaryBackgroundColor = "#111a21"
textColor = "#dbe7ff"
font = "sans serif"

[logger]
level = "info"
```

---

## Security Considerations

### For NZDF Deployment:

1. **Network Isolation**
   - Deploy on internal network only
   - No external internet access required (except for NOAA/BOM APIs)
   - Use firewall rules

2. **Authentication**
   ```bash
   # Option 1: Use reverse proxy (nginx/Apache) with authentication
   # Option 2: VPN requirement
   # Option 3: IP whitelisting
   ```

3. **HTTPS**
   ```bash
   # Use reverse proxy for SSL termination
   # nginx example:
   server {
       listen 443 ssl;
       server_name spaceweather.nzdf.mil.nz;
       
       ssl_certificate /path/to/cert.pem;
       ssl_certificate_key /path/to/key.pem;
       
       location / {
           proxy_pass http://localhost:8501;
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection "upgrade";
           proxy_set_header Host $host;
       }
   }
   ```

4. **Data Security**
   - All NOAA/BOM data is public domain
   - No sensitive data stored locally
   - PDFs generated on-demand (not stored)

---

## Air-Gapped Deployment

### For Secure/Classified Networks:

1. **Pre-download Dependencies**
   ```bash
   # On internet-connected machine
   pip download -r requirements.txt -d packages/
   
   # Transfer packages/ folder to secure network
   
   # On secure machine
   pip install --no-index --find-links=packages/ -r requirements.txt
   ```

2. **Cache Data Sources**
   - NOAA APIs are public and can be proxied
   - Consider caching recent data
   - Update manually if needed

3. **Alternative: Offline Mode**
   - Modify app to load from local files
   - Update data files periodically

---

## Monitoring & Maintenance

### Health Checks

```bash
# Check if app is running
curl http://localhost:8501/_stcore/health

# Check NOAA API accessibility
curl https://services.swpc.noaa.gov/json/goes/primary/xrays-6-hour.json
```

### Logs

```bash
# View Streamlit logs
tail -f ~/.streamlit/logs/app.log

# View system logs (if using systemd)
sudo journalctl -u tawhiri-spaceweather -f

# View container logs (if using Docker)
docker logs -f tawhiri-spaceweather
```

### Automatic Restarts

**Streamlit has built-in restart:**
- Auto-restarts on code changes (development)
- Configure restart behavior in config.toml

**Systemd auto-restart:**
- Configured in service file with `Restart=always`

**Docker auto-restart:**
```bash
docker run --restart=unless-stopped -p 8501:8501 tawhiri-spaceweather
```

### Updates

```bash
# Pull latest code
git pull origin main

# Update dependencies
pip install -r requirements.txt --upgrade

# Restart service
sudo systemctl restart tawhiri-spaceweather

# Or restart Docker container
docker restart tawhiri-spaceweather
```

---

## Testing Deployment

### 1. Unit Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=tawhiri --cov-report=html

# Expected: 80+ tests passing
```

### 2. Integration Tests

```bash
# Test data fetching
python -c "from tawhiri.space_weather.data_fetchers import get_noaa_rsg_now_and_past; print(get_noaa_rsg_now_and_past())"

# Test chart creation
python -c "from tawhiri.space_weather.plotting import create_xray_chart; fig = create_xray_chart(); print('OK' if fig else 'FAIL')"

# Test PDF generation
python -c "from tawhiri.space_weather.pdf_export import check_reportlab_available; print('PDF: OK' if check_reportlab_available() else 'PDF: Install reportlab')"
```

### 3. UI Testing

```bash
# Start app
streamlit run tawhiri/space_weather/app.py

# Test in browser
# - Navigate to http://localhost:8501
# - Test all 8 tabs
# - Test PDF export
# - Test settings (contrast, font scale)
# - Test auto-refresh
```

---

## Troubleshooting

### Issue: App won't start

```bash
# Check Python version (need 3.8+)
python --version

# Check dependencies
pip list | grep streamlit

# Check for port conflicts
lsof -i :8501  # On Linux/Mac
netstat -ano | findstr :8501  # On Windows

# Run with verbose logging
streamlit run app.py --logger.level=debug
```

### Issue: Charts not displaying

```bash
# Check plotly installation
python -c "import plotly; print(plotly.__version__)"

# Check network access to NOAA APIs
curl https://services.swpc.noaa.gov/json/goes/primary/xrays-6-hour.json

# Check browser console for errors
```

### Issue: PDF generation fails

```bash
# Check reportlab installation
python -c "import reportlab; print(reportlab.Version)"

# For chart embedding, check kaleido
python -c "import kaleido; print('OK')"

# If kaleido fails, PDFs will work without charts
```

### Issue: Data not updating

```bash
# Check network connectivity
ping services.swpc.noaa.gov

# Check cache settings
# Data cached for 10 minutes by default

# Force refresh by restarting app
```

---

## Performance Optimization

### For High-Traffic Deployments:

1. **Enable Caching**
   - Already implemented in data_fetchers.py
   - Adjust DEFAULT_CACHE_TTL in constants.py

2. **Use Load Balancer**
   - Run multiple instances
   - Use nginx/HAProxy for load balancing

3. **CDN for Static Assets**
   - Serve images/CSS from CDN
   - Reduce server load

4. **Database for Historical Data**
   - Store historical data in PostgreSQL/SQLite
   - Reduce API calls

---

## Support Contacts

### NZDF IT Support:
- **Email:** it.support@nzdf.mil.nz
- **Phone:** [classified]

### Application Developer:
- **Email:** developer@example.com

### Data Sources:
- **NOAA SWPC:** https://www.swpc.noaa.gov/contact-us
- **BOM SWS:** https://www.sws.bom.gov.au/Contact

---

## Backup & Recovery

### Backup (Minimal - No User Data):

```bash
# Backup application code
tar -czf tawhiri-backup-$(date +%Y%m%d).tar.gz tawhiri/

# Backup configuration
cp -r .streamlit/ streamlit-config-backup/

# No data backup needed (all data from APIs)
```

### Recovery:

```bash
# Extract backup
tar -xzf tawhiri-backup-YYYYMMDD.tar.gz

# Restore configuration
cp -r streamlit-config-backup/ .streamlit/

# Reinstall dependencies
pip install -r requirements.txt

# Start app
streamlit run tawhiri/space_weather/app.py
```

---

## License & Compliance

### Data Sources:
- **NOAA Data:** Public domain, no restrictions
- **BOM Data:** Check BOM terms of use

### Application Code:
- Developed for NZDF use
- Contact your legal department for distribution

---

**Deployment Guide Complete!**

For additional support, refer to the complete documentation in the `docs/` directory.
