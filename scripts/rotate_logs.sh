#!/bin/bash
LOG_FILE="SESSION_LOG.md"
MAX_LINES=100
ARCHIVE_DIR="specs/logs/$(date +%Y-%m-%d)"

if [ -f "$LOG_FILE" ]; then
    LINE_COUNT=$(wc -l < "$LOG_FILE")
    if [ "$LINE_COUNT" -gt "$MAX_LINES" ]; then
        mkdir -p "$ARCHIVE_DIR"
        TIMESTAMP=$(date +%H%M%S)
        cp "$LOG_FILE" "$ARCHIVE_DIR/session_log_$TIMESTAMP.md"
        
        # Garder le header (ligne 1) et les 20 dernières lignes
        HEADER=$(head -n 1 "$LOG_FILE")
        TAIL_CONTENT=$(tail -n 20 "$LOG_FILE")
        
        echo "$HEADER" > "$LOG_FILE"
        echo -e "\n... [Rotation automatique : Contenu archivé dans $ARCHIVE_DIR] ...\n" >> "$LOG_FILE"
        echo "$TAIL_CONTENT" >> "$LOG_FILE"
        
        echo "Rotation effectuée : $LINE_COUNT lignes -> Archive créée."
    fi
fi
