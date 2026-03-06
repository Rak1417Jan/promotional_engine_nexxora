#!/bin/bash

# Script to fix DATABASE_URL in .env file for macOS Homebrew PostgreSQL

echo "Fixing DATABASE_URL in .env file..."

# Get current username
USERNAME=$(whoami)

# Backup .env file if it exists
if [ -f .env ]; then
    echo "Backing up existing .env file..."
    cp .env .env.backup
fi

# Update DATABASE_URL in .env file
if [ -f .env ]; then
    # Check if DATABASE_URL exists
    if grep -q "^DATABASE_URL=" .env; then
        # Update existing DATABASE_URL
        sed -i.bak "s|^DATABASE_URL=.*|DATABASE_URL=postgresql://${USERNAME}@localhost:5432/promotional_engine|" .env
        echo "Updated DATABASE_URL to use username: ${USERNAME}"
    else
        # Add DATABASE_URL if it doesn't exist
        echo "DATABASE_URL=postgresql://${USERNAME}@localhost:5432/promotional_engine" >> .env
        echo "Added DATABASE_URL with username: ${USERNAME}"
    fi
    # Remove backup file created by sed
    rm -f .env.bak
else
    echo "Error: .env file not found!"
    echo "Please create .env file from .env.example first:"
    echo "  cp .env.example .env"
    exit 1
fi

echo ""
echo "DATABASE_URL has been updated to:"
grep "^DATABASE_URL=" .env

echo ""
echo "Now you can run: alembic upgrade head"

