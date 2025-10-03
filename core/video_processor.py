import os
import time
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass
import json
import cv2

from .scene_detector import SceneDetector
from .motion_analyzer import MotionAnalyzer
from .audio_analyzer import AudioAnalyzer
from .highlight_ranker import HighlightRanker, Segment
from .video_composer import VideoComposer, CompositionSegment

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ProcessingConfig:
    target_duration: int = 180  # 3 minutes default
    min_segment_duration: float = 1.0
    max_segment_duration: float = 10.0
    quality_threshold: float = 0.3
    enable_speech_recognition: bool = True
    output_quality: str = 'high'
    output_resolution: str = '1920x1080'
    output_fps: int = 30

class VideoProcessor:
    def __init__(self, config: ProcessingConfig = None):
        self.config = config or ProcessingConfig()

        self.scene_detector = SceneDetector()
        self.motion_analyzer = MotionAnalyzer()
        self.audio_analyzer = AudioAnalyzer()
        self.highlight_ranker = HighlightRanker()
        self.video_composer = VideoComposer()

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
            logger.info("Detecting scenes...")
            scenes = self.scene_detector.detect_scenes(input_path)
            logger.info(f"Found {len(scenes)} scenes")

            if not scenes:
                logger.warning("No scenes detected, treating entire video as one scene")
                video_duration = self._get_video_duration(input_path)
                scenes = [(0, video_duration)]

            logger.info("Analyzing scenes...")
            segments = self._analyze_scenes(input_path, scenes)

            if not segments:
                raise ValueError("No valid segments found after analysis")

            logger.info("Ranking segments...")
            video_duration = self._get_video_duration(input_path)
            ranked_segments = self.highlight_ranker.rank_segments(segments, video_duration)

            logger.info("Selecting highlights...")
            selected_segments = self.highlight_ranker.select_highlights(
                ranked_segments,
                self.config.target_duration,
                self.config.min_segment_duration,
                self.config.max_segment_duration
            )

            if not selected_segments:
                raise ValueError("No segments selected for highlights")

            logger.info("Composing final video...")
            composition_segments = self._prepare_composition(selected_segments, input_path)
            self.video_composer.compose_video(
                composition_segments,
                output_path,
                self.config.output_resolution,
                self.config.output_fps,
                self.config.output_quality
            )

            processing_time = time.time() - start_time
            metadata = self._generate_metadata(
                input_path,
                output_path,
                selected_segments,
                processing_time
            )

            metadata_path = output_path.replace('.mp4', '_metadata.json')
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)

            logger.info(f"Processing complete! Output: {output_path}")
            logger.info(f"Processing time: {processing_time:.2f} seconds")

            return metadata

        except Exception as e:
            logger.error(f"Processing failed: {e}")
            raise

    def _analyze_scenes(self, video_path: str, scenes: List[Tuple[float, float]]) -> List[Segment]:
        """Analyze each scene for various features"""

        segments = []
        total_scenes = len(scenes)

        for i, (start_time, end_time) in enumerate(scenes):
            logger.info(f"Analyzing scene {i+1}/{total_scenes}")

            if end_time - start_time < 0.5:
                continue

            motion_data = self.motion_analyzer.analyze_segment(
                video_path, start_time, end_time
            )

            audio_data = self.audio_analyzer.analyze_segment(
                video_path, start_time, end_time
            ) if self.config.enable_speech_recognition else {}

            quality_score = 0.5 + (motion_data.get('motion_intensity', 0) * 0.01)
            quality_score = min(1.0, quality_score)

            if quality_score < self.config.quality_threshold:
                logger.warning(f"Skipping low quality scene {i+1}")
                continue

            segment = Segment(
                start_time=start_time,
                end_time=end_time,
                scene_score=0,
                motion_data=motion_data,
                audio_data=audio_data,
                quality_score=quality_score
            )

            segments.append(segment)

        return segments

    def _prepare_composition(self, segments: List[Segment],
                           input_path: str) -> List[CompositionSegment]:
        """Prepare segments for video composition"""

        composition_segments = []

        for i, segment in enumerate(segments):
            if i == 0:
                transition = 'cut'
            elif segment.audio_data.get('has_speech'):
                transition = 'cut'
            else:
                transition = 'fade'

            comp_segment = CompositionSegment(
                input_file=input_path,
                start_time=segment.start_time,
                end_time=min(segment.end_time, segment.start_time + self.config.max_segment_duration),
                transition_type=transition,
                transition_duration=0.5
            )

            composition_segments.append(comp_segment)

        return composition_segments

    def _get_video_duration(self, video_path: str) -> float:
        """Get video duration in seconds"""
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
        cap.release()
        return frame_count / fps if fps > 0 else 0

    def _generate_metadata(self, input_path: str, output_path: str,
                          segments: List[Segment], processing_time: float) -> Dict:
        """Generate metadata about the processing"""

        input_duration = self._get_video_duration(input_path)
        output_duration = sum(s.duration for s in segments)

        return {
            'input_file': input_path,
            'output_file': output_path,
            'input_duration': input_duration,
            'output_duration': output_duration,
            'compression_ratio': input_duration / output_duration if output_duration > 0 else 0,
            'processing_time': processing_time,
            'segments_selected': len(segments),
            'segments': [
                {
                    'start': s.start_time,
                    'end': s.end_time,
                    'duration': s.duration,
                    'has_speech': s.audio_data.get('has_speech', False),
                    'quality_score': s.quality_score
                }
                for s in segments
            ]
        }