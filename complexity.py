# Complexity map for the Football Player Intelligence System.
#
# This file is only a reference for viva/report preparation.
# It is not used by the project at runtime.
# It lists complex features, exact code locations, and what each part does.


# ============================================================
# PART A: PLAYER TRACKING AND PITCH MAPPING
# ============================================================


# 1. Video upload, allowed UHD/large match videos, and storage folders
# -------------------------------------------------------------------
# File:
#   app.py
#
# Lines:
#   32-35  -> static/upload/output folder paths
#   41-47  -> allowed formats and MAX_UPLOAD_MB = 800
#   728-750 -> normal football upload route
#   753-776 -> async football upload/start route
#
# What this does:
#   - Allows football videos in mp4, mov, avi, mkv, and webm formats.
#   - Supports large uploads up to 800 MB.
#   - Saves uploaded videos inside static/uploads/.
#   - Starts video analysis as a background job from /football/start.
#
# Why it is complex:
#   Video files are heavy. The app must validate file type, save it safely,
#   create a job id, and continue processing without freezing the browser.


# 2. OpenCV frame reading and FPS/frame count
# ------------------------------------------
# File:
#   Part a Player Tracking And Mapping/
#   football-analysis-CV-main/local_exec/utils/video.py
#
# Lines:
#   8-24  -> get_number_of_frames(video_path)
#   30-42 -> get_frames(video_path, stride=1, start=0, end=None)
#
# What this does:
#   - Uses cv2.VideoCapture to open the match video.
#   - Reads total frame count using cv2.CAP_PROP_FRAME_COUNT.
#   - Reads FPS using cv2.CAP_PROP_FPS.
#   - Uses supervision.get_video_frames_generator to stream frames one by one.
#
# Why it is complex:
#   The video is not loaded all at once. It is processed frame by frame,
#   which is necessary for large or UHD videos.


# 3. Main video processing loop
# ----------------------------
# File:
#   Part a Player Tracking And Mapping/
#   football-analysis-CV-main/local_exec/main_test.py
#
# Lines:
#   437-578 -> main()
#   449-456 -> get total frames, FPS, first frame size
#   476-561 -> loop through each frame and process it
#
# What this does:
#   - Creates object detector.
#   - Opens input video.
#   - Creates output video writers.
#   - Loops frame by frame.
#   - Runs detection, team assignment, tracking, possession, pitch map,
#     annotation, and writes output frames.
#
# Why it is complex:
#   This is the core computer vision pipeline. Every frame passes through
#   multiple steps before final output is generated.


# 4. Roboflow HTTP API object detection
# ------------------------------------
# File:
#   Part a Player Tracking And Mapping/
#   football-analysis-CV-main/local_exec/main_test.py
#
# Lines:
#   54-81  -> RoboflowHttpClient
#   63-81  -> infer(frame, model_id)
#   84-132 -> RoboflowHttpObjectDetector
#   89-129 -> converts Roboflow JSON predictions into sv.Detections
#   131-132 -> sends frame to PLAYER_DETECTION_MODEL_ID
#   135-142 -> create_object_detector()
#
# Also see config:
#   Part a Player Tracking And Mapping/
#   football-analysis-CV-main/local_exec/config/config.py
#
# Lines:
#   19-22 -> ROBOFLOW_API_KEY, API URL, model IDs
#   24-29 -> confidence and timeout settings
#   36-43 -> class IDs for ball, goalkeeper, player, referee, teams
#
# What this does:
#   - Encodes each video frame as JPEG.
#   - Converts the frame to base64.
#   - Sends it to Roboflow serverless API.
#   - Receives detections for player, ball, goalkeeper, and referee.
#   - Converts prediction boxes from x/y/width/height to x1/y1/x2/y2.
#
# Why it is complex:
#   This connects local video processing with an external computer vision
#   detection model. It also converts external API output into a local format
#   that tracking and annotation code can use.


