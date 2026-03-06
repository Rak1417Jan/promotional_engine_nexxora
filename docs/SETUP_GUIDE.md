# Setup Guide - Phase 1
## AI-Powered iGaming Promotional Engine

**Last Updated:** January 2025

---

## 🚀 Quick Start (5 Minutes)

**For Windows Users - Simplest Method:**

1. **Start Docker Desktop** - Make sure it's running (whale icon in system tray)

2. **Start Services:**
   ```powershell
   # From project root directory
   .\start-services.ps1
   ```
   
   Or manually:
   ```powershell
   docker-compose up -d
   ```

3. **Wait for services to start** (30-60 seconds), then verify:
   ```powershell
   docker-compose ps
   ```
   All services should show "Up" status.

4. **Initialize Database:**
   ```powershell
   cd backend
   python scripts/init_database.py
   ```

5. **Start Backend:**
   ```powershell
   # Make sure you're in backend directory with venv activated
   uvicorn app.main:app --reload
   ```

6. **Test:** Open http://localhost:8000/api/docs

**That's it!** The application should now be running.

---

## Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [Platform Setup](#2-platform-setup)
3. [Local Development Setup](#3-local-development-setup)
4. [Environment Variables](#4-environment-variables)
5. [Database Setup](#5-database-setup)
6. [Service Configuration](#6-service-configuration)
7. [Verification](#7-verification)

---

## 1. Prerequisites

### Required Software

- **Python 3.11+** - [Download](https://www.python.org/downloads/)
- **Node.js 18+** - [Download](https://nodejs.org/)
- **Docker & Docker Compose** - [Download](https://www.docker.com/products/docker-desktop)
- **Git** - [Download](https://git-scm.com/downloads)

### Required Accounts & API Keys

You'll need to sign up for these services (all have free tiers for development):

1. **Groq (Recommended - FREE)** - [Sign Up](https://console.groq.com/)
   - For AI-powered insights and natural language generation
   - **100% Free** - No credit card required
   - Fast inference with Llama 3.1, Mixtral models
   - See [LLM Setup Guide](LLM_SETUP.md) for details

   **OR**

   **OpenAI** - [Sign Up](https://platform.openai.com/signup)
   - For AI-powered insights and natural language generation
   - Free tier: $5 credit

2. **SendGrid** - [Sign Up](https://signup.sendgrid.com/)
   - For email delivery
   - Free tier: 100 emails/day

3. **Twilio** - [Sign Up](https://www.twilio.com/try-twilio)
   - For SMS delivery
   - Free tier: Trial account with $15 credit

---

## 2. Platform Setup

### 2.1 LLM Provider Setup (Groq Recommended - FREE)

**We recommend using Groq (free) instead of OpenAI. See [LLM Setup Guide](LLM_SETUP.md) for details.**

#### Option A: Groq (Recommended - FREE) 🆓

1. Go to [Groq Console](https://console.groq.com/)
2. Sign up (free, no credit card required)
3. Navigate to **API Keys** section
4. Click **"Create API Key"**
5. Copy the API key (starts with `gsk_`)
6. Save it securely - you'll add it to `.env` file

**Benefits:**
- 100% Free (30 requests/minute, 14,400/day)
- Extremely fast (up to 10x faster than OpenAI)
- Open-source models (Llama 3.1, Mixtral)

#### Option B: OpenAI (Paid)

1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Sign up or log in
3. Navigate to **API Keys** section
4. Click **"Create new secret key"**
5. Copy the API key (starts with `sk-`)
6. Save it securely - you'll add it to `.env` file

**Note:** Keep your API key secret. Never commit it to version control.

### 2.2 SendGrid Setup

1. Go to [SendGrid](https://signup.sendgrid.com/)
2. Sign up for a free account
3. Complete email verification
4. Navigate to **Settings → API Keys**
5. Click **"Create API Key"**
6. Name it (e.g., "Promotional Engine Dev")
7. Select **"Full Access"** or **"Restricted Access"** with Mail Send permissions
8. Copy the API key
9. Save it securely

**Optional:** Verify a sender email:
- Go to **Settings → Sender Authentication**
- Verify a single sender email (for development)

### 2.3 Twilio Setup

1. Go to [Twilio](https://www.twilio.com/try-twilio)
2. Sign up for a free trial account
3. Complete phone verification
4. Navigate to **Console Dashboard**
5. Copy your **Account SID** (starts with `AC`)
6. Copy your **Auth Token** (click to reveal)
7. Get a **Phone Number**:
   - Go to **Phone Numbers → Manage → Buy a number**
   - Select a number (free trial numbers available)
   - Copy the phone number

**Note:** Trial accounts have limitations. For production, upgrade to a paid account.

---

## 3. Local Development Setup

### 3.1 Clone and Navigate

```bash
# If not already cloned
git clone <your-repo-url>
cd nexxora_promotional_engine-main

# Navigate to backend
cd backend
```

### 3.2 Python Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate

# Upgrade pip
pip install --upgrade pip
```

### 3.3 Install Python Dependencies

```bash
# Install requirements
pip install -r requirements.txt

# If implementing ML features, also install:
pip install -r requirements-ml.txt
```

### 3.4 Frontend Setup

```bash
# Navigate to frontend
cd ../frontend

# Install dependencies (if using npm/yarn)
# For now, frontend is static HTML/JS, no build step needed
```

### 3.5 Docker Compose Setup

Create `docker-compose.yml` in the project root:

```bash
cd ..  # Back to project root
```

The `docker-compose.yml` file will be created in the next step.

---

## 4. Environment Variables

### 4.1 Create .env File

Create a `.env` file in the `backend/` directory:

```bash
cd backend
touch .env  # On Windows: type nul > .env
```

### 4.2 Environment Variables Template

Copy the following into your `.env` file and fill in the values:

```bash
# ============================================
# Application Configuration
# ============================================
APP_NAME=Promotional Marketing Engine
APP_VERSION=1.0.0
DEBUG=True
SECRET_KEY=your-super-secret-key-change-this-in-production-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# ============================================
# Database Configuration
# ============================================
# PostgreSQL (Canonical Data)
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/promotional_engine
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=10

# MongoDB (Dynamic Data)
MONGODB_URL=mongodb://localhost:27017/nexora_attributes
MONGODB_DB_NAME=nexora_attributes

# ============================================
# Redis Configuration
# ============================================
REDIS_URL=redis://localhost:6379/0
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# ============================================
# Kafka Configuration
# ============================================
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
KAFKA_CLIENT_ID=promotional_engine
KAFKA_GROUP_ID=promotional_engine_group

# ============================================
# MinIO (File Storage) Configuration
# ============================================
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET_NAME=promotional-engine-uploads
MINIO_USE_SSL=False

# ============================================
# LLM Provider Configuration
# ============================================
# Choose: "groq" (FREE, recommended) or "openai" (paid)
LLM_PROVIDER=groq

# Groq Configuration (FREE - Recommended)
GROQ_API_KEY=gsk-your-groq-api-key-here
GROQ_MODEL=llama-3.1-70b-versatile  # or llama-3.1-8b-instant, mixtral-8x7b-32768

# OpenAI Configuration (Optional - if using OpenAI)
OPENAI_API_KEY=sk-your-openai-api-key-here
OPENAI_MODEL=gpt-4-turbo-preview

# ============================================
# Email Configuration (SendGrid)
# ============================================
SENDGRID_API_KEY=SG.your-sendgrid-api-key-here
SENDGRID_FROM_EMAIL=noreply@yourdomain.com
SENDGRID_FROM_NAME=Promotional Engine

# ============================================
# SMS Configuration (Twilio)
# ============================================
TWILIO_ACCOUNT_SID=ACyour-twilio-account-sid
TWILIO_AUTH_TOKEN=your-twilio-auth-token
TWILIO_PHONE_NUMBER=+1234567890
TWILIO_WHATSAPP_NUMBER=whatsapp:+1234567890

# ============================================
# Celery Configuration (Async Tasks)
# ============================================
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2

# ============================================
# CORS Configuration
# ============================================
CORS_ORIGINS=http://localhost:3000,http://localhost:8080,http://127.0.0.1:8080

# ============================================
# Logging Configuration
# ============================================
LOG_LEVEL=INFO

# ============================================
# Performance Configuration
# ============================================
MAX_WORKERS=4
API_RATE_LIMIT=1000

# ============================================
# Feature Flags
# ============================================
ENABLE_ML_MODELS=True
ENABLE_OPENAI=True
ENABLE_EMAIL=True
ENABLE_SMS=True
```

### 4.3 Generate Secret Key

Generate a secure secret key for JWT:

```bash
# Python one-liner
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Or use OpenSSL
openssl rand -hex 32
```

Replace `SECRET_KEY` in `.env` with the generated value.

### 4.4 Environment Variables by Service

| Service | Required Variables | Optional Variables |
|---------|-------------------|-------------------|
| **Application** | `SECRET_KEY`, `DEBUG` | `APP_NAME`, `APP_VERSION` |
| **PostgreSQL** | `DATABASE_URL` | `DATABASE_POOL_SIZE`, `DATABASE_MAX_OVERFLOW` |
| **MongoDB** | `MONGODB_URL` | `MONGODB_DB_NAME` |
| **Redis** | `REDIS_URL` | `REDIS_HOST`, `REDIS_PORT`, `REDIS_DB` |
| **Kafka** | `KAFKA_BOOTSTRAP_SERVERS` | `KAFKA_CLIENT_ID`, `KAFKA_GROUP_ID` |
| **MinIO** | `MINIO_ENDPOINT`, `MINIO_ACCESS_KEY`, `MINIO_SECRET_KEY` | `MINIO_BUCKET_NAME`, `MINIO_USE_SSL` |
| **OpenAI** | `OPENAI_API_KEY` | `OPENAI_MODEL` |
| **SendGrid** | `SENDGRID_API_KEY` | `SENDGRID_FROM_EMAIL`, `SENDGRID_FROM_NAME` |
| **Twilio** | `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_PHONE_NUMBER` | `TWILIO_WHATSAPP_NUMBER` |
| **Celery** | `CELERY_BROKER_URL`, `CELERY_RESULT_BACKEND` | - |

---

## 5. Database Setup

### 5.1 Docker Compose Services

Create `docker-compose.yml` in the project root:

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15
    container_name: nexora_postgres
    environment:
      POSTGRES_DB: promotional_engine
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  mongodb:
    image: mongo:7
    container_name: nexora_mongodb
    ports:
      - "27017:27017"
    volumes:
      - mongodb_data:/data/db
    environment:
      MONGO_INITDB_DATABASE: nexora_attributes
    healthcheck:
      test: ["CMD", "mongosh", "--eval", "db.adminCommand('ping')"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: nexora_redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  zookeeper:
    image: confluentinc/cp-zookeeper:latest
    container_name: nexora_zookeeper
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181
      ZOOKEEPER_TICK_TIME: 2000
    ports:
      - "2181:2181"

  kafka:
    image: confluentinc/cp-kafka:latest
    container_name: nexora_kafka
    depends_on:
      - zookeeper
    ports:
      - "9092:9092"
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://localhost:9092
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
    healthcheck:
      test: ["CMD", "kafka-broker-api-versions", "--bootstrap-server", "localhost:9092"]
      interval: 30s
      timeout: 10s
      retries: 5

  minio:
    image: minio/minio:latest
    container_name: nexora_minio
    ports:
      - "9000:9000"
      - "9001:9001"
    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: minioadmin
    volumes:
      - minio_data:/data
    command: server /data --console-address ":9001"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:9000/minio/health/live"]
      interval: 30s
      timeout: 20s
      retries: 3

volumes:
  postgres_data:
  mongodb_data:
  redis_data:
  minio_data:
```

### 5.2 Start Docker Services

**Windows (Recommended):**
```powershell
# Use the provided script (easiest)
.\start-services.ps1

# Or manually start all services
docker-compose up -d

# Or start essential services only (if having issues)
docker-compose up -d postgres mongodb redis
```

**Linux/Mac:**
```bash
# Start all services
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f
```

**Common Commands:**
```bash
# Check service status
docker-compose ps

# View logs
docker-compose logs -f

# View logs for specific service
docker-compose logs postgres

# Stop services
docker-compose down

# Stop and remove volumes (CAUTION: deletes data)
docker-compose down -v

# Restart a specific service
docker-compose restart postgres
```

**Troubleshooting:**
- If services fail to start, try starting them one at a time:
  ```powershell
  docker-compose up -d postgres
  docker-compose up -d mongodb
  docker-compose up -d redis
  ```
- If images are stuck pulling, see [Docker Pull Issues](#issue-docker-images-stuck-while-pulling)

### 5.3 Initialize PostgreSQL Database

```bash
cd backend

# Activate virtual environment (if not already)
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Initialize database tables
python scripts/init_database.py

# (Optional) Seed sample data
python scripts/seed_sample_data.py
```

### 5.4 Verify Database Connections

```bash
# Test PostgreSQL
psql -h localhost -U postgres -d promotional_engine
# Password: postgres
# Type \dt to list tables, then \q to quit

# Test MongoDB
mongosh mongodb://localhost:27017/nexora_attributes

# Test Redis
redis-cli -h localhost -p 6379
# Type PING, should return PONG
```

---

## 6. Service Configuration

### 6.1 MinIO Setup

1. Access MinIO Console:
   - Open browser: http://localhost:9001
   - Login: `minioadmin` / `minioadmin`

2. Create Bucket:
   - Click **"Buckets"** → **"Create Bucket"**
   - Name: `promotional-engine-uploads`
   - Click **"Create Bucket"**

3. Set Bucket Policy (for development):
   - Click on bucket → **"Access Policy"**
   - Select **"Public"** (for local dev only)
   - Click **"Set"**

### 6.2 Kafka Topics Setup

Kafka topics will be created automatically when the application starts, but you can verify:

```bash
# List topics
docker exec -it nexora_kafka kafka-topics --list --bootstrap-server localhost:9092

# Create topic manually (if needed)
docker exec -it nexora_kafka kafka-topics --create \
  --bootstrap-server localhost:9092 \
  --topic nexora.events.raw \
  --partitions 3 \
  --replication-factor 1
```

### 6.3 Celery Worker Setup

```bash
cd backend

# Activate virtual environment
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Start Celery worker
celery -A app.tasks.celery_app worker --loglevel=info

# In a separate terminal, start Celery beat (for scheduled tasks)
celery -A app.tasks.celery_app beat --loglevel=info
```

---

## 7. Verification

### 7.1 Start Backend Server

```bash
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Start FastAPI server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 7.2 Verify API

1. Open browser: http://localhost:8000
2. Should see: `{"message": "Welcome to Promotional Marketing Engine", ...}`
3. API Docs: http://localhost:8000/api/docs
4. Health Check: http://localhost:8000/health

### 7.3 Start Frontend

```bash
cd frontend

# Using Python's built-in server
python3 -m http.server 8080

# Or using Node.js http-server (if installed)
npx http-server -p 8080
```

Open browser: http://localhost:8080

### 7.4 Test Services

```bash
# Test PostgreSQL
curl http://localhost:8000/health

# Test Redis (via API if endpoint exists)
# Test MongoDB (via API if endpoint exists)
# Test Kafka (via API if endpoint exists)
```

---

## 8. Troubleshooting

### Common Issues

**Issue: Docker daemon not accessible (Windows)**
```
Error: unable to get image 'minio/minio:latest': error during connect: 
in the default daemon configuration on Windows, the docker client must be run 
with elevated privileges to connect: Get "http://%2F%2F.%2Fpipe%2Fdocker_engine/v1.51/...": 
open //./pipe/docker_engine: The system cannot find the file specified.
```

**Solution:**
1. **Start Docker Desktop:**
   - Open Docker Desktop application from Start Menu
   - Wait for Docker Desktop to fully start (whale icon in system tray should be steady)
   - You should see "Docker Desktop is running" in the Docker Desktop window

2. **Verify Docker is running:**
   ```powershell
   # In PowerShell
   docker ps
   # Should return empty list or running containers (not an error)
   ```

3. **If Docker Desktop won't start:**
   - Restart Docker Desktop: Right-click system tray icon → Restart
   - Check Windows Services: `services.msc` → Look for "Docker Desktop Service"
   - Restart the service if needed
   - Ensure WSL 2 is installed and updated (Docker Desktop on Windows requires WSL 2)
   - Check Docker Desktop settings → General → Ensure "Use WSL 2 based engine" is enabled

4. **Run PowerShell as Administrator (if needed):**
   - Right-click PowerShell → "Run as Administrator"
   - Try `docker ps` again

5. **Reinstall Docker Desktop (last resort):**
   - Download latest from: https://www.docker.com/products/docker-desktop
   - Uninstall current version
   - Install new version
   - Restart computer

**Issue: Docker services won't start**
```bash
# Check Docker is running
docker ps

# Check port conflicts
# On Windows PowerShell:
netstat -an | Select-String "5432"   # PostgreSQL
netstat -an | Select-String "27017"  # MongoDB
netstat -an | Select-String "6379"   # Redis
netstat -an | Select-String "9092"   # Kafka
netstat -an | Select-String "9000"   # MinIO

# On Linux/Mac:
netstat -an | grep 5432  # PostgreSQL
netstat -an | grep 27017 # MongoDB
netstat -an | grep 6379  # Redis
netstat -an | grep 9092  # Kafka
netstat -an | grep 9000  # MinIO
```

**Issue: Database connection errors**
- Verify Docker services are running: `docker-compose ps`
- Check DATABASE_URL in `.env` matches docker-compose.yml
- Wait for services to be healthy: `docker-compose ps`

**Issue: Import errors**
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Check Python version
python --version  # Should be 3.11+
```

**Issue: Kafka connection errors**
- Wait for Zookeeper to start first
- Check Kafka logs: `docker-compose logs kafka`
- Verify KAFKA_BOOTSTRAP_SERVERS in `.env`

**Issue: MinIO connection errors**
- Access MinIO console: http://localhost:9001
- Verify bucket exists
- Check MINIO_ACCESS_KEY and MINIO_SECRET_KEY

**Issue: Docker images stuck while pulling**
```
Images appear to be pulling but get stuck at certain percentages
Process takes 200+ seconds with no progress
```

**Quick Fix:**
1. **Cancel (Ctrl+C) and start essential services only:**
   ```powershell
   # Start only what you need to get running
   docker-compose up -d postgres mongodb redis
   ```
   This starts only the 3 essential services (smaller images, faster).

2. **If still stuck, pull images one at a time:**
   ```powershell
   docker pull postgres:15-alpine
   docker pull mongo:7
   docker pull redis:7-alpine
   docker-compose up -d postgres mongodb redis
   ```

3. **Disable Docker proxy (if not needed):**
   - Docker Desktop → Settings → Resources → Proxies
   - Uncheck "Manual proxy configuration" if you don't need it
   - Apply & Restart

4. **Increase Docker resources:**
   - Docker Desktop → Settings → Resources → Advanced
   - Increase CPUs (4+) and Memory (4GB+)
   - Apply & Restart

5. **Clean and retry:**
   ```powershell
   docker-compose down
   docker image prune -a
   docker-compose up -d postgres mongodb redis
   ```

**Note:** You can run the application with just PostgreSQL, MongoDB, and Redis. Kafka and MinIO are optional and can be added later.

---

## 9. Development Workflow

### Daily Startup

```bash
# 1. Start Docker services
docker-compose up -d

# 2. Activate virtual environment
cd backend
source venv/bin/activate

# 3. Start Celery worker (in separate terminal)
celery -A app.tasks.celery_app worker --loglevel=info

# 4. Start FastAPI server
uvicorn app.main:app --reload

# 5. Start frontend (in separate terminal)
cd frontend
python3 -m http.server 8080
```

### Daily Shutdown

```bash
# Stop FastAPI (Ctrl+C)
# Stop Celery (Ctrl+C)
# Stop frontend (Ctrl+C)

# Stop Docker services (optional - can leave running)
docker-compose stop
```

---

## 10. Next Steps

After setup is complete:

1. ✅ Verify all services are running: `docker-compose ps`
2. ✅ Test API: http://localhost:8000/api/docs
3. ✅ Create your first operator via API
4. ✅ Register a user and start using the system

---

## Support & Troubleshooting

### Quick Troubleshooting

**Services won't start:**
```powershell
# Check Docker is running
docker ps

# Check service status
docker-compose ps

# View logs for a specific service
docker-compose logs postgres
docker-compose logs mongodb
```

**Database connection errors:**
- Wait 30 seconds after starting services
- Verify services are healthy: `docker-compose ps`
- Check DATABASE_URL in `.env` matches docker-compose.yml

**Images stuck pulling:**
- Start essential services only: `docker-compose up -d postgres mongodb redis`
- See [Docker Pull Issues](#issue-docker-images-stuck-while-pulling) section above

**For more help:**
- Check logs: `docker-compose logs <service-name>`
- Review error messages in terminal
- Check `.env` file configuration
- Verify all API keys are correct
- See `QUICK_START_WINDOWS.md` for Windows-specific help

---

## Simplified Setup Summary

**Minimum Required Services:**
- PostgreSQL (essential)
- MongoDB (essential)
- Redis (recommended)

**Optional Services:**
- Kafka + Zookeeper (for event streaming)
- MinIO (for file storage)

You can run the application with just PostgreSQL, MongoDB, and Redis. Other services can be added later.

---

**Setup Status:** Ready for Phase 1 Development 🚀
