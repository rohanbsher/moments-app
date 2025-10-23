"""
AI-Powered Video Analysis
Intelligent moment detection using face detection, emotion recognition, and speech transcription
"""

import cv2
import numpy as np
import logging
import tempfile
import subprocess
import os
import ssl
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

# Fix SSL certificate verification issues for model downloads
try:
    ssl._create_default_https_context = ssl._create_unverified_context
except Exception:
    pass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class AIAnalysisResult:
    """Container for AI analysis results"""
    face_score: float = 0.0
    emotion_score: float = 0.0
    speech_score: float = 0.0
    has_faces: bool = False
    has_happy_faces: bool = False
    has_speech: bool = False
    transcription: str = ""
    metadata: Dict = None


class YuNetFaceDetector:
    """
    Fast face detection using OpenCV YuNet
    Ultra-fast: 1000 FPS on 320x320 images
    Model size: Only 233 KB
    """

    def __init__(self, model_path: str = None):
        """
        Initialize YuNet face detector

        Args:
            model_path: Path to YuNet ONNX model (auto-downloads if None)
        """
        if model_path is None:
            # Auto-download model
            model_path = self._download_model()

        self.model_path = model_path

        try:
            # Initialize detector
            self.detector = cv2.FaceDetectorYN.create(
                self.model_path,
                "",
                (320, 320),
                0.6,  # score_threshold
                0.3,  # nms_threshold
                5000  # top_k
            )
            logger.info("✅ YuNet face detector initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize YuNet: {e}")
            self.detector = None

    def _download_model(self) -> str:
        """Download YuNet model if not present"""
        import urllib.request

        model_dir = os.path.join(os.path.dirname(__file__), 'models')
        os.makedirs(model_dir, exist_ok=True)

        model_path = os.path.join(model_dir, 'yunet_2023mar.onnx')

        if os.path.exists(model_path):
            logger.info(f"Using existing YuNet model: {model_path}")
            return model_path

        # Download from OpenCV zoo
        model_url = "https://github.com/opencv/opencv_zoo/raw/main/models/face_detection_yunet/face_detection_yunet_2023mar.onnx"

        logger.info("Downloading YuNet model (233 KB)...")
        try:
            urllib.request.urlretrieve(model_url, model_path)
            logger.info(f"✅ Model downloaded: {model_path}")
        except Exception as e:
            logger.error(f"❌ Failed to download model: {e}")
            raise

        return model_path

    def detect_faces(self, frame: np.ndarray) -> List[np.ndarray]:
        """
        Detect faces in a frame

        Args:
            frame: BGR image from OpenCV

        Returns:
            List of face detections [x, y, w, h, conf, *landmarks]
        """
        if self.detector is None:
            return []

        try:
            h, w = frame.shape[:2]
            self.detector.setInputSize((w, h))

            _, faces = self.detector.detect(frame)
            return faces if faces is not None else []
        except Exception as e:
            logger.warning(f"Face detection failed: {e}")
            return []

    def process_video_segment(self, video_path: str, start_time: float, end_time: float) -> Dict:
        """
        Process video segment and detect faces

        Args:
            video_path: Path to video file
            start_time, end_time: Segment boundaries in seconds

        Returns:
            Dictionary with face detection statistics
        """
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)

        start_frame = int(start_time * fps)
        end_frame = int(end_time * fps)
        cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)

        face_detections = []

        # Sample every 5 frames for performance (still ~6 fps sampling)
        for frame_idx in range(start_frame, end_frame, 5):
            ret, frame = cap.read()
            if not ret:
                break

            faces = self.detect_faces(frame)
            face_detections.append({
                'frame': frame_idx,
                'timestamp': frame_idx / fps,
                'num_faces': len(faces),
                'faces': faces
            })

        cap.release()

        total_faces = sum(d['num_faces'] for d in face_detections)
        avg_faces = total_faces / len(face_detections) if face_detections else 0

        return {
            'num_frames_analyzed': len(face_detections),
            'total_faces': total_faces,
            'avg_faces_per_frame': avg_faces,
            'has_faces': total_faces > 0,
            'detections': face_detections
        }


