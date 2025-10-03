"""
Moments - AI-powered video highlight extraction
Phase 1.5: Enhanced with audio analysis and diversity scoring
"""

__version__ = "1.5.0"

# Always available - simple processor with Phase 1.5 enhancements
__all__ = ['SimpleVideoProcessor', 'SimpleConfig']

# Optional advanced modules (require whisper/torch)
# Import these directly if needed: from core.video_processor import VideoProcessor