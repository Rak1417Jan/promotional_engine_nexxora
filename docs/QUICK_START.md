# Quick Start Guide - Phase 1

**Status:** ✅ All Features Implemented - Ready to Test!

---

## 🚀 Quick Setup (5 Minutes)

### 1. Start Services
```bash
# Start all Docker services
docker-compose up -d

# Wait for services to be healthy (30 seconds)
docker-compose ps
```

### 2. Setup Environment
```bash
cd backend

# Create .env file (copy from SETUP_GUIDE.md section 4.2)
# Fill in your API keys:
# - SECRET_KEY (generate with: python -c "import secrets; print(secrets.token_urlsafe(32))")
# - OPENAI_API_KEY
# - SENDGRID_API_KEY
# - TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER
```

### 3. Initialize Database
```bash
# Activate virtual environment
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Initialize database
python scripts/init_database.py
```

### 4. Start Server
```bash
# Start FastAPI server
uvicorn app.main:app --reload
```

### 5. Test API
Open browser: http://localhost:8000/api/docs

---

## 📋 API Testing Examples

### 1. Register & Login
```bash
# Register a user (you'll need an operator_id first - create via /api/v1/operators)
curl -X POST "http://localhost:8000/api/v1/auth/register?operator_id=1" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "SecurePass123!",
    "first_name": "Admin",
    "last_name": "User",
    "role": "admin"
  }'

# Login
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "SecurePass123!"
  }'

# Save the access_token from response
```

### 2. Import Data
```bash
# Upload a CSV file
curl -X POST "http://localhost:8000/api/v1/imports?entity_type=player&file_format=csv" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "file=@players.csv"

# Check import status
curl -X GET "http://localhost:8000/api/v1/imports/1" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 3. Get Insights
```bash
# Get player insights
curl -X GET "http://localhost:8000/api/v1/insights/players/player_123" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Get campaign recommendations
curl -X GET "http://localhost:8000/api/v1/insights/campaigns/recommendations" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 4. Create & Execute Campaign
```bash
# Create campaign
curl -X POST "http://localhost:8000/api/v1/campaigns" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "operator_id": 1,
    "name": "Welcome Campaign",
    "campaign_type": "email",
    "trigger_type": "manual",
    "config": {
      "template": "welcome",
      "subject": "Welcome!"
    }
  }'

# Execute campaign
curl -X POST "http://localhost:8000/api/v1/campaigns/1/execute" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Get analytics
curl -X GET "http://localhost:8000/api/v1/campaigns/1/analytics" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## ✅ What's Implemented

### Authentication ✅
- User registration & login
- JWT tokens with refresh
- Multi-tenancy support
- Password management

### Import/Export ✅
- CSV, JSON, Excel, XML import
- Schema detection
- MongoDB storage
- Export in multiple formats
- MinIO file storage

### ML Insights ✅
- Churn prediction (7-day, 30-day)
- LTV prediction
- Campaign recommendations
- Business intelligence
- OpenAI integration

### Campaigns ✅
- Campaign creation
- Multi-channel delivery (Email, SMS, WhatsApp)
- Message personalization
- Campaign analytics
- AI campaign generation

---

## 📚 Documentation

- **SETUP_GUIDE.md** - Complete setup instructions
- **PHASE_1_PRD.md** - Product requirements
- **PHASE_1_IMPLEMENTATION.md** - Implementation details
- **PHASE_1_COMPLETE.md** - Completion summary
- **DATABASE_ARCHITECTURE_AND_TECHNOLOGIES.md** - Architecture docs

---

## 🎯 Next Steps

1. **Test all endpoints** using FastAPI docs (http://localhost:8000/api/docs)
2. **Import sample data** to test import/export
3. **Create test campaigns** and execute them
4. **Check insights** for imported players
5. **Build frontend** to consume these APIs

---

**You're all set! 🎉**