# 5. Detection class mapping
# -------------------------
# File:
#   Part a Player Tracking And Mapping/
#   football-analysis-CV-main/local_exec/main_test.py
#
# Lines:
#   31-43 -> CLASS_NAME_TO_PROJECT_ID
#
# What this does:
#   - Maps Roboflow class names like ball, player, referee, goalkeeper
#     to the project's internal class IDs.
#
# Why it is complex:
#   Detection models can return slightly different labels, such as
#   "goal keeper", "keeper", "sports ball", or "soccer ball".
#   This mapping keeps the project stable.


# 6. Non-Maximum Suppression for duplicate player boxes
# ----------------------------------------------------
# File:
#   Part a Player Tracking And Mapping/
#   football-analysis-CV-main/local_exec/main_test.py
#
# Lines:
#   484-485
#
# What this does:
#   - Applies NMS with threshold 0.5 to player detections.
#   - Removes overlapping duplicate boxes for the same player.
#
# Why it is complex:
#   Object detectors can detect one player multiple times. NMS keeps the
#   cleanest boxes before tracking and team assignment.


# 7. KMeans jersey color team assignment
# -------------------------------------
# File:
#   Part a Player Tracking And Mapping/
#   football-analysis-CV-main/local_exec/team_assigner/Assigner.py
#
# Lines:
#   1      -> imports KMeans
#   16-58  -> _get_torso_pixels()
#   60-74  -> get_player_color()
#   76-82  -> get_player_team()
#   84-107 -> assign_team_color()
#
# Main pipeline usage:
#   Part a Player Tracking And Mapping/
#   football-analysis-CV-main/local_exec/main_test.py
#
# Lines:
#   467-472 -> creates Assigner and KMeans holder
#   487-490 -> fits KMeans team colors on detected players
#   492-504 -> assigns each player to team1 or team2
#
# What this does:
#   - Crops the detected player from the frame.
#   - Focuses on torso region because jersey color is clearer there.
#   - Converts torso to HSV to remove green pitch pixels.
#   - Converts torso to LAB color space for clustering.
#   - Uses KMeans to get dominant player color.
#   - Uses KMeans with 2 clusters to separate Team 1 and Team 2.
#
# Why it is complex:
#   The detector only says "player"; it does not know the team.
#   Team identity is inferred using image color analysis and clustering.


# 8. ByteTrack player tracking by Supervision
# ------------------------------------------
# File:
#   Part a Player Tracking And Mapping/
#   football-analysis-CV-main/local_exec/main_test.py
#
# Lines:
#   462-465 -> creates and resets sv.ByteTrack trackers
#   523-524 -> updates trackers with team detections
#   248-252 -> labels_for() reads tracker IDs for display
#
# What this does:
#   - Gives each detected player a tracking ID.
#   - Keeps player identity stable across frames.
#   - Uses separate trackers for Team 1 and Team 2.
#
# Why it is complex:
#   Detection alone only knows objects in one frame. Tracking connects
#   detections across time so the same player can be followed.


# 9. Ball possession calculation
# ------------------------------
# File:
#   Part a Player Tracking And Mapping/
#   football-analysis-CV-main/local_exec/main_test.py
#
# Lines:
#   274-347 -> BallPossessionTracker
#   280-296 -> selects best ball detection
#   298-329 -> assigns ball to nearest player foot/low-body points
#   331-347 -> returns player index and possession team
#   512-521 -> pipeline updates possession counter
#   418-434 -> write_stats() calculates final percentages
#
# What this does:
#   - Selects the most likely ball if multiple ball detections exist.
#   - Measures distance from ball center to candidate points near player feet.
#   - Assigns possession to the nearest valid player.
#   - Carries last possession briefly when the ball is hidden.
#   - Writes final Team 1 and Team 2 possession percentages.
#
# Formula:
#   Team possession percent =
#   team possession frames / total possession frames * 100
#
# Why it is complex:
#   Ball possession is not directly detected by the model. It is inferred
#   from ball position, player positions, distance thresholds, and temporal
#   memory.


