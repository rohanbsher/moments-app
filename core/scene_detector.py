import numpy as np
from scenedetect import detect, ContentDetector, AdaptiveDetector
from typing import List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

class SceneDetector:
    def __init__(self, threshold: float = 30.0, min_scene_len: int = 15):
        self.threshold = threshold
        self.min_scene_len = min_scene_len

    def detect_scenes(self, video_path: str) -> List[Tuple[float, float]]:
        """Detect scene boundaries in video"""
        try:
            scenes = detect(
                video_path,
                AdaptiveDetector(
                    adaptive_threshold=3.0,
                    min_scene_len=self.min_scene_len
                )
            )

            scene_list = [
                (scene[0].get_seconds(), scene[1].get_seconds())
                for scene in scenes
            ]

            logger.info(f"Detected {len(scene_list)} scenes")
            return scene_list

        except Exception as e:
            logger.error(f"Scene detection failed: {e}")
            return []

    def merge_short_scenes(self, scenes: List[Tuple[float, float]],
                          min_duration: float = 1.0) -> List[Tuple[float, float]]:
        """Merge scenes shorter than minimum duration"""
        if not scenes:
            return []

        merged = []
        current_start = scenes[0][0]
        current_end = scenes[0][1]

        for start, end in scenes[1:]:
            if end - current_start < min_duration:
                current_end = end
            else:
                merged.append((current_start, current_end))
                current_start = start
                current_end = end

        if scenes:
            merged.append((current_start, current_end))

        return merged