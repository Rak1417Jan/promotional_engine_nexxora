# Quick Fix: Docker Images Stuck While Pulling

## Immediate Action

Your Docker pull is stuck. Here's what to do:

### Step 1: Cancel Current Operation
Press `Ctrl+C` in your PowerShell terminal to cancel the stuck pull.

### Step 2: Check Docker Proxy Settings

Your Docker is configured with a proxy (`http.docker.internal:3128`). This might be causing the issue.

**To fix:**
1. Open **Docker Desktop**
2. Click the **Settings** icon (gear icon)
3. Go to **Resources** → **Proxies**
4. If you see proxy settings but don't need them:
   - Uncheck **"Manual proxy configuration"**
   - Click **"Apply & Restart"**
5. Wait for Docker Desktop to restart

### Step 3: Pull Images One at a Time

Instead of pulling all at once, pull them individually:

```powershell
# Pull smaller images first
docker pull redis:7-alpine

# Then medium images
docker pull postgres:15
docker pull mongo:7
docker pull minio/minio:latest

# Then large images (these are the biggest)
docker pull confluentinc/cp-kafka:latest
docker pull confluentinc/cp-zookeeper:latest
```

**Note:** The zookeeper image is ~593MB and kafka is ~295MB, so they will take longer.

### Step 4: Start Services

Once all images are pulled:

```powershell
docker-compose up -d
```

### Alternative: If Still Stuck

If individual pulls also get stuck:

1. **Check your internet connection:**
   ```powershell
   Test-NetConnection hub.docker.com -Port 443
   ```

2. **Try with verbose output:**
   ```powershell
   docker pull --progress=plain postgres:15
   ```

3. **Clean Docker cache and retry:**
   ```powershell
   docker system prune -a --volumes
   docker-compose up -d
   ```

4. **Check Docker Desktop resources:**
   - Settings → Resources → Advanced
   - Ensure you have at least 4GB RAM and 2 CPUs allocated
   - Click "Apply & Restart"

### Expected Pull Times

- **redis:7-alpine**: ~15 seconds (smallest, ~14MB)
- **postgres:15**: ~30-60 seconds (~164MB)
- **mongo:7**: ~60-90 seconds (~286MB)
- **minio/minio:latest**: ~30-60 seconds (~62MB)
- **kafka**: ~90-120 seconds (~295MB)
- **zookeeper**: ~120-180 seconds (~593MB)

**Total time:** 5-10 minutes on a good connection.

### If Nothing Works

1. **Restart Docker Desktop completely:**
   - Right-click system tray icon → Quit Docker Desktop
   - Wait 10 seconds
   - Start Docker Desktop again
   - Wait for it to fully start

2. **Check Windows Firewall:**
   - Windows Security → Firewall & network protection
   - Ensure Docker Desktop is allowed

3. **Try pulling from a different network:**
   - If on corporate network, try mobile hotspot
   - Corporate proxies often block Docker Hub

4. **Use Docker Desktop's built-in terminal:**
   - Docker Desktop → Settings → General
   - Enable "Use the WSL 2 based engine"
   - Try commands from WSL terminal instead

---

**Most Common Fix:** Disable the proxy in Docker Desktop settings if you don't need it!
