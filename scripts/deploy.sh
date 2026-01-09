#!/bin/bash

# Deployment script for Qwen3-VL Inference Server
# Usage: ./scripts/deploy.sh [dev|prod]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Default to dev if no argument
ENVIRONMENT=${1:-dev}

echo -e "${GREEN}🚀 Starting deployment for ${ENVIRONMENT} environment...${NC}"

# Validate environment
if [[ "$ENVIRONMENT" != "dev" && "$ENVIRONMENT" != "prod" ]]; then
    echo -e "${RED}❌ Invalid environment. Use 'dev' or 'prod'${NC}"
    exit 1
fi

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  .env file not found. Creating from .env.docker...${NC}"
    cp .env.docker .env
    echo -e "${YELLOW}📝 Please edit .env file with your configuration${NC}"
    exit 1
fi

# Check Docker and Docker Compose
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed${NC}"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose is not installed${NC}"
    exit 1
fi

# Check NVIDIA Docker runtime
if ! docker run --rm --gpus all nvidia/cuda:12.1.0-base-ubuntu22.04 nvidia-smi &> /dev/null; then
    echo -e "${RED}❌ NVIDIA Docker runtime is not properly configured${NC}"
    exit 1
fi

# Build Docker image
echo -e "${GREEN}🏗️  Building Docker image...${NC}"
if [ "$ENVIRONMENT" = "prod" ]; then
    docker-compose -f docker-compose.yml -f docker-compose.prod.yml build --no-cache
else
    docker-compose -f docker-compose.yml -f docker-compose.dev.yml build
fi

# Stop old containers
echo -e "${GREEN}🛑 Stopping old containers...${NC}"
if [ "$ENVIRONMENT" = "prod" ]; then
    docker-compose -f docker-compose.yml -f docker-compose.prod.yml down
else
    docker-compose -f docker-compose.yml -f docker-compose.dev.yml down
fi

# Start new containers
echo -e "${GREEN}▶️  Starting new containers...${NC}"
if [ "$ENVIRONMENT" = "prod" ]; then
    docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
else
    docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
fi

# Wait for service to be ready
echo -e "${GREEN}⏳ Waiting for service to be ready...${NC}"
MAX_RETRIES=60
RETRY_COUNT=0
HEALTH_URL="http://localhost:8000/api/health"

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -sf $HEALTH_URL > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Service is healthy!${NC}"
        break
    fi
    RETRY_COUNT=$((RETRY_COUNT + 1))
    echo -e "${YELLOW}⏳ Waiting... ($RETRY_COUNT/$MAX_RETRIES)${NC}"
    sleep 5
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    echo -e "${RED}❌ Service failed to start within expected time${NC}"
    echo -e "${YELLOW}📋 Showing logs:${NC}"
    if [ "$ENVIRONMENT" = "prod" ]; then
        docker-compose -f docker-compose.yml -f docker-compose.prod.yml logs --tail=50
    else
        docker-compose -f docker-compose.yml -f docker-compose.dev.yml logs --tail=50
    fi
    exit 1
fi

# Display status
echo -e "${GREEN}📊 Container status:${NC}"
if [ "$ENVIRONMENT" = "prod" ]; then
    docker-compose -f docker-compose.yml -f docker-compose.prod.yml ps
else
    docker-compose -f docker-compose.yml -f docker-compose.dev.yml ps
fi

echo -e "${GREEN}✅ Deployment successful!${NC}"
echo -e "${GREEN}🌐 API documentation: http://localhost:8000/docs${NC}"
echo -e "${GREEN}🏥 Health check: http://localhost:8000/api/health${NC}"
