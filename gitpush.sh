#!/bin/bash

FILE="$1"

if [ -z "$FILE" ]; then
    echo "Usage: $0 <file>"
    exit 1
fi

if [ ! -f "$FILE" ]; then
    echo "File not found: $FILE"
    exit 1
fi

COMMENT=$(grep '^#' "$FILE" | tail -n 1 | sed 's/^# *//')

if [ -z "$COMMENT" ]; then
    COMMENT="Auto commit"
fi

echo "Commit message: $COMMENT"

git add .
git commit -m "$COMMENT" || exit 1
git push