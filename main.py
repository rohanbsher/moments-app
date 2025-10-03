#!/usr/bin/env python3
"""
Moments - AI-powered video highlight extraction
Command-line interface
"""

import argparse
import sys
import os
import logging
from pathlib import Path

from core.video_processor import VideoProcessor, ProcessingConfig

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(
        description='Moments - Turn long videos into watchable highlights'
    )

    parser.add_argument(
        'input',
        type=str,
        help='Path to input video file'
    )

    parser.add_argument(
        '-o', '--output',
        type=str,
        default=None,
        help='Path for output video (default: input_highlights.mp4)'
    )

    parser.add_argument(
        '-d', '--duration',
        type=int,
        default=180,
        help='Target duration for highlights in seconds (default: 180)'
    )

    parser.add_argument(
        '-q', '--quality',
        type=str,
        choices=['low', 'medium', 'high'],
        default='high',
        help='Output video quality (default: high)'
    )

    parser.add_argument(
        '--no-speech',
        action='store_true',
        help='Disable speech recognition (faster processing)'
    )

    parser.add_argument(
        '--min-segment',
        type=float,
        default=1.0,
        help='Minimum segment duration in seconds (default: 1.0)'
    )

    parser.add_argument(
        '--max-segment',
        type=float,
        default=10.0,
        help='Maximum segment duration in seconds (default: 10.0)'
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    if not os.path.exists(args.input):
        print(f"Error: Input file not found: {args.input}")
        sys.exit(1)

    if not args.input.lower().endswith(('.mp4', '.mov', '.avi', '.mkv', '.webm')):
        print(f"Error: Unsupported video format. Supported: mp4, mov, avi, mkv, webm")
        sys.exit(1)

    config = ProcessingConfig(
        target_duration=args.duration,
        min_segment_duration=args.min_segment,
        max_segment_duration=args.max_segment,
        output_quality=args.quality,
        enable_speech_recognition=not args.no_speech
    )

    processor = VideoProcessor(config)

    try:
        print(f"\n✨ Processing: {args.input}")
        print(f"Target duration: {args.duration} seconds")
        print(f"Quality: {args.quality}")
        print("-" * 50)

        metadata = processor.process_video(args.input, args.output)

        print("\n✅ Success!")
        print(f"Output: {metadata['output_file']}")
        print(f"Original duration: {metadata['input_duration']:.1f}s")
        print(f"Highlight duration: {metadata['output_duration']:.1f}s")
        print(f"Compression ratio: {metadata['compression_ratio']:.1f}x")
        print(f"Processing time: {metadata['processing_time']:.1f}s")
        print(f"Segments selected: {metadata['segments_selected']}")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()