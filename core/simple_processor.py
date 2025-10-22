import os
import time
import logging
import cv2
import numpy as np
from typing import Dict, List, Tuple
from dataclasses import dataclass
import json
import subprocess

from .audio_volume_analyzer import AudioVolumeAnalyzer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from .diversity_scorer import DiversityScorer
except ImportError:
    DiversityScorer = None
    logger.warning("DiversityScorer not available")

# NEW: AI-powered analyzers
try:
    from .ai_analyzers import AIVideoAnalyzer
    AI_AVAILABLE = True
    logger.info("✅ AI analyzers available")
except ImportError as e:
    AI_AVAILABLE = False
    logger.warning(f"⚠️ AI analyzers not available: {e}. Falling back to basic analysis.")

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
        self.diversity_scorer = DiversityScorer() if DiversityScorer else None

        # NEW: Initialize AI analyzer if available
        self.ai_analyzer = AIVideoAnalyzer() if AI_AVAILABLE else None
        if self.ai_analyzer:
            logger.info("🧠 AI-powered analysis enabled")
        else:
            logger.info("📊 Using basic analysis (AI not available)")

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

            # Apply diversity scoring to reduce repetition (if available)
            if self.diversity_scorer:
                logger.info("Applying diversity scoring...")
                selected = self.diversity_scorer.calculate_diversity_penalty(input_path, selected)
            else:
                logger.info("Skipping diversity scoring (not available)")

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
        """Analyze each scene for motion, audio, and AI features"""

        segments = []

        for i, (start, end) in enumerate(scenes):
            logger.info(f"Analyzing scene {i+1}/{len(scenes)}")

            # Existing analysis
            motion_data = self._analyze_motion(video_path, start, end)
            audio_data = self.audio_analyzer.analyze_segment(video_path, start, end)

            # NEW: AI analysis (if available)
            ai_result = None
            if self.ai_analyzer:
                try:
                    logger.info(f"  🧠 AI analyzing scene {i+1} ({start:.1f}s-{end:.1f}s)")
                    ai_result = self.ai_analyzer.analyze_segment(video_path, start, end)
                    logger.info(f"  ✅ AI: faces={ai_result.face_score:.2f}, emotion={ai_result.emotion_score:.2f}, speech={ai_result.speech_score:.2f}")
                except Exception as e:
                    logger.warning(f"  ⚠️ AI analysis failed for scene {i+1}: {e}")
                    ai_result = None

            # Simple quality score based on motion
            quality_score = 0.5 + min(motion_data['motion_intensity'] * 0.01, 0.4)

            # Position score (beginning and end are important)
            total_duration = scenes[-1][1] if scenes else end
            position_ratio = start / total_duration if total_duration > 0 else 0
            position_score = 1.0 if position_ratio < 0.1 else 0.8 if position_ratio > 0.9 else 0.5

            # Audio excitement score
            audio_score = audio_data.get('excitement_level', 0.0)

            # Calculate score with or without AI
            if ai_result and AI_AVAILABLE:
                # NEW: AI-powered scoring (much better!)
                score = (
                    ai_result.emotion_score * 0.30 +      # Emotion is most important
                    ai_result.speech_score * 0.25 +       # Speech keywords very important
                    ai_result.face_score * 0.15 +         # Having faces is important
                    audio_score * 0.15 +                  # Loud moments still matter
                    motion_data['motion_intensity'] * 0.001 +  # Motion less important now (10%)
                    position_score * 0.05                 # Position minor factor
                )
                logger.info(f"  📊 AI Score: {score:.3f} (emotion: {ai_result.emotion_score:.2f}, speech: {ai_result.speech_score:.2f})")
            else:
                # Fallback: Original scoring without AI
                score = (
                    motion_data['motion_intensity'] * 0.003 +
                    quality_score * 0.25 +
                    position_score * 0.20 +
                    (1 if motion_data['has_significant_motion'] else 0) * 0.25 +
                    audio_score * 0.30
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
                'volume_peak': audio_data.get('volume_peak', 0.0),
                # NEW: AI features
                'has_faces': ai_result.has_faces if ai_result else False,
                'has_happy_faces': ai_result.has_happy_faces if ai_result else False,
                'has_speech': ai_result.has_speech if ai_result else False,
                'transcription': ai_result.transcription if ai_result else '',
                'emotion_score': ai_result.emotion_score if ai_result else 0.0,
                'speech_score': ai_result.speech_score if ai_result else 0.0,
                'ai_enabled': ai_result is not None
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

        # First pass: select high-quality segments
        for segment in segments:
            duration = min(segment['duration'], self.config.max_segment_duration)

            if duration < self.config.min_segment_duration:
                continue

            if total_duration + duration <= target:
                selected.append(segment)
                total_duration += duration

            if total_duration >= target * 0.95:
                break

        # Second pass: if we didn't hit target, be more lenient
        if total_duration < target * 0.7 and len(selected) < len(segments):
            logger.warning(f"Only selected {total_duration:.1f}s of {target}s target. Adding more segments...")

            # Add remaining segments even if lower scored
            for segment in segments:
                if segment in selected:
                    continue

                duration = min(segment['duration'], self.config.max_segment_duration)

                if duration < self.config.min_segment_duration:
                    continue

                if total_duration + duration <= target:
                    selected.append(segment)
                    total_duration += duration

                if total_duration >= target * 0.9:
                    break

        logger.info(f"Selected {len(selected)} segments totaling {total_duration:.1f}s (target: {target}s)")

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

        # First pass: select high-quality segments
        for segment in scored_segments:
            duration = min(segment['duration'], self.config.max_segment_duration)

            if duration < self.config.min_segment_duration:
                continue

            if total_duration + duration <= target:
                selected.append(segment)
                total_duration += duration

            if total_duration >= target * 0.95:
                break

        # Second pass: if we didn't hit target, be more lenient
        if total_duration < target * 0.7 and len(selected) < len(scored_segments):
            logger.warning(f"After diversity scoring: Only {total_duration:.1f}s of {target}s. Adding more...")

            for segment in scored_segments:
                if segment in selected:
                    continue

                duration = min(segment['duration'], self.config.max_segment_duration)

                if duration < self.config.min_segment_duration:
                    continue

                if total_duration + duration <= target:
                    selected.append(segment)
                    total_duration += duration

                if total_duration >= target * 0.9:
                    break

        logger.info(f"Final selection: {len(selected)} segments totaling {total_duration:.1f}s")

        # Sort by time order
        selected.sort(key=lambda x: x['start'])

        return selected

    def _check_audio_stream(self, video_path: str) -> bool:
        """Check if video has audio stream using ffprobe"""
        try:
            cmd = [
                'ffprobe', '-v', 'quiet',
                '-print_format', 'json',
                '-show_streams',
                video_path
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=30)
            data = json.loads(result.stdout)

            has_audio = any(s.get('codec_type') == 'audio' for s in data.get('streams', []))
            logger.info(f"Audio stream {'found' if has_audio else 'not found'} in {video_path}")
            return has_audio

        except Exception as e:
            logger.warning(f"Could not check audio stream: {e}, assuming no audio")
            return False

    def _build_filter_complex_with_audio(self, segments: List[Dict]) -> str:
        """Build FFmpeg filter_complex for segments with audio"""
        filter_parts = []

        for i, segment in enumerate(segments):
            start = segment['start']
            duration = min(
                segment['end'] - segment['start'],
                self.config.max_segment_duration
            )

            # Video trim
            filter_parts.append(
                f"[0:v]trim=start={start}:duration={duration},setpts=PTS-STARTPTS[v{i}]"
            )

            # Audio trim
            filter_parts.append(
                f"[0:a]atrim=start={start}:duration={duration},asetpts=PTS-STARTPTS[a{i}]"
            )

        # Concatenate video streams
        video_inputs = ''.join(f"[v{i}]" for i in range(len(segments)))
        video_concat = f"{video_inputs}concat=n={len(segments)}:v=1:a=0[outv]"

        # Concatenate audio streams
        audio_inputs = ''.join(f"[a{i}]" for i in range(len(segments)))
        audio_concat = f"{audio_inputs}concat=n={len(segments)}:v=0:a=1[outa]"

        # Combine
        filter_complex = ';'.join(filter_parts) + ';' + video_concat + ';' + audio_concat

        return filter_complex

    def _build_filter_complex_video_only(self, segments: List[Dict]) -> str:
        """Build FFmpeg filter_complex for video-only segments"""
        filter_parts = []

        for i, segment in enumerate(segments):
            start = segment['start']
            duration = min(
                segment['end'] - segment['start'],
                self.config.max_segment_duration
            )

            filter_parts.append(
                f"[0:v]trim=start={start}:duration={duration},setpts=PTS-STARTPTS[v{i}]"
            )

        # Concatenate
        video_inputs = ''.join(f"[v{i}]" for i in range(len(segments)))
        video_concat = f"{video_inputs}concat=n={len(segments)}:v=1:a=0[outv]"

        filter_complex = ';'.join(filter_parts) + ';' + video_concat

        return filter_complex

    def _run_ffmpeg(self, cmd: List[str]):
        """Execute FFmpeg command with error handling"""
        try:
            # Log the full command for debugging
            cmd_str = ' '.join(cmd)
            logger.info(f"Running FFmpeg command: {cmd_str}")

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
                timeout=600  # 10 min timeout
            )

            logger.info("FFmpeg completed successfully")
            if result.stdout:
                logger.debug(f"FFmpeg stdout: {result.stdout}")
            if result.stderr:
                logger.info(f"FFmpeg stderr: {result.stderr}")

        except subprocess.CalledProcessError as e:
            logger.error(f"FFmpeg failed: {e.stderr}")
            raise RuntimeError(f"Video composition failed: {e.stderr}")

        except subprocess.TimeoutExpired:
            logger.error("FFmpeg timeout after 10 minutes")
            raise RuntimeError("Video composition timeout")

        except Exception as e:
            logger.error(f"FFmpeg error: {e}")
            raise RuntimeError(f"Video composition error: {e}")

    def _create_output_video(self, input_path: str, segments: List[Dict], output_path: str):
        """Create output video WITH AUDIO using FFmpeg"""

        if not segments:
            raise ValueError("No segments to process")

        # Check if input has audio
        has_audio = self._check_audio_stream(input_path)
        logger.info(f"Audio stream detection result: has_audio={has_audio}")

        # Build filter_complex command
        if has_audio:
            logger.info("Building filter with audio preservation...")
            filter_complex = self._build_filter_complex_with_audio(segments)
            output_map = ['-map', '[outv]', '-map', '[outa]']
            logger.info(f"Using audio preservation mode with {len(segments)} segments")
        else:
            logger.info("Building filter for video-only...")
            filter_complex = self._build_filter_complex_video_only(segments)
            output_map = ['-map', '[outv]']
            logger.info(f"Using video-only mode with {len(segments)} segments")

        # Execute FFmpeg
        cmd = [
            'ffmpeg',
            '-i', input_path,
            '-filter_complex', filter_complex,
            *output_map,
            '-c:v', 'libx264',
            '-preset', 'medium',  # Balance speed/quality
            '-crf', '23',         # Quality (18-28, lower=better)
            '-c:a', 'aac',
            '-b:a', '192k',       # Audio bitrate
            '-y',                 # Overwrite output
            output_path
        ]

        self._run_ffmpeg(cmd)

        logger.info(f"Output video created with audio: {output_path}")