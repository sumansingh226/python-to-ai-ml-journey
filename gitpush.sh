#!/bin/bash

echo "SCRIPT RUNNING FOR: $1"

FILE="$1"

if [ -z "$FILE" ]; then
    echo "Usage: $0 <file>"
    exit 1
fi

if [ ! -f "$FILE" ]; then
    echo "File not found: $FILE"
    exit 1
fi

# Extract the last line starting with # (ignoring leading whitespace)
COMMENT=$(grep -E '^[[:space:]]*#' "$FILE" | tail -n 1 | sed 's/^[[:space:]]*#[[:space:]]*//')

if [ -z "$COMMENT" ]; then
    COMMENT="Auto commit: update $(basename "$FILE")"
fi

echo "Commit message: $COMMENT"

git add .
git commit -m "$COMMENT" || exit 1
git push