#!/bin/bash

# Periodic Map Saver for ROS 2 Nav2
# This script saves maps from the Nav2 map server at regular intervals with timestamped filenames

set -e  # Exit on error

# Default values
INTERVAL_MINUTES=${1:-5}           # Interval between map saves (default 5 minutes)
OUTPUT_DIR=${2:-.}                 # Output directory (default current directory)
MAP_TOPIC=${3:-map}                # Map topic name (default "map")
MAP_SAVER_SERVICE=${4:-/map_saver/save_map}  # Map saver service name

# Validate interval is a positive number
if ! [[ "$INTERVAL_MINUTES" =~ ^[0-9]+$ ]] || [ "$INTERVAL_MINUTES" -le 0 ]; then
    echo "Error: Interval must be a positive integer (in minutes)"
    echo "Usage: $0 [INTERVAL_MINUTES] [OUTPUT_DIR] [MAP_TOPIC] [MAP_SAVER_SERVICE]"
    echo "Example: $0 5 ./maps map /map_saver/save_map"
    exit 1
fi

# Create output directory if it doesn't exist
if [ ! -d "$OUTPUT_DIR" ]; then
    echo "Creating output directory: $OUTPUT_DIR"
    mkdir -p "$OUTPUT_DIR"
fi

# Check if ROS 2 is set up
if [ -z "$ROS_DOMAIN_ID" ] && [ -z "$ROS_DISTRO" ]; then
    echo "Warning: ROS 2 environment not detected. Make sure to source setup.bash before running this script."
fi

INTERVAL_SECONDS=$((INTERVAL_MINUTES * 60))
COUNTER=1

echo "======================================================"
echo "Periodic Map Saver Started"
echo "======================================================"
echo "Interval: $INTERVAL_MINUTES minutes ($INTERVAL_SECONDS seconds)"
echo "Output directory: $(cd "$OUTPUT_DIR" && pwd)"
echo "Map topic: $MAP_TOPIC"
echo "Map saver service: $MAP_SAVER_SERVICE"
echo "======================================================"
echo ""

# Main loop
while true; do
    TIMESTAMP=$(date '+%Y%m%d_%H%M%S')
    MAP_FILENAME="map_${TIMESTAMP}"
    MAP_FILEPATH="$OUTPUT_DIR/$MAP_FILENAME"
    
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ($COUNTER) Saving map to: $MAP_FILEPATH"
    
    # Call the map saver service
    # The service saves both .pgm and .yaml files
    if ros2 service call "$MAP_SAVER_SERVICE" nav2_msgs/srv/SaveMap "{map_topic: $MAP_TOPIC, map_url: $MAP_FILEPATH}" > /dev/null 2>&1; then
        if [ -f "${MAP_FILEPATH}.pgm" ] && [ -f "${MAP_FILEPATH}.yaml" ]; then
            FILE_SIZE_PGM=$(du -h "${MAP_FILEPATH}.pgm" | cut -f1)
            echo "  ✓ Success: Map saved (${MAP_FILEPATH}.pgm: $FILE_SIZE_PGM, ${MAP_FILEPATH}.yaml)"
        else
            echo "  ⚠ Service call succeeded but files not found. Checking service response..."
            # Try alternative call format for different Nav2 versions
            if ros2 service call "$MAP_SAVER_SERVICE" nav2_msgs/srv/SaveMap "{map_url: $MAP_FILEPATH}" > /dev/null 2>&1; then
                if [ -f "${MAP_FILEPATH}.pgm" ]; then
                    echo "  ✓ Success: Map saved (alternative format)"
                else
                    echo "  ✗ Failed: Service call succeeded but files not created"
                fi
            else
                echo "  ✗ Failed: Service call unsuccessful"
            fi
        fi
    else
        echo "  ✗ Failed: Could not call $MAP_SAVER_SERVICE"
        echo "  Ensure the map_saver node is running and the service is available."
        echo "  Check with: ros2 service list | grep map_saver"
    fi
    
    echo "  Waiting $INTERVAL_MINUTES minutes until next save..."
    echo ""
    
    # Sleep for the specified interval
    sleep "$INTERVAL_SECONDS"
    
    ((COUNTER++))
done
