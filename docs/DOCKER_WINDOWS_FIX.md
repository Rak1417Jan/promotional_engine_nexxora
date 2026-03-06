# Docker Windows Setup Fix

## Issue Resolved

✅ **Fixed:** Removed obsolete `version: '3.8'` from `docker-compose.yml`

## Current Issue: Docker Desktop Not Running

### Error Message
```
unable to get image 'minio/minio:latest': error during connect: 
in the default daemon configuration on Windows, the docker client must be run 
with elevated privileges to connect: Get "http://%2F%2F.%2Fpipe%2Fdocker_engine/...": 
open //./pipe/docker_engine: The system cannot find the file specified.
```

### Quick Fix Steps

1. **Start Docker Desktop**
   - Open Docker Desktop from Windows Start Menu
   - Wait for it to fully start (check system tray for Docker icon)
   - The Docker Desktop window should show "Docker Desktop is running"

2. **Verify Docker is Running**
   ```powershell
   docker ps
   ```
   - Should return an empty list or list of containers (NOT an error)

3. **Try docker-compose again**
   ```powershell
   docker-compose up -d
   ```

### If Docker Desktop Won't Start

1. **Check WSL 2 Installation**
   - Docker Desktop on Windows requires WSL 2
   - Open PowerShell as Administrator:
     ```powershell
     wsl --status
     wsl --update
     ```

2. **Restart Docker Desktop Service**
   - Right-click Docker Desktop icon in system tray
   - Select "Restart"
   - Or restart via Windows Services (`services.msc`)

3. **Check Docker Desktop Settings**
   - Open Docker Desktop
   - Go to Settings → General
   - Ensure "Use WSL 2 based engine" is checked
   - Click "Apply & Restart"

4. **Run PowerShell as Administrator**
   - Right-click PowerShell → "Run as Administrator"
   - Navigate to project directory
   - Try `docker-compose up -d` again

### Verify All Services Started

After Docker Desktop is running, verify services:

```powershell
# Check all services are running
docker-compose ps

# Check individual service logs if needed
docker-compose logs postgres
docker-compose logs mongodb
docker-compose logs redis
docker-compose logs kafka
docker-compose logs minio
```

### Expected Output

After running `docker-compose up -d`, you should see:
```
[+] Running 7/7
 ✔ Container nexora_postgres    Started
 ✔ Container nexora_mongodb     Started
 ✔ Container nexora_redis       Started
 ✔ Container nexora_zookeeper   Started
 ✔ Container nexora_kafka        Started
 ✔ Container nexora_minio        Started
```

### Issue: Docker Images Stuck While Pulling

**Symptoms:**
- Images appear to be pulling but get stuck at certain percentages
- Process takes a very long time (200+ seconds)
- Only some images complete (e.g., redis) while others remain stuck

**Common Causes:**
1. **Proxy Configuration** - Docker Desktop has proxy settings that aren't working
2. **Slow Internet Connection** - Large images (zookeeper ~593MB, kafka ~295MB, mongodb ~286MB)
3. **Docker Registry Rate Limiting** - Too many concurrent pulls
4. **WSL 2 Network Issues** - Network problems in WSL 2 backend

**Solutions:**

#### Solution 1: Cancel and Retry (Recommended)
```powershell
# Press Ctrl+C to cancel current pull
# Then retry - sometimes it works on second attempt
docker-compose up -d
```

#### Solution 2: Disable Docker Proxy (If Not Needed)
1. Open Docker Desktop
2. Go to **Settings** → **Resources** → **Proxies**
3. If proxy is configured but you don't need it:
   - Uncheck "Manual proxy configuration"
   - Click "Apply & Restart"
4. Retry: `docker-compose up -d`

#### Solution 3: Pull Images One at a Time
```powershell
# Pull images individually to identify which one is problematic
docker pull postgres:15
docker pull mongo:7
docker pull redis:7-alpine
docker pull confluentinc/cp-zookeeper:latest
docker pull confluentinc/cp-kafka:latest
docker pull minio/minio:latest

# Then start services
docker-compose up -d
```

#### Solution 4: Use Alternative Registry Mirror (If in Restricted Network)
1. Open Docker Desktop
2. Go to **Settings** → **Docker Engine**
3. Add registry mirrors (if available in your region):
   ```json
   {
     "registry-mirrors": [
       "https://mirror.gcr.io"
     ]
   }
   ```
4. Click "Apply & Restart"

#### Solution 5: Increase Docker Resources
1. Open Docker Desktop
2. Go to **Settings** → **Resources** → **Advanced**
3. Increase:
   - **CPUs**: 4+ (if available)
   - **Memory**: 4GB+ (if available)
4. Click "Apply & Restart"

#### Solution 6: Check Network/Firewall
```powershell
# Test internet connectivity from Docker
docker run --rm curlimages/curl:latest curl -I https://hub.docker.com

# If this fails, check:
# - Windows Firewall settings
# - Antivirus software blocking Docker
# - Corporate proxy/VPN settings
```

#### Solution 7: Clean Docker and Retry
```powershell
# Stop all containers
docker-compose down

# Remove incomplete images
docker image prune -a

# Clear Docker build cache
docker builder prune -a

# Retry
docker-compose up -d
```

### Next Steps

Once Docker services are running:

1. Wait 30 seconds for services to be healthy
2. Verify with: `docker-compose ps`
3. Initialize database: `cd backend && python scripts/init_database.py`
4. Start backend server: `uvicorn app.main:app --reload`

---

**Note:** The `version` field warning has been fixed. The main issue is that Docker Desktop needs to be running before you can use `docker-compose`.