class EmotionAnalyzer:
    """
    Emotion recognition using HSEmotion
    Speed: 20-50ms per face on CPU
    Emotions: Happiness, Surprise, Sadness, Anger, Fear, Disgust, Contempt, Neutral
    """

    def __init__(self, model_name: str = 'enet_b0_8_best_afew'):
        """
        Initialize emotion recognizer

        Args:
            model_name: HSEmotion model name
                - 'enet_b0_8_best_afew': EfficientNet-B0, 8 emotions (RECOMMENDED)
                - 'enet_b2_8': EfficientNet-B2, more accurate but slower
        """
        try:
            # Add safe globals for PyTorch 2.6+ compatibility
            import torch
            if hasattr(torch.serialization, 'add_safe_globals'):
                try:
                    import timm.models.efficientnet
                    import timm.layers.conv2d_same
                    import timm.layers.activations
                    import timm.layers.create_act
                    torch.serialization.add_safe_globals([
                        timm.models.efficientnet.EfficientNet,
                        timm.layers.conv2d_same.Conv2dSame,
                        timm.layers.activations.Swish
                    ])
                except Exception:
                    pass

            from hsemotion.facial_emotions import HSEmotionRecognizer
            self.recognizer = HSEmotionRecognizer(model_name=model_name)
            logger.info(f"✅ HSEmotion initialized with model: {model_name}")

            # Positive emotions for moment detection
            self.positive_emotions = {'Happiness', 'Surprise'}
            self.neutral_emotions = {'Neutral'}

        except Exception as e:
            logger.error(f"❌ Failed to initialize HSEmotion: {e}")
            self.recognizer = None

    def analyze_face(self, face_image: np.ndarray) -> Dict:
        """
        Analyze emotion in a face image

        Args:
            face_image: Cropped face image (BGR)

        Returns:
            Dictionary with emotion, confidence, and excitement_score
        """
        if self.recognizer is None:
            return self._empty_result()

        try:
            # HSEmotion expects RGB
            rgb_face = cv2.cvtColor(face_image, cv2.COLOR_BGR2RGB)

            # Get emotion prediction
            emotion, scores = self.recognizer.predict_emotions(rgb_face, logits=False)

            # Calculate excitement score (0.0 to 1.0)
            excitement_score = self._calculate_excitement(emotion, scores)

            return {
                'emotion': emotion,
                'confidence': scores[emotion],
                'all_scores': scores,
                'excitement_score': excitement_score,
                'is_positive': emotion in self.positive_emotions
            }
        except Exception as e:
            logger.warning(f"Emotion analysis failed: {e}")
            return self._empty_result()

    def _calculate_excitement(self, emotion: str, scores: Dict) -> float:
        """Calculate excitement score based on emotion probabilities"""
        # Weight positive emotions heavily
        excitement = (
            scores.get('Happiness', 0) * 1.0 +
            scores.get('Surprise', 0) * 0.8 +
            scores.get('Neutral', 0) * 0.1
        )
        return float(min(excitement, 1.0))

    def analyze_segment(self, video_path: str, start_time: float, end_time: float,
                       face_detections: List[Dict]) -> Dict:
        """
        Analyze emotions for faces detected in a video segment

        Args:
            video_path: Path to video
            start_time, end_time: Segment boundaries
            face_detections: List of face detections from YuNet

        Returns:
            Emotion statistics for the segment
        """
        if self.recognizer is None:
            return self._empty_segment_result()

        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)

        emotion_data = []
        positive_emotion_count = 0
        total_excitement = 0.0

        for detection in face_detections:
            frame_idx = detection['frame']
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
            ret, frame = cap.read()

            if not ret:
                continue

            # Process each face in the frame
            for face in detection['faces']:
                x, y, w, h = map(int, face[:4])

                # Add padding for better emotion detection
                padding = int(w * 0.2)
                x1 = max(0, x - padding)
                y1 = max(0, y - padding)
                x2 = min(frame.shape[1], x + w + padding)
                y2 = min(frame.shape[0], y + h + padding)

                face_img = frame[y1:y2, x1:x2]

                if face_img.size == 0:
                    continue

                # Analyze emotion
                result = self.analyze_face(face_img)
                emotion_data.append(result)

                if result['is_positive']:
                    positive_emotion_count += 1

                total_excitement += result['excitement_score']

        cap.release()

        # Calculate statistics
        num_faces = len(emotion_data)

        return {
            'num_faces_analyzed': num_faces,
            'positive_emotion_count': positive_emotion_count,
            'positive_emotion_ratio': positive_emotion_count / num_faces if num_faces > 0 else 0,
            'avg_excitement': total_excitement / num_faces if num_faces > 0 else 0,
            'has_happy_moments': positive_emotion_count > 0,
            'emotion_distribution': self._get_emotion_distribution(emotion_data)
        }

    def _get_emotion_distribution(self, emotion_data: List[Dict]) -> Dict:
        """Get distribution of emotions"""
        distribution = {}
        for result in emotion_data:
            emotion = result['emotion']
            distribution[emotion] = distribution.get(emotion, 0) + 1
        return distribution

    def _empty_result(self) -> Dict:
        """Return empty result when analysis fails"""
        return {
            'emotion': 'Unknown',
            'confidence': 0.0,
            'all_scores': {},
            'excitement_score': 0.0,
            'is_positive': False
        }

    def _empty_segment_result(self) -> Dict:
        """Return empty segment result"""
        return {
            'num_faces_analyzed': 0,
            'positive_emotion_count': 0,
            'positive_emotion_ratio': 0.0,
            'avg_excitement': 0.0,
            'has_happy_moments': False,
            'emotion_distribution': {}
        }


