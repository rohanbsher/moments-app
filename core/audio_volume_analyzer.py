"""
Audio Volume Analyzer
Detects volume spikes, loud moments, and audio excitement for highlight selection
Uses librosa for advanced audio analysis
"""

import numpy as np
import logging
from typing import Dict, List, Tuple, Optional
import tempfile
import os

logger = logging.getLogger(__name__)

class AudioVolumeAnalyzer:
    """
    Analyzes audio for volume-based features to identify exciting moments
    """

    def __init__(self, sample_rate: int = 22050):
        """
        Initialize AudioVolumeAnalyzer

        Args:
            sample_rate: Target sample rate for audio processing
        """
        self.sample_rate = sample_rate

        # Try to import librosa
        try:
            import librosa
            self.librosa = librosa
            self.librosa_available = True
            logger.info("Librosa available - using advanced audio analysis")
        except ImportError:
            self.librosa = None
            self.librosa_available = False
            logger.warning("Librosa not available - using basic audio analysis")

    def analyze_segment(self, video_path: str, start_time: float, end_time: float) -> Dict:
        """
        Analyze audio volume features for a video segment

        Args:
            video_path: Path to video file
            start_time: Segment start time in seconds
            end_time: Segment end time in seconds

        Returns:
            Dictionary with audio volume features
        """
        # Always use NumPy-based analysis for compatibility
        # Librosa has architecture issues with soxr dependency
        return self._analyze_with_numpy(video_path, start_time, end_time)

    def _analyze_with_numpy(self, video_path: str, start_time: float, end_time: float) -> Dict:
        """
        Pure NumPy-based audio analysis (no librosa dependencies)

        This method provides similar functionality to librosa but using only NumPy,
        avoiding architecture issues with native binary dependencies like soxr.

        Features extracted:
        - RMS energy (overall loudness)
        - Peak detection (sudden loud moments)
        - Simple onset detection (audio events)
        - Energy-based spectral flux
        - Zero crossing rate
        """
        try:
            # Extract audio segment using ffmpeg (proven working)
            audio_data = self._extract_audio_segment(video_path, start_time, end_time)

            if audio_data is None or len(audio_data) == 0:
                return self._empty_analysis()

            y = audio_data
            sr = self.sample_rate

            # 1. RMS Energy Calculation (frame-based)
            frame_length = 2048
            hop_length = 512

            # Calculate RMS for each frame
            rms_frames = []
            for i in range(0, len(y) - frame_length, hop_length):
                frame = y[i:i + frame_length]
                rms = np.sqrt(np.mean(frame ** 2))
                rms_frames.append(rms)

            rms = np.array(rms_frames)

            if len(rms) == 0:
                return self._empty_analysis()

            # 2. Simple Onset Detection (peaks in RMS energy)
            # Find frames with significantly higher energy than neighbors
            onset_threshold = np.percentile(rms, 75)
            onset_frames = []

            for i in range(1, len(rms) - 1):
                # Peak if higher than both neighbors and above threshold
                if rms[i] > onset_threshold and rms[i] > rms[i-1] and rms[i] > rms[i+1]:
                    onset_frames.append(i)

            # Convert frame indices to time
            onset_times = [frame_idx * hop_length / sr for frame_idx in onset_frames]

            # 3. Energy-based Spectral Flux (rate of change in energy)
            spectral_flux = np.abs(np.diff(rms))
            if len(spectral_flux) == 0:
                spectral_flux = np.array([0.0])

            # 4. Zero Crossing Rate (simple version)
            # Count sign changes in audio signal
            zcr_frames = []
            for i in range(0, len(y) - frame_length, hop_length):
                frame = y[i:i + frame_length]
                # Count zero crossings
                zero_crossings = np.sum(np.abs(np.diff(np.sign(frame)))) / 2
                zcr = zero_crossings / frame_length
                zcr_frames.append(zcr)

            zcr = np.array(zcr_frames)

            # Calculate statistics
            rms_mean = float(np.mean(rms))
            rms_max = float(np.max(rms))
            rms_std = float(np.std(rms))
            rms_min = float(np.min(rms))

            # Identify volume spikes (above 75th percentile)
            spike_threshold = np.percentile(rms, 75)
            spike_frames = np.where(rms > spike_threshold)[0]

            # Calculate excitement score
            excitement_score = self._calculate_excitement_score(
                rms_mean, rms_max, rms_std,
                len(onset_frames), len(spike_frames),
                float(np.mean(spectral_flux))
            )

            # Silence detection
            silence_threshold = 0.01
            silence_frames = np.sum(rms < silence_threshold)
            silence_ratio = float(silence_frames / len(rms)) if len(rms) > 0 else 1.0

            return {
                'volume_mean': rms_mean,
                'volume_peak': rms_max,
                'volume_std': rms_std,
                'num_onsets': len(onset_frames),
                'onset_times': onset_times,
                'num_spikes': len(spike_frames),
                'spike_ratio': float(len(spike_frames) / len(rms)) if len(rms) > 0 else 0.0,
                'excitement_level': excitement_score,
                'silence_ratio': silence_ratio,
                'has_loud_moments': rms_max > 0.3,
                'has_frequent_events': len(onset_frames) > 3,
                'audio_dynamic_range': float(rms_max - rms_min),
                'spectral_flux_mean': float(np.mean(spectral_flux)),
                'zero_crossing_rate': float(np.mean(zcr)) if len(zcr) > 0 else 0.0
            }

        except Exception as e:
            logger.error(f"NumPy audio analysis failed: {e}")
            return self._empty_analysis()

    def _analyze_with_librosa(self, video_path: str, start_time: float, end_time: float) -> Dict:
        """
        Advanced audio analysis using librosa

        Features extracted:
        - RMS energy (overall loudness)
        - Peak detection (sudden loud moments)
        - Onset strength (audio events)
        - Spectral flux (audio changes)
        """
        try:
            # Extract audio segment
            audio_data = self._extract_audio_segment(video_path, start_time, end_time)

            if audio_data is None or len(audio_data) == 0:
                return self._empty_analysis()

            y = audio_data
            sr = self.sample_rate

            # 1. RMS Energy (overall loudness)
            rms = self.librosa.feature.rms(
                y=y,
                frame_length=1024,
                hop_length=256
            )[0]

            # 2. Onset Detection (sudden audio events like applause, cheers)
            onset_env = self.librosa.onset.onset_strength(
                y=y,
                sr=sr,
                hop_length=256
            )

            onset_frames = self.librosa.onset.onset_detect(
                onset_envelope=onset_env,
                sr=sr,
                hop_length=256,
                backtrack=True
            )

            onset_times = self.librosa.frames_to_time(
                onset_frames,
                sr=sr,
                hop_length=256
            )

            # 3. Spectral Flux (measure of audio change)
            spectral_flux = onset_env

            # 4. Zero Crossing Rate (useful for detecting speech vs noise)
            zcr = self.librosa.feature.zero_crossing_rate(y, hop_length=256)[0]

            # Calculate statistics
            rms_mean = float(np.mean(rms))
            rms_max = float(np.max(rms))
            rms_std = float(np.std(rms))

            # Identify volume spikes (above 75th percentile)
            spike_threshold = np.percentile(rms, 75)
            spike_frames = np.where(rms > spike_threshold)[0]
            spike_times = self.librosa.frames_to_time(spike_frames, sr=sr, hop_length=256)

            # Calculate excitement score (0-1)
            # Based on volume, onsets, and spectral change
            excitement_score = self._calculate_excitement_score(
                rms_mean, rms_max, rms_std,
                len(onset_frames), len(spike_frames),
                np.mean(spectral_flux)
            )

            # Silence detection
            silence_threshold = 0.01
            silence_frames = np.sum(rms < silence_threshold)
            silence_ratio = float(silence_frames / len(rms)) if len(rms) > 0 else 1.0

            return {
                'volume_mean': rms_mean,
                'volume_peak': rms_max,
                'volume_std': rms_std,
                'num_onsets': len(onset_frames),
                'onset_times': onset_times.tolist(),
                'num_spikes': len(spike_frames),
                'spike_ratio': float(len(spike_frames) / len(rms)) if len(rms) > 0 else 0.0,
                'excitement_level': excitement_score,
                'silence_ratio': silence_ratio,
                'has_loud_moments': rms_max > 0.3,
                'has_frequent_events': len(onset_frames) > 3,
                'audio_dynamic_range': float(rms_max - np.min(rms)),
                'spectral_flux_mean': float(np.mean(spectral_flux)),
                'zero_crossing_rate': float(np.mean(zcr))
            }

        except Exception as e:
            logger.error(f"Librosa audio analysis failed: {e}")
            return self._analyze_basic(video_path, start_time, end_time)

    def _analyze_basic(self, video_path: str, start_time: float, end_time: float) -> Dict:
        """
        Basic audio analysis without librosa (fallback)
        Uses moviepy for audio extraction
        """
        try:
            from moviepy.editor import VideoFileClip

            # Extract audio segment
            video = VideoFileClip(video_path).subclip(start_time, end_time)

            if video.audio is None:
                return self._empty_analysis()

            # Get audio array
            audio_array = video.audio.to_soundarray(fps=self.sample_rate)

            # Convert to mono if stereo
            if len(audio_array.shape) > 1:
                audio_array = np.mean(audio_array, axis=1)

            video.close()

            # Basic RMS calculation
            rms = np.sqrt(np.mean(audio_array**2))
            peak = np.max(np.abs(audio_array))

            # Simple spike detection
            threshold = np.percentile(np.abs(audio_array), 75)
            spikes = np.sum(np.abs(audio_array) > threshold)
            spike_ratio = float(spikes / len(audio_array)) if len(audio_array) > 0 else 0.0

            # Silence detection
            silence_threshold = 0.01
            silence_ratio = float(np.sum(np.abs(audio_array) < silence_threshold) / len(audio_array))

            # Basic excitement score
            excitement = min(1.0, rms * 5 + spike_ratio * 0.5)

            return {
                'volume_mean': float(rms),
                'volume_peak': float(peak),
                'volume_std': float(np.std(audio_array)),
                'num_onsets': 0,  # Not available
                'onset_times': [],
                'num_spikes': int(spikes),
                'spike_ratio': spike_ratio,
                'excitement_level': float(excitement),
                'silence_ratio': silence_ratio,
                'has_loud_moments': peak > 0.3,
                'has_frequent_events': spike_ratio > 0.2,
                'audio_dynamic_range': float(peak - np.min(np.abs(audio_array))),
                'spectral_flux_mean': 0.0,  # Not available
                'zero_crossing_rate': 0.0   # Not available
            }

        except Exception as e:
            logger.error(f"Basic audio analysis failed: {e}")
            return self._empty_analysis()

    def _extract_audio_segment(self, video_path: str, start_time: float, end_time: float) -> Optional[np.ndarray]:
        """
        Extract audio segment from video using multiple methods with fallbacks

        Priority:
        1. Direct librosa load from video (if supported)
        2. FFmpeg extraction to temp file
        3. MoviePy extraction (fallback)

        Args:
            video_path: Path to video file
            start_time: Start time in seconds
            end_time: End time in seconds

        Returns:
            Audio array or None if extraction fails
        """

        # Method 1: Try direct librosa load with offset/duration
        if self.librosa_available:
            try:
                duration = end_time - start_time
                y, sr = self.librosa.load(
                    video_path,
                    sr=self.sample_rate,
                    offset=start_time,
                    duration=duration
                )
                logger.debug(f"Audio extracted using librosa direct load")
                return y
            except Exception as e:
                logger.debug(f"Librosa direct load failed: {e}, trying ffmpeg")

        # Method 2: Try ffmpeg extraction
        try:
            return self._extract_audio_ffmpeg(video_path, start_time, end_time)
        except Exception as e:
            logger.debug(f"FFmpeg extraction failed: {e}, trying moviepy")

        # Method 3: Fallback to moviepy (original method)
        try:
            return self._extract_audio_moviepy(video_path, start_time, end_time)
        except Exception as e:
            logger.error(f"All audio extraction methods failed: {e}")
            return None

    def _extract_audio_ffmpeg(self, video_path: str, start_time: float, end_time: float) -> Optional[np.ndarray]:
        """
        Extract audio using ffmpeg directly

        Args:
            video_path: Path to video file
            start_time: Start time in seconds
            end_time: End time in seconds

        Returns:
            Audio array or None if extraction fails
        """
        import subprocess

        # Create temporary WAV file
        temp_audio = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
        temp_path = temp_audio.name
        temp_audio.close()

        try:
            duration = end_time - start_time

            # FFmpeg command to extract audio segment
            command = [
                'ffmpeg',
                '-i', video_path,
                '-ss', str(start_time),
                '-t', str(duration),
                '-vn',  # No video
                '-acodec', 'pcm_s16le',  # PCM 16-bit little-endian
                '-ar', str(self.sample_rate),  # Sample rate
                '-ac', '1',  # Mono
                '-y',  # Overwrite output file
                temp_path
            ]

            # Run ffmpeg
            result = subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=30
            )

            if result.returncode != 0:
                logger.debug(f"FFmpeg returned error code {result.returncode}")
                os.unlink(temp_path)
                return None

            # Load the extracted audio with basic WAV loading
            # (Avoiding librosa.load due to potential soxr architecture issues)
            import wave
            with wave.open(temp_path, 'rb') as wav_file:
                frames = wav_file.readframes(wav_file.getnframes())
                y = np.frombuffer(frames, dtype=np.int16).astype(np.float32) / 32768.0

            # Clean up
            os.unlink(temp_path)

            logger.debug(f"Audio extracted using ffmpeg")
            return y

        except subprocess.TimeoutExpired:
            logger.error("FFmpeg extraction timed out")
            if os.path.exists(temp_path):
                os.unlink(temp_path)
            return None
        except Exception as e:
            logger.error(f"FFmpeg extraction failed: {e}")
            if os.path.exists(temp_path):
                os.unlink(temp_path)
            return None

    def _extract_audio_moviepy(self, video_path: str, start_time: float, end_time: float) -> Optional[np.ndarray]:
        """
        Extract audio using moviepy (fallback method)

        Args:
            video_path: Path to video file
            start_time: Start time in seconds
            end_time: End time in seconds

        Returns:
            Audio array or None if extraction fails
        """
        try:
            from moviepy.editor import VideoFileClip

            video = VideoFileClip(video_path).subclip(start_time, end_time)

            if video.audio is None:
                logger.debug("Video has no audio track")
                return None

            # Save to temporary WAV file
            temp_audio = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
            temp_path = temp_audio.name
            temp_audio.close()

            video.audio.write_audiofile(
                temp_path,
                fps=self.sample_rate,
                logger=None,
                verbose=False
            )

            video.close()

            # Load with librosa
            if self.librosa_available:
                y, sr = self.librosa.load(temp_path, sr=self.sample_rate)
            else:
                # Basic load
                import wave
                with wave.open(temp_path, 'rb') as wav_file:
                    frames = wav_file.readframes(wav_file.getnframes())
                    y = np.frombuffer(frames, dtype=np.int16).astype(np.float32) / 32768.0

            # Clean up
            os.unlink(temp_path)

            logger.debug(f"Audio extracted using moviepy")
            return y

        except Exception as e:
            logger.error(f"MoviePy audio extraction failed: {e}")
            return None

    def _calculate_excitement_score(
        self,
        rms_mean: float,
        rms_max: float,
        rms_std: float,
        num_onsets: int,
        num_spikes: int,
        spectral_flux: float
    ) -> float:
        """
        Calculate overall excitement score from audio features

        Score ranges from 0 (silent/boring) to 1 (very exciting)

        Components:
        - Volume level (30%)
        - Volume variability (20%)
        - Number of events/onsets (25%)
        - Volume spikes (15%)
        - Spectral change (10%)
        """
        # Normalize components to 0-1 range
        volume_score = min(1.0, rms_mean * 3)
        variability_score = min(1.0, rms_std * 5)
        onset_score = min(1.0, num_onsets / 10)
        spike_score = min(1.0, num_spikes / 20)
        flux_score = min(1.0, spectral_flux / 10)

        # Weighted combination
        excitement = (
            volume_score * 0.30 +
            variability_score * 0.20 +
            onset_score * 0.25 +
            spike_score * 0.15 +
            flux_score * 0.10
        )

        return float(excitement)

    def detect_exciting_moments(self, video_path: str, duration: float) -> List[Tuple[float, float]]:
        """
        Detect exciting audio moments in entire video

        Args:
            video_path: Path to video file
            duration: Total video duration in seconds

        Returns:
            List of (start_time, end_time) tuples for exciting moments
        """
        if not self.librosa_available:
            logger.warning("Librosa not available - cannot detect exciting moments")
            return []

        try:
            # Analyze in 5-second chunks
            chunk_duration = 5.0
            exciting_moments = []

            current_time = 0.0
            while current_time < duration:
                end_time = min(current_time + chunk_duration, duration)

                analysis = self.analyze_segment(video_path, current_time, end_time)

                # Mark as exciting if excitement level > 0.6
                if analysis['excitement_level'] > 0.6:
                    exciting_moments.append((current_time, end_time))

                current_time = end_time

            return exciting_moments

        except Exception as e:
            logger.error(f"Exciting moment detection failed: {e}")
            return []

    def _empty_analysis(self) -> Dict:
        """
        Return empty analysis structure when audio is unavailable
        """
        return {
            'volume_mean': 0.0,
            'volume_peak': 0.0,
            'volume_std': 0.0,
            'num_onsets': 0,
            'onset_times': [],
            'num_spikes': 0,
            'spike_ratio': 0.0,
            'excitement_level': 0.0,
            'silence_ratio': 1.0,
            'has_loud_moments': False,
            'has_frequent_events': False,
            'audio_dynamic_range': 0.0,
            'spectral_flux_mean': 0.0,
            'zero_crossing_rate': 0.0
        }
