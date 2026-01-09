#!/bin/bash

# Backup script for Qwen3-VL volumes and configuration
# Usage: ./scripts/backup.sh [backup_dir]

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Default backup directory
BACKUP_BASE_DIR=${1:-./backups}
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
BACKUP_DIR="$BACKUP_BASE_DIR/qwen-backup-$TIMESTAMP"

echo -e "${GREEN}📦 Creating backup at $BACKUP_DIR${NC}"

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Backup configuration files
echo -e "${GREEN}📄 Backing up configuration files...${NC}"
cp .env "$BACKUP_DIR/.env" 2>/dev/null || echo -e "${YELLOW}⚠️  .env not found${NC}"
cp docker-compose.yml "$BACKUP_DIR/"
cp docker-compose.*.yml "$BACKUP_DIR/" 2>/dev/null || true

# Backup Docker volumes
echo -e "${GREEN}💾 Backing up model cache volume...${NC}"
docker run --rm \
  -v qwen_model-cache:/data \
  -v "$(pwd)/$BACKUP_DIR":/backup \
  alpine tar czf /backup/model-cache.tar.gz -C /data . 2>/dev/null || \
  echo -e "${YELLOW}⚠️  Model cache volume not found or empty${NC}"

echo -e "${GREEN}💾 Backing up HuggingFace cache volume...${NC}"
docker run --rm \
  -v qwen_hf-cache:/data \
  -v "$(pwd)/$BACKUP_DIR":/backup \
  alpine tar czf /backup/hf-cache.tar.gz -C /data . 2>/dev/null || \
  echo -e "${YELLOW}⚠️  HF cache volume not found or empty${NC}"

echo -e "${GREEN}💾 Backing up Transformers cache volume...${NC}"
docker run --rm \
  -v qwen_transformers-cache:/data \
  -v "$(pwd)/$BACKUP_DIR":/backup \
  alpine tar czf /backup/transformers-cache.tar.gz -C /data . 2>/dev/null || \
  echo -e "${YELLOW}⚠️  Transformers cache volume not found or empty${NC}"

# Create backup metadata
echo -e "${GREEN}📝 Creating backup metadata...${NC}"
cat > "$BACKUP_DIR/backup_info.txt" << EOF
Backup created: $TIMESTAMP
Hostname: $(hostname)
Docker version: $(docker --version)
Docker Compose version: $(docker-compose --version)

Volumes backed up:
- model-cache
- hf-cache
- transformers-cache

Configuration files backed up:
- .env
- docker-compose.yml
- docker-compose.*.yml
EOF

# Calculate backup size
BACKUP_SIZE=$(du -sh "$BACKUP_DIR" | cut -f1)

echo -e "${GREEN}✅ Backup completed!${NC}"
echo -e "${GREEN}📊 Backup location: $BACKUP_DIR${NC}"
echo -e "${GREEN}📊 Backup size: $BACKUP_SIZE${NC}"
echo ""
echo -e "${YELLOW}To restore from this backup:${NC}"
echo -e "${YELLOW}  ./scripts/restore.sh $BACKUP_DIR${NC}"
