from sklearn.cluster import KMeans
import cv2
import numpy as np


class Assigner:
    def __init__(self) -> None:
        self.team_colors = {}
        self._warned_messages = set()

    def _warn_once(self, message):
        if message not in self._warned_messages:
            print(message)
            self._warned_messages.add(message)

    def _get_torso_pixels(self, frame, bbox):
        h, w = frame.shape[:2]
        x1, y1, x2, y2 = map(int, bbox)
        x1 = max(0, min(w - 1, x1))
        x2 = max(0, min(w, x2))
        y1 = max(0, min(h - 1, y1))
        y2 = max(0, min(h, y2))

        if x2 <= x1 or y2 <= y1:
            return None

        player = frame[y1:y2, x1:x2]
        if player.size == 0:
            return None

        ph, pw = player.shape[:2]
        torso_y1 = max(0, int(ph * 0.15))
        torso_y2 = max(torso_y1 + 1, int(ph * 0.62))
        torso_x1 = max(0, int(pw * 0.18))
        torso_x2 = max(torso_x1 + 1, int(pw * 0.82))
        torso = player[torso_y1:torso_y2, torso_x1:torso_x2]

        if torso.size == 0:
            return None

        hsv = cv2.cvtColor(torso, cv2.COLOR_BGR2HSV)
        hue = hsv[:, :, 0]
        saturation = hsv[:, :, 1]
        value = hsv[:, :, 2]

        green_field = (hue >= 35) & (hue <= 85) & (saturation > 35)
        visible = value > 45
        colored_or_bright = (saturation > 20) | (value > 135)
        mask = visible & colored_or_bright & ~green_field

        if np.count_nonzero(mask) < 20:
            mask = visible

        if np.count_nonzero(mask) < 20:
            return None

        lab = cv2.cvtColor(torso, cv2.COLOR_BGR2LAB)
        return lab[mask].reshape(-1, 3)

    def get_player_color(self, frame, bbox):
        pixels = self._get_torso_pixels(frame, bbox)
        if pixels is None or len(pixels) < 20:
            return None

        if len(pixels) > 800:
            step = max(1, len(pixels) // 800)
            pixels = pixels[::step]

        n_clusters = min(3, len(pixels))
        kmeans = KMeans(n_clusters=n_clusters, n_init=5, random_state=0)
        kmeans.fit(pixels)
        counts = np.bincount(kmeans.labels_)
        player_cluster = int(np.argmax(counts))
        return kmeans.cluster_centers_[player_cluster]

    def get_player_team(self, frame, player_bbox, kmeans):
        player_color = self.get_player_color(frame, player_bbox)

        if player_color is None or kmeans is None:
            return -1

        return int(kmeans.predict(player_color.reshape(1, -1))[0])

    def assign_team_color(self, frame, players_detections):
        player_colors = []

        if players_detections is None or len(players_detections.xyxy) == 0:
            self._warn_once("No players detected yet; team assignment will retry on the next frame.")
            return None

        for bbox in players_detections.xyxy:
            color = self.get_player_color(frame, bbox)
            if color is not None:
                player_colors.append(color)

        if len(player_colors) < 2:
            self._warn_once("Not enough readable jersey colors yet; team assignment will retry.")
            return None

        player_colors = np.array(player_colors)
        kmeans = KMeans(n_clusters=2, init="k-means++", n_init=10, random_state=0)
        kmeans.fit(player_colors)

        self.team_colors[1] = kmeans.cluster_centers_[0]
        self.team_colors[2] = kmeans.cluster_centers_[1]

        return kmeans