class AudioTranscriber:
    """
    Speech transcription using faster-whisper
    Speed: 16x real-time with base.en model on CPU
    Memory: ~280 MB (base.en), ~140 MB with INT8 quantization
    """

    def __init__(self, model_size: str = 'base.en', compute_type: str = 'int8'):
        """
        Initialize Whisper transcriber with faster-whisper

        Args:
            model_size: 'tiny.en', 'base.en', 'small.en', 'medium.en'
            compute_type: 'int8' (fast, 50% smaller), 'float16', 'float32'
        """
        try:
            from faster_whisper import WhisperModel

            # For M1/M2 Macs, use CPU with optimal settings
            self.model = WhisperModel(
                model_size,
                device='cpu',
                compute_type=compute_type,
                cpu_threads=4,  # Optimize for M-series
                num_workers=1
            )
            logger.info(f"✅ Whisper initialized: {model_size} ({compute_type})")

            # Keywords that indicate exciting moments
            self.excitement_keywords = {
                'yes', 'yeah', 'wow', 'amazing', 'awesome', 'goal',
                'beautiful', 'love', 'happy', 'birthday', 'congratulations',
                'surprise', 'yay', 'woohoo', 'nice', 'incredible', 'perfect',
                'fantastic', 'excellent', 'wonderful', 'spectacular', 'outstanding'
            }

        except Exception as e:
            logger.error(f"❌ Failed to initialize Whisper: {e}")
            self.model = None

    def transcribe_segment(self, video_path: str, start_time: float, end_time: float) -> Dict:
        """
        Transcribe audio from video segment

        Args:
            video_path: Path to video
            start_time, end_time: Segment boundaries in seconds

        Returns:
            Dictionary with transcription and excitement analysis
        """
        if self.model is None:
            return self._empty_result()

        # Extract audio segment using ffmpeg
        audio_path = self._extract_audio_segment(video_path, start_time, end_time)

        if audio_path is None:
            return self._empty_result()

        try:
            # Transcribe with faster-whisper
            segments, info = self.model.transcribe(
                audio_path,
                language='en',
                vad_filter=True,  # Voice Activity Detection
                vad_parameters=dict(min_silence_duration_ms=500)
            )

            # Collect transcription
            full_text = []
            word_timestamps = []

            for segment in segments:
                full_text.append(segment.text)
                word_timestamps.append({
                    'start': segment.start,
                    'end': segment.end,
                    'text': segment.text
                })

            text = ' '.join(full_text).strip()

            # Analyze for excitement
            excitement_analysis = self._analyze_excitement(text, word_timestamps)

            return {
                'text': text,
                'language': info.language,
                'language_probability': info.language_probability,
                'segments': word_timestamps,
                'has_speech': len(text) > 0,
                'excitement_score': excitement_analysis['score'],
                'keywords_found': excitement_analysis['keywords'],
                'num_words': len(text.split())
            }

        except Exception as e:
            logger.warning(f"Transcription failed: {e}")
            return self._empty_result()
        finally:
            # Clean up temp audio file
            if audio_path and os.path.exists(audio_path):
                os.remove(audio_path)

    def _extract_audio_segment(self, video_path: str, start_time: float, end_time: float) -> Optional[str]:
        """Extract audio segment to temporary WAV file"""
        duration = end_time - start_time

        # Create temp file
        temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
        temp_path = temp_file.name
        temp_file.close()

        try:
            # Extract audio with ffmpeg
            cmd = [
                'ffmpeg',
                '-i', video_path,
                '-ss', str(start_time),
                '-t', str(duration),
                '-vn',  # No video
                '-acodec', 'pcm_s16le',  # WAV format
                '-ar', '16000',  # 16kHz sample rate (Whisper optimal)
                '-ac', '1',  # Mono
                '-y',  # Overwrite
                temp_path
            ]

            result = subprocess.run(cmd, capture_output=True, check=True, timeout=30)
            return temp_path

        except subprocess.TimeoutExpired:
            logger.error("Audio extraction timed out")
            if os.path.exists(temp_path):
                os.remove(temp_path)
            return None
        except Exception as e:
            logger.warning(f"Audio extraction failed: {e}")
            if os.path.exists(temp_path):
                os.remove(temp_path)
            return None

    def _analyze_excitement(self, text: str, segments: List[Dict]) -> Dict:
        """Analyze transcription for exciting keywords"""
        text_lower = text.lower()
        words = text_lower.split()

        # Find matching keywords
        keywords_found = [w for w in words if w in self.excitement_keywords]

        # Calculate excitement score
        keyword_score = min(len(keywords_found) * 0.3, 1.0)

        # Check for exclamation marks (enthusiasm)
        exclamation_score = min(text.count('!') * 0.2, 0.5)

        # Check for laughter transcriptions
        laughter_keywords = ['laugh', 'haha', 'hehe', 'lol']
        has_laughter = any(word in text_lower for word in laughter_keywords)
        laughter_score = 0.3 if has_laughter else 0

        # Check for intensity words (very, really, so, super)
        intensity_words = ['very', 'really', 'so', 'super', 'extremely', 'totally']
        has_intensity = any(word in text_lower for word in intensity_words)
        intensity_score = 0.2 if has_intensity else 0

        total_score = min(keyword_score + exclamation_score + laughter_score + intensity_score, 1.0)

        return {
            'score': total_score,
            'keywords': keywords_found,
            'has_laughter': has_laughter,
            'has_intensity': has_intensity
        }

    def _empty_result(self) -> Dict:
        """Return empty result when transcription fails"""
        return {
            'text': '',
            'language': 'en',
            'language_probability': 0.0,
            'segments': [],
            'has_speech': False,
            'excitement_score': 0.0,
            'keywords_found': [],
            'num_words': 0
        }


