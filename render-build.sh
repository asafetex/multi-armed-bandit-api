#!/usr/bin/env bash
# Build script for Render
# This script is executed during the build process

echo "🚀 Starting Render build process..."

# Upgrade pip and install build tools
echo "📦 Installing build tools..."
pip install --upgrade pip setuptools wheel

# Install production dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Run any database migrations if needed
echo "🗄️ Preparing database..."
# python -c "from app.models import Base; from app.core.database import engine; Base.metadata.create_all(bind=engine)"

echo "✅ Build process completed successfully!"
