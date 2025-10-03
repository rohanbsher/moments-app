import numpy as np
import whisper
from moviepy.editor import VideoFileClip
from typing import Dict, List, Tuple
import tempfile
import os
import logging

logger = logging.getLogger(__name__)

class AudioAnalyzer:
    def __init__(self, whisper_model: str = "base"):
        try:
            self.whisper_model = whisper.load_model(whisper_model)
        except Exception as e:
            logger.warning(f"Failed to load Whisper model: {e}. Speech detection disabled.")
            self.whisper_model = None

    def analyze_segment(self, video_path: str,
                       start_time: float,
                       end_time: float) -> Dict:
        """Comprehensive audio analysis of video segment"""

        audio_data = self._extract_audio_segment(video_path, start_time, end_time)

        if audio_data is None:
            return self._empty_analysis()

        analysis = {
            'has_speech': False,
            'speech_segments': [],
            'transcript': "",
            'volume_mean': 0,
            'volume_peak': 0,
            'has_music': False,
            'excitement_level': 0,
            'silence_ratio': 1.0
        }

        if self.whisper_model and audio_data.get('path'):
            speech_analysis = self._analyze_speech(audio_data['path'])
            analysis.update(speech_analysis)

        if 'signal' in audio_data:
            y = audio_data['signal']

            analysis['volume_mean'] = float(np.mean(np.abs(y)))
            analysis['volume_peak'] = float(np.max(np.abs(y)))
            analysis['silence_ratio'] = self._calculate_silence_ratio(y)
            analysis['has_music'] = self._detect_music(y)
            analysis['excitement_level'] = self._calculate_excitement(y)

        if audio_data.get('path') and os.path.exists(audio_data['path']):
            os.remove(audio_data['path'])

        return analysis

    def _extract_audio_segment(self, video_path: str,
                              start_time: float,
                              end_time: float) -> Dict:
        """Extract audio segment from video"""
        try:
            video = VideoFileClip(video_path).subclip(start_time, end_time)

            if video.audio is None:
                return None

            temp_audio = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
            video.audio.write_audiofile(temp_audio.name, logger=None, verbose=False)

            with open(temp_audio.name, 'rb') as f:
                audio_bytes = f.read()

            audio_array = np.frombuffer(audio_bytes[44:], dtype=np.int16).astype(np.float32) / 32768.0

            return {
                'path': temp_audio.name,
                'signal': audio_array,
                'sample_rate': 44100
            }

        except Exception as e:
            logger.error(f"Audio extraction failed: {e}")
            return None

    def _analyze_speech(self, audio_path: str) -> Dict:
        """Detect and transcribe speech"""
        try:
            result = self.whisper_model.transcribe(
                audio_path,
                language='en',
                fp16=False
            )

            has_speech = len(result['text'].strip()) > 0

            return {
                'has_speech': has_speech,
                'transcript': result['text'],
                'speech_segments': result.get('segments', [])
            }

        except Exception as e:
            logger.error(f"Speech analysis failed: {e}")
            return {'has_speech': False, 'transcript': '', 'speech_segments': []}

    def _calculate_silence_ratio(self, y: np.ndarray, threshold: float = 0.01) -> float:
        """Calculate ratio of silence in audio"""
        silence_samples = np.sum(np.abs(y) < threshold)
        return float(silence_samples / len(y)) if len(y) > 0 else 1.0

    def _detect_music(self, y: np.ndarray) -> bool:
        """Simple music detection using spectral features"""
        try:
            fft = np.fft.rfft(y)
            magnitude = np.abs(fft)

            low_freq_energy = np.sum(magnitude[:len(magnitude)//4])
            high_freq_energy = np.sum(magnitude[len(magnitude)//4:])

            ratio = low_freq_energy / (high_freq_energy + 1e-10)

            return ratio > 2.0

        except Exception as e:
            logger.error(f"Music detection failed: {e}")
            return False

    def _calculate_excitement(self, y: np.ndarray) -> float:
        """Calculate excitement level from audio features"""
        try:
            energy = np.mean(y**2)
            energy_variance = np.var(y**2)

            excitement = min(1.0, (energy * 10 + energy_variance * 100))

            return float(excitement)

        except Exception as e:
            logger.error(f"Excitement calculation failed: {e}")
            return 0.0

    def _empty_analysis(self) -> Dict:
        """Return empty analysis structure"""
        return {
            'has_speech': False,
            'speech_segments': [],
            'transcript': "",
            'volume_mean': 0,
            'volume_peak': 0,
            'has_music': False,
            'excitement_level': 0,
            'silence_ratio': 1.0
        }