# 10. Pitch projection and field keypoints
# ---------------------------------------
# File:
#   Part a Player Tracking And Mapping/
#   football-analysis-CV-main/local_exec/main_test.py
#
# Lines:
#   145-241 -> PitchProjector
#   160-181 -> fallback approximate pitch projection
#   183-212 -> builds transformer from Roboflow field keypoints
#   214-234 -> refreshes/reuses field transformer
#   236-241 -> transforms detections to pitch coordinates
#
# What this does:
#   - Converts camera-view points into pitch-view points.
#   - Uses field keypoints from Roboflow when available.
#   - Falls back to an approximate trapezoid projection when keypoints fail.
#
# Why it is complex:
#   Football video is shot from an angle. The project must convert positions
#   from camera perspective to top-down pitch perspective.


# 11. Homography / view transformation
# -----------------------------------
# File:
#   Part a Player Tracking And Mapping/
#   football-analysis-CV-main/local_exec/sports/common/view.py
#
# Lines:
#   7-33  -> ViewTransformer initialization
#   31    -> cv2.findHomography(source, target)
#   35-59 -> transform_points()
#   57-59 -> cv2.perspectiveTransform()
#   61-81 -> transform_image() with cv2.warpPerspective()
#
# What this does:
#   - Calculates a homography matrix from source points to target pitch points.
#   - Applies perspective transformation to player/ball points.
#
# Why it is complex:
#   Homography is the mathematical part that makes pitch mapping possible.
#   It maps 2D points from one camera plane to another plane.


# 12. Pitch radar drawing
# ----------------------
# File:
#   Part a Player Tracking And Mapping/
#   football-analysis-CV-main/local_exec/main_test.py
#
# Lines:
#   350-415 -> build_pitch_radar_frame()
#
# What this does:
#   - Draws a mini pitch.
#   - Transforms ball, team1, team2, and referee detections to pitch points.
#   - Draws colored points on the pitch.
#   - Fits the pitch into a lower panel under the video frame.
#
# Why it is complex:
#   The final output combines live detection with a tactical map view.


# 13. Annotated video drawing
# --------------------------
# File:
#   Part a Player Tracking And Mapping/
#   football-analysis-CV-main/local_exec/utils/annotation.py
#
# Lines:
#   3-10  -> team/player/ball colors
#   16-27 -> Supervision annotators for players, referee, goalkeeper, ball
#   31-44 -> annotate_frames()
#
# Related possession overlay:
#   Part a Player Tracking And Mapping/
#   football-analysis-CV-main/local_exec/utils/graphics.py
#
# Lines:
#   4-43 -> draw_team_ball_control()
#
# What this does:
#   - Draws ellipses under players.
#   - Draws triangle over the ball.
#   - Draws referee and goalkeeper labels.
#   - Draws active player marker.
#   - Draws ball control/possession percentages.
#
# Why it is complex:
#   This converts raw detections into a human-readable video analysis output.


# 14. Output video, pitch video, pitch map image, and stats
# --------------------------------------------------------
# File:
#   Part a Player Tracking And Mapping/
#   football-analysis-CV-main/local_exec/main_test.py
#
# Lines:
#   458-460 -> creates OpenCV VideoWriter objects
#   557-560 -> writes annotated combined frame and pitch frame
#   563-564 -> releases video writers
#   566-567 -> saves pitch map image with cv2.imwrite()
#   569     -> writes possession stats
#   571-574 -> prints output locations
#
# Browser conversion:
#   app.py
#
# Lines:
#   397-464 -> convert_video_for_browser()
#   511-514 -> converts processed and pitch videos for browser display
#
# What this does:
#   - Writes the full processed video.
#   - Writes the pitch movement video.
#   - Saves pitch radar image.
#   - Saves stats text file.
#   - Converts videos to MP4 for browser playback when possible.
#
# Why it is complex:
#   The system generates multiple synchronized output formats, not just one
#   prediction or one image.


