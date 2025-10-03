import cv2
import numpy as np
from typing import Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)

class MotionAnalyzer:
    def __init__(self):
        self.optical_flow = None

    def analyze_segment(self, video_path: str,
                       start_time: float,
                       end_time: float,
                       sample_rate: int = 5) -> Dict:
        """Analyze motion in video segment"""

        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)

        start_frame = int(start_time * fps)
        end_frame = int(end_time * fps)
        cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)

        motion_scores = []
        camera_movement = []
        prev_gray = None

        for frame_idx in range(start_frame, end_frame, sample_rate):
            ret, frame = cap.read()
            if not ret:
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray = cv2.resize(gray, (640, 480))

            if prev_gray is not None:
                flow = cv2.calcOpticalFlowFarneback(
                    prev_gray, gray, None,
                    pyr_scale=0.5, levels=3, winsize=15,
                    iterations=3, poly_n=5, poly_sigma=1.2, flags=0
                )

                magnitude = np.sqrt(flow[..., 0]**2 + flow[..., 1]**2)
                motion_score = np.mean(magnitude)
                motion_scores.append(motion_score)

                camera_score = self._detect_camera_movement(flow)
                camera_movement.append(camera_score)

            prev_gray = gray

        cap.release()

        return {
            'motion_intensity': np.mean(motion_scores) if motion_scores else 0,
            'motion_variance': np.std(motion_scores) if motion_scores else 0,
            'peak_motion': np.max(motion_scores) if motion_scores else 0,
            'camera_movement': np.mean(camera_movement) if camera_movement else 0,
            'has_significant_motion': np.mean(motion_scores) > 2.0 if motion_scores else False
        }

    def _detect_camera_movement(self, flow: np.ndarray) -> float:
        """Detect global camera movement"""
        mean_flow_x = np.mean(flow[..., 0])
        mean_flow_y = np.mean(flow[..., 1])
        return np.sqrt(mean_flow_x**2 + mean_flow_y**2)

    def detect_action_moments(self, video_path: str,
                            threshold: float = 5.0) -> List[Tuple[float, float]]:
        """Detect high-action moments in video"""
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)

        action_moments = []
        current_action_start = None
        prev_gray = None
        frame_idx = 0

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray = cv2.resize(gray, (320, 240))

            if prev_gray is not None and frame_idx % 5 == 0:
                flow = cv2.calcOpticalFlowFarneback(
                    prev_gray, gray, None, 0.5, 3, 15, 3, 5, 1.2, 0
                )
                magnitude = np.mean(np.sqrt(flow[..., 0]**2 + flow[..., 1]**2))

                if magnitude > threshold:
                    if current_action_start is None:
                        current_action_start = frame_idx / fps
                elif current_action_start is not None:
                    action_moments.append((current_action_start, frame_idx / fps))
                    current_action_start = None

            prev_gray = gray
            frame_idx += 1

        cap.release()
        return action_moments