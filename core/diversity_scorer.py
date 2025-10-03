"""
Scene Diversity Scorer
Prevents repetitive segments by measuring visual similarity
Uses perceptual hashing and histogram comparison
"""

import cv2
import numpy as np
import logging
from typing import List, Dict, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class FrameSample:
    """Represents a sampled frame from a video segment"""
    segment_index: int
    timestamp: float
    frame: np.ndarray


class DiversityScorer:
    """
    Measures visual diversity between video segments to avoid repetitive content
    """

    def __init__(self, similarity_threshold: float = 0.80):
        """
        Initialize DiversityScorer

        Args:
            similarity_threshold: Segments with similarity > this are considered similar (0-1)
        """
        self.similarity_threshold = similarity_threshold

        # Try to import imagehash for perceptual hashing
        try:
            import imagehash
            from PIL import Image
            self.imagehash = imagehash
            self.PIL_Image = Image
            self.perceptual_hash_available = True
            logger.info("Perceptual hashing available - using advanced similarity detection")
        except ImportError:
            self.imagehash = None
            self.PIL_Image = None
            self.perceptual_hash_available = False
            logger.warning("imagehash not available - using histogram-based similarity")

    def calculate_diversity_penalty(
        self,
        video_path: str,
        selected_segments: List[Dict]
    ) -> List[Dict]:
        """
        Calculate diversity penalty for selected segments

        Args:
            video_path: Path to video file
            selected_segments: List of segment dictionaries with 'start' and 'end' times

        Returns:
            Updated segments with 'diversity_penalty' field added
        """
        if len(selected_segments) <= 1:
            # No diversity issues with 0 or 1 segment
            for seg in selected_segments:
                seg['diversity_penalty'] = 0.0
            return selected_segments

        # Extract representative frames from each segment
        frame_samples = self._extract_representative_frames(video_path, selected_segments)

        # Calculate pairwise similarities
        similarities = self._calculate_pairwise_similarities(frame_samples)

        # Apply penalties based on similarities
        for i, segment in enumerate(selected_segments):
            penalty = self._calculate_segment_penalty(i, similarities)
            segment['diversity_penalty'] = penalty

            # Reduce score based on penalty
            if 'score' in segment:
                original_score = segment['score']
                segment['score'] = original_score * (1.0 - penalty)
                logger.debug(
                    f"Segment {i}: diversity penalty {penalty:.2f}, "
                    f"score {original_score:.3f} → {segment['score']:.3f}"
                )

        return selected_segments

    def ensure_diversity(
        self,
        video_path: str,
        candidate_segments: List[Dict],
        target_num_distinct: int = 3
    ) -> List[Dict]:
        """
        Ensure minimum number of visually distinct segments

        Args:
            video_path: Path to video file
            candidate_segments: List of candidate segments (sorted by score)
            target_num_distinct: Minimum number of distinct visual styles

        Returns:
            Filtered segments with diversity guaranteed
        """
        if len(candidate_segments) <= target_num_distinct:
            return candidate_segments

        # Extract frames
        frame_samples = self._extract_representative_frames(video_path, candidate_segments)

        # Select diverse segments
        selected_indices = [0]  # Always include highest-scored segment
        selected_frames = [frame_samples[0]]

        for i in range(1, len(candidate_segments)):
            # Check similarity to already selected segments
            is_distinct = True

            for selected_idx in selected_indices:
                similarity = self._compare_frames(
                    frame_samples[i].frame,
                    frame_samples[selected_idx].frame
                )

                if similarity > self.similarity_threshold:
                    is_distinct = False
                    break

            if is_distinct:
                selected_indices.append(i)
                selected_frames.append(frame_samples[i])

                if len(selected_indices) >= target_num_distinct:
                    # Check if we have enough distinct segments
                    break

        # Return only selected segments
        diverse_segments = [candidate_segments[i] for i in selected_indices]

        logger.info(
            f"Diversity filtering: {len(candidate_segments)} → "
            f"{len(diverse_segments)} distinct segments"
        )

        return diverse_segments

    def _extract_representative_frames(
        self,
        video_path: str,
        segments: List[Dict]
    ) -> List[FrameSample]:
        """
        Extract one representative frame from each segment

        Args:
            video_path: Path to video file
            segments: List of segments

        Returns:
            List of FrameSample objects
        """
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)

        frame_samples = []

        for i, segment in enumerate(segments):
            # Get middle frame of segment
            mid_time = (segment['start'] + segment['end']) / 2
            mid_frame = int(mid_time * fps)

            cap.set(cv2.CAP_PROP_POS_FRAMES, mid_frame)
            ret, frame = cap.read()

            if ret:
                # Resize for faster comparison
                frame_resized = cv2.resize(frame, (320, 240))

                frame_samples.append(FrameSample(
                    segment_index=i,
                    timestamp=mid_time,
                    frame=frame_resized
                ))

        cap.release()

        return frame_samples

    def _calculate_pairwise_similarities(
        self,
        frame_samples: List[FrameSample]
    ) -> np.ndarray:
        """
        Calculate similarity matrix for all frame pairs

        Args:
            frame_samples: List of FrameSample objects

        Returns:
            NxN similarity matrix (values 0-1, where 1 = identical)
        """
        n = len(frame_samples)
        similarities = np.zeros((n, n))

        for i in range(n):
            similarities[i, i] = 1.0  # Self-similarity is 1

            for j in range(i + 1, n):
                sim = self._compare_frames(
                    frame_samples[i].frame,
                    frame_samples[j].frame
                )

                similarities[i, j] = sim
                similarities[j, i] = sim

        return similarities

    def _compare_frames(self, frame1: np.ndarray, frame2: np.ndarray) -> float:
        """
        Compare two frames for visual similarity

        Args:
            frame1: First frame
            frame2: Second frame

        Returns:
            Similarity score (0-1, where 1 = identical)
        """
        if self.perceptual_hash_available:
            return self._compare_perceptual_hash(frame1, frame2)
        else:
            return self._compare_histogram(frame1, frame2)

    def _compare_perceptual_hash(self, frame1: np.ndarray, frame2: np.ndarray) -> float:
        """
        Compare frames using perceptual hashing (most accurate)

        Args:
            frame1: First frame (BGR format)
            frame2: Second frame (BGR format)

        Returns:
            Similarity score (0-1)
        """
        try:
            # Convert to PIL Images
            frame1_rgb = cv2.cvtColor(frame1, cv2.COLOR_BGR2RGB)
            frame2_rgb = cv2.cvtColor(frame2, cv2.COLOR_BGR2RGB)

            img1 = self.PIL_Image.fromarray(frame1_rgb)
            img2 = self.PIL_Image.fromarray(frame2_rgb)

            # Calculate perceptual hashes
            hash1 = self.imagehash.average_hash(img1, hash_size=8)
            hash2 = self.imagehash.average_hash(img2, hash_size=8)

            # Hash difference (0 = identical, 64 = completely different for 8x8 hash)
            hash_diff = hash1 - hash2

            # Convert to similarity (0-1)
            max_diff = 64  # Maximum possible difference for 8x8 hash
            similarity = 1.0 - (hash_diff / max_diff)

            return float(similarity)

        except Exception as e:
            logger.warning(f"Perceptual hash comparison failed: {e}, falling back to histogram")
            return self._compare_histogram(frame1, frame2)

    def _compare_histogram(self, frame1: np.ndarray, frame2: np.ndarray) -> float:
        """
        Compare frames using color histogram (fallback method)

        Args:
            frame1: First frame (BGR format)
            frame2: Second frame (BGR format)

        Returns:
            Similarity score (0-1)
        """
        try:
            # Calculate histograms for each channel
            hist1 = []
            hist2 = []

            for channel in range(3):
                h1 = cv2.calcHist([frame1], [channel], None, [32], [0, 256])
                h2 = cv2.calcHist([frame2], [channel], None, [32], [0, 256])

                # Normalize
                h1 = cv2.normalize(h1, h1, 0, 1, cv2.NORM_MINMAX)
                h2 = cv2.normalize(h2, h2, 0, 1, cv2.NORM_MINMAX)

                hist1.append(h1)
                hist2.append(h2)

            # Compare using correlation
            similarities = []
            for h1, h2 in zip(hist1, hist2):
                sim = cv2.compareHist(h1, h2, cv2.HISTCMP_CORREL)
                similarities.append(sim)

            # Average across channels
            avg_similarity = float(np.mean(similarities))

            # Correlation ranges from -1 to 1, normalize to 0-1
            normalized_similarity = (avg_similarity + 1) / 2

            return normalized_similarity

        except Exception as e:
            logger.error(f"Histogram comparison failed: {e}")
            return 0.5  # Neutral similarity on error

    def _calculate_segment_penalty(self, segment_idx: int, similarities: np.ndarray) -> float:
        """
        Calculate diversity penalty for a segment based on similarities to others

        Args:
            segment_idx: Index of the segment
            similarities: Similarity matrix

        Returns:
            Penalty value (0-1, where 0 = no penalty, 1 = maximum penalty)
        """
        # Get similarities to all other segments
        segment_similarities = similarities[segment_idx, :]

        # Remove self-similarity
        other_similarities = np.concatenate([
            segment_similarities[:segment_idx],
            segment_similarities[segment_idx + 1:]
        ])

        if len(other_similarities) == 0:
            return 0.0

        # Count how many segments are too similar
        num_similar = np.sum(other_similarities > self.similarity_threshold)

        # Maximum similarity to any other segment
        max_similarity = np.max(other_similarities)

        # Penalty increases with:
        # 1. Number of similar segments
        # 2. Degree of similarity
        count_penalty = min(1.0, num_similar / len(other_similarities))
        similarity_penalty = max(0.0, max_similarity - self.similarity_threshold) / (1.0 - self.similarity_threshold)

        # Combined penalty
        penalty = (count_penalty * 0.5 + similarity_penalty * 0.5)

        return float(penalty)

    def get_visual_diversity_score(
        self,
        video_path: str,
        segments: List[Dict]
    ) -> float:
        """
        Calculate overall visual diversity score for a set of segments

        Args:
            video_path: Path to video file
            segments: List of segments

        Returns:
            Diversity score (0-1, where 1 = very diverse, 0 = all identical)
        """
        if len(segments) <= 1:
            return 1.0  # Single segment is perfectly diverse

        # Extract frames
        frame_samples = self._extract_representative_frames(video_path, segments)

        # Calculate similarities
        similarities = self._calculate_pairwise_similarities(frame_samples)

        # Get upper triangle (excluding diagonal)
        n = len(similarities)
        upper_triangle_indices = np.triu_indices(n, k=1)
        pairwise_similarities = similarities[upper_triangle_indices]

        # Diversity is inverse of average similarity
        avg_similarity = np.mean(pairwise_similarities)
        diversity_score = 1.0 - avg_similarity

        return float(diversity_score)
