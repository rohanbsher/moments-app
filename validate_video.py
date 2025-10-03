#!/usr/bin/env python3
"""
Video Validation Tool
Tests the Moments processor with user-provided videos
"""

import cv2
import os
import sys
import time
import json
from pathlib import Path
from core.simple_processor import SimpleVideoProcessor, SimpleConfig

class VideoValidator:
    def __init__(self):
        self.supported_formats = {'.mp4', '.mov', '.avi', '.mkv', '.webm', '.m4v'}

    def validate_video_file(self, video_path):
        """Validate that the video file can be processed"""
        print(f"🔍 Validating video: {video_path}")
        print("-" * 50)

        # Check file existence
        if not os.path.exists(video_path):
            print(f"❌ File not found: {video_path}")
            return False

        # Check file extension
        ext = Path(video_path).suffix.lower()
        if ext not in self.supported_formats:
            print(f"❌ Unsupported format: {ext}")
            print(f"   Supported: {', '.join(self.supported_formats)}")
            return False

        # Check file size
        file_size = os.path.getsize(video_path) / (1024 * 1024)  # MB
        print(f"📄 File size: {file_size:.1f} MB")

        if file_size > 1000:  # > 1GB
            print("⚠️  Large file - processing may take longer")

        # Try to open with OpenCV
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print("❌ Cannot open video file")
            cap.release()
            return False

        # Get video properties
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        duration = frame_count / fps if fps > 0 else 0

        print(f"📹 Video properties:")
        print(f"   Duration: {duration:.1f} seconds ({duration/60:.1f} minutes)")
        print(f"   Resolution: {width}x{height}")
        print(f"   FPS: {fps:.1f}")
        print(f"   Frames: {int(frame_count)}")

        # Check for potential issues
        if duration < 10:
            print("⚠️  Video is very short (< 10s) - may not have enough content for highlights")
        elif duration > 3600:  # > 1 hour
            print("⚠️  Video is very long (> 1 hour) - processing will take time")

        if fps < 15:
            print("⚠️  Low frame rate - motion detection may be less accurate")

        if width < 480 or height < 360:
            print("⚠️  Low resolution - may affect quality")

        # Test reading a few frames
        frames_tested = 0
        for i in range(0, min(int(frame_count), 100), 10):
            cap.set(cv2.CAP_PROP_POS_FRAMES, i)
            ret, frame = cap.read()
            if ret:
                frames_tested += 1
            else:
                break

        cap.release()

        if frames_tested < 5:
            print("❌ Cannot read video frames properly")
            return False

        print(f"✅ Video validation successful")
        print(f"   Tested {frames_tested} frames - all readable")

        return True

    def estimate_processing_time(self, video_path):
        """Estimate how long processing will take"""
        cap = cv2.VideoCapture(video_path)
        duration = cap.get(cv2.CAP_PROP_FRAME_COUNT) / cap.get(cv2.CAP_PROP_FPS)
        cap.release()

        # Based on test results: ~36x real-time processing
        estimated_time = duration / 30  # Conservative estimate

        print(f"⏱️  Estimated processing time: {estimated_time:.1f} seconds")

        if estimated_time > 60:
            print(f"   That's about {estimated_time/60:.1f} minutes")

        return estimated_time

    def test_processing(self, video_path, test_duration=10):
        """Test processing with a short segment"""
        print(f"\n🧪 Testing processing with {test_duration}s target...")
        print("-" * 50)

        config = SimpleConfig(
            target_duration=test_duration,
            min_segment_duration=1.0,
            max_segment_duration=5.0
        )

        processor = SimpleVideoProcessor(config)

        base_name = Path(video_path).stem
        test_output = f"{base_name}_test_highlights.mp4"

        try:
            start_time = time.time()
            metadata = processor.process_video(video_path, test_output)
            processing_time = time.time() - start_time

            print(f"✅ Test processing successful!")
            print(f"   Input: {metadata['input_duration']:.1f}s")
            print(f"   Output: {metadata['output_duration']:.1f}s")
            print(f"   Compression: {metadata['input_duration']/metadata['output_duration']:.1f}x")
            print(f"   Processing time: {processing_time:.1f}s")
            print(f"   Segments selected: {metadata['segments_selected']}")

            # Check output file
            if os.path.exists(test_output):
                output_size = os.path.getsize(test_output) / (1024 * 1024)
                print(f"   Output size: {output_size:.1f} MB")
                print(f"   Output file: {test_output}")

                # Test playback
                test_cap = cv2.VideoCapture(test_output)
                if test_cap.isOpened():
                    print("   ✅ Output video is playable")
                    test_cap.release()
                else:
                    print("   ⚠️  Output video may have issues")

            return True, metadata

        except Exception as e:
            print(f"❌ Test processing failed: {e}")
            return False, None

    def interactive_test(self, video_path):
        """Interactive testing with user choices"""
        print(f"\n🎛️  Interactive Testing")
        print("=" * 50)

        durations = [30, 60, 120, 180, 300]  # Different highlight lengths

        print("Choose target duration for highlights:")
        for i, duration in enumerate(durations, 1):
            minutes = duration // 60
            seconds = duration % 60
            if minutes > 0:
                time_str = f"{minutes}m {seconds}s" if seconds > 0 else f"{minutes}m"
            else:
                time_str = f"{seconds}s"
            print(f"  {i}. {time_str} ({duration}s)")

        print("  6. Custom duration")

        try:
            choice = input("\nEnter choice (1-6): ").strip()

            if choice == '6':
                custom = input("Enter duration in seconds: ").strip()
                target_duration = int(custom)
            else:
                target_duration = durations[int(choice) - 1]

        except (ValueError, IndexError):
            print("Invalid choice, using 3 minutes (180s)")
            target_duration = 180

        print(f"\n🎬 Creating {target_duration}s highlights...")

        config = SimpleConfig(target_duration=target_duration)
        processor = SimpleVideoProcessor(config)

        base_name = Path(video_path).stem
        output_file = f"{base_name}_highlights_{target_duration}s.mp4"

        try:
            start_time = time.time()
            metadata = processor.process_video(video_path, output_file)
            processing_time = time.time() - start_time

            print(f"\n✅ Highlights created successfully!")
            print("=" * 50)
            print(f"📊 Results:")
            print(f"   Original: {metadata['input_duration']:.1f}s ({metadata['input_duration']/60:.1f} minutes)")
            print(f"   Highlights: {metadata['output_duration']:.1f}s ({metadata['output_duration']/60:.1f} minutes)")
            print(f"   Compression: {metadata['input_duration']/metadata['output_duration']:.1f}x")
            print(f"   Processing time: {processing_time:.1f}s")
            print(f"   Speed: {metadata['input_duration']/processing_time:.1f}x real-time")

            print(f"\n📁 Output file: {output_file}")

            if os.path.exists(output_file):
                output_size = os.path.getsize(output_file) / (1024 * 1024)
                print(f"   Size: {output_size:.1f} MB")

            # Show selected segments
            print(f"\n🎯 Selected segments:")
            for i, seg in enumerate(metadata['segments'], 1):
                print(f"   {i}. {seg['start']:.1f}s - {seg['end']:.1f}s")

            return True

        except Exception as e:
            print(f"\n❌ Processing failed: {e}")
            import traceback
            traceback.print_exc()
            return False

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 validate_video.py VIDEO_FILE")
        print("\nExample:")
        print("  python3 validate_video.py /path/to/your/video.mp4")
        sys.exit(1)

    video_path = sys.argv[1]

    print("🎬 Moments Video Validator")
    print("=" * 60)

    validator = VideoValidator()

    # Step 1: Validate the video file
    if not validator.validate_video_file(video_path):
        print("\n❌ Video validation failed. Cannot proceed.")
        sys.exit(1)

    # Step 2: Estimate processing time
    validator.estimate_processing_time(video_path)

    # Step 3: Quick test
    print(f"\n" + "=" * 60)
    proceed = input("Proceed with quick test? (Y/n): ").lower().strip()

    if proceed != 'n':
        success, metadata = validator.test_processing(video_path, test_duration=10)

        if not success:
            print("\n❌ Quick test failed. Your video may have compatibility issues.")
            sys.exit(1)

        # Step 4: Interactive test
        print(f"\n" + "=" * 60)
        full_test = input("Proceed with full processing? (Y/n): ").lower().strip()

        if full_test != 'n':
            validator.interactive_test(video_path)

    print(f"\n🎉 Testing complete!")
    print("💡 If everything worked well, you can use the CLI:")
    print(f"   python3 simple_main.py \"{video_path}\" -d 180 -v")

if __name__ == "__main__":
    main()