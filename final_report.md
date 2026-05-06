# Football Player Intelligence System

## Complete Final Project Report

### Part A: Player Tracking and Pitch Mapping

### Part B: Player Transfer Fee Prediction

---

## Section 1: Title Page

| Field | Details |
|---|---|
| Project Title | Football Player Intelligence System |
| Part A | Football Player Tracking and Pitch Mapping |
| Part B | Football Player Transfer Fee Prediction |
| Domain | Sports Analytics, Computer Vision, Machine Learning |
| Submitted By | [Your Name] |
| Roll Number | [Your Roll Number] |
| Class | [Your Class] |
| Submitted To | [Teacher Name] |
| Date | May 6, 2026 |
| Project Root | `c:\.Me\.Semester 6\Coding\Python\VS Code\IDS Theory\Football Analysis Model` |

---

## Section 2: Abstract

Football analysis is becoming important in modern sports because clubs, scouts, analysts, and fans want decisions to be based on data instead of only opinion. This project, called the Football Player Intelligence System, combines two football analysis modules into one system.

Part A is a computer vision module. It takes football match video as input and processes it frame by frame. It detects players, the ball, goalkeepers, and referees using a Roboflow object detection model. It assigns players into two teams by checking jersey colors with KMeans clustering. It tracks players using ByteTrack, calculates ball possession by checking which player is nearest to the ball, and maps player and ball positions onto a pitch radar view. The output includes an annotated match video, pitch movement video, pitch radar image, and possession statistics.

Part B is a machine learning module. It predicts football player transfer fees using the Transfermarkt Kaggle dataset. The dataset contains 12 CSV files with player information, club information, appearances, transfer history, market values, games, events, and other context. The system cleans and merges this data, creates football features such as goals per 90 minutes, assists per 90 minutes, age factor, league tier, club strength, international caps, contract years left, and value trend, then trains machine learning models. The trained models are XGBoost, Random Forest, and Neural Network. XGBoost gives the best reported result with MAE of EUR 2.71 million, RMSE of EUR 6.53 million, R2 score of 0.618, and MAPE of 18.5%.

Both parts are integrated into one Flask web application through `app.py`. The user can upload a football video for Part A or use the transfer prediction tools for Part B from the same browser interface. The project also supports downloadable outputs such as processed videos, CSV, JSON, TXT statistics, and PDF transfer reports.

---

## Section 3: Table of Contents

1. Title Page
2. Abstract
3. Introduction
4. Problem Definition
5. Objectives
6. Scope
7. Existing Systems
8. Requirements
9. Technology Stack
10. System Design
11. Part A: Player Tracking and Pitch Mapping
12. Part B: Transfer Fee Prediction
13. Flask Web Integration
14. Complete Working of the Project
15. Results and Analysis
16. Recommended Diagrams and Screenshots
17. Advantages and Limitations
18. Challenges Faced
19. Future Scope
20. Viva Preparation
21. Conclusion
22. References
23. Appendix

---

## Section 4: Recommended Figures and Screenshots

Your old report listed too many diagrams. You do not need to place all 18 diagrams. For a clean final report, use these important figures only.

### Recommended Diagrams

| Figure No. | Figure Name | Why It Is Needed |
|---|---|---|
| Figure 1 | Combined System Architecture Diagram | Shows how Part A, Part B, and Flask connect |
| Figure 2 | DFD Level 0 Context Diagram | Shows user input and final output at a high level |
| Figure 3 | DFD Level 1 System Flow | Shows main processes: video analysis, prediction, reports |
| Figure 4 | Part A Computer Vision Pipeline Flowchart | Shows video to detection to tracking to pitch map |
| Figure 5 | Part A Ball Possession Logic Diagram | Shows ball-to-player and team possession calculation |
| Figure 6 | Part A Pitch Mapping Diagram | Shows camera coordinates to pitch coordinates |
| Figure 7 | Part B Data Loading and Merging Flow | Shows how 12 CSV files become enriched data |
| Figure 8 | Part B Feature Engineering Flowchart | Shows raw columns to football features |
| Figure 9 | Model Training Flowchart | Shows train-test split and model saving |
| Figure 10 | Transfer Prediction Flowchart | Shows player input to predicted fee |
| Figure 11 | Flask Integration Sequence Diagram | Shows browser, Flask, modules, outputs |
| Figure 12 | Model Comparison Bar Chart | Shows XGBoost, Random Forest, Neural Network results |

### Recommended Screenshots

| Screenshot No. | Screenshot Name | Where To Take It From |
|---|---|---|
| Screenshot 1 | Home Dashboard | `templates/index.html` running in browser |
| Screenshot 2 | Football Video Upload Page | `/football` page |
| Screenshot 3 | Football Processing Progress Bar | Upload a video and capture processing state |
| Screenshot 4 | Input Video Preview | Result section on `/football/result/<job_id>` |
| Screenshot 5 | Processed Annotated Video | Result section after Part A completes |
| Screenshot 6 | Pitch Movement Video | Part A pitch video result |
| Screenshot 7 | Pitch Radar Snapshot | Generated `pitch_map.png` |
| Screenshot 8 | Possession Statistics Panel | Team 1 and Team 2 possession output |
| Screenshot 9 | Transfer Prediction Page | `/transfer` page |
| Screenshot 10 | Player Search Result | Transfer action 1 |
| Screenshot 11 | Predicted Transfer Fee Result | Transfer action 2 |
| Screenshot 12 | Future Performance Table | Transfer action 3 |
| Screenshot 13 | Advanced Filter Result | Transfer action 4 |
| Screenshot 14 | Player Comparison Result | Transfer action 5 |
| Screenshot 15 | Market Insights Report | Transfer action 6 |
| Screenshot 16 | Transfer Simulation Result | Transfer action 7 |
| Screenshot 17 | Downloaded PDF Report | Generated transfer PDF from `static/outputs` |

---

## Section 5: Introduction

Football is one of the most data-rich sports in the world. Every match creates video data, movement data, player statistics, transfer history, market value changes, and tactical information. Clubs use this information to make decisions about tactics, scouting, player recruitment, player valuation, and match analysis.

This project was created to show two important areas of football analytics:

1. Computer vision analysis from football match video.
2. Machine learning based player transfer fee prediction.

The project is not only a model or script. It is a complete local web application. A user can open the Flask interface, choose the football video analysis module or the transfer prediction module, provide input, and receive useful results.

The main file that connects both parts is:

`app.py`

Important web pages are:

`templates/index.html`  
`templates/football.html`  
`templates/transfer.html`  
`templates/base.html`

The frontend behavior is handled in:

`static/js/app.js`

The styling is handled in:

`static/css/styles.css`

---

## Section 6: Problem Definition

### Problem in Part A