# 15. Flask integration for Part A processing
# ------------------------------------------
# File:
#   app.py
#
# Lines:
#   467-537 -> run_football_analysis()
#   477-484 -> sets Part A input/output globals before calling main()
#   486-501 -> replaces tqdm with web progress tracking
#   503-507 -> calls football_main.main()
#   516-520 -> creates stats JSON and CSV from TXT stats
#   691-710 -> start_football_worker() background processing
#
# What this does:
#   - Connects the CLI-style Part A code to the Flask web app.
#   - Runs video processing in background.
#   - Tracks progress and returns output paths to the browser.
#
# Why it is complex:
#   A long-running video pipeline is made usable from a browser interface.


# ============================================================
# PART B: PLAYER TRANSFER FEE PREDICTION
# ============================================================


# 16. Transfermarkt dataset discovery and required CSV files
# ---------------------------------------------------------
# File:
#   Part b Players Transfer Fee Prediction/src/data_loader.py
#
# Lines:
#   23-29  -> REQUIRED_FILES list
#   32-36  -> find_data_dir()
#   38-45  -> _read_csv()
#   224-235 -> build_enriched_data() checks missing files
#   237-256 -> reads players, clubs, competitions, appearances,
#              transfers, valuations, games, countries, national teams,
#              lineups, and events
#
# What this does:
#   - Uses 12 Transfermarkt CSV files.
#   - Supports csv_files/ or data/raw/.
#   - Validates that required files exist before processing.
#
# Why it is complex:
#   The project is not using one simple CSV. It builds a football intelligence
#   dataset from many connected files.


# 17. Data merging into enriched player dataset
# --------------------------------------------
# File:
#   Part b Players Transfer Fee Prediction/src/data_loader.py
#
# Lines:
#   258-271 -> base player cleanup and rename columns
#   273-288 -> aggregates appearances into goals, assists, minutes, games
#   290-308 -> latest value, peak value, one-year-ago value
#   310-324 -> latest transfer information
#   326-335 -> league tier and competition lookup
#   337-351 -> main merge chain using player_id, club_id, league id,
#              nationality, and national team id
#   394-408 -> merge enriched player features back into transfers
#   411-413 -> save processed CSV files
#
# What this does:
#   - Combines separate raw CSVs into players_enriched.csv.
#   - Combines transfer rows with player features into transfers_enriched.csv.
#
# Why it is complex:
#   The model needs many types of football context, so the loader joins
#   player, club, league, appearance, valuation, transfer, country, and
#   national team information.


# 18. Missing value cleaning and imputation
# ----------------------------------------
# File:
#   Part b Players Transfer Fee Prediction/src/data_loader.py
#
# Lines:
#   353-359 -> fills important value fields
#   361-370 -> numeric defaults and numeric conversion
#   417-430 -> impute_missing()
#
# What this does:
#   - Converts values to numeric safely.
#   - Fills missing numeric values by position-group median when possible.
#   - Fills remaining numeric values with median or zero.
#   - Fills text/categorical missing values with "Unknown".
#
# Why it is complex:
#   Real datasets are messy. Missing values must be handled before ML training.


# 19. Core football feature engineering
# ------------------------------------
# File:
#   Part b Players Transfer Fee Prediction/src/feature_engineering.py
#
# Lines:
#   20-27  -> league_tier_factor()
#   30-37  -> international_factor()
#   40-47  -> contract_years_left()
#   50-55  -> selling_need_factor()
#   58-61  -> detailed_position_multiplier()
#   64-82  -> performance_factor()
#   85-104 -> height_factor() and foot_factor()
#   107-172 -> add_features()
#   175-186 -> model_matrix()
#
# Important features created:
#   - goals_per_90
#   - assists_per_90
#   - goal_contribution
#   - age_factor
#   - position_multiplier
#   - league_tier_factor
#   - international_factor
#   - consistency_score
#   - peak_ratio
#   - log_current_value
#   - contract_years_left
#   - selling_club_need
#   - position_scarcity
#   - value_trend
#   - market_inflation
#   - performance_factor
#
# Why it is complex:
#   Raw football data is converted into meaningful ML features that explain
#   how age, position, performance, club, league, and contract context affect
#   transfer value.


