#!/usr/bin/env python3
"""
Basic test without Whisper dependencies
Tests core video processing functionality
"""

import cv2
import numpy as np
import os
import sys
from dataclasses import dataclass

# Basic config without Whisper
@dataclass
class SimpleConfig:
    target_duration: int = 5
    min_segment_duration: float = 1.0
    max_segment_duration: float = 10.0
    enable_speech_recognition: bool = False

def create_test_video(filename="simple_test.mp4", duration=10, fps=30):
    """Create a simple test video"""
    width, height = 640, 480
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(filename, fourcc, fps, (width, height))

    total_frames = duration * fps

    for frame_num in range(total_frames):
        # Create colorful frame
        hue = int((frame_num / total_frames) * 179)
        hsv = np.zeros((height, width, 3), dtype=np.uint8)
        hsv[:, :, 0] = hue
        hsv[:, :, 1] = 255
        hsv[:, :, 2] = 255

        frame = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

        # Add moving circle
        center_x = int(width * (0.5 + 0.3 * np.sin(frame_num * 0.1)))
        center_y = height // 2
        cv2.circle(frame, (center_x, center_y), 50, (255, 255, 255), -1)

        # Add text
        text = f"Frame {frame_num}"
        cv2.putText(frame, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        out.write(frame)

    out.release()
    print(f"✅ Created test video: {filename}")
    return filename

def simple_motion_analysis(video_path, start_time, end_time):
    """Simple motion analysis without complex dependencies"""
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)

    start_frame = int(start_time * fps)
    end_frame = int(end_time * fps)
    cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)

    motion_scores = []
    prev_gray = None

    for frame_idx in range(start_frame, min(end_frame, int(cap.get(cv2.CAP_PROP_FRAME_COUNT))), 5):
        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        if prev_gray is not None:
            diff = cv2.absdiff(prev_gray, gray)
            motion_score = np.mean(diff)
            motion_scores.append(motion_score)

        prev_gray = gray

    cap.release()

    return {
        'motion_intensity': np.mean(motion_scores) if motion_scores else 0,
        'peak_motion': np.max(motion_scores) if motion_scores else 0,
        'has_significant_motion': np.mean(motion_scores) > 5.0 if motion_scores else False
    }

def simple_scene_detection(video_path):
    """Basic scene detection by dividing video into segments"""
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    duration = frame_count / fps
    cap.release()

    # Simple: divide into 3-second segments
    segments = []
    current_time = 0
    segment_length = 3.0

    while current_time < duration:
        end_time = min(current_time + segment_length, duration)
        segments.append((current_time, end_time))
        current_time = end_time

    return segments

def simple_video_processor(input_path, output_path, config):
    """Simplified video processor"""

    print(f"Processing: {input_path}")

    # 1. Simple scene detection
    print("Detecting scenes...")
    scenes = simple_scene_detection(input_path)
    print(f"Found {len(scenes)} segments")

    # 2. Analyze segments
    print("Analyzing segments...")
    scored_segments = []

    for i, (start, end) in enumerate(scenes):
        motion_data = simple_motion_analysis(input_path, start, end)

        # Simple scoring
        score = motion_data['motion_intensity'] * 0.01
        if motion_data['has_significant_motion']:
            score += 0.5

        scored_segments.append(((start, end), score))
        print(f"  Segment {i+1}: {start:.1f}-{end:.1f}s, score: {score:.2f}")

    # 3. Select best segments
    print("Selecting highlights...")
    scored_segments.sort(key=lambda x: x[1], reverse=True)

    selected = []
    total_duration = 0
    target = config.target_duration

    for (start, end), score in scored_segments:
        segment_duration = end - start
        if total_duration + segment_duration <= target:
            selected.append((start, end))
            total_duration += segment_duration

        if total_duration >= target * 0.9:
            break

    selected.sort()  # Sort by time

    # 4. Create output using moviepy
    try:
        from moviepy.editor import VideoFileClip, concatenate_videoclips

        print("Creating highlight video...")
        clips = []

        for start, end in selected:
            clip = VideoFileClip(input_path).subclip(start, end)
            clips.append(clip)

        if clips:
            final = concatenate_videoclips(clips)
            final.write_videofile(output_path, logger=None, verbose=False)
            final.close()

            for clip in clips:
                clip.close()

        print(f"✅ Created: {output_path}")

        return {
            'input_duration': sum(end - start for start, end in scenes),
            'output_duration': total_duration,
            'segments_selected': len(selected)
        }

    except ImportError:
        print("❌ MoviePy not available, skipping video creation")
        return {
            'input_duration': sum(end - start for start, end in scenes),
            'output_duration': total_duration,
            'segments_selected': len(selected)
        }

def main():
    print("Moments - Basic Test")
    print("=" * 50)

    # Create test video
    test_video = create_test_video(duration=10)

    try:
        config = SimpleConfig()

        result = simple_video_processor(test_video, "basic_highlights.mp4", config)

        print("\n✨ Results:")
        print(f"  Input duration: {result['input_duration']:.1f}s")
        print(f"  Output duration: {result['output_duration']:.1f}s")
        print(f"  Segments selected: {result['segments_selected']}")

        if os.path.exists("basic_highlights.mp4"):
            size = os.path.getsize("basic_highlights.mp4") / (1024 * 1024)
            print(f"  Output size: {size:.2f} MB")
            print("\n✅ Basic test passed!")
        else:
            print("\n⚠️  Video not created but analysis worked")

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # Cleanup
        for file in ["simple_test.mp4", "basic_highlights.mp4"]:
            if os.path.exists(file):
                os.remove(file)
                print(f"🧹 Cleaned up {file}")

if __name__ == "__main__":
    main()