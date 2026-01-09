#!/bin/bash

# Restore script for Qwen3-VL volumes and configuration
# Usage: ./scripts/restore.sh <backup_dir>

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check if backup directory is provided
if [ -z "$1" ]; then
    echo -e "${RED}❌ Usage: ./scripts/restore.sh <backup_dir>${NC}"
    exit 1
fi

BACKUP_DIR=$1

# Check if backup directory exists
if [ ! -d "$BACKUP_DIR" ]; then
    echo -e "${RED}❌ Backup directory not found: $BACKUP_DIR${NC}"
    exit 1
fi

echo -e "${GREEN}🔄 Restoring from backup: $BACKUP_DIR${NC}"

# Display backup info
if [ -f "$BACKUP_DIR/backup_info.txt" ]; then
    echo -e "${GREEN}📋 Backup information:${NC}"
    cat "$BACKUP_DIR/backup_info.txt"
    echo ""
fi

# Confirm restoration
read -p "⚠️  This will overwrite current data. Continue? (yes/no): " CONFIRM
if [ "$CONFIRM" != "yes" ]; then
    echo -e "${YELLOW}❌ Restore cancelled${NC}"
    exit 0
fi

# Stop containers
echo -e "${GREEN}🛑 Stopping containers...${NC}"
docker-compose down || true

# Restore configuration files
echo -e "${GREEN}📄 Restoring configuration files...${NC}"
if [ -f "$BACKUP_DIR/.env" ]; then
    cp "$BACKUP_DIR/.env" .env
    echo -e "${GREEN}✅ Restored .env${NC}"
fi

if [ -f "$BACKUP_DIR/docker-compose.yml" ]; then
    cp "$BACKUP_DIR/docker-compose.yml" .
    echo -e "${GREEN}✅ Restored docker-compose.yml${NC}"
fi

# Restore volumes
if [ -f "$BACKUP_DIR/model-cache.tar.gz" ]; then
    echo -e "${GREEN}💾 Restoring model cache volume...${NC}"
    docker run --rm \
      -v qwen_model-cache:/data \
      -v "$(pwd)/$BACKUP_DIR":/backup \
      alpine sh -c "cd /data && tar xzf /backup/model-cache.tar.gz"
    echo -e "${GREEN}✅ Restored model cache${NC}"
fi

if [ -f "$BACKUP_DIR/hf-cache.tar.gz" ]; then
    echo -e "${GREEN}💾 Restoring HuggingFace cache volume...${NC}"
    docker run --rm \
      -v qwen_hf-cache:/data \
      -v "$(pwd)/$BACKUP_DIR":/backup \
      alpine sh -c "cd /data && tar xzf /backup/hf-cache.tar.gz"
    echo -e "${GREEN}✅ Restored HF cache${NC}"
fi

if [ -f "$BACKUP_DIR/transformers-cache.tar.gz" ]; then
    echo -e "${GREEN}💾 Restoring Transformers cache volume...${NC}"
    docker run --rm \
      -v qwen_transformers-cache:/data \
      -v "$(pwd)/$BACKUP_DIR":/backup \
      alpine sh -c "cd /data && tar xzf /backup/transformers-cache.tar.gz"
    echo -e "${GREEN}✅ Restored Transformers cache${NC}"
fi

echo -e "${GREEN}✅ Restore completed!${NC}"
echo -e "${YELLOW}To start the service, run:${NC}"
echo -e "${YELLOW}  docker-compose up -d${NC}"