In football video analysis, it is difficult to manually track every player and the ball throughout a match. A human analyst can watch the video, but manually writing player positions, ball possession, and team movement is slow and error-prone. The problem is to automatically process football match footage and create useful visual outputs such as player tracking, possession statistics, and a pitch map.

### Problem in Part B

Football transfer fees are difficult to predict because they depend on many factors. A player's age, position, goals, assists, current value, club strength, league level, international experience, contract situation, and market demand all affect the final transfer price. There is no simple fixed formula. The problem is to use historical football data and machine learning to estimate a fair transfer fee.

### Combined Problem

The complete problem is to build one system that can support both video-based football analysis and data-based transfer valuation through a simple interface.

---

## Section 7: Objectives

### Primary Objectives

- Build a football video analysis module for player, ball, goalkeeper, and referee detection.
- Assign detected players into teams using jersey color clustering.
- Track player movement across frames.
- Calculate team ball possession.
- Map player and ball positions onto a pitch radar.
- Build a machine learning system for player transfer fee prediction.
- Load and process Transfermarkt CSV data.
- Train and compare XGBoost, Random Forest, and Neural Network models.
- Integrate both modules into one Flask web application.

### Secondary Objectives

- Provide player search with fuzzy matching.
- Provide future performance prediction.
- Provide advanced player filtering.
- Provide player comparison.
- Provide market insights.
- Provide transfer simulation.
- Generate downloadable reports and output files.
- Make the interface usable for non-technical users.

---

## Section 8: Scope

### Included in the Project

- Football video upload.
- Video frame processing with OpenCV.
- Roboflow object detection for players, ball, goalkeeper, and referee.
- Team assignment using KMeans jersey color clustering.
- Player tracking using ByteTrack.
- Ball possession calculation.
- Pitch radar visualization.
- Annotated video output.
- Pitch movement video output.
- TXT, CSV, and JSON statistics output.
- Transfermarkt dataset loading.
- Data cleaning and feature engineering.
- XGBoost, Random Forest, and Neural Network training.
- Transfer fee prediction.
- Player search, comparison, filtering, market report, future projection, and simulation.
- Flask web interface.
- PDF report generation for Part B actions.

### Not Included in the Project

- Real-time live match broadcast analysis.
- Manual labelled video benchmark for Part A accuracy.
- Live Transfermarkt scraping.
- Injury history analysis.
- Agent fee, release clause, salary database, and media hype analysis.
- Professional club scouting replacement.

---

## Section 9: Existing Systems

### Transfermarkt

Transfermarkt provides football player market values, club information, transfer history, and player profiles. It is useful, but the exact valuation process is not fully transparent.

### CIES Football Observatory

CIES publishes football valuation reports using advanced data and proprietary models. It is respected, but users cannot freely run custom interactive predictions for every transfer scenario.

### EA FC Ratings

EA FC gives player ratings for gaming. These ratings are useful for entertainment but are not designed to estimate real transfer fees.

### This Project

This project is different because it combines two areas:

- Computer vision based match video analysis.
- Machine learning based transfer fee prediction.

It is also transparent because the data processing, feature engineering, and prediction code are inside the project.

---

## Section 10: Requirements

### Functional Requirements

| ID | Requirement | Project Part |
|---|---|---|
| FR1 | Upload football video | Part A |
| FR2 | Detect players, ball, goalkeeper, referee | Part A |
| FR3 | Assign players to teams | Part A |
| FR4 | Track players across frames | Part A |
| FR5 | Calculate ball possession | Part A |
| FR6 | Generate annotated video and pitch map | Part A |
| FR7 | Search football player by name | Part B |
| FR8 | Predict transfer fee | Part B |
| FR9 | Predict future performance | Part B |
| FR10 | Filter players by conditions | Part B |
| FR11 | Compare two players | Part B |
| FR12 | Generate market insights | Part B |
| FR13 | Simulate transfer | Part B |
| FR14 | Generate downloadable outputs | Both |

### Non-Functional Requirements

| Category | Requirement |
|---|---|
| Usability | Browser interface should be simple and easy to use |
| Performance | Transfer prediction should run quickly after model loading |
| Reliability | Invalid input should show useful errors |
| Maintainability | Code should be divided into modules |
| Portability | Project should run locally on Windows with Python |
| Explainability | Prediction output should include a breakdown |

---

## Section 11: Technology Stack

### Root Web Application

| Technology | Purpose | Code Path |
|---|---|---|
| Python | Main programming language | `app.py` |
| Flask | Web application framework | `app.py` |
| HTML/Jinja | Web templates | `templates/` |
| CSS | Styling | `static/css/styles.css` |
| JavaScript | Progress bar and UI actions | `static/js/app.js` |
| FFmpeg / imageio-ffmpeg | Browser-friendly video conversion | `app.py` |

### Part A Technologies

| Technology | Purpose | Code Path |
|---|---|---|
| OpenCV | Video reading, writing, drawing, image processing | `main_test.py`, `utils/video.py` |
| Roboflow HTTP API | Object detection and field keypoint detection | `main_test.py` |
| Requests | Sending frames to Roboflow | `main_test.py` |
| Supervision | Detections, annotators, ByteTrack | `main_test.py`, `utils/annotation.py` |
| ByteTrack | Player tracking IDs | `main_test.py` |
| KMeans | Team assignment by jersey color | `team_assigner/Assigner.py` |
| NumPy | Numeric arrays and distance calculations | `main_test.py` |
| tqdm | Frame loop progress | `main_test.py` |

### Part B Technologies

| Technology | Purpose | Code Path |
|---|---|---|
| Pandas | CSV loading, merging, cleaning | `src/data_loader.py` |
| NumPy | Numeric calculations | `src/feature_engineering.py` |
| Scikit-learn | Random Forest, MLP, scaler, metrics | `src/model_trainer.py` |
| XGBoost | Main transfer fee model | `src/model_trainer.py` |
| Joblib | Save and load trained models | `src/model_trainer.py`, `src/predictor.py` |
| Rich | CLI tables and panels | `src/display.py` |

---

## Section 12: Project Directory Structure

```text
Football Analysis Model/
|-- app.py
|-- requirements.txt
|-- PROJECT_REPORT.md
|-- final_report.md
|-- templates/
|   |-- base.html
|   |-- index.html
|   |-- football.html
|   |-- transfer.html
|-- static/
|   |-- css/styles.css
|   |-- js/app.js
|   |-- uploads/
|   |-- outputs/
|-- Part a Player Tracking And Mapping/
|   |-- football-analysis-CV-main/
|       |-- local_exec/
|           |-- main_test.py
|           |-- config/config.py
|           |-- team_assigner/Assigner.py
|           |-- utils/
|           |-- sports/
|           |-- input_video/
|           |-- output_video/
|-- Part b Players Transfer Fee Prediction/
|   |-- main.py
|   |-- setup.py
|   |-- README.md
|   |-- requirements.txt
|   |-- csv_files/
|   |-- data/processed/
|   |-- models/
|   |-- src/
```

