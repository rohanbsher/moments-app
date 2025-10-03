import numpy as np
from typing import List, Dict, Tuple
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class Segment:
    start_time: float
    end_time: float
    scene_score: float
    motion_data: Dict
    audio_data: Dict
    quality_score: float = 0.5

    @property
    def duration(self):
        return self.end_time - self.start_time

    @property
    def position_ratio(self):
        """Position in video (0=beginning, 1=end)"""
        return getattr(self, '_position_ratio', 0.5)

class HighlightRanker:
    def __init__(self):
        self.weights = {
            'motion': 0.30,
            'audio': 0.25,
            'quality': 0.20,
            'position': 0.15,
            'duration': 0.10
        }

    def rank_segments(self, segments: List[Segment],
                      video_duration: float) -> List[Tuple[Segment, float]]:
        """Rank segments by importance"""

        for segment in segments:
            segment._position_ratio = segment.start_time / video_duration if video_duration > 0 else 0

        scored_segments = []
        for segment in segments:
            score = self._calculate_segment_score(segment)
            scored_segments.append((segment, score))

        scored_segments = self._apply_context_rules(scored_segments)
        scored_segments.sort(key=lambda x: x[1], reverse=True)

        return scored_segments

    def _calculate_segment_score(self, segment: Segment) -> float:
        """Calculate importance score for a segment"""

        score = 0.0

        motion_score = (
            segment.motion_data.get('motion_intensity', 0) * 0.4 +
            segment.motion_data.get('peak_motion', 0) * 0.3 +
            (1 if segment.motion_data.get('has_significant_motion') else 0) * 0.3
        )
        score += min(motion_score, 1.0) * self.weights['motion']

        audio_score = (
            (1 if segment.audio_data.get('has_speech') else 0) * 0.4 +
            segment.audio_data.get('excitement_level', 0) * 0.3 +
            (1 if segment.audio_data.get('has_music') else 0) * 0.2 +
            (1 - segment.audio_data.get('silence_ratio', 1)) * 0.1
        )
        score += min(audio_score, 1.0) * self.weights['audio']

        quality_score = segment.quality_score
        score += quality_score * self.weights['quality']

        position_score = 0
        if segment._position_ratio < 0.1:
            position_score = 1.0
        elif segment._position_ratio > 0.9:
            position_score = 0.8
        elif 0.45 < segment._position_ratio < 0.55:
            position_score = 0.5
        score += position_score * self.weights['position']

        duration_score = 1.0
        if segment.duration < 1:
            duration_score = 0.5
        elif segment.duration > 30:
            duration_score = 0.7
        score += duration_score * self.weights['duration']

        return score

    def _apply_context_rules(self,
                            scored_segments: List[Tuple[Segment, float]]) -> List[Tuple[Segment, float]]:
        """Apply contextual rules to adjust scores"""

        adjusted = []
        prev_segment = None

        for i, (segment, score) in enumerate(scored_segments):
            adjusted_score = score

            if prev_segment and prev_segment[1] < 0.3:
                adjusted_score *= 1.2

            if prev_segment and self._are_similar(segment, prev_segment[0]):
                adjusted_score *= 0.8

            if self._is_key_moment(segment):
                adjusted_score = max(adjusted_score, 0.7)

            adjusted.append((segment, adjusted_score))
            prev_segment = (segment, adjusted_score)

        return adjusted

    def _are_similar(self, seg1: Segment, seg2: Segment) -> bool:
        """Check if two segments are very similar"""
        time_gap = abs(seg1.start_time - seg2.end_time)
        if time_gap > 30:
            return False

        motion_diff = abs(
            seg1.motion_data.get('motion_intensity', 0) -
            seg2.motion_data.get('motion_intensity', 0)
        )

        return motion_diff < 0.1

    def _is_key_moment(self, segment: Segment) -> bool:
        """Detect if segment contains a key moment"""
        if segment.audio_data.get('excitement_level', 0) > 0.8:
            return True

        if segment.motion_data.get('peak_motion', 0) > 10:
            return True

        if (segment.audio_data.get('has_speech') and
            segment.quality_score > 0.7):
            return True

        return False

    def select_highlights(self, ranked_segments: List[Tuple[Segment, float]],
                         target_duration: float,
                         min_segment_duration: float = 1.0,
                         max_segment_duration: float = 10.0) -> List[Segment]:
        """Select best segments to create highlight reel"""

        selected = []
        total_duration = 0

        for segment, score in ranked_segments:
            if score < 0.2:
                continue

            segment_duration = segment.duration

            if segment_duration < min_segment_duration:
                continue

            if segment_duration > max_segment_duration:
                segment_duration = max_segment_duration

            if total_duration + segment_duration <= target_duration:
                selected.append(segment)
                total_duration += segment_duration

            if total_duration >= target_duration * 0.95:
                break

        selected.sort(key=lambda s: s.start_time)

        return selected