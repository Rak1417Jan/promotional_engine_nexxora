#!/bin/bash

# Setup Script for Promotional Marketing Engine
# This script sets up the database and seeds sample data

set -e  # Exit on error

echo "🚀 Setting up Promotional Marketing Engine..."
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3.11 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
if [ ! -f "venv/.installed" ]; then
    echo "Installing dependencies..."
    pip3 install --upgrade pip
    pip3 install -r requirements.txt
    touch venv/.installed
    echo "✅ Dependencies installed"
else
    echo "✅ Dependencies already installed"
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Creating from .env.example..."
    cp .env.example .env
    echo "⚠️  Please update .env with your configuration before continuing!"
    echo ""
    read -p "Press Enter to continue after updating .env, or Ctrl+C to exit..."
fi

# Initialize database
echo ""
echo "Initializing database..."
python3 scripts/init_database.py --drop-existing --yes

# Seed sample data
echo ""
echo "Seeding sample data..."
python3 scripts/seed_sample_data.py

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Start the backend: uvicorn app.main:app --reload"
echo "  2. Start the frontend: cd ../frontend && python3 -m http.server 8080"
echo "  3. Visit: http://localhost:8080"
echo ""

