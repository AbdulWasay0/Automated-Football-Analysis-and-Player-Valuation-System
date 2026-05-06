"""
Player position tracking throughout the video.
"""
from typing import Dict, List, Tuple
from collections import defaultdict


class PlayerTracker:
    """Track player positions throughout the video."""
    
    def __init__(self):
        """Initialize the player tracker."""
        # Store positions: {frame_num: {player_id: (norm_x, norm_y, team_id)}}
        self.positions = defaultdict(dict)
        self.ball_positions = []  # List of (frame_num, norm_x, norm_y)
        self.current_frame = 0
        
    def add_player_position(self, player_id: int, norm_x: float, norm_y: float, 
                          team_id: int) -> None:
        """
        Record a player's position in the current frame.
        
        Args:
            player_id: Unique player tracker ID
            norm_x: Normalized X coordinate (0-1)
            norm_y: Normalized Y coordinate (0-1)
            team_id: Team ID (4 for team1, 5 for team2, 3 for referee)
        """
        self.positions[self.current_frame][player_id] = {
            'x': norm_x,
            'y': norm_y,
            'team_id': team_id
        }
    
    def add_ball_position(self, norm_x: float, norm_y: float) -> None:
        """
        Record the ball's position in the current frame.
        
        Args:
            norm_x: Normalized X coordinate (0-1)
            norm_y: Normalized Y coordinate (0-1)
        """
        self.ball_positions.append((self.current_frame, norm_x, norm_y))
    
    def increment_frame(self) -> None:
        """Move to the next frame."""
        self.current_frame += 1
    
    def get_frame_players(self, frame_num: int) -> Dict[int, Dict]:
        """
        Get all players in a specific frame.
        
        Args:
            frame_num: Frame number to retrieve
            
        Returns:
            Dictionary of {player_id: {x, y, team_id}}
        """
        return self.positions.get(frame_num, {})
    
    def get_average_positions(self) -> Dict[int, Tuple[float, float, int]]:
        """
        Get average position of each player across all frames where they appear.
        
        Returns:
            Dictionary of {player_id: (avg_x, avg_y, team_id)}
        """
        player_data = defaultdict(lambda: {'x_sum': 0, 'y_sum': 0, 'count': 0, 'team_id': None})
        
        for frame_data in self.positions.values():
            for player_id, pos_data in frame_data.items():
                player_data[player_id]['x_sum'] += pos_data['x']
                player_data[player_id]['y_sum'] += pos_data['y']
                player_data[player_id]['count'] += 1
                player_data[player_id]['team_id'] = pos_data['team_id']
        
        result = {}
        for player_id, data in player_data.items():
            if data['count'] > 0:
                avg_x = data['x_sum'] / data['count']
                avg_y = data['y_sum'] / data['count']
                result[player_id] = (avg_x, avg_y, data['team_id'])
        
        return result
    
    def get_all_positions(self) -> Dict[int, Dict[int, Dict]]:
        """
        Get all recorded positions.
        
        Returns:
            Complete position history
        """
        return dict(self.positions)
    
    def clear(self) -> None:
        """Clear all tracked positions."""
        self.positions.clear()
        self.ball_positions.clear()
        self.current_frame = 0