---

## Section 13: System Design

### 13.1 Combined System Architecture

The system has three main layers.

1. User Interface Layer:
   - Browser pages for dashboard, football analysis, and transfer prediction.
   - CLI interface for Part B.

2. Application Layer:
   - Flask app in `app.py`.
   - It receives video uploads and transfer form input.
   - It routes the request to the correct module.

3. Processing Layer:
   - Part A computer vision pipeline.
   - Part B data and machine learning pipeline.

4. Storage Layer:
   - Uploaded videos in `static/uploads/`.
   - Generated outputs in `static/outputs/`.
   - Transfer CSV files in `Part b Players Transfer Fee Prediction/csv_files/`.
   - Trained models in `Part b Players Transfer Fee Prediction/models/`.

[INSERT FIGURE 1: COMBINED SYSTEM ARCHITECTURE DIAGRAM]

### 13.2 High-Level Data Flow

For Part A:

```text
User video upload -> Flask -> Save video -> Part A pipeline -> Roboflow detection -> Team assignment -> Tracking -> Pitch mapping -> Output files -> Browser result
```

For Part B:

```text
User player input -> Flask or CLI -> Load processed data -> Find player -> Prepare features -> Load model -> Predict fee -> Display result/PDF
```

[INSERT FIGURE 2: DFD LEVEL 0 CONTEXT DIAGRAM]

[INSERT FIGURE 3: DFD LEVEL 1 SYSTEM FLOW]

---

## Section 14: Part A - Player Tracking and Pitch Mapping

### 14.1 Purpose of Part A

Part A analyzes football match video. Its main purpose is to automatically detect objects in the match, track movement, calculate possession, and show a tactical pitch view.

The active main file for Part A is:

`Part a Player Tracking And Mapping/football-analysis-CV-main/local_exec/main_test.py`

Important supporting files are:

| File | Purpose |
|---|---|
| `local_exec/main_test.py` | Main video processing pipeline |
| `local_exec/config/config.py` | Video paths, model IDs, thresholds, class IDs |
| `local_exec/team_assigner/Assigner.py` | Jersey color based team assignment |
| `local_exec/utils/video.py` | Frame count, FPS, and frame generator |
| `local_exec/utils/annotation.py` | Draws players, ball, referee, labels, possession overlay |
| `local_exec/utils/graphics.py` | Draws possession overlay on frame |
| `local_exec/sports/common/view.py` | Homography based coordinate transformation |
| `local_exec/sports/configs/soccer.py` | Real pitch dimensions and key vertices |
| `local_exec/sports/annotators/soccer.py` | Draws pitch and points on pitch |

### 14.2 Important Part A Code References

| Feature | Code Path | Line Reference |
|---|---|---|
| Roboflow HTTP client | `main_test.py` | `class RoboflowHttpClient`, line 54 |
| Object detection conversion | `main_test.py` | `class RoboflowHttpObjectDetector`, line 84 |
| Detection backend creation | `main_test.py` | `create_object_detector`, line 135 |
| Pitch projection | `main_test.py` | `class PitchProjector`, line 145 |
| Ball possession logic | `main_test.py` | `class BallPossessionTracker`, line 274 |
| Pitch radar frame | `main_test.py` | `build_pitch_radar_frame`, line 350 |
| Stats writing | `main_test.py` | `write_stats`, line 418 |
| Main pipeline | `main_test.py` | `main`, line 437 |
| Config values | `config/config.py` | lines 10 to 42 |
| Team assignment | `team_assigner/Assigner.py` | `class Assigner`, line 6 |
| Torso color extraction | `team_assigner/Assigner.py` | `_get_torso_pixels`, line 16 |
| Team color clustering | `team_assigner/Assigner.py` | `assign_team_color`, line 84 |
| Homography transform | `sports/common/view.py` | `class ViewTransformer` |

### 14.3 Part A Configuration

Part A configuration is stored in:

`Part a Player Tracking And Mapping/football-analysis-CV-main/local_exec/config/config.py`

Important values:

| Config Variable | Meaning |
|---|---|
| `VIDEO_SRC` | Input video path |
| `OUT_VIDEO` | Output annotated video path |
| `OUT_PITCH_MAP` | Output pitch map image path |
| `OUT_PITCH_VIDEO` | Output pitch movement video path |
| `OUT_STATS` | Output possession stats file path |
| `ROBOFLOW_API_KEY` | API key used for Roboflow detection |
| `PLAYER_DETECTION_MODEL_ID` | Roboflow model for players, ball, referee |
| `FIELD_DETECTION_MODEL_ID` | Roboflow model for field keypoints |
| `PLAYER_DETECTION_CONFIDENCE` | Minimum confidence for object detections |
| `FIELD_KEYPOINT_CONFIDENCE` | Minimum confidence for field keypoints |
| `FIELD_REFRESH_FRAMES` | How often field keypoints are refreshed |
| `BALL_POSSESSION_CARRY_FRAMES` | Frames for keeping last possession if ball is temporarily missing |
| `BALL_ASSIGNMENT_MAX_DISTANCE` | Maximum ball-to-player distance for possession |
| `MODEL_CLASSES` | Numeric class IDs for ball, player, referee, teams |

### 14.4 How Part A Works Step by Step

#### Step 1: Input Video

The user uploads a video from the Flask `/football` page. The uploaded file is saved in:

`static/uploads/`

When running Part A directly, the default input video is configured in `config.py` using `VIDEO_SRC`.

In the web app, `app.py` temporarily sets the Part A module paths before calling `football_main.main()`. This happens in:

`app.py`, `run_football_analysis`, line 467.

#### Step 2: Read Video Frames

OpenCV and Supervision are used to read the video frame by frame.

Code path:

`local_exec/utils/video.py`

Main functions:

- `get_number_of_frames(video_path)`
- `get_frames(video_path)`

These functions get the total frame count, FPS, and generate frames for processing.

#### Step 3: Send Frame to Roboflow

Each video frame is encoded as JPEG and sent to Roboflow through HTTP.

Code path:

`main_test.py`, `RoboflowHttpClient.infer`

Simple explanation:

The system converts the frame into an image, sends it to the Roboflow model, and receives detected objects with coordinates.

Detected objects include:

- Ball
- Player
- Goalkeeper
- Referee

#### Step 4: Convert Roboflow Output to Supervision Detections

Roboflow returns predictions as JSON. The project converts these predictions into `sv.Detections`, which are easier to use with Supervision annotators and ByteTrack.

Code path:

`main_test.py`, `RoboflowHttpObjectDetector._to_detections`

The bounding box format is converted from center-based Roboflow format:

```text
x, y, width, height
```

to corner format:

```text
x1, y1, x2, y2
```

#### Step 5: Separate Classes

After detection, objects are separated by class ID.

Examples:

```text
ball -> class 0
goalkeeper -> class 1
player -> class 2
referee -> class 3
team1 -> class 4
team2 -> class 5
active_player -> class 6
```

These IDs are defined in:

`config/config.py`, `MODEL_CLASSES`

#### Step 6: Remove Duplicate Player Boxes

For player detections, Non-Maximum Suppression is applied:

```python
players_detections = players_detections.with_nms(threshold=0.5)
```

This removes overlapping duplicate boxes so the same player is not detected multiple times.

#### Step 7: Team Assignment by Jersey Color

Players are assigned to Team 1 or Team 2 using jersey color.

Code path:

`team_assigner/Assigner.py`

How it works:

1. Crop the player from the frame using the bounding box.
2. Focus mainly on the torso area because shirt color is strongest there.
3. Convert pixels into HSV and LAB color spaces.
4. Remove green field pixels so the pitch color does not confuse the model.
5. Use KMeans clustering to find two main jersey color groups.
6. Assign each player to one of the two clusters.

Easy explanation for teacher:

I detect the color of each player's shirt and group the players into two teams using KMeans clustering.

#### Step 8: Track Players with ByteTrack

After team assignment, the project tracks players using ByteTrack from the Supervision library.

Code path:

`main_test.py`, inside `main`

Trackers:

```python
tracker_team1 = sv.ByteTrack()
tracker_team2 = sv.ByteTrack()
```

Why tracking is needed:

Detection only tells us where a player is in the current frame. Tracking helps keep the same player identity across multiple frames.

#### Step 9: Ball Possession Calculation

Ball possession is calculated in:

`main_test.py`, `BallPossessionTracker`

The system first selects the most likely ball detection. If multiple balls are detected, it uses confidence and distance from the last ball position.

Then it finds the closest player to the ball. The system checks points near the player's feet because in football the ball is normally near the feet, not the center of the body.

If the ball is close enough to a player, that player's team receives possession for that frame.

Formula:

```text
Team Possession % = Team Possession Frames / Total Possession Frames * 100
```

Example output from an actual generated stats file:

```text
Team 1 Possession: 60.31% (231 frames)
Team 2 Possession: 39.69% (152 frames)
Frames Written: 621
```

The example stats file is:

`static/outputs/football_20260506_005724_49db0b8a_stats.txt`

#### Step 10: Pitch Mapping

The system maps player and ball positions from camera coordinates to pitch coordinates.

Code paths:

`main_test.py`, `PitchProjector`  
`sports/common/view.py`, `ViewTransformer`  
`sports/configs/soccer.py`, `SoccerPitchConfiguration`

The project uses homography transformation. In simple words, homography is a method that converts points from one view to another. Here, it converts video frame positions into top-down pitch positions.

If field keypoints are detected by Roboflow, the system builds a better transformer using those keypoints. If field keypoints are not available, the system uses an approximate pitch projection.

[INSERT FIGURE 6: CAMERA VIEW TO PITCH VIEW MAPPING]

#### Step 11: Draw Pitch Radar

The pitch radar is drawn in:

`main_test.py`, `build_pitch_radar_frame`

It draws:

- Team 1 players
- Team 2 players
- Referee
- Ball

The system uses:

`sports/annotators/soccer.py`

for drawing the football pitch and points.

#### Step 12: Annotate Original Video

The original video frame is annotated in:

`utils/annotation.py`

It draws:

- Blue ellipse for Team 1
- Red ellipse for Team 2
- Yellow marker for referee
- White marker for goalkeeper
- Orange triangle for ball
- Red triangle for active player
- Player tracking IDs
- Ball possession overlay

The ball possession overlay is drawn in:

`utils/graphics.py`

#### Step 13: Write Output Files

At the end of processing, Part A creates:

| Output | Meaning | Location |
|---|---|---|
| Processed video | Annotated video with match frame and pitch radar | `static/outputs/` |
| Pitch movement video | Separate pitch radar video | `static/outputs/` |
| Pitch map image | Last pitch radar frame as PNG | `static/outputs/` |
| Stats TXT | Team possession percentages | `static/outputs/` |
| Stats CSV | Web-generated CSV version of stats | `static/outputs/` |
| Stats JSON | Web-generated JSON version of stats | `static/outputs/` |

The web app also converts AVI to browser-friendly MP4 using:

`app.py`, `convert_video_for_browser`

### 14.5 Part A Accuracy and Evaluation

Part A does not have a formal accuracy percentage in this project because no manually labelled ground-truth video dataset is included. For exact accuracy, we would need human-labelled frames showing correct player boxes, ball boxes, team labels, and possession labels.

So the correct statement is:

Part A is evaluated visually and qualitatively. The system checks whether detections, team colors, tracking IDs, pitch map, and possession statistics look correct on sample videos.

The Roboflow model uses a detection confidence threshold, default:

```text
PLAYER_DETECTION_CONFIDENCE = 0.3
```

This means detections below 0.3 confidence are ignored.

### 14.6 Part A Limitations

- Exact accuracy is not calculated because ground-truth labels are not available.
- Ball detection can be difficult because the ball is small and sometimes hidden.
- Team assignment depends on visible jersey color.
- Similar jersey colors can confuse KMeans.
- Camera angle affects pitch mapping quality.
- Roboflow API requires internet access and an API key.
- Possession is estimated by proximity, not by official match event data.

---

## Section 15: Part B - Player Transfer Fee Prediction

### 15.1 Purpose of Part B

Part B predicts the transfer fee of a football player. It uses historical data from the Transfermarkt Kaggle dataset and trains machine learning models to estimate player value.

Main folder:

`Part b Players Transfer Fee Prediction/`

Main CLI file:

`Part b Players Transfer Fee Prediction/main.py`

Main source folder:

`Part b Players Transfer Fee Prediction/src/`

### 15.2 Dataset

The dataset is the Transfermarkt Kaggle Player Scores dataset.

Dataset files are stored in:

`Part b Players Transfer Fee Prediction/csv_files/`

Required CSV files:

| File | Use |
|---|---|
| `players.csv` | Player name, age, position, club, nationality, value |
| `clubs.csv` | Club information |
| `competitions.csv` | League and competition information |
| `appearances.csv` | Player match appearances, goals, assists, minutes |
| `transfers.csv` | Transfer fee and transfer history |
| `player_valuations.csv` | Historical player market values |
| `games.csv` | Game information |
| `club_games.csv` | Club performance information |
| `game_events.csv` | Goals, cards, substitutions, assists |
| `game_lineups.csv` | Starts, substitutes, captain appearances |
| `countries.csv` | Country context |
| `national_teams.csv` | National team strength information |

