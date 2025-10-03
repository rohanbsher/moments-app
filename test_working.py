#!/usr/bin/env python3
"""
Working test with the simplified processor
"""

import cv2
import numpy as np
import os
from core.simple_processor import SimpleVideoProcessor, SimpleConfig

def create_demo_video(filename="demo_video.mp4", duration=30, fps=30):
    """Create a demo video with different activity levels"""

    width, height = 640, 480
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(filename, fourcc, fps, (width, height))

    total_frames = duration * fps

    for frame_num in range(total_frames):
        # Create different scenes with varying motion
        scene_progress = (frame_num / total_frames)

        if scene_progress < 0.2:
            # Scene 1: Static scene (low interest)
            frame = np.zeros((height, width, 3), dtype=np.uint8)
            frame[:, :] = [50, 50, 100]  # Dark blue
            text = "Boring static scene"

        elif scene_progress < 0.4:
            # Scene 2: High motion scene (high interest)
            hue = int((frame_num % 100) * 1.8)
            hsv = np.zeros((height, width, 3), dtype=np.uint8)
            hsv[:, :, 0] = hue
            hsv[:, :, 1] = 255
            hsv[:, :, 2] = 200
            frame = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

            # Multiple moving objects
            for i in range(3):
                x = int(width * (0.3 + 0.4 * np.sin(frame_num * 0.1 + i * 2)))
                y = int(height * (0.3 + 0.4 * np.cos(frame_num * 0.1 + i * 2)))
                cv2.circle(frame, (x, y), 30, (255, 255, 255), -1)

            text = "High action scene"

        elif scene_progress < 0.6:
            # Scene 3: Medium motion (medium interest)
            frame = np.zeros((height, width, 3), dtype=np.uint8)
            frame[:, :] = [100, 150, 100]  # Green

            # Single moving object
            x = int(width * (0.5 + 0.3 * np.sin(frame_num * 0.05)))
            y = height // 2
            cv2.circle(frame, (x, y), 40, (255, 255, 255), -1)

            text = "Medium action scene"

        elif scene_progress < 0.8:
            # Scene 4: Another high action scene (high interest)
            frame = np.random.randint(0, 256, (height, width, 3), dtype=np.uint8)
            text = "Chaotic high action"

        else:
            # Scene 5: Calm ending (low interest)
            frame = np.zeros((height, width, 3), dtype=np.uint8)
            frame[:, :] = [150, 100, 150]  # Purple
            text = "Calm ending"

        # Add text overlay
        cv2.putText(frame, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(frame, f"Time: {frame_num/fps:.1f}s", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        out.write(frame)

    out.release()
    print(f"✅ Created demo video: {filename} ({duration}s)")
    return filename

def main():
    print("Moments - Working Demo Test")
    print("=" * 60)

    # Create a 30-second demo video with varying content
    demo_video = create_demo_video(duration=30)

    try:
        # Test with different target durations
        configs = [
            SimpleConfig(target_duration=5, min_segment_duration=1.0, max_segment_duration=3.0),
            SimpleConfig(target_duration=10, min_segment_duration=1.0, max_segment_duration=5.0),
            SimpleConfig(target_duration=15, min_segment_duration=2.0, max_segment_duration=8.0)
        ]

        for i, config in enumerate(configs, 1):
            print(f"\n🎬 Test {i}: {config.target_duration}s highlights")
            print("-" * 40)

            processor = SimpleVideoProcessor(config)
            output_file = f"highlights_{config.target_duration}s.mp4"

            metadata = processor.process_video(demo_video, output_file)

            print(f"✨ Results:")
            print(f"  Input: {metadata['input_duration']:.1f}s")
            print(f"  Output: {metadata['output_duration']:.1f}s")
            print(f"  Compression: {metadata['input_duration']/metadata['output_duration']:.1f}x")
            print(f"  Processing time: {metadata['processing_time']:.1f}s")
            print(f"  Segments: {metadata['segments_selected']}")

            # Show selected segments
            print("  Selected moments:")
            for j, seg in enumerate(metadata['segments'], 1):
                print(f"    {j}. {seg['start']:.1f}s-{seg['end']:.1f}s "
                      f"(score: {seg['score']:.2f})")

            if os.path.exists(output_file):
                size = os.path.getsize(output_file) / (1024 * 1024)
                print(f"  Output size: {size:.1f} MB")

        print("\n🎉 All tests completed successfully!")
        print("\nFiles created:")
        for config in configs:
            output_file = f"highlights_{config.target_duration}s.mp4"
            if os.path.exists(output_file):
                print(f"  ✅ {output_file}")

        print("\n📝 Try the CLI version:")
        print(f"python3 simple_main.py {demo_video} -d 10 -v")

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # Optional cleanup
        cleanup = input("\nClean up test files? (y/N): ").lower().strip()
        if cleanup == 'y':
            files_to_clean = [demo_video] + [f"highlights_{c.target_duration}s.mp4" for c in configs]
            for file in files_to_clean:
                if os.path.exists(file):
                    os.remove(file)
                    print(f"🧹 Removed {file}")

if __name__ == "__main__":
    main()