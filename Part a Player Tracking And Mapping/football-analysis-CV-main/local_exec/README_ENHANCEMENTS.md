# Football Analysis Project - Enhanced with Pitch Map Visualization

## New Features Added

This enhanced version of the football analysis project includes:

### 1. **Player Position Tracking**
- Tracks all detected players' positions throughout the video
- Stores normalized coordinates for each player
- Maintains separate tracking for both teams and referees
- Calculates average positions across all frames

### 2. **Mini Football Pitch Visualization**
- Creates a realistic miniature football pitch with proper markings:
  - Halfway line
  - Center circle with center spot
  - Penalty areas and goal areas (both sides)
  - Penalty spots
  - Corner arcs
  - Boundary lines
- Pitch dimensions: 300x450 pixels (customizable)

### 3. **Player Mapping on Pitch**
- Maps detected video coordinates to normalized pitch coordinates
- Automatically scales to pitch dimensions
- Color-coded player visualization:
  - **Blue circles**: Team 1 players
  - **Red circles**: Team 2 players
  - **Yellow circles**: Referee
  - **Orange dots**: Ball position
- Each player's ID is displayed on the pitch

### 4. **Ball Possession Calculation**
- Calculates ball possession percentage for each team
- Displays on both the video and the pitch map
- Format: "Team 1 Possession: X.XX%" and "Team 2 Possession: Y.YY%"

### 5. **Output Generation**
- **Video Output**: Annotated video with player detection, team colors, and ball possession
- **Pitch Map Output**: PNG image showing tactical player positions on the field
- **Statistics Output**: Text file with ball possession statistics
- All outputs saved to: `output/` folder

## File Structure

```
football-analysis-CV-main/local_exec/
├── main_test.py              # Main pipeline with pitch map generation
├── config/config.py          # Configuration (updated with output paths)
├── utils/
│   ├── pitch_map.py          # NEW: Pitch visualization and coordinate mapping
│   ├── player_tracker.py     # NEW: Player position tracking
│   ├── annotation.py         # Frame annotation
│   ├── video.py              # Video I/O
│   └── ...other utilities
├── input_video/
│   └── 08fd33_4.mp4          # Input video file
└── output_video/
    └── result.avi            # Output annotated video

output/                         # NEW: Output folder for results
├── pitch_map.png             # Tactical pitch visualization
└── stats.txt                 # Ball possession statistics
```

## Key Classes and Functions

### PitchMap Class (`utils/pitch_map.py`)
```python
pitch_map = PitchMap(pitch_width=300, pitch_height=450)

# Normalize video coordinates to 0-1 range
norm_x, norm_y = PitchMap.normalize_coordinates(x, y, frame_width, frame_height)

# Draw players on pitch
pitch = pitch_map.draw_player(pitch, norm_x, norm_y, color, player_id)

# Draw ball on pitch
pitch = pitch_map.draw_ball(pitch, norm_x, norm_y, color)

# Get fresh copy of pitch
pitch = pitch_map.get_blank_pitch()
```

### PlayerTracker Class (`utils/player_tracker.py`)
```python
tracker = PlayerTracker()

# Add player position for current frame
tracker.add_player_position(player_id, norm_x, norm_y, team_id)

# Get average positions across all frames
avg_positions = tracker.get_average_positions()  # {player_id: (avg_x, avg_y, team_id)}

# Move to next frame
tracker.increment_frame()
```

## Configuration

Edit `config/config.py` to customize:
- `VIDEO_SRC`: Input video path
- `OUT_VIDEO`: Output video path
- `OUTPUT_FOLDER`: Output folder for pitch map and statistics
- `ROBOFLOW_API_KEY`: Roboflow API key for detection
- `PLAYER_DETECTION_MODEL_ID`: Roboflow player/object detection model
- `FIELD_DETECTION_MODEL_ID`: Roboflow field keypoint detection model

## Output Files

After running the pipeline, you'll get:

1. **result.avi** - Annotated video with:
   - Player detection boxes (blue/red for teams, yellow for referee)
   - Player IDs and positions
   - Ball possession percentage
   - Active player highlighting

2. **pitch_map.png** - Tactical visualization showing:
   - All player positions (averaged across video)
   - Team colors (blue/red)
   - Referee position (yellow)
   - Ball position
   - Ball possession percentages

3. **stats.txt** - Statistics file with:
   - Team 1 possession percentage
   - Team 2 possession percentage
   - Frame counts

## Workflow

1. **Video Processing Loop**:
   - Roboflow detects players, ball, and referee
   - Team assignment based on jersey colors
   - Ball possession tracking
   - Player positions normalized and stored

2. **After Video Complete**:
   - Player positions are averaged
   - Pitch map is generated with player visualizations
   - Statistics are calculated and saved
   - All outputs written to `output/` folder

## Coordinate Mapping

The system uses normalized coordinates (0-1) for the pitch mapping:
- Video pixel coordinates → Normalized coordinates → Pitch pixel coordinates
- This ensures the mapping works with any video resolution
- Coordinates are automatically clamped to valid ranges

## Customization

### Adjust Pitch Dimensions
```python
pitch_map = PitchMap(pitch_width=400, pitch_height=600)
```

### Change Player Circle Size
Modify in `main_test.py` `generate_pitch_map()` function:
```python
pitch = pitch_map.draw_player(pitch, avg_x, avg_y, color, player_id=str(player_id), radius=8)
```

### Modify Colors
Edit color tuples in `generate_pitch_map()`:
```python
team1_color = (255, 0, 0)      # Blue in BGR
team2_color = (0, 0, 255)      # Red in BGR
referee_color = (0, 255, 255)  # Yellow in BGR
```

## Performance Notes

- Frame skipping in main loop: processes 1 in 10 frames (optimize performance)
- ByteTrack used for temporal consistency
- Ball possession calculated on actual frames with ball detection
- Position averaging provides smooth tactical visualization

## Requirements

- requests
- supervision
- opencv-python (cv2)
- numpy
- tqdm
- sklearn

## Future Enhancements

Possible improvements:
- Heatmaps of player activity areas
- Ball trajectory visualization
- Player movement trails
- Real-time play-by-play annotations
- Formation detection
- Pass completion tracking