Dataset size from project files:

| Data | Count |
|---|---:|
| Players CSV rows including header | 47,703 |
| Actual players | 47,702 |
| Transfers CSV rows including header | 157,187 |
| Actual transfers | 157,186 |
| Processed player rows including header | 47,703 |
| Processed transfer rows including header | 157,187 |

### 15.3 Important Part B Code References

| Feature | Code Path | Line Reference |
|---|---|---|
| Load and merge dataset | `src/data_loader.py` | `build_enriched_data`, line 224 |
| Missing value handling | `src/data_loader.py` | `impute_missing`, line 417 |
| Load players | `src/data_loader.py` | `load_data`, line 433 |
| Load transfers | `src/data_loader.py` | `load_transfers`, line 439 |
| Add football features | `src/feature_engineering.py` | `add_features`, line 107 |
| Prepare model matrix | `src/feature_engineering.py` | `model_matrix`, line 175 |
| Train models | `src/model_trainer.py` | `train_all`, line 36 |
| XGBoost setup | `src/model_trainer.py` | line 66 |
| Random Forest setup | `src/model_trainer.py` | line 83 |
| Neural Network setup | `src/model_trainer.py` | line 86 |
| Save models | `src/model_trainer.py` | lines 95 to 99 |
| Fuzzy player matching | `src/predictor.py` | `fuzzy_match`, line 24 |
| Find player | `src/predictor.py` | `find_player`, line 29 |
| Rule formula fallback | `src/predictor.py` | `_formula_prediction`, line 55 |
| Load trained model | `src/predictor.py` | `_load_model`, line 104 |
| Predict transfer fee | `src/predictor.py` | `predict_transfer_fee`, line 125 |

### 15.4 Data Loading and Merging

Data loading is handled in:

`src/data_loader.py`

The loader first checks whether all required CSV files exist. It supports two data locations:

- `csv_files/`
- `data/raw/`

Then it reads CSV files using Pandas and merges them using IDs such as:

- `player_id`
- `club_id`
- `game_id`
- `competition_id`

The processed files are saved in:

`Part b Players Transfer Fee Prediction/data/processed/players_enriched.csv`  
`Part b Players Transfer Fee Prediction/data/processed/transfers_enriched.csv`

[INSERT FIGURE 7: DATA LOADING AND MERGING FLOW]

### 15.5 Data Cleaning

The project handles missing values in:

`src/data_loader.py`, `impute_missing`

The cleaning method is:

- Numeric missing values are filled using median values.
- If `position_category` is available, medians are calculated by position group.
- Remaining numeric missing values are filled with global median or zero.
- Categorical missing values are filled with `"Unknown"`.

This is important because machine learning models cannot train properly with many empty values.

### 15.6 Feature Engineering

Feature engineering is handled in:

`src/feature_engineering.py`

Important features include:

| Feature | Meaning |
|---|---|
| `age` | Player age |
| `height_cm` | Player height |
| `goals_total` | Total goals |
| `assists_total` | Total assists |
| `goals_per_90` | Goals per 90 minutes |
| `assists_per_90` | Assists per 90 minutes |
| `goal_contribution` | Goals per 90 + assists per 90 |
| `current_value_eur` | Current market value |
| `peak_value_eur` | Highest market value |
| `league_tier` | Strength level of league |
| `club_strength_score` | Club strength estimate |
| `international_caps` | National team appearances |
| `position_multiplier` | Value multiplier by position |
| `age_factor` | Value factor based on age |
| `contract_years_left` | Years left in contract |
| `value_trend` | Value growth or decline |
| `performance_factor` | Performance-based multiplier |

Important formulas:

```text
goals_per_90 = goals_total / (minutes_played / 90)
```

```text
assists_per_90 = assists_total / (minutes_played / 90)
```

```text
goal_contribution = goals_per_90 + assists_per_90
```

The model target is transformed using:

```text
y = log1p(transfer_fee)
```

After prediction, it is converted back using:

```text
transfer_fee = expm1(predicted_log_value)
```

This log transformation helps because football transfer fees are highly uneven. Many players have small transfer fees, while a few players have very large fees.

[INSERT FIGURE 8: FEATURE ENGINEERING FLOWCHART]

### 15.7 Model Training

Model training is handled in:

`src/model_trainer.py`

The project trains three models:

1. XGBoost Regressor
2. Random Forest Regressor
3. MLPRegressor Neural Network

The training process:

1. Load enriched transfer data.
2. Keep only paid transfers where `transfer_fee > 0`.
3. Add engineered features.
4. Prepare numeric feature matrix.
5. Split data into training and testing sets using 80/20 split.
6. Scale data for the neural network using `StandardScaler`.
7. Train XGBoost.
8. Train Random Forest.
9. Train Neural Network.
10. Evaluate models using MAE, RMSE, R2, and MAPE.
11. Save models using Joblib.

Saved model files:

| Model File | Purpose |
|---|---|
| `models/xgboost_transfer_model.pkl` | Main model |
| `models/rf_transfer_model.pkl` | Random Forest model |
| `models/nn_transfer_model.pkl` | Neural Network model |
| `models/scaler.pkl` | Scaler for neural network |
| `models/feature_columns.pkl` | Feature column list |

[INSERT FIGURE 9: MODEL TRAINING FLOWCHART]

### 15.8 Prediction Logic

Prediction is handled in:

`src/predictor.py`

Working:

1. User enters player name, from club, to club, and model name.
2. The system loads player data.
3. It searches the player using exact matching, contains matching, or fuzzy matching.
4. It calculates a formula-based value using football rules.
5. It loads the trained model if available.
6. It prepares the player's numeric features.
7. The model predicts transfer fee.
8. The system blends ML prediction with formula-based football pricing.
9. A readable breakdown is returned.

Formula fallback factors include:

- Current value
- Peak value
- Age factor
- Position multiplier
- League tier factor
- International factor
- Buying club premium
- Performance factor
- Contract urgency

[INSERT FIGURE 10: TRANSFER PREDICTION FLOWCHART]

### 15.9 Part B Features

The Part B module offers seven main features.

| No. | Feature | Code Path |
|---|---|---|
| 1 | Search Player by Name | `src/player_search.py` |
| 2 | Predict Transfer Value | `src/predictor.py` |
| 3 | Future Performance Prediction | `src/performance_predictor.py` |
| 4 | Advanced Filter and Search | `src/player_search.py` |
| 5 | Compare Two Players | `src/player_compare.py` |
| 6 | Market Insights and Reports | `src/market_insights.py` |
| 7 | Simulate Player Transfer | `src/transfer_simulator.py` |

