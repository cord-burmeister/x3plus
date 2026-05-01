#!/bin/bash

# Simple wrapper to run periodic_map_saver in the background
# Usage: ./run_map_saver_bg.sh [INTERVAL_MINUTES] [OUTPUT_DIR]

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PERIODIC_SAVER="$SCRIPT_DIR/periodic_map_saver.sh"

INTERVAL=${1:-5}
OUTPUT_DIR=${2:-./maps}

# Check if script exists
if [ ! -f "$PERIODIC_SAVER" ]; then
    echo "Error: periodic_map_saver.sh not found at $PERIODIC_SAVER"
    exit 1
fi

# Create maps directory if needed
mkdir -p "$OUTPUT_DIR"

# Run in background and capture PID
nohup "$PERIODIC_SAVER" "$INTERVAL" "$OUTPUT_DIR" > "$OUTPUT_DIR/periodic_map_saver.log" 2>&1 &
PID=$!

echo "Periodic map saver started (PID: $PID)"
echo "Interval: $INTERVAL minutes"
echo "Output directory: $(cd "$OUTPUT_DIR" && pwd)"
echo "Log file: $(cd "$OUTPUT_DIR" && pwd)/periodic_map_saver.log"
echo ""
echo "To stop: kill $PID"
echo "To view logs: tail -f $OUTPUT_DIR/periodic_map_saver.log"
