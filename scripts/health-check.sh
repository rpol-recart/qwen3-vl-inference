#!/bin/bash

# Health check script for Qwen3-VL Inference Server
# Usage: ./scripts/health-check.sh [url]

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Default URL
HEALTH_URL=${1:-http://localhost:8000/api/health}

echo -e "${GREEN}🏥 Checking health at: $HEALTH_URL${NC}"

# Perform health check
RESPONSE=$(curl -s -w "\n%{http_code}" $HEALTH_URL)
HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | head -n-1)

if [ "$HTTP_CODE" -eq 200 ]; then
    echo -e "${GREEN}✅ Service is healthy${NC}"
    echo -e "${GREEN}Response:${NC}"
    echo "$BODY" | jq . 2>/dev/null || echo "$BODY"

    # Check GPU status
    echo -e "\n${GREEN}🎮 GPU Status:${NC}"
    docker-compose exec qwen3-vl-server nvidia-smi --query-gpu=index,name,utilization.gpu,memory.used,memory.total --format=csv,noheader 2>/dev/null || \
    echo -e "${YELLOW}⚠️  Could not query GPU status${NC}"

    exit 0
else
    echo -e "${RED}❌ Service is unhealthy${NC}"
    echo -e "${RED}HTTP Code: $HTTP_CODE${NC}"
    echo -e "${RED}Response: $BODY${NC}"

    # Show recent logs
    echo -e "\n${YELLOW}📋 Recent logs:${NC}"
    docker-compose logs --tail=20 qwen3-vl-server

    exit 1
fi
