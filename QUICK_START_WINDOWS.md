# Quick Start Guide - Windows

## 🚀 Get Running in 5 Minutes

### Step 1: Start Docker Desktop
- Open Docker Desktop from Start Menu
- Wait until it shows "Docker Desktop is running"
- Check system tray for Docker icon (should be steady, not animating)

### Step 2: Start Services

**Option A: Use the script (Easiest)**
```powershell
.\start-services.ps1
```

**Option B: Manual**
```powershell
# Start essential services only (recommended for first run)
docker-compose up -d postgres mongodb redis

# Wait 30 seconds, then check status
docker-compose ps
```

### Step 3: Initialize Database
```powershell
cd backend
python scripts/init_database.py
```

### Step 4: Start Backend Server
```powershell
# Make sure you're in backend directory
# Activate virtual environment if not already
.\venv\Scripts\activate

# Start server
uvicorn app.main:app --reload
```

### Step 5: Test
- Open browser: http://localhost:8000/api/docs
- You should see the API documentation

## ✅ Success Checklist

- [ ] Docker Desktop is running
- [ ] `docker-compose ps` shows all services as "Up"
- [ ] Database initialized (no errors)
- [ ] Backend server running (see "Application startup complete")
- [ ] Can access http://localhost:8000/api/docs

## 🔧 Common Issues

### "Docker daemon not accessible"
- **Fix:** Start Docker Desktop and wait for it to fully load

### "Images stuck while pulling"
- **Fix:** Cancel (Ctrl+C) and run:
  ```powershell
  docker-compose up -d postgres mongodb redis
  ```
  This starts only essential services with smaller images.

### "Port already in use"
- **Fix:** Stop the service using the port:
  ```powershell
  # Check what's using the port
  netstat -ano | findstr :5432
  
  # Or use Docker Desktop to stop containers
  ```

### "Database connection error"
- **Fix:** Wait 30 seconds after starting services, then retry
- Check services are running: `docker-compose ps`
- Check logs: `docker-compose logs postgres`

## 📋 Service Ports

- **PostgreSQL:** 5432
- **MongoDB:** 27017
- **Redis:** 6379
- **Kafka:** 9092 (optional)
- **MinIO:** 9000, 9001 (optional)
- **Backend API:** 8000

## 🎯 Next Steps

1. Create an operator: `POST /api/v1/operators`
2. Register a user: `POST /api/v1/auth/register`
3. Login: `POST /api/v1/auth/login`
4. Start using the API!

---

**Need Help?** Check `docs/SETUP_GUIDE.md` for detailed instructions.
