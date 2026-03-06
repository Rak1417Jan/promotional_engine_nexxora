#!/bin/bash

# Script to get your exact PostgreSQL connection URL

echo "=== PostgreSQL Setup Check ==="
echo ""

# Check if PostgreSQL is running
echo "1. Checking PostgreSQL status..."
if brew services list | grep -q "postgresql.*started"; then
    echo "   ✅ PostgreSQL is running"
    brew services list | grep postgresql
else
    echo "   ❌ PostgreSQL is NOT running"
    echo "   Run: brew services start postgresql@14"
    exit 1
fi

echo ""
echo "2. Getting your username..."
USERNAME=$(whoami)
echo "   Username: $USERNAME"

echo ""
echo "3. Checking port..."
if lsof -i :5432 > /dev/null 2>&1; then
    PORT="5432"
    echo "   ✅ PostgreSQL is listening on port $PORT"
else
    PORT="5432"
    echo "   ⚠️  Port $PORT may not be active (this is normal if not connected)"
fi

echo ""
echo "=== Your PostgreSQL Connection URL ==="
echo ""
echo "DATABASE_URL=postgresql://${USERNAME}@localhost:${PORT}/promotional_engine"
echo ""

# Check if database exists
echo "4. Checking if database exists..."
if psql -d postgres -tAc "SELECT 1 FROM pg_database WHERE datname='promotional_engine'" | grep -q 1; then
    echo "   ✅ Database 'promotional_engine' exists"
else
    echo "   ⚠️  Database 'promotional_engine' does NOT exist"
    echo "   Create it with: psql -d postgres -c \"CREATE DATABASE promotional_engine;\""
fi

echo ""
echo "=== To update your .env file, run: ==="
echo "echo 'DATABASE_URL=postgresql://${USERNAME}@localhost:${PORT}/promotional_engine' >> .env"
echo ""
echo "OR manually edit .env and set:"
echo "DATABASE_URL=postgresql://${USERNAME}@localhost:${PORT}/promotional_engine"