# 20. Full numeric feature list used by models
# -------------------------------------------
# File:
#   Part b Players Transfer Fee Prediction/src/constants.py
#
# Lines:
#   58-78 -> NUMERIC_FEATURES
#
# What this does:
#   - Defines the exact columns used as model input.
#
# Why it is complex:
#   The model uses many football-specific numeric inputs instead of only
#   simple player age or goals.


# 21. Log transform of transfer fee target
# ---------------------------------------
# File:
#   Part b Players Transfer Fee Prediction/src/feature_engineering.py
#
# Lines:
#   175-186 -> model_matrix()
#   181-185 -> y = np.log1p(transfer_fee)
#
# Prediction conversion:
#   Part b Players Transfer Fee Prediction/src/predictor.py
#
# Lines:
#   139 -> np.expm1(estimator.predict(x)[0])
#
# What this does:
#   - Converts transfer fees to log scale during training.
#   - Converts predicted log value back to normal EUR value during prediction.
#
# Why it is complex:
#   Transfer fees are uneven. Log transform reduces the effect of extreme
#   superstar fees and helps the model learn more stable patterns.


# 22. Train/test split and scaling
# -------------------------------
# File:
#   Part b Players Transfer Fee Prediction/src/model_trainer.py
#
# Lines:
#   42-50 -> loads transfers, keeps paid transfers, prepares x and y
#   52-60 -> train_test_split(test_size=0.2)
#   62-64 -> StandardScaler for neural network
#
# What this does:
#   - Uses only paid transfers for model training.
#   - Splits the data into training and testing sets.
#   - Scales features for neural network training.
#
# Why it is complex:
#   Good ML training needs proper split and scaling, especially for neural
#   networks.


# 23. XGBoost model
# ----------------
# File:
#   Part b Players Transfer Fee Prediction/src/model_trainer.py
#
# Lines:
#   20-23 -> imports XGBRegressor if available
#   66-81 -> creates and trains XGBoost or fallback boosting model
#
# Parameters:
#   n_estimators=500
#   learning_rate=0.05
#   max_depth=6
#   subsample=0.8
#   colsample_bytree=0.8
#   objective="reg:squarederror"
#   n_jobs=-1
#
# What this does:
#   - Trains the main gradient boosting model for transfer fee prediction.
#
# Why it is complex:
#   XGBoost builds many decision trees, where each new tree improves the
#   mistakes of earlier trees. This is why it performs well on tabular data.


# 24. Random Forest model
# ----------------------
# File:
#   Part b Players Transfer Fee Prediction/src/model_trainer.py
#
# Lines:
#   9     -> imports RandomForestRegressor
#   83-84 -> creates and trains Random Forest
#
# Parameters:
#   n_estimators=200
#   max_depth=10
#   random_state=42
#   n_jobs=-1
#
# What this does:
#   - Trains an ensemble of decision trees.
#   - Uses the average of many trees for prediction.
#
# Why it is complex:
#   Random Forest reduces overfitting compared with a single decision tree
#   and acts as a strong comparison model.


# 25. Neural Network model
# -----------------------
# File:
#   Part b Players Transfer Fee Prediction/src/model_trainer.py
#
# Lines:
#   12    -> imports MLPRegressor
#   62-64 -> scales input features
#   86-93 -> creates and trains neural network
#
# Architecture:
#   hidden_layer_sizes=(256, 128, 64)
#   activation="relu"
#   max_iter=500
#   early_stopping=True
#
# What this does:
#   - Trains a multi-layer perceptron regression model.
#
# Why it is complex:
#   A neural network learns non-linear relationships through multiple hidden
#   layers, but it needs scaled features and more data to perform strongly.


# 26. Model saving with Joblib
# ---------------------------
# File:
#   Part b Players Transfer Fee Prediction/src/model_trainer.py
#
# Lines:
#   95-99 -> joblib.dump() for all models, scaler, and feature list
#
# Saved files:
#   Part b Players Transfer Fee Prediction/models/xgboost_transfer_model.pkl
#   Part b Players Transfer Fee Prediction/models/rf_transfer_model.pkl
#   Part b Players Transfer Fee Prediction/models/nn_transfer_model.pkl
#   Part b Players Transfer Fee Prediction/models/scaler.pkl
#   Part b Players Transfer Fee Prediction/models/feature_columns.pkl
#
# What this does:
#   - Saves trained models so the system does not need to retrain every time.
#
# Why it is complex:
#   This separates training time from prediction time and makes the app faster.