### 15.10 Part B Accuracy and Evaluation

Part B is a regression problem, so normal classification accuracy is not the best metric. Instead, the project uses MAE, RMSE, R2, and MAPE.

Reported results:

| Model | MAE | RMSE | R2 Score | MAPE |
|---|---:|---:|---:|---:|
| XGBoost | EUR 2.71M | EUR 6.53M | 0.618 | 18.5% |
| Random Forest | EUR 2.90M | EUR 7.26M | 0.598 | Not listed |
| Neural Network | EUR 3.71M | EUR 20.41M | 0.543 | Not listed |

Simple explanation:

The best model is XGBoost. On average, its prediction is wrong by about EUR 2.71 million. Its R2 score is 0.618, which means it explains about 62% of the variation in transfer fees. Its MAPE is 18.5%, so roughly speaking the average percentage accuracy is about 81.5%, but the proper ML metrics are MAE, RMSE, R2, and MAPE.

---

## Section 16: Flask Web Integration

The root Flask app integrates both project parts.

Main file:

`app.py`

### 16.1 Important Flask Code References

| Feature | Code Path | Line Reference |
|---|---|---|
| Find Part B folder | `app.py` | `find_transfer_dir`, line 54 |
| Find Part A folder | `app.py` | `find_football_dir`, line 64 |
| Football progress wrapper | `app.py` | `FootballProgress`, line 171 |
| Run Part A analysis | `app.py` | `run_football_analysis`, line 467 |
| Run Part B prediction | `app.py` | `predict_transfer`, line 540 |
| Run Part B actions | `app.py` | `run_transfer_action`, line 574 |
| Background Part A worker | `app.py` | `start_football_worker`, line 691 |
| Dashboard route | `app.py` | `/`, line 723 |
| Football route | `app.py` | `/football`, line 728 |
| Football start route | `app.py` | `/football/start`, line 753 |
| Football status route | `app.py` | `/football/status/<job_id>`, line 779 |
| Football result route | `app.py` | `/football/result/<job_id>`, line 800 |
| Transfer route | `app.py` | `/transfer`, line 815 |
| Download route | `app.py` | `/download/<path:filename>`, line 862 |

### 16.2 How Flask Runs Part A

1. User opens `/football`.
2. User uploads a video.
3. JavaScript sends the video to `/football/start`.
4. Flask saves the video in `static/uploads/`.
5. Flask creates a job ID.
6. A background thread starts `run_football_analysis`.
7. `app.py` imports Part A `main_test.py`.
8. `app.py` sets input and output paths inside the Part A module.
9. Part A processes the video.
10. Flask polls `/football/status/<job_id>` for progress.
11. When processing completes, the browser opens `/football/result/<job_id>`.
12. The result page displays videos, pitch map, stats, and download buttons.

Progress bar logic is in:

`static/js/app.js`

### 16.3 How Flask Runs Part B

1. User opens `/transfer`.
2. User selects one of seven actions.
3. User submits form.
4. Flask calls `run_transfer_action`.
5. The correct Part B module runs.
6. The result is displayed on the web page.
7. Flask creates a downloadable PDF report.

[INSERT FIGURE 11: FLASK INTEGRATION SEQUENCE DIAGRAM]

---

## Section 17: Complete Working of the Project

### 17.1 Setup

Install root requirements:

```bash
pip install -r requirements.txt
```

Install Part B requirements:

```bash
cd "Part b Players Transfer Fee Prediction"
pip install -r requirements.txt
```

Optional full setup for Part B:

```bash
python setup.py
```

Run web app from project root:

```bash
python app.py
```

Then open:

```text
http://127.0.0.1:5000
```

### 17.2 Working of Dashboard

The dashboard gives two choices:

- Football Analysis
- Transfer Fee Prediction

Screenshot to add:

[INSERT SCREENSHOT 1: HOME DASHBOARD]

### 17.3 Working of Part A From Web

1. Open the Football Analysis page.
2. Select a football video.
3. Click Start Analysis.
4. The video uploads to `static/uploads/`.
5. Flask starts a background job.
6. Part A reads the video frame by frame.
7. Roboflow detects players, ball, goalkeeper, and referee.
8. KMeans assigns players to teams using shirt color.
9. ByteTrack tracks players.
10. Ball possession is calculated frame by frame.
11. Player and ball positions are mapped to pitch radar.
12. Annotated video and pitch video are written.
13. Stats are saved as TXT, CSV, and JSON.
14. The result page displays all outputs.

Screenshots to add:

[INSERT SCREENSHOT 2: FOOTBALL VIDEO UPLOAD PAGE]  
[INSERT SCREENSHOT 3: FOOTBALL PROCESSING PROGRESS BAR]  
[INSERT SCREENSHOT 4: INPUT VIDEO PREVIEW]  
[INSERT SCREENSHOT 5: PROCESSED ANNOTATED VIDEO]  
[INSERT SCREENSHOT 6: PITCH MOVEMENT VIDEO]  
[INSERT SCREENSHOT 7: PITCH RADAR SNAPSHOT]  
[INSERT SCREENSHOT 8: POSSESSION STATISTICS PANEL]

### 17.4 Working of Part B From Web

1. Open the Transfer Prediction page.
2. Select one of the seven actions.
3. Enter required input.
4. Submit the form.
5. Flask calls the matching module in `src/`.
6. The result is shown in the browser.
7. A PDF report is generated in `static/outputs/`.

Screenshots to add:

[INSERT SCREENSHOT 9: TRANSFER PREDICTION PAGE]  
[INSERT SCREENSHOT 10: PLAYER SEARCH RESULT]  
[INSERT SCREENSHOT 11: PREDICTED TRANSFER FEE RESULT]  
[INSERT SCREENSHOT 12: FUTURE PERFORMANCE TABLE]  
[INSERT SCREENSHOT 13: ADVANCED FILTER RESULT]  
[INSERT SCREENSHOT 14: PLAYER COMPARISON RESULT]  
[INSERT SCREENSHOT 15: MARKET INSIGHTS REPORT]  
[INSERT SCREENSHOT 16: TRANSFER SIMULATION RESULT]  
[INSERT SCREENSHOT 17: DOWNLOADED PDF REPORT]

### 17.5 Working of Part B From CLI

Part B can also run as a terminal application.

Command:

```bash
cd "Part b Players Transfer Fee Prediction"
python main.py
```

The CLI menu gives:

```text
1. Search Player by Name
2. Predict Transfer Value
3. Future Performance Prediction
4. Advanced Filter & Search
5. Compare Two Players
6. Market Insights & Reports
7. Simulate Player Transfer
8. Exit
```

---

## Section 18: Results and Analysis

### 18.1 Part A Results

