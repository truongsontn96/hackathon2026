#!/bin/bash

# Quick start script

echo "Starting Threat Hunting Lab..."
docker-compose up -d

echo ""
echo "Waiting for services to be ready..."
sleep 5

echo ""
echo "Checking service status..."
docker-compose ps

echo ""
echo "✓ Lab is running!"
echo ""
echo "Access Splunk: http://localhost:8000 (admin/Admin@123456)"
echo "View logs: docker-compose logs -f"
