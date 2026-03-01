import os
import cv2
import av
import numpy as np
import mediapipe as mp
from streamlit_webrtc import VideoProcessorBase

RESOURCES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Resources")
MODEL_PATH = os.path.join(RESOURCES_DIR, "hand_landmarker.task")

# Game resolution constants
GAME_W, GAME_H = 1280, 720


def overlay_png(background, overlay_img, pos):
    """Overlay a BGRA image onto a BGR background at the given (x, y) position."""
    x, y = int(pos[0]), int(pos[1])
    h, w = overlay_img.shape[:2]
    bg_h, bg_w = background.shape[:2]

    # Clip to background bounds
    x1, y1 = max(x, 0), max(y, 0)
    x2, y2 = min(x + w, bg_w), min(y + h, bg_h)
    ox1, oy1 = x1 - x, y1 - y
    ox2, oy2 = ox1 + (x2 - x1), oy1 + (y2 - y1)

    if x2 <= x1 or y2 <= y1:
        return background

    if overlay_img.shape[2] == 4:
        alpha = overlay_img[oy1:oy2, ox1:ox2, 3] / 255.0
        for c in range(3):
            background[y1:y2, x1:x2, c] = (
                alpha * overlay_img[oy1:oy2, ox1:ox2, c]
                + (1 - alpha) * background[y1:y2, x1:x2, c]
            )
    else:
        background[y1:y2, x1:x2] = overlay_img[oy1:oy2, ox1:ox2]

    return background


