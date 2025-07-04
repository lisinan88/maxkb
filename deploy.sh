#!/bin/bash

# MaxKB AIOps Deployment Script

echo "Starting MaxKB AIOps deployment..."

# Method 1: Docker (Recommended)
deploy_docker() {
    echo "Deploying with Docker..."
    docker-compose up -d
    echo "MaxKB AIOps deployed at http://localhost:8080"
    echo "Default login: admin / MaxKB@123.."
}

# Method 2: Manual deployment
deploy_manual() {
    echo "Manual deployment..."
    
    # Install dependencies
    pip install -r requirements-aiops.txt
    
    # Database setup
    python apps/manage.py migrate
    
    # Collect static files
    python apps/manage.py collectstatic --noinput
    
    # Start services
    python main.py start all -d
    
    echo "MaxKB AIOps deployed at http://localhost:8080"
}

# Check if Docker is available
if command -v docker &> /dev/null && command -v docker-compose &> /dev/null; then
    deploy_docker
else
    echo "Docker not found, using manual deployment..."
    deploy_manual
fi

echo "Deployment complete!"
echo "Access AIOps dashboard at: http://localhost:8080/aiops/"