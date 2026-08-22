#!/bin/bash
set -e

APP_DIR=/opt/agrovision
BACKUP_DIR=/opt/agrovision-backups
DATE=$(date +%F_%H%M%S)
RETAIN_DAYS=14

mkdir -p "$BACKUP_DIR"

cd "$APP_DIR"
docker compose -f docker-compose.prod.yml exec -T db pg_dump -U agrovision -d agrovision --no-owner --no-acl \
  | gzip > "$BACKUP_DIR/db_${DATE}.sql.gz"

tar czf "$BACKUP_DIR/media_${DATE}.tar.gz" -C backend media

find "$BACKUP_DIR" -type f -mtime +"$RETAIN_DAYS" -delete