class PongVideoProcessor(VideoProcessorBase):
    # Class-level attributes written by Streamlit UI, read by recv() thread.
    game_active: bool = False
    restart_flag: bool = False
    ball_speed: int = 15

    def __init__(self):
        # Load resource images
        self.imgBackground = cv2.imread(os.path.join(RESOURCES_DIR, "Background.png"))
        self.imgGameOver = cv2.imread(os.path.join(RESOURCES_DIR, "gameOver.png"))
        self.imgBall = cv2.imread(os.path.join(RESOURCES_DIR, "Ball.png"), cv2.IMREAD_UNCHANGED)
        self.imgBat1 = cv2.imread(os.path.join(RESOURCES_DIR, "bat1.png"), cv2.IMREAD_UNCHANGED)
        self.imgBat2 = cv2.imread(os.path.join(RESOURCES_DIR, "bat2.png"), cv2.IMREAD_UNCHANGED)

        # Resize background and game-over to match game resolution
        if self.imgBackground is not None:
            self.imgBackground = cv2.resize(self.imgBackground, (GAME_W, GAME_H))
        if self.imgGameOver is not None:
            self.imgGameOver = cv2.resize(self.imgGameOver, (GAME_W, GAME_H))

        # Hand detector using mediapipe Task API
        options = mp.tasks.vision.HandLandmarkerOptions(
            base_options=mp.tasks.BaseOptions(model_asset_path=MODEL_PATH),
            running_mode=mp.tasks.vision.RunningMode.VIDEO,
            num_hands=2,
            min_hand_detection_confidence=0.5,
            min_hand_presence_confidence=0.5,
            min_tracking_confidence=0.5,
        )
        self.detector = mp.tasks.vision.HandLandmarker.create_from_options(options)
        self.frame_timestamp_ms = 0

        # Game state
        self.ballpos = [100, 100]
        self.speedX = 15
        self.speedY = 15
        self.game_over = False
        self.score = [0, 0]

    def _reset_game(self):
        self.ballpos = [100, 100]
        self.speedX = self.ball_speed
        self.speedY = self.ball_speed
        self.game_over = False
        self.score = [0, 0]
        raw = cv2.imread(os.path.join(RESOURCES_DIR, "gameOver.png"))
        if raw is not None:
            self.imgGameOver = cv2.resize(raw, (GAME_W, GAME_H))

    def _detect_hands(self, img):
        """Run hand detection and return list of dicts with 'type' and 'bbox'."""
        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        self.frame_timestamp_ms += 33  # ~30fps
        result = self.detector.detect_for_video(mp_image, self.frame_timestamp_ms)

        hands = []
        if not result.hand_landmarks:
            return hands

        for i, landmarks in enumerate(result.hand_landmarks):
            # Get handedness (Left/Right) — mediapipe reports from camera's
            # perspective, but we flipped the image, so we swap labels
            handedness = result.handedness[i][0].category_name
            if handedness == "Left":
                handedness = "Right"
            elif handedness == "Right":
                handedness = "Left"

            # Calculate bounding box from landmarks
            xs = [lm.x * GAME_W for lm in landmarks]
            ys = [lm.y * GAME_H for lm in landmarks]
            x_min, x_max = int(min(xs)), int(max(xs))
            y_min, y_max = int(min(ys)), int(max(ys))

            hands.append({
                "type": handedness,
                "bbox": (x_min, y_min, x_max - x_min, y_max - y_min),
            })

        return hands

    def recv(self, frame: av.VideoFrame) -> av.VideoFrame:
        img = frame.to_ndarray(format="bgr24")

        # Handle restart
        if self.restart_flag:
            self._reset_game()
            self.restart_flag = False

        # Normalize to game resolution and mirror
        img = cv2.resize(img, (GAME_W, GAME_H))
        img = cv2.flip(img, 1)

        # --- Pre-game idle screen ---
        if not self.game_active:
            overlay = img.copy()
            cv2.rectangle(overlay, (0, 0), (GAME_W, GAME_H), (15, 12, 41), -1)
            img = cv2.addWeighted(img, 0.3, overlay, 0.7, 0)

            text = "Toggle START to play"
            font = cv2.FONT_HERSHEY_SIMPLEX
            scale, thickness = 1.4, 3
            (tw, th), _ = cv2.getTextSize(text, font, scale, thickness)
            tx = (GAME_W - tw) // 2
            ty = (GAME_H + th) // 2

            cv2.putText(img, text, (tx + 2, ty + 2), font, scale, (0, 0, 0), thickness + 2)
            cv2.putText(img, text, (tx, ty), font, scale, (102, 126, 234), thickness)

            sub = "Show both hands to the camera"
            (sw, sh), _ = cv2.getTextSize(sub, font, 0.7, 2)
            cv2.putText(img, sub, ((GAME_W - sw) // 2, ty + 50), font, 0.7, (160, 174, 192), 2)

            return av.VideoFrame.from_ndarray(img, format="bgr24")

        # --- Active game ---
        # Sync speed magnitude with the UI slider (preserve direction)
        target = self.ball_speed
        if abs(self.speedX) != target:
            self.speedX = target if self.speedX > 0 else -target
        if abs(self.speedY) != target:
            self.speedY = target if self.speedY > 0 else -target

        hands = self._detect_hands(img)

        # Overlay background
        if self.imgBackground is not None:
            img = cv2.addWeighted(img, 0.05, self.imgBackground, 0.95, 0)

        # Process hands
        if hands:
            for hand in hands:
                x, y, w, h = hand["bbox"]
                h1, w1, _ = self.imgBat1.shape
                y1 = y - h1 // 2
                y1 = int(np.clip(y1, 20, 415))

                if hand["type"] == "Left":
                    img = overlay_png(img, self.imgBat1, (59, y1))
                    if 59 < self.ballpos[0] < 59 + w1 and y1 < self.ballpos[1] < y1 + h1:
                        self.speedX = abs(self.speedX)
                        self.ballpos[0] += 30
                        self.score[0] += 1

                if hand["type"] == "Right":
                    img = overlay_png(img, self.imgBat2, (1195, y1))
                    if 1195 - 50 < self.ballpos[0] < 1195 - 30 and y1 < self.ballpos[1] < y1 + h1:
                        self.speedX = -abs(self.speedX)
                        self.ballpos[0] -= 30
                        self.score[1] += 1

        # Game over check
        if self.ballpos[0] < 40 or self.ballpos[0] > 1200:
            self.game_over = True

        if self.game_over:
            img = self.imgGameOver.copy()
            total = str(self.score[0] + self.score[1]).zfill(2)
            cv2.putText(
                img, total, (585, 360),
                cv2.FONT_HERSHEY_COMPLEX, 2.5, (200, 0, 200), 5,
            )
        else:
            # Ball physics
            if self.ballpos[1] >= 500 or self.ballpos[1] <= 10:
                self.speedY = -self.speedY
            self.ballpos[0] += self.speedX
            self.ballpos[1] += self.speedY

        # Clamp ball position to prevent overlay crash
        self.ballpos[0] = int(np.clip(self.ballpos[0], 0, GAME_W - 50))
        self.ballpos[1] = int(np.clip(self.ballpos[1], 0, GAME_H - 50))

        # Draw ball and scores
        img = overlay_png(img, self.imgBall, self.ballpos)
        cv2.putText(img, str(self.score[0]), (300, 650), cv2.FONT_HERSHEY_COMPLEX, 3, (255, 255, 255), 5)
        cv2.putText(img, str(self.score[1]), (900, 650), cv2.FONT_HERSHEY_COMPLEX, 3, (255, 255, 255), 5)

        return av.VideoFrame.from_ndarray(img, format="bgr24")