Part A generated the following output types:

- Processed annotated video.
- Pitch movement video.
- Pitch radar image.
- Ball possession TXT file.
- Ball possession CSV file.
- Ball possession JSON file.

Example generated files are visible in:

`static/outputs/`

Example possession result:

```text
Team 1 Possession: 60.31% (231 frames)
Team 2 Possession: 39.69% (152 frames)
Frames Written: 621
```

Analysis:

- The system successfully performs object detection, tracking, team assignment, pitch radar generation, and possession calculation.
- The results are useful for visual football analysis.
- Part A output quality depends on detection quality, video angle, camera motion, and visibility of players and ball.

### 18.2 Part B Results

Model comparison:

| Model | MAE | RMSE | R2 |
|---|---:|---:|---:|
| XGBoost | EUR 2.71M | EUR 6.53M | 0.618 |
| Random Forest | EUR 2.90M | EUR 7.26M | 0.598 |
| Neural Network | EUR 3.71M | EUR 20.41M | 0.543 |

[INSERT FIGURE 12: MODEL COMPARISON BAR CHART]

XGBoost performs best because it works well on tabular data with mixed numeric football features.

### 18.3 Important Evaluation Metrics

MAE means average absolute error.

```text
MAE = average of absolute(actual fee - predicted fee)
```

RMSE gives higher penalty to large mistakes.

```text
RMSE = square root of average squared error
```

R2 shows how much variation the model explains.

```text
R2 closer to 1 is better
```

MAPE shows average percentage error.

```text
MAPE = average percentage error
```

In easy words:

- Lower MAE is better.
- Lower RMSE is better.
- Higher R2 is better.
- Lower MAPE is better.

---

## Section 19: Advantages

### Part A Advantages

- Automatically analyzes football video.
- Detects players, ball, goalkeeper, and referee.
- Shows player tracking IDs.
- Calculates possession automatically.
- Creates a pitch radar view.
- Generates downloadable output files.
- Integrated into a web interface.

### Part B Advantages

- Uses real football dataset.
- Trains multiple machine learning models.
- Gives explainable prediction breakdown.
- Provides player search, comparison, filter, future prediction, market insights, and simulation.
- Saves trained models for reuse.
- Has both CLI and web interface.

### Combined System Advantages

- One project contains both video analysis and transfer intelligence.
- User can interact through browser.
- Outputs are downloadable.
- Code is modular and easier to explain.

---

## Section 20: Limitations

### Part A Limitations

- No formal detection accuracy is calculated.
- Depends on Roboflow API and internet access.
- Ball detection can fail when the ball is hidden or too small.
- Similar jersey colors may confuse team assignment.
- Pitch mapping may be approximate if field keypoints are not detected.
- Possession is based on nearest player distance, not official event data.

### Part B Limitations

- Dataset is not live.
- Model may underpredict superstar players.
- Transfer fees also depend on non-data factors like media hype, release clauses, injuries, club rivalry, agent influence, and negotiation pressure.
- Neural Network performs weaker than XGBoost for this tabular dataset.
- Salary and detailed contract data are limited.

---

## Section 21: Challenges Faced

### Challenge 1: Combining Two Different Projects

Part A and Part B were separate. One was a computer vision project and the other was a machine learning transfer prediction project.

Solution:

`app.py` was created to find both modules and integrate them into one Flask web application.

### Challenge 2: Video Processing Takes Time

Football video processing is slow because each frame needs detection, tracking, mapping, and writing.

Solution:

The web app runs Part A in a background thread and shows progress using `/football/status/<job_id>`.

### Challenge 3: Browser Video Compatibility

OpenCV writes AVI files, but browsers usually play MP4 better.

Solution:

`app.py` converts output video to H.264 MP4 using FFmpeg when available.

### Challenge 4: Team Assignment

Player detection gives generic players, not team names.

Solution:

Jersey color clustering with KMeans was used to divide players into two teams.

### Challenge 5: Merging 12 CSV Files

Part B data was spread across many CSV files.

Solution:

Pandas merge operations were used with IDs like `player_id`, `club_id`, and `game_id`.

### Challenge 6: Missing Values

Many player rows have missing values.

Solution:

Numeric missing values were filled using medians, and categorical missing values were filled with `"Unknown"`.

### Challenge 7: Elite Player Prediction

Superstar players are hard to predict because their prices include reputation and marketing value.

Solution:

The model uses current value, peak value, age, position, performance, and buying club premium, but the limitation is still clearly mentioned.

---

## Section 22: Future Scope

### Future Work for Part A

- Add formal labelled dataset evaluation.
- Add object detection precision, recall, and mAP.
- Add heatmaps for player movement.
- Add ball trajectory visualization.
- Add pass detection.
- Add formation detection.
- Add player speed and distance covered.
- Add real-time webcam or live match processing.

### Future Work for Part B

- Add live Transfermarkt data updates.
- Add injury history.
- Add salary and wage dataset.
- Add contract release clauses.
- Add SHAP explainability.
- Add confidence intervals for predicted fees.
- Add player similarity search.
- Add team fit and formation fit analysis.

### Future Work for Web App

- Add login system.
- Add saved reports.
- Add dashboard charts.
- Add progress time estimation.
- Add admin page for API keys and model settings.

---

## Section 23: Viva Preparation

### Short Project Intro

My project is a Football Player Intelligence System. It has two parts. Part A is a computer vision module that analyzes football video, detects players, ball, and referees, maps movement onto a pitch view, and calculates ball possession. Part B is a machine learning module that predicts player transfer fees using Transfermarkt data. I integrated both parts into a Flask web app.

### Explain Part A in One Minute

My Part A is a football video analysis pipeline. I take an input match video, process it frame by frame using OpenCV, detect players and ball using Roboflow, assign players to teams using jersey color clustering with KMeans, track players using ByteTrack, calculate ball possession by checking the nearest player to the ball, and map positions onto a pitch using coordinate transformation. Finally, I generate an annotated video, pitch map, pitch movement video, and possession statistics. Then I integrated it into Flask so the user can upload a video and see results on the web.

### Explain Part B in One Minute

Part B is a machine learning system for predicting football transfer fees. I loaded Transfermarkt CSV data, cleaned it, merged player and transfer records, created football-related features, trained three models, and selected XGBoost because it performed best. The model predicts a player's transfer value based on age, performance, position, current value, league level, club strength, contract information, and other factors.

### Why Did You Use Roboflow?

I used Roboflow because it already provides trained football object detection models. This avoids training YOLO from scratch and lets the project focus on integration, tracking, mapping, and analysis.

### How Does Team Detection Work?

I crop the player region from the frame, focus mainly on the torso area, remove green pitch pixels, convert colors to HSV and LAB color space, and then use KMeans clustering to separate jersey colors into two teams.

