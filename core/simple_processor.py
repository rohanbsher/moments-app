import os
import time
import logging
import cv2
import numpy as np
from typing import Dict, List, Tuple
from dataclasses import dataclass
import json

from .audio_volume_analyzer import AudioVolumeAnalyzer
from .diversity_scorer import DiversityScorer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class SimpleConfig:
    target_duration: int = 180  # 3 minutes default
    min_segment_duration: float = 1.0
    max_segment_duration: float = 10.0
    output_quality: str = 'high'

class SimpleVideoProcessor:
    """Simplified video processor without complex dependencies"""

    def __init__(self, config: SimpleConfig = None):
        self.config = config or SimpleConfig()
        self.audio_analyzer = AudioVolumeAnalyzer()
        self.diversity_scorer = DiversityScorer()

    def process_video(self, input_path: str, output_path: str = None) -> Dict:
        """Main processing pipeline"""

        start_time = time.time()

        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input video not found: {input_path}")

        if output_path is None:
            base_name = os.path.splitext(input_path)[0]
            output_path = f"{base_name}_highlights.mp4"

        logger.info(f"Processing video: {input_path}")

        try:
            # Get video info
            cap = cv2.VideoCapture(input_path)
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
            video_duration = frame_count / fps
            cap.release()

            logger.info(f"Video duration: {video_duration:.1f}s, FPS: {fps}")

            # Simple scene detection
            logger.info("Detecting scenes...")
            scenes = self._detect_scenes(input_path, video_duration)
            logger.info(f"Found {len(scenes)} scenes")

            # Analyze scenes
            logger.info("Analyzing scenes...")
            segments = self._analyze_scenes(input_path, scenes)

            # Rank and select
            logger.info("Selecting highlights...")
            selected = self._select_highlights(segments)

            # Apply diversity scoring to reduce repetition
            logger.info("Applying diversity scoring...")
            selected = self.diversity_scorer.calculate_diversity_penalty(input_path, selected)

            # Re-sort by updated scores
            selected.sort(key=lambda x: x['score'], reverse=True)

            # Re-select based on updated scores
            selected = self._select_highlights_from_scored(selected)

            if not selected:
                raise ValueError("No segments selected for highlights")

            # Create output video
            logger.info("Creating highlight video...")
            self._create_output_video(input_path, selected, output_path)

            processing_time = time.time() - start_time

            # Generate metadata
            metadata = {
                'input_file': input_path,
                'output_file': output_path,
                'input_duration': video_duration,
                'output_duration': sum(s['end'] - s['start'] for s in selected),
                'processing_time': processing_time,
                'segments_selected': len(selected),
                'segments': selected
            }

            logger.info(f"Processing complete! Output: {output_path}")
            logger.info(f"Processing time: {processing_time:.2f} seconds")

            return metadata

        except Exception as e:
            logger.error(f"Processing failed: {e}")
            raise

    def _detect_scenes(self, video_path: str, duration: float) -> List[Tuple[float, float]]:
        """Simple scene detection by analyzing frame differences"""

        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)

        scenes = []
        scene_start = 0
        prev_frame = None
        frame_idx = 0
        threshold = 30.0  # Scene change threshold

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Sample every 30 frames for speed
            if frame_idx % 30 == 0:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                gray = cv2.resize(gray, (160, 120))  # Small for speed

                if prev_frame is not None:
                    diff = cv2.absdiff(prev_frame, gray)
                    mean_diff = np.mean(diff)

                    # Scene change detected
                    if mean_diff > threshold:
                        scene_end = frame_idx / fps
                        if scene_end - scene_start >= 2.0:  # Min scene length
                            scenes.append((scene_start, scene_end))
                            scene_start = scene_end

                prev_frame = gray

            frame_idx += 1

        # Add final scene
        if duration - scene_start >= 2.0:
            scenes.append((scene_start, duration))

        cap.release()

        # If no scenes detected, create segments every 5 seconds
        if not scenes:
            scenes = []
            t = 0
            while t < duration:
                end_t = min(t + 5, duration)
                scenes.append((t, end_t))
                t = end_t

        return scenes

    def _analyze_scenes(self, video_path: str, scenes: List[Tuple[float, float]]) -> List[Dict]:
        """Analyze each scene for motion and quality"""

        segments = []

        for i, (start, end) in enumerate(scenes):
            logger.info(f"Analyzing scene {i+1}/{len(scenes)}")

            motion_data = self._analyze_motion(video_path, start, end)
            audio_data = self.audio_analyzer.analyze_segment(video_path, start, end)

            # Simple quality score based on motion
            quality_score = 0.5 + min(motion_data['motion_intensity'] * 0.01, 0.4)

            # Position score (beginning and end are important)
            total_duration = scenes[-1][1] if scenes else end
            position_ratio = start / total_duration if total_duration > 0 else 0

            position_score = 1.0 if position_ratio < 0.1 else 0.8 if position_ratio > 0.9 else 0.5

            # Audio excitement score
            audio_score = audio_data.get('excitement_level', 0.0)

            # Combined score with audio
            score = (
                motion_data['motion_intensity'] * 0.003 +
                quality_score * 0.25 +
                position_score * 0.20 +
                (1 if motion_data['has_significant_motion'] else 0) * 0.25 +
                audio_score * 0.30  # Audio is now 30% of the score!
            )

            segment = {
                'start': start,
                'end': end,
                'duration': end - start,
                'score': score,
                'motion_intensity': motion_data['motion_intensity'],
                'has_motion': motion_data['has_significant_motion'],
                'audio_excitement': audio_score,
                'has_loud_moments': audio_data.get('has_loud_moments', False),
                'volume_peak': audio_data.get('volume_peak', 0.0)
            }

            segments.append(segment)

        return segments

    def _analyze_motion(self, video_path: str, start_time: float, end_time: float) -> Dict:
        """Analyze motion in video segment"""

        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)

        start_frame = int(start_time * fps)
        end_frame = int(end_time * fps)
        cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)

        motion_scores = []
        prev_gray = None

        # Sample every 10 frames for speed
        for frame_idx in range(start_frame, end_frame, 10):
            ret, frame = cap.read()
            if not ret:
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray = cv2.resize(gray, (320, 240))

            if prev_gray is not None:
                # Simple motion detection using frame difference
                diff = cv2.absdiff(prev_gray, gray)
                motion_score = np.mean(diff)
                motion_scores.append(motion_score)

            prev_gray = gray

        cap.release()

        motion_intensity = np.mean(motion_scores) if motion_scores else 0
        peak_motion = np.max(motion_scores) if motion_scores else 0

        return {
            'motion_intensity': motion_intensity,
            'peak_motion': peak_motion,
            'has_significant_motion': motion_intensity > 5.0
        }

    def _select_highlights(self, segments: List[Dict]) -> List[Dict]:
        """Select best segments for highlight reel"""

        # Sort by score
        segments.sort(key=lambda x: x['score'], reverse=True)

        selected = []
        total_duration = 0
        target = self.config.target_duration

        for segment in segments:
            duration = min(segment['duration'], self.config.max_segment_duration)

            if duration < self.config.min_segment_duration:
                continue

            if total_duration + duration <= target:
                selected.append(segment)
                total_duration += duration

            if total_duration >= target * 0.95:
                break

        # Sort by time order
        selected.sort(key=lambda x: x['start'])

        return selected

    def _select_highlights_from_scored(self, scored_segments: List[Dict]) -> List[Dict]:
        """
        Re-select highlights after diversity scoring has updated the scores

        Args:
            scored_segments: Segments with updated scores (already sorted by score)

        Returns:
            Selected segments for highlight reel
        """
        selected = []
        total_duration = 0
        target = self.config.target_duration

        for segment in scored_segments:
            duration = min(segment['duration'], self.config.max_segment_duration)

            if duration < self.config.min_segment_duration:
                continue

            if total_duration + duration <= target:
                selected.append(segment)
                total_duration += duration

            if total_duration >= target * 0.95:
                break

        # Sort by time order
        selected.sort(key=lambda x: x['start'])

        return selected

    def _create_output_video(self, input_path: str, segments: List[Dict], output_path: str):
        """Create output video using OpenCV"""

        if not segments:
            raise ValueError("No segments to process")

        # Input video
        cap = cv2.VideoCapture(input_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        # Output video
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

        for segment in segments:
            start_frame = int(segment['start'] * fps)
            end_frame = int(min(segment['end'], segment['start'] + self.config.max_segment_duration) * fps)

            cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)

            for frame_idx in range(start_frame, end_frame):
                ret, frame = cap.read()
                if not ret:
                    break
                out.write(frame)

        cap.release()
        out.release()

        logger.info(f"Output video created: {output_path}")