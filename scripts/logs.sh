#!/bin/bash

# Log viewing script for Qwen3-VL Inference Server
# Usage: ./scripts/logs.sh [options]

# Colors
GREEN='\033[0;32m'
NC='\033[0m'

# Parse arguments
FOLLOW=""
TAIL=""
ENVIRONMENT="dev"

while [[ $# -gt 0 ]]; do
    case $1 in
        -f|--follow)
            FOLLOW="-f"
            shift
            ;;
        -n|--tail)
            TAIL="--tail=$2"
            shift 2
            ;;
        --prod)
            ENVIRONMENT="prod"
            shift
            ;;
        --dev)
            ENVIRONMENT="dev"
            shift
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: ./scripts/logs.sh [-f|--follow] [-n|--tail NUM] [--dev|--prod]"
            exit 1
            ;;
    esac
done

echo -e "${GREEN}📋 Viewing logs for $ENVIRONMENT environment...${NC}"

if [ "$ENVIRONMENT" = "prod" ]; then
    docker-compose -f docker-compose.yml -f docker-compose.prod.yml logs $FOLLOW $TAIL
else
    docker-compose -f docker-compose.yml -f docker-compose.dev.yml logs $FOLLOW $TAIL
fi
