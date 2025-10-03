#!/usr/bin/env python3
"""
Comprehensive Test Suite for Moments Video Processor
Tests different video types and scenarios
"""

import cv2
import numpy as np
import os
import time
import json
from core.simple_processor import SimpleVideoProcessor, SimpleConfig

class VideoTestSuite:
    def __init__(self):
        self.test_results = []
        self.test_videos = {}

    def create_test_video_library(self):
        """Create various test videos simulating real-world scenarios"""

        print("🎬 Creating Test Video Library...")
        print("=" * 60)

        # Test 1: Birthday Party Simulation
        self.create_birthday_video()

        # Test 2: Sports/Action Video
        self.create_sports_video()

        # Test 3: Meeting/Presentation
        self.create_meeting_video()

        # Test 4: Nature/Scenic Video
        self.create_nature_video()

        # Test 5: Mixed Content
        self.create_mixed_content_video()

        print(f"\n✅ Created {len(self.test_videos)} test videos")

    def create_birthday_video(self):
        """Simulate a birthday party video with varied activity"""
        filename = "test_birthday.mp4"
        duration = 45  # 45 seconds
        fps = 30
        width, height = 640, 480

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(filename, fourcc, fps, (width, height))

        total_frames = duration * fps

        for frame_num in range(total_frames):
            progress = frame_num / total_frames

            # Create different party scenes
            if progress < 0.2:
                # Setting up (low interest)
                frame = self._create_static_scene("Setting up party", (100, 100, 150))

            elif progress < 0.4:
                # Guests arriving (medium interest)
                frame = self._create_medium_motion_scene("Guests arriving", frame_num)

            elif progress < 0.6:
                # Cake moment (high interest!)
                frame = self._create_high_motion_scene("🎂 Blowing candles!", frame_num)

            elif progress < 0.8:
                # Gift opening (high interest)
                frame = self._create_high_motion_scene("Opening presents!", frame_num)

            else:
                # Cleanup (low interest)
                frame = self._create_static_scene("Party ending", (80, 80, 120))

            # Add timestamp
            self._add_timestamp(frame, frame_num / fps, duration)
            out.write(frame)

        out.release()
        self.test_videos['birthday'] = {
            'filename': filename,
            'duration': duration,
            'expected_highlights': [(18, 36)],  # Cake and gifts moments
            'description': 'Birthday party with cake and gift moments'
        }
        print(f"  ✅ Birthday party video: {filename}")

    def create_sports_video(self):
        """Simulate a sports/action video"""
        filename = "test_sports.mp4"
        duration = 30
        fps = 30
        width, height = 640, 480

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(filename, fourcc, fps, (width, height))

        total_frames = duration * fps

        for frame_num in range(total_frames):
            progress = frame_num / total_frames

            if progress < 0.3:
                # Warm-up (low action)
                frame = self._create_medium_motion_scene("Warm-up", frame_num, speed=0.5)

            elif progress < 0.7:
                # Main action (high action)
                frame = self._create_extreme_motion_scene("⚽ Game action!", frame_num)

            else:
                # Cool down (low action)
                frame = self._create_static_scene("Cool down", (150, 130, 100))

            self._add_timestamp(frame, frame_num / fps, duration)
            out.write(frame)

        out.release()
        self.test_videos['sports'] = {
            'filename': filename,
            'duration': duration,
            'expected_highlights': [(9, 21)],  # Main action
            'description': 'Sports video with high action middle section'
        }
        print(f"  ✅ Sports/action video: {filename}")

    def create_meeting_video(self):
        """Simulate a meeting/presentation video"""
        filename = "test_meeting.mp4"
        duration = 60
        fps = 30
        width, height = 640, 480

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(filename, fourcc, fps, (width, height))

        total_frames = duration * fps

        for frame_num in range(total_frames):
            progress = frame_num / total_frames

            # Mostly static with occasional slide changes
            if int(progress * 10) % 2 == 0:
                # Slide view (static)
                slide_num = int(progress * 5) + 1
                frame = self._create_slide_scene(f"Slide {slide_num}", frame_num)
            else:
                # Speaker view (minimal motion)
                frame = self._create_talking_head_scene("Speaker presenting", frame_num)

            self._add_timestamp(frame, frame_num / fps, duration)
            out.write(frame)

        out.release()
        self.test_videos['meeting'] = {
            'filename': filename,
            'duration': duration,
            'expected_highlights': [(0, 10), (50, 60)],  # Beginning and end
            'description': 'Meeting video with slides and speaker'
        }
        print(f"  ✅ Meeting/presentation video: {filename}")

    def create_nature_video(self):
        """Simulate a nature/scenic video"""
        filename = "test_nature.mp4"
        duration = 40
        fps = 30
        width, height = 640, 480

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(filename, fourcc, fps, (width, height))

        total_frames = duration * fps

        for frame_num in range(total_frames):
            progress = frame_num / total_frames

            if progress < 0.25:
                # Sunrise (gradual change)
                frame = self._create_gradient_scene("Sunrise", frame_num, (50, 100, 200))

            elif progress < 0.5:
                # Wildlife appears (sudden interest)
                frame = self._create_wildlife_scene("🦅 Wildlife!", frame_num)

            elif progress < 0.75:
                # Scenic view (static beauty)
                frame = self._create_scenic_scene("Mountain view", frame_num)

            else:
                # Sunset (gradual change)
                frame = self._create_gradient_scene("Sunset", frame_num, (200, 100, 50))

            self._add_timestamp(frame, frame_num / fps, duration)
            out.write(frame)

        out.release()
        self.test_videos['nature'] = {
            'filename': filename,
            'duration': duration,
            'expected_highlights': [(10, 20)],  # Wildlife moment
            'description': 'Nature video with wildlife appearance'
        }
        print(f"  ✅ Nature/scenic video: {filename}")

    def create_mixed_content_video(self):
        """Create a video with mixed content types"""
        filename = "test_mixed.mp4"
        duration = 50
        fps = 30
        width, height = 640, 480

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(filename, fourcc, fps, (width, height))

        total_frames = duration * fps

        for frame_num in range(total_frames):
            progress = frame_num / total_frames
            segment = int(progress * 5)  # 5 different segments

            if segment == 0:
                frame = self._create_static_scene("Intro", (50, 50, 50))
            elif segment == 1:
                frame = self._create_high_motion_scene("Action 1", frame_num)
            elif segment == 2:
                frame = self._create_medium_motion_scene("Transition", frame_num)
            elif segment == 3:
                frame = self._create_extreme_motion_scene("Peak moment!", frame_num)
            else:
                frame = self._create_static_scene("Outro", (100, 100, 100))

            self._add_timestamp(frame, frame_num / fps, duration)
            out.write(frame)

        out.release()
        self.test_videos['mixed'] = {
            'filename': filename,
            'duration': duration,
            'expected_highlights': [(10, 20), (30, 40)],  # Action segments
            'description': 'Mixed content with varying activity levels'
        }
        print(f"  ✅ Mixed content video: {filename}")

    # Helper methods for creating different scene types
    def _create_static_scene(self, text, color):
        """Create a static scene with text"""
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        frame[:, :] = color
        cv2.putText(frame, text, (50, 240), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        return frame

    def _create_medium_motion_scene(self, text, frame_num, speed=1.0):
        """Create scene with medium motion"""
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        frame[:, :] = [100, 150, 100]

        # Moving circle
        x = int(320 + 200 * np.sin(frame_num * 0.05 * speed))
        y = int(240 + 100 * np.cos(frame_num * 0.05 * speed))
        cv2.circle(frame, (x, y), 50, (255, 255, 255), -1)

        cv2.putText(frame, text, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        return frame

    def _create_high_motion_scene(self, text, frame_num):
        """Create scene with high motion"""
        frame = np.zeros((480, 640, 3), dtype=np.uint8)

        # Colorful, changing background
        hue = int((frame_num * 2) % 179)
        hsv = np.zeros((480, 640, 3), dtype=np.uint8)
        hsv[:, :, 0] = hue
        hsv[:, :, 1] = 200
        hsv[:, :, 2] = 200
        frame = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

        # Multiple moving objects
        for i in range(3):
            x = int(320 + 150 * np.sin(frame_num * 0.1 + i * 2.1))
            y = int(240 + 150 * np.cos(frame_num * 0.1 + i * 2.1))
            cv2.circle(frame, (x, y), 30, (255, 255, 255), -1)

        cv2.putText(frame, text, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 3)
        return frame

    def _create_extreme_motion_scene(self, text, frame_num):
        """Create scene with extreme motion"""
        # Random pixels for maximum motion
        frame = np.random.randint(0, 256, (480, 640, 3), dtype=np.uint8)

        # Add some structure
        cv2.rectangle(frame, (100, 100), (540, 380), (255, 255, 255), 5)
        cv2.putText(frame, text, (150, 240), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 0), 3)
        cv2.putText(frame, text, (148, 238), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 2)

        return frame

    def _create_slide_scene(self, text, frame_num):
        """Create a presentation slide"""
        frame = np.ones((480, 640, 3), dtype=np.uint8) * 240  # Light gray
        cv2.rectangle(frame, (50, 50), (590, 430), (0, 0, 0), 2)
        cv2.putText(frame, text, (100, 150), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 0), 2)

        # Add bullet points
        for i in range(3):
            y = 220 + i * 50
            cv2.circle(frame, (120, y), 5, (0, 0, 0), -1)
            cv2.putText(frame, f"Point {i+1}", (150, y+5), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 1)

        return frame

    def _create_talking_head_scene(self, text, frame_num):
        """Create a talking head scene"""
        frame = np.ones((480, 640, 3), dtype=np.uint8) * 200

        # Simulate face
        cv2.ellipse(frame, (320, 200), (80, 100), 0, 0, 360, (150, 130, 100), -1)

        # Minimal motion (mouth)
        mouth_y = 230 + int(5 * np.sin(frame_num * 0.3))
        cv2.ellipse(frame, (320, mouth_y), (30, 15), 0, 0, 360, (100, 80, 80), 2)

        cv2.putText(frame, text, (50, 400), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
        return frame

    def _create_wildlife_scene(self, text, frame_num):
        """Create wildlife scene"""
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        frame[:, :] = [50, 150, 50]  # Forest green

        # Moving "bird"
        x = int(100 + (frame_num * 2) % 440)
        y = int(200 + 50 * np.sin(frame_num * 0.1))

        # Draw bird shape
        points = np.array([[x, y], [x-20, y+10], [x-10, y], [x-20, y-10]], np.int32)
        cv2.fillPoly(frame, [points], (255, 255, 255))

        cv2.putText(frame, text, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        return frame

    def _create_scenic_scene(self, text, frame_num):
        """Create scenic view"""
        frame = np.zeros((480, 640, 3), dtype=np.uint8)

        # Sky gradient
        for y in range(240):
            frame[y, :] = [200 - y//2, 150 - y//3, 100]

        # Ground
        frame[240:, :] = [50, 100, 50]

        # Mountain
        points = np.array([[200, 240], [320, 140], [440, 240]], np.int32)
        cv2.fillPoly(frame, [points], (100, 100, 100))

        cv2.putText(frame, text, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        return frame

    def _create_gradient_scene(self, text, frame_num, base_color):
        """Create gradient scene"""
        frame = np.zeros((480, 640, 3), dtype=np.uint8)

        # Gradual color change
        progress = (frame_num % 100) / 100
        r, g, b = base_color

        for y in range(480):
            intensity = y / 480
            frame[y, :] = [
                int(b * (1 - intensity * progress)),
                int(g * (1 - intensity * 0.5)),
                int(r * intensity)
            ]

        cv2.putText(frame, text, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        return frame

    def _add_timestamp(self, frame, current_time, total_time):
        """Add timestamp to frame"""
        text = f"{current_time:.1f}s / {total_time:.0f}s"
        cv2.putText(frame, text, (500, 470), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

    def run_tests(self):
        """Run tests on all created videos"""
        print("\n🧪 Running Comprehensive Tests...")
        print("=" * 60)

        for video_type, video_info in self.test_videos.items():
            print(f"\n📹 Testing: {video_info['description']}")
            print("-" * 40)

            # Test with different configurations
            configs = [
                SimpleConfig(target_duration=5, min_segment_duration=1.0),
                SimpleConfig(target_duration=10, min_segment_duration=1.5),
                SimpleConfig(target_duration=15, min_segment_duration=2.0)
            ]

            for config in configs:
                result = self.test_video_with_config(video_info['filename'], config, video_type)
                self.test_results.append(result)

                # Display result
                self.display_test_result(result)

    def test_video_with_config(self, filename, config, video_type):
        """Test a single video with specific configuration"""
        processor = SimpleVideoProcessor(config)
        output_file = f"output_{video_type}_{config.target_duration}s.mp4"

        start_time = time.time()

        try:
            metadata = processor.process_video(filename, output_file)
            processing_time = time.time() - start_time

            # Verify output exists
            output_exists = os.path.exists(output_file)
            output_size = os.path.getsize(output_file) / (1024 * 1024) if output_exists else 0

            return {
                'video_type': video_type,
                'config': config.target_duration,
                'success': True,
                'processing_time': processing_time,
                'input_duration': metadata['input_duration'],
                'output_duration': metadata['output_duration'],
                'segments_selected': metadata['segments_selected'],
                'output_size': output_size,
                'output_file': output_file,
                'compression_ratio': metadata['input_duration'] / metadata['output_duration']
            }

        except Exception as e:
            return {
                'video_type': video_type,
                'config': config.target_duration,
                'success': False,
                'error': str(e)
            }

    def display_test_result(self, result):
        """Display a single test result"""
        if result['success']:
            print(f"  ✅ {result['config']}s highlights: "
                  f"{result['output_duration']:.1f}s from {result['input_duration']:.1f}s "
                  f"({result['compression_ratio']:.1f}x compression) "
                  f"in {result['processing_time']:.2f}s")
        else:
            print(f"  ❌ {result['config']}s highlights: {result['error']}")

    def generate_report(self):
        """Generate comprehensive test report"""
        print("\n📊 Test Report")
        print("=" * 60)

        successful_tests = [r for r in self.test_results if r['success']]
        failed_tests = [r for r in self.test_results if not r['success']]

        print(f"\nTotal tests: {len(self.test_results)}")
        print(f"✅ Successful: {len(successful_tests)}")
        print(f"❌ Failed: {len(failed_tests)}")

        if successful_tests:
            # Performance statistics
            avg_processing_time = np.mean([r['processing_time'] for r in successful_tests])
            avg_compression = np.mean([r['compression_ratio'] for r in successful_tests])

            print(f"\n📈 Performance Statistics:")
            print(f"  Average processing time: {avg_processing_time:.2f}s")
            print(f"  Average compression ratio: {avg_compression:.1f}x")

            # Processing speed
            total_input = sum(r['input_duration'] for r in successful_tests)
            total_processing = sum(r['processing_time'] for r in successful_tests)
            speed_ratio = total_input / total_processing

            print(f"  Processing speed: {speed_ratio:.1f}x real-time")

        # Save detailed report
        report_file = 'test_report.json'
        with open(report_file, 'w') as f:
            json.dump({
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'summary': {
                    'total_tests': len(self.test_results),
                    'successful': len(successful_tests),
                    'failed': len(failed_tests)
                },
                'results': self.test_results
            }, f, indent=2)

        print(f"\n💾 Detailed report saved to: {report_file}")

    def cleanup(self, remove_all=False):
        """Clean up test files"""
        print("\n🧹 Cleanup Options:")

        files_to_clean = []

        # Test videos
        for video_info in self.test_videos.values():
            files_to_clean.append(video_info['filename'])

        # Output files
        for result in self.test_results:
            if result['success'] and 'output_file' in result:
                files_to_clean.append(result['output_file'])

        print(f"Found {len(files_to_clean)} files to clean")

        if remove_all or input("Remove all test files? (y/N): ").lower() == 'y':
            for file in files_to_clean:
                if os.path.exists(file):
                    os.remove(file)
                    print(f"  Removed: {file}")
            print("✅ Cleanup complete")
        else:
            print("⏭️  Skipped cleanup (files retained for inspection)")

def main():
    """Main test execution"""
    print("=" * 60)
    print("🎯 MOMENTS - Comprehensive Test Suite")
    print("=" * 60)

    suite = VideoTestSuite()

    try:
        # Create test videos
        suite.create_test_video_library()

        # Run comprehensive tests
        suite.run_tests()

        # Generate report
        suite.generate_report()

        print("\n✅ All tests completed!")

        # Offer to test with user's own video
        print("\n" + "=" * 60)
        print("💡 Want to test with your own video?")
        print("Run: python3 simple_main.py YOUR_VIDEO.mp4 -d 180 -v")

    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # Cleanup
        suite.cleanup()

if __name__ == "__main__":
    main()