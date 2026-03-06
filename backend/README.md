# Backend - Promotional Marketing Engine

FastAPI backend for the AI-powered iGaming promotional marketing engine.

## Quick Start

1. **Set up environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your database and API keys
   ```

3. **Set up database:**
   ```bash
   # Initialize database tables
   python3 scripts/init_database.py
   
   # Seed sample data (optional)
   python3 scripts/seed_sample_data.py
   ```

4. **Run server:**
   ```bash
   uvicorn app.main:app --reload
   ```

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

## Project Structure

```
backend/
├── app/
│   ├── api/          # API routes
│   ├── models/       # Database models
│   ├── schemas/      # Pydantic schemas
│   ├── services/     # Business logic
│   ├── ml/           # ML/AI services
│   ├── utils/        # Utilities
│   ├── config.py     # Configuration
│   ├── database.py   # Database setup
│   └── main.py        # FastAPI app
├── scripts/          # Setup scripts (init_database, seed_data)
└── requirements.txt  # Dependencies
```

## Environment Variables

See `.env.example` for all required environment variables.

Key variables:
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `OPENAI_API_KEY`: OpenAI API key for AI features
- `SENDGRID_API_KEY`: SendGrid API key for emails
- `TWILIO_ACCOUNT_SID`: Twilio account for SMS

## Development

### Running Tests
```bash
pytest
```

### Database Setup
```bash
# Initialize database tables
python3 scripts/init_database.py

# Seed sample data
python3 scripts/seed_sample_data.py

# Reset database (if needed)
psql -d postgres -c "DROP DATABASE IF EXISTS promotional_engine;"
psql -d postgres -c "CREATE DATABASE promotional_engine;"
python3 scripts/init_database.py
python3 scripts/seed_sample_data.py
```

**Note**: We use simple SQLAlchemy `create_all()` instead of Alembic migrations for simplicity.

### Code Style
```bash
# Format code (if using black)
black app/

# Lint code (if using flake8)
flake8 app/
```

