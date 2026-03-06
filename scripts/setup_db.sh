#!/bin/bash

# Database Setup Script
# This script helps set up the PostgreSQL database for the promotional engine

echo "Setting up PostgreSQL database for Promotional Marketing Engine..."

# Check if PostgreSQL is running
if ! pg_isready -U postgres > /dev/null 2>&1; then
    echo "Error: PostgreSQL is not running. Please start PostgreSQL first."
    exit 1
fi

# Create database
echo "Creating database..."
psql -U postgres -c "CREATE DATABASE promotional_engine;" 2>/dev/null || echo "Database may already exist"

# Create user (optional)
# psql -U postgres -c "CREATE USER promo_user WITH PASSWORD 'your_password';" 2>/dev/null || echo "User may already exist"
# psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE promotional_engine TO promo_user;" 2>/dev/null

echo "Database setup complete!"
echo "Next steps:"
echo "1. Update DATABASE_URL in backend/.env"
echo "2. Run migrations: cd backend && alembic upgrade head"

