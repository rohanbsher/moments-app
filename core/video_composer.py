import os
import tempfile
from typing import List, Dict, Optional
import logging
from dataclasses import dataclass
from moviepy.editor import VideoFileClip, concatenate_videoclips

logger = logging.getLogger(__name__)

@dataclass
class CompositionSegment:
    input_file: str
    start_time: float
    end_time: float
    transition_type: str = 'cut'
    transition_duration: float = 0.5

class VideoComposer:
    def __init__(self):
        self.transitions = {
            'cut': self._create_cut,
            'fade': self._create_fade
        }

    def compose_video(self,
                     segments: List[CompositionSegment],
                     output_path: str,
                     resolution: str = '1920x1080',
                     fps: int = 30,
                     quality: str = 'high') -> str:
        """Compose final video from segments"""

        try:
            clips = []

            for segment in segments:
                clip = VideoFileClip(segment.input_file).subclip(
                    segment.start_time,
                    segment.end_time
                )

                if segment.transition_type == 'fade' and len(clips) > 0:
                    clip = clip.crossfadein(segment.transition_duration)

                clips.append(clip)

            if not clips:
                raise ValueError("No clips to compose")

            final_video = concatenate_videoclips(clips, method="compose")

            codec = 'libx264'
            if quality == 'high':
                bitrate = '4000k'
            elif quality == 'medium':
                bitrate = '2000k'
            else:
                bitrate = '1000k'

            final_video.write_videofile(
                output_path,
                fps=fps,
                codec=codec,
                bitrate=bitrate,
                audio_codec='aac',
                logger=None,
                verbose=False
            )

            for clip in clips:
                clip.close()
            final_video.close()

            logger.info(f"Video composed successfully: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Video composition failed: {e}")
            raise

    def _create_cut(self, clip1, clip2):
        """Simple cut transition"""
        return clip2

    def _create_fade(self, clip1, clip2, duration=0.5):
        """Fade transition between clips"""
        return clip2.crossfadein(duration)

    def create_thumbnail(self, video_path: str,
                        timestamp: float = None,
                        output_path: str = None) -> str:
        """Extract thumbnail from video"""

        if output_path is None:
            output_path = video_path.replace('.mp4', '_thumb.jpg')

        try:
            clip = VideoFileClip(video_path)

            if timestamp is None:
                timestamp = clip.duration * 0.1

            frame = clip.get_frame(timestamp)

            from PIL import Image
            img = Image.fromarray(frame)
            img.save(output_path, 'JPEG', quality=95)

            clip.close()

            return output_path

        except Exception as e:
            logger.error(f"Failed to create thumbnail: {e}")
            raise