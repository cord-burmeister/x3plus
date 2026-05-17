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

Optional environment variables:

```bash
MAP_MODE=trinary          # trinary | scale | raw
FREE_THRESH=0.25          # [0.0..1.0]
OCC_THRESH=0.65           # [0.0..1.0]
IMAGE_FORMAT=pgm          # pgm | png | bmp
```

### Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `INTERVAL_MINUTES` | `5` | Minutes between map saves |
| `OUTPUT_DIR` | `.` (current dir) | Directory to save map files |
| `MAP_TOPIC` | `map` | ROS topic name of the map |
| `MAP_SAVER_SERVICE` | `/map_saver/save_map` | Nav2 map saver service name |

The script now sends `image_format`, `map_mode`, `free_thresh`, and
`occupied_thresh` in each save request so `map_saver` does not need to fall
back to defaults.

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

**Use `png` output and `scale` map mode:**

```bash
IMAGE_FORMAT=png MAP_MODE=scale ./periodic_map_saver.sh 5 ./maps
```

### Output

Creates timestamped map files:

```text
maps/map_20260426_083015.pgm
maps/map_20260426_083015.yaml
maps/map_20260426_083515.pgm
maps/map_20260426_083515.yaml
```

## export_nav2_map_sequence.py

Converts a set of saved Nav2 map YAML files into an equally sized frame sequence
and optionally encodes a video.

The script uses each YAML file's `resolution` and `origin` to align maps on one
global canvas, so all output frames have the same dimensions.

### Sequence Prerequisites

- Python 3
- Optional for video export: `ffmpeg` in `PATH`
- Optional for PNG/JPG frame output: `pillow` (`pip install pillow`)

### Sequence Usage

```bash
./export_nav2_map_sequence.py INPUT [INPUT ...] [OPTIONS]
```

Where each `INPUT` can be:

- A YAML file
- A directory (searched recursively for `*.yaml`/`*.yml`)
- A glob pattern (for example: `maps/*.yaml`)

### Common Examples

```bash
# Export equally sized PGM frames from all maps in ./maps
./export_nav2_map_sequence.py ./maps --output-dir ./map_frames

# Export PNG frames and create MP4 video
./export_nav2_map_sequence.py ./maps --image-format png --video ./map_timelapse.mp4

# Force output resolution (meters/pixel)
./export_nav2_map_sequence.py ./maps --target-resolution 0.05 --video ./map_005.mp4
```

### Key Options

- `--output-dir`: Directory where frame images are written (default: `./map_frames`)
- `--image-format`: Frame format (`pgm`, `png`, or `jpg`; default: `pgm`)
- `--video`: Optional output video path, for example `map.mp4`
- `--fps`: Video framerate for `--video` (default: `2.0`)
- `--target-resolution`: Output meters/pixel (default: finest input resolution)
- `--background-value`: Fill value for empty canvas regions (default: `205`)
- `--overwrite`: Overwrite existing frames/video
- `--allow-yaw`: Ignore non-zero yaw in YAML origin (default behavior fails on yaw != 0)

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
