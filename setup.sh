#!/bin/bash

# Setup script for Hackathon 2026 - Threat Hunting Lab

echo "========================================="
echo "Hackathon 2026 - Threat Hunting Lab Setup"
echo "========================================="
echo ""

# Check prerequisites
echo "[1/5] Checking prerequisites..."

if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose not found. Please install Docker Compose first."
    exit 1
fi

echo "✓ Docker found: $(docker --version)"
echo "✓ Docker Compose found: $(docker-compose --version)"
echo ""

# Create .env file if not exists
echo "[2/5] Setting up environment..."

if [ ! -f .env ]; then
    cp .env.example .env
    echo "⚠️  Please edit .env file and add your ANTHROPIC_API_KEY"
    echo ""
    read -p "Enter your Anthropic API key (or press Enter to skip): " api_key

    if [ ! -z "$api_key" ]; then
        sed -i "s/your_anthropic_api_key_here/$api_key/" .env
        echo "✓ API key configured"
    else
        echo "⚠️  Skipped. You can add it later in .env file"
    fi
else
    echo "✓ .env file already exists"
fi
echo ""

# Create necessary directories
echo "[3/5] Creating directories..."
mkdir -p data splunk_data/{etc,var} threat-hunter/{config,reports}
echo "✓ Directories created"
echo ""

# Build Docker images
echo "[4/5] Building Docker images..."
echo "This may take several minutes on first run..."
docker-compose build
echo "✓ Images built successfully"
echo ""

# Start services
echo "[5/5] Starting services..."
docker-compose up -d

echo ""
echo "========================================="
echo "Setup Complete!"
echo "========================================="
echo ""
echo "Services starting up..."
echo ""
echo "📊 Splunk Web UI: http://localhost:8000"
echo "   Username: admin"
echo "   Password: Admin@123456"
echo ""
echo "⏳ Please wait 2-3 minutes for Splunk to fully initialize"
echo ""
echo "Useful commands:"
echo "  docker-compose logs -f               # View all logs"
echo "  docker-compose logs -f splunk-lab    # View Splunk logs"
echo "  docker-compose logs -f threat-hunter-agent  # View agent logs"
echo "  docker-compose ps                    # Check service status"
echo "  docker-compose down                  # Stop all services"
echo ""
echo "To manually trigger threat hunt:"
echo "  docker exec threat-hunter-agent python agent.py --hunt-now"
echo ""
echo "Reports will be saved to: ./threat-hunter/reports/"
echo ""
