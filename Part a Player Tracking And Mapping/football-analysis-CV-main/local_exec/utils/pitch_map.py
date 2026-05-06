"""
Football pitch visualization and coordinate conversion module.
"""
import cv2
import numpy as np
from typing import Tuple


class PitchMap:
    """Create and manage a mini football pitch visualization."""
    
    def __init__(self, pitch_width: int = 300, pitch_height: int = 450):
        """
        Initialize pitch map with given dimensions.
        
        Args:
            pitch_width: Width of the pitch in pixels
            pitch_height: Height of the pitch in pixels
        """
        self.pitch_width = pitch_width
        self.pitch_height = pitch_height
        self.pitch = self._create_pitch()
    
    def _create_pitch(self) -> np.ndarray:
        """Create a blank football pitch with field markings."""
        # Create green background
        pitch = np.ones((self.pitch_height, self.pitch_width, 3), dtype=np.uint8)
        pitch[:, :] = [34, 139, 34]  # Dark green (BGR)
        
        # Draw pitch markings (white lines)
        line_color = (255, 255, 255)  # White
        line_thickness = 2
        
        # Outer boundary
        cv2.rectangle(pitch, (0, 0), (self.pitch_width - 1, self.pitch_height - 1), 
                      line_color, line_thickness)
        
        # Halfway line
        mid_y = self.pitch_height // 2
        cv2.line(pitch, (0, mid_y), (self.pitch_width, mid_y), line_color, line_thickness)
        
        # Center circle
        center_x = self.pitch_width // 2
        center_y = mid_y
        radius = 30
        cv2.circle(pitch, (center_x, center_y), radius, line_color, line_thickness)
        
        # Center spot
        cv2.circle(pitch, (center_x, center_y), 3, line_color, -1)
        
        # Penalty areas (left side)
        penalty_width = 50
        penalty_height = 100
        cv2.rectangle(pitch, (0, (mid_y - penalty_height // 2)), 
                      (penalty_width, (mid_y + penalty_height // 2)), 
                      line_color, line_thickness)
        
        # Goal area (left side)
        goal_width = 30
        goal_height = 60
        cv2.rectangle(pitch, (0, (mid_y - goal_height // 2)), 
                      (goal_width, (mid_y + goal_height // 2)), 
                      line_color, line_thickness)
        
        # Penalty spot (left)
        spot_x = 15
        cv2.circle(pitch, (spot_x, mid_y), 2, line_color, -1)
        
        # Penalty areas (right side)
        cv2.rectangle(pitch, (self.pitch_width - penalty_width, (mid_y - penalty_height // 2)), 
                      (self.pitch_width, (mid_y + penalty_height // 2)), 
                      line_color, line_thickness)
        
        # Goal area (right side)
        cv2.rectangle(pitch, (self.pitch_width - goal_width, (mid_y - goal_height // 2)), 
                      (self.pitch_width, (mid_y + goal_height // 2)), 
                      line_color, line_thickness)
        
        # Penalty spot (right)
        spot_x = self.pitch_width - 15
        cv2.circle(pitch, (spot_x, mid_y), 2, line_color, -1)
        
        # Corner arcs (small circles at each corner)
        corner_radius = 8
        cv2.circle(pitch, (0, 0), corner_radius, line_color, line_thickness)
        cv2.circle(pitch, (self.pitch_width - 1, 0), corner_radius, line_color, line_thickness)
        cv2.circle(pitch, (0, self.pitch_height - 1), corner_radius, line_color, line_thickness)
        cv2.circle(pitch, (self.pitch_width - 1, self.pitch_height - 1), corner_radius, 
                   line_color, line_thickness)
        
        return pitch
    
    def get_blank_pitch(self) -> np.ndarray:
        """Get a fresh copy of the pitch."""
        return self.pitch.copy()
    
    @staticmethod
    def normalize_coordinates(x: float, y: float, frame_width: int, 
                             frame_height: int) -> Tuple[float, float]:
        """
        Convert video frame coordinates to normalized pitch coordinates (0-1 range).
        
        Args:
            x: X coordinate in video frame (pixels)
            y: Y coordinate in video frame (pixels)
            frame_width: Width of video frame
            frame_height: Height of video frame
            
        Returns:
            Tuple of normalized coordinates (norm_x, norm_y) in range 0-1
        """
        norm_x = max(0, min(1, x / frame_width))
        norm_y = max(0, min(1, y / frame_height))
        return norm_x, norm_y
    
    def map_to_pitch_pixel(self, norm_x: float, norm_y: float) -> Tuple[int, int]:
        """
        Convert normalized coordinates (0-1) to pitch pixel coordinates.
        
        Args:
            norm_x: Normalized X coordinate (0-1)
            norm_y: Normalized Y coordinate (0-1)
            
        Returns:
            Tuple of pixel coordinates on the pitch
        """
        pitch_x = int(norm_x * self.pitch_width)
        pitch_y = int(norm_y * self.pitch_height)
        
        # Clamp to pitch boundaries
        pitch_x = max(0, min(self.pitch_width - 1, pitch_x))
        pitch_y = max(0, min(self.pitch_height - 1, pitch_y))
        
        return pitch_x, pitch_y
    
    def draw_player(self, pitch: np.ndarray, norm_x: float, norm_y: float, 
                   color: Tuple[int, int, int], player_id: str = None, 
                   radius: int = 6) -> np.ndarray:
        """
        Draw a player on the pitch at normalized coordinates.
        
        Args:
            pitch: Pitch image to draw on
            norm_x: Normalized X coordinate (0-1)
            norm_y: Normalized Y coordinate (0-1)
            color: BGR color tuple for the player
            player_id: Optional player ID to draw as text
            radius: Radius of the player circle
            
        Returns:
            Modified pitch image
        """
        pitch_x, pitch_y = self.map_to_pitch_pixel(norm_x, norm_y)
        
        # Draw circle for player
        cv2.circle(pitch, (pitch_x, pitch_y), radius, color, -1)
        cv2.circle(pitch, (pitch_x, pitch_y), radius, (255, 255, 255), 1)  # White outline
        
        # Draw player ID if provided
        if player_id:
            # Use smaller font for player numbers
            font_scale = 0.3
            cv2.putText(pitch, str(player_id), (pitch_x - 3, pitch_y + 3),
                       cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 255, 255), 1)
        
        return pitch
    
    def draw_ball(self, pitch: np.ndarray, norm_x: float, norm_y: float,
                 color: Tuple[int, int, int] = (0, 165, 255),  # Orange
                 radius: int = 4) -> np.ndarray:
        """
        Draw the ball on the pitch at normalized coordinates.
        
        Args:
            pitch: Pitch image to draw on
            norm_x: Normalized X coordinate (0-1)
            norm_y: Normalized Y coordinate (0-1)
            color: BGR color tuple for the ball
            radius: Radius of the ball circle
            
        Returns:
            Modified pitch image
        """
        pitch_x, pitch_y = self.map_to_pitch_pixel(norm_x, norm_y)
        
        # Draw ball with highlight
        cv2.circle(pitch, (pitch_x, pitch_y), radius, color, -1)
        cv2.circle(pitch, (pitch_x, pitch_y), radius, (255, 255, 255), 1)
        
        return pitch
