import cv2
import supervision as sv
from config import *

def draw_team_ball_control(frame, ball_control):

    # --- Safe values ---
    team1_val = ball_control.get(MODEL_CLASSES["team1"], 0)
    team2_val = ball_control.get(MODEL_CLASSES["team2"], 0)

    total = team1_val + team2_val

    # --- FIX: avoid division by zero ---
    if total == 0:
        team_1 = 0
        team_2 = 0
    else:
        team_1 = team1_val / total
        team_2 = team2_val / total

    # --- Clamp overlay inside frame ---
    h, w = frame.shape[:2]
    x1, y1 = int(w * 0.65), int(h * 0.05)
    x2, y2 = int(w * 0.98), int(h * 0.15)

    # --- Draw semi-transparent rectangle ---
    overlay = frame.copy()
    cv2.rectangle(overlay, (x1, y1), (x2, y2), (255, 255, 255), -1)

    alpha = 0.6
    cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)

    # --- Text positions ---
    text_y = y1 + 35

    cv2.putText(frame, "Ball Control:", (x1 + 10, text_y),
                cv2.FONT_HERSHEY_DUPLEX, 0.8, (0, 0, 0), 2)

    cv2.putText(frame, f"{team_1 * 100:.1f}%", (x1 + 220, text_y),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8,
                sv.Color.as_bgr(sv.Color.from_hex('#1E90FF')), 2)

    cv2.putText(frame, f"{team_2 * 100:.1f}%", (x1 + 320, text_y),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8,
                sv.Color.as_bgr(sv.Color.from_hex('#DC143C')), 2)

    return frame