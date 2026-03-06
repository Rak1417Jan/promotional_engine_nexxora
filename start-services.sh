#!/usr/bin/env bash
# Start Docker services for Nexxora Promotional Engine (macOS/Linux)
# Run from the project root directory.

set -e

# Use docker-compose (v1) or docker compose (v2)
if command -v docker-compose &>/dev/null; then
    DCOMPOSE="docker-compose"
else
    DCOMPOSE="docker compose"
fi

echo ""
echo "Starting Nexxora Promotional Engine Services..."
echo ""

# Check if Docker is running
echo "Checking Docker..."
if ! docker ps &>/dev/null; then
    echo "Docker is not running!"
    echo "Please start Docker Desktop and try again."
    exit 1
fi
echo "Docker is running"
echo ""

echo "Starting essential services (PostgreSQL, MongoDB, Redis)..."
echo "This may take a few minutes on first run..."
echo ""

$DCOMPOSE up -d postgres mongodb redis

echo ""
echo "Essential services started!"
echo ""
echo "Waiting 10 seconds for services to initialize..."
sleep 10

echo ""
echo "Starting optional services (Kafka, Zookeeper, MinIO)..."
$DCOMPOSE up -d zookeeper kafka minio 2>/dev/null || true

echo ""
echo "Checking service status..."
$DCOMPOSE ps

echo ""
echo "Next Steps:"
echo "  1. Initialize database:  cd backend && python scripts/init_database.py"
echo "  2. Start backend:        cd backend && source myenv/bin/activate && uvicorn app.main:app --reload --port 8001"
echo "  3. Open frontend:        open frontend/index.html  (or serve frontend folder)"
echo "  4. API docs:             http://localhost:8001/api/docs"
echo ""
