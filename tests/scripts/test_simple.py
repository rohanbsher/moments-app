#!/usr/bin/env python3
"""
Simple test script to verify the Moments video processor works
Creates a test video and processes it
"""

import cv2
import numpy as np
import os
from core.video_processor import VideoProcessor, ProcessingConfig

def create_test_video(filename="test_video.mp4", duration=10, fps=30):
    """Create a simple test video with color changes and motion"""

    width, height = 640, 480
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(filename, fourcc, fps, (width, height))

    total_frames = duration * fps

    for frame_num in range(total_frames):
        # Create frame with changing colors
        hue = int((frame_num / total_frames) * 179)
        hsv = np.zeros((height, width, 3), dtype=np.uint8)
        hsv[:, :, 0] = hue
        hsv[:, :, 1] = 255
        hsv[:, :, 2] = 255

        frame = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

        # Add moving circle for motion
        center_x = int(width * (0.5 + 0.3 * np.sin(frame_num * 0.1)))
        center_y = height // 2
        cv2.circle(frame, (center_x, center_y), 50, (255, 255, 255), -1)

        # Add text
        text = f"Frame {frame_num}/{total_frames}"
        cv2.putText(frame, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
                   1, (255, 255, 255), 2)

        out.write(frame)

    out.release()
    print(f"✅ Created test video: {filename}")
    return filename

def main():
    print("Moments - Simple Test")
    print("=" * 50)

    # Create test video
    test_video = create_test_video(duration=15)

    try:
        # Configure processor
        config = ProcessingConfig(
            target_duration=5,  # 5 second highlights
            enable_speech_recognition=False,  # Faster without speech
            output_quality='medium'
        )

        # Process video
        processor = VideoProcessor(config)

        print("\n🎬 Processing video...")
        metadata = processor.process_video(test_video, "test_highlights.mp4")

        print("\n✨ Success!")
        print(f"  Input duration: {metadata['input_duration']:.1f}s")
        print(f"  Output duration: {metadata['output_duration']:.1f}s")
        print(f"  Segments selected: {metadata['segments_selected']}")
        print(f"  Processing time: {metadata['processing_time']:.1f}s")

        # Verify output exists
        if os.path.exists("test_highlights.mp4"):
            size = os.path.getsize("test_highlights.mp4") / (1024 * 1024)
            print(f"  Output file size: {size:.2f} MB")
            print("\n✅ Test passed! The system is working correctly.")
        else:
            print("\n❌ Output file not created")

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # Cleanup
        if os.path.exists(test_video):
            os.remove(test_video)
            print(f"\n🧹 Cleaned up test video")

if __name__ == "__main__":
    main()