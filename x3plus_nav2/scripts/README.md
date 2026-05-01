# Map Saving Scripts

## periodic_map_saver.sh

Automatically saves maps from the Nav2 map server at regular intervals with timestamped filenames.

### Prerequisites

- ROS 2 installed and sourced
- Nav2 running with map_saver service available
- Write permissions to the output directory

### Usage

```bash
./periodic_map_saver.sh [INTERVAL_MINUTES] [OUTPUT_DIR] [MAP_TOPIC] [MAP_SAVER_SERVICE]
```

### Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `INTERVAL_MINUTES` | `5` | Minutes between map saves |
| `OUTPUT_DIR` | `.` (current dir) | Directory to save map files |
| `MAP_TOPIC` | `map` | ROS topic name of the map |
| `MAP_SAVER_SERVICE` | `/map_saver/save_map` | Nav2 map saver service name |

### Examples

**Save map every 5 minutes to current directory:**

```bash
./periodic_map_saver.sh
```

**Save every 10 minutes to ./maps folder:**

```bash
./periodic_map_saver.sh 10 ./maps
```

**Save every 2 minutes from custom map topic and service:**

```bash
./periodic_map_saver.sh 2 /home/user/my_maps custom_map /my_custom_map_saver
```

### Output

Creates timestamped map files:

```
maps/map_20260426_083015.pgm
maps/map_20260426_083015.yaml
maps/map_20260426_083515.pgm
maps/map_20260426_083515.yaml
```

### Stopping the Script

Press `Ctrl+C` to stop the periodic saving.

### Troubleshooting

**Service not found:**

```bash
ros2 service list | grep map_saver
```

**Check if map_saver is running:**

```bash
ros2 node list | grep map_saver
```

**View available maps topics:**

```bash
ros2 topic list | grep map
```

### Integration with Systemd (Optional)

To run as a background service on system startup, create a systemd unit file or use a launch file:

```bash
# Option 1: Run directly in tmux/screen
screen -dm ./periodic_map_saver.sh 10 ./maps

# Option 2: Run with nohup (output to file)
nohup ./periodic_map_saver.sh 10 ./maps > periodic_map_saver.log 2>&1 &
```