# 27. Model comparison metrics
# ---------------------------
# File:
#   Part b Players Transfer Fee Prediction/src/model_trainer.py
#
# Lines:
#   26-33  -> _metrics()
#   101-105 -> compares XGBoost, Random Forest, and Neural Network
#   107-112 -> prints MAE, RMSE, R2, and MAPE
#   114-118 -> prints XGBoost feature importance if available
#
# What this does:
#   - Converts log predictions back to EUR using expm1.
#   - Calculates MAE, RMSE, R2, and MAPE.
#   - Compares all trained models on the test set.
#
# Why it is complex:
#   Transfer fee prediction is regression, so normal accuracy is not enough.
#   These metrics explain average error, large-error penalty, and model fit.


# 28. Player search and fuzzy matching before prediction
# -----------------------------------------------------
# File:
#   Part b Players Transfer Fee Prediction/src/predictor.py
#
# Lines:
#   24-26 -> fuzzy_match()
#   29-43 -> find_player()
#
# What this does:
#   - Finds exact player name first.
#   - Then tries contains search.
#   - Then uses fuzzy matching for spelling mistakes.
#
# Why it is complex:
#   Users may type imperfect names. The system still tries to find the
#   closest player instead of failing immediately.


# 29. Formula fallback and explainable pricing breakdown
# -----------------------------------------------------
# File:
#   Part b Players Transfer Fee Prediction/src/predictor.py
#
# Lines:
#   46-52 -> buying_club_premium()
#   55-91 -> _formula_prediction()
#
# What this does:
#   - Calculates a formula-based price using:
#     current value, peak value, age, position, league tier, international
#     caps, buying club premium, performance, consistency, and contract urgency.
#   - Returns a readable breakdown for the user.
#
# Why it is complex:
#   If ML model files are missing, the project can still predict using
#   football business rules. It also makes the result explainable.


# 30. Final transfer fee prediction
# --------------------------------
# File:
#   Part b Players Transfer Fee Prediction/src/predictor.py
#
# Lines:
#   104-122 -> _load_model()
#   125-158 -> predict_transfer_fee()
#   134-139 -> prepares features and runs model prediction
#   137-138 -> applies scaler if neural network is used
#   139     -> converts log prediction back to EUR
#   141-143 -> blends ML prediction with formula value
#
# What this does:
#   - Loads the selected model.
#   - Finds the player.
#   - Creates model-ready features.
#   - Predicts transfer fee.
#   - Blends ML result with formula result.
#   - Returns predicted fee and breakdown.
#
# Why it is complex:
#   This is the final connection between dataset, engineered features,
#   trained model, and user-facing prediction.


# 31. Market insight and comparison-style analytics
# ------------------------------------------------
# File:
#   Part b Players Transfer Fee Prediction/src/market_insights.py
#
# Lines:
#   16-57 -> generate_market_insights()
#   20    -> average value by position
#   21    -> top players by current value
#   22-23 -> value vs age curve
#   25-31 -> undervalued player calculation
#   33-36 -> top spending clubs, sellers, most transferred players
#
# What this does:
#   - Creates market reports from the enriched dataset.
#   - Shows average value by position and age bucket.
#   - Finds top players and undervalued players.
#   - Summarizes spending clubs and transfer activity.
#
# Why it is complex:
#   This is not just prediction. It uses grouped analysis and football
#   business logic to summarize the transfer market.


# 32. Web transfer action integration
# ----------------------------------
# File:
#   app.py
#
# Lines:
#   540-571 -> predict_transfer()
#   574-688 -> run_transfer_action()
#
# What this does:
#   - Connects web forms to Part B modules.
#   - Supports search, predict, future, filter, compare, market, and simulate.
#   - Formats results for browser display and PDF output.
#
# Why it is complex:
#   One web page controls multiple machine learning and analytics workflows.

