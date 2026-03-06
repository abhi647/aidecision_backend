#!/bin/bash
# Simple deployment script for Boardroom Copilot Backend

echo "🚀 Building Docker image..."
docker build -t boardroom-backend .

echo "🛑 Stopping existing container (if any)..."
docker stop boardroom-backend || true
docker rm boardroom-backend || true

echo "🏃 Starting new container on port 8001..."
docker run -d --name boardroom-backend -p 8001:8001 --restart unless-stopped boardroom-backend

echo "✅ Deployment complete! API is running on port 8001."