class AIVideoAnalyzer:
    """
    Unified AI analyzer combining face detection, emotion recognition, and speech transcription
    """

    def __init__(self):
        """Initialize all AI components"""
        logger.info("Initializing AI Video Analyzer...")

        self.face_detector = YuNetFaceDetector()
        self.emotion_analyzer = EmotionAnalyzer()
        self.transcriber = AudioTranscriber(model_size='base.en', compute_type='int8')

        logger.info("✅ AI Video Analyzer ready")

    def analyze_segment(self, video_path: str, start_time: float, end_time: float) -> AIAnalysisResult:
        """
        Comprehensive AI analysis of a video segment

        Args:
            video_path: Path to video file
            start_time, end_time: Segment boundaries in seconds

        Returns:
            AIAnalysisResult with all AI scores and metadata
        """
        # Face detection
        face_data = self.face_detector.process_video_segment(video_path, start_time, end_time)

        # Emotion recognition (only if faces detected)
        emotion_data = {'avg_excitement': 0, 'has_happy_moments': False, 'positive_emotion_ratio': 0}
        if face_data['total_faces'] > 0:
            emotion_data = self.emotion_analyzer.analyze_segment(
                video_path, start_time, end_time, face_data['detections']
            )

        # Speech transcription (only if segment is long enough)
        speech_data = {'excitement_score': 0, 'has_speech': False, 'text': ''}
        if end_time - start_time >= 2.0:
            try:
                speech_data = self.transcriber.transcribe_segment(video_path, start_time, end_time)
            except Exception as e:
                logger.warning(f"Transcription failed for segment {start_time}-{end_time}: {e}")

        # Calculate normalized scores
        face_score = min(face_data['avg_faces_per_frame'] / 3.0, 1.0)  # 3+ faces = 1.0
        emotion_score = emotion_data['avg_excitement']
        speech_score = speech_data['excitement_score']

        return AIAnalysisResult(
            face_score=face_score,
            emotion_score=emotion_score,
            speech_score=speech_score,
            has_faces=face_data['has_faces'],
            has_happy_faces=emotion_data['has_happy_moments'],
            has_speech=speech_data['has_speech'],
            transcription=speech_data['text'],
            metadata={
                'faces': face_data,
                'emotions': emotion_data,
                'speech': speech_data
            }
        )