### How Is Ball Possession Calculated?

Possession is calculated by finding the nearest player to the detected ball. I check distance from the ball to the player's lower body or foot area. If the distance is below a threshold, that player's team gets possession for that frame. At the end, possession percentage is calculated from frame counts.

### What Is Pitch Mapping?

Pitch mapping converts video coordinates into football pitch coordinates. The project uses a `ViewTransformer` and homography. It uses field keypoints when available, otherwise it uses an approximate pitch projection.

### What Is the Accuracy of Part A?

Part A does not have a fixed accuracy percentage because I did not use a manually labelled test video. It is visually tested. It detects players, ball, referees, tracks movement, assigns teams, and shows possession on sample videos.

### What Is the Accuracy of Part B?

Part B is a regression model, so we do not use normal accuracy. The best model is XGBoost. Its MAE is EUR 2.71 million, RMSE is EUR 6.53 million, R2 is 0.618, and MAPE is 18.5%. In simple language, the average error is about EUR 2.71 million and the average percentage accuracy is roughly 81.5%.

### Why Is XGBoost Better?

XGBoost works very well with tabular data. Football transfer data is tabular, with features like age, goals, assists, value, club strength, league tier, and contract years. XGBoost can learn non-linear relationships and handle mixed feature effects better than a simple model.

### Why Did You Use Log Transformation?

Transfer fees are not evenly distributed. Many players have low transfer fees and a few players have very high fees. Log transformation reduces the effect of extreme values and helps the model learn more stable patterns.

---

## Section 24: Conclusion

The Football Player Intelligence System is a complete football analytics project with two strong parts. Part A analyzes football match video using computer vision. It detects players, ball, goalkeeper, and referee, assigns players to teams, tracks movement, calculates possession, and creates pitch radar outputs. Part B predicts football transfer fees using machine learning on Transfermarkt data. It loads and cleans 12 CSV files, creates football-specific features, trains XGBoost, Random Forest, and Neural Network models, and provides prediction plus extra tools like search, comparison, filtering, future projection, market reports, and transfer simulation.

The project is integrated through a Flask web app, so both modules can be used from one browser interface. The system demonstrates practical use of Python, OpenCV, Roboflow, KMeans, ByteTrack, Pandas, Scikit-learn, XGBoost, Joblib, and Flask.

Part A is best evaluated visually because no labelled ground-truth video dataset is included. Part B has reported model results, with XGBoost performing best at MAE EUR 2.71 million and R2 score 0.618. Overall, the project shows how football video analysis and transfer market prediction can be combined into one useful sports analytics system.

---

## Section 25: References

1. Transfermarkt Kaggle Dataset: https://www.kaggle.com/datasets/davidcariboo/player-scores
2. Pandas Documentation: https://pandas.pydata.org/docs/
3. Scikit-learn Documentation: https://scikit-learn.org/stable/documentation.html
4. XGBoost Documentation: https://xgboost.readthedocs.io/
5. Flask Documentation: https://flask.palletsprojects.com/
6. OpenCV Documentation: https://docs.opencv.org/
7. Roboflow Documentation: https://docs.roboflow.com/
8. Supervision Documentation: https://supervision.roboflow.com/
9. Joblib Documentation: https://joblib.readthedocs.io/
10. Rich Documentation: https://rich.readthedocs.io/

---

## Section 26: Appendix

### Appendix A: Root Requirements

Code path:

`requirements.txt`

```text
Flask==3.0.3
imageio-ffmpeg>=0.5.1
requests>=2.31.0
```

### Appendix B: Part B Requirements

Code path:

`Part b Players Transfer Fee Prediction/requirements.txt`

```text
pandas==2.1.0
numpy==1.24.0
scikit-learn==1.3.0
xgboost==2.0.0
rich==13.7.0
joblib==1.3.0
matplotlib==3.7.0
seaborn==0.12.0
colorama==0.4.6
tabulate==0.9.0
```

### Appendix C: Part A Imported Libraries

Part A imports these main libraries in code:

```text
cv2
numpy
requests
supervision
tqdm
sklearn.cluster.KMeans
```

### Appendix D: Main Code Paths Summary

| Area | Path |
|---|---|
| Root Flask app | `app.py` |
| Home page | `templates/index.html` |
| Football page | `templates/football.html` |
| Transfer page | `templates/transfer.html` |
| Frontend JS | `static/js/app.js` |
| Part A main pipeline | `Part a Player Tracking And Mapping/football-analysis-CV-main/local_exec/main_test.py` |
| Part A config | `Part a Player Tracking And Mapping/football-analysis-CV-main/local_exec/config/config.py` |
| Part A team assigner | `Part a Player Tracking And Mapping/football-analysis-CV-main/local_exec/team_assigner/Assigner.py` |
| Part A video helpers | `Part a Player Tracking And Mapping/football-analysis-CV-main/local_exec/utils/video.py` |
| Part A annotation helpers | `Part a Player Tracking And Mapping/football-analysis-CV-main/local_exec/utils/annotation.py` |
| Part A pitch transform | `Part a Player Tracking And Mapping/football-analysis-CV-main/local_exec/sports/common/view.py` |
| Part B CLI | `Part b Players Transfer Fee Prediction/main.py` |
| Part B setup | `Part b Players Transfer Fee Prediction/setup.py` |
| Part B data loader | `Part b Players Transfer Fee Prediction/src/data_loader.py` |
| Part B features | `Part b Players Transfer Fee Prediction/src/feature_engineering.py` |
| Part B trainer | `Part b Players Transfer Fee Prediction/src/model_trainer.py` |
| Part B predictor | `Part b Players Transfer Fee Prediction/src/predictor.py` |
| Part B search | `Part b Players Transfer Fee Prediction/src/player_search.py` |
| Part B compare | `Part b Players Transfer Fee Prediction/src/player_compare.py` |
| Part B future | `Part b Players Transfer Fee Prediction/src/performance_predictor.py` |
| Part B market | `Part b Players Transfer Fee Prediction/src/market_insights.py` |
| Part B simulation | `Part b Players Transfer Fee Prediction/src/transfer_simulator.py` |

### Appendix E: Important Output Locations

| Output Type | Location |
|---|---|
| Uploaded videos | `static/uploads/` |
| Generated football videos | `static/outputs/` |
| Generated football stats | `static/outputs/` |
| Generated pitch maps | `static/outputs/` |
| Generated transfer PDFs | `static/outputs/` |
| Processed Part B player data | `Part b Players Transfer Fee Prediction/data/processed/players_enriched.csv` |
| Processed Part B transfer data | `Part b Players Transfer Fee Prediction/data/processed/transfers_enriched.csv` |
| Saved ML models | `Part b Players Transfer Fee Prediction/models/` |