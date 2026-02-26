#!/bin/bash
# Deployment script for VPS

set -e

echo "========================================"
echo "Real Estate Platform Deployment"
echo "========================================"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
    echo "✓ Docker installed"
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Installing..."
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    echo "✓ Docker Compose installed"
fi

echo ""
echo "📋 Pre-deployment checklist:"
echo "1. .env file configured? (copy from .env.production)"
echo "2. REACT_APP_BACKEND_URL set to your VPS IP?"
echo "3. Ports 80, 8001, 27017 available?"
echo ""
read -p "Continue with deployment? (y/n) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Deployment cancelled."
    exit 1
fi

echo "🔨 Building Docker images..."
docker-compose build

echo ""
echo "🚀 Starting services..."
docker-compose up -d

echo ""
echo "⏳ Waiting for services to be healthy..."
sleep 10

echo ""
echo "📊 Service status:"
docker-compose ps

echo ""
echo "✅ Deployment complete!"
echo ""
echo "🌐 Access your application:"
echo "   Frontend: http://$(hostname -I | awk '{print $1}')"
echo "   Backend API: http://$(hostname -I | awk '{print $1}'):8001/api/"
echo "   MongoDB: mongodb://$(hostname -I | awk '{print $1}'):27017"
echo ""
echo "📝 Useful commands:"
echo "   View logs: docker-compose logs -f"
echo "   Stop all: docker-compose down"
echo "   Restart: docker-compose restart"
echo "   View volumes: docker volume ls"
echo ""
echo "🗄️  Database backup command:"
echo "   docker exec real-estate-mongodb mongodump --out /data/backup"
echo ""