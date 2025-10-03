#!/usr/bin/env python3
"""
Fast video processor for large files
Optimized for 4K videos by downscaling during analysis
"""

import cv2
import numpy as np
import sys
import time
from pathlib import Path

def fast_process_video(input_path, output_path, target_duration=180):
    """Process video quickly by analyzing at lower resolution"""

    print(f"\n🎬 Processing: {input_path}")
    start_time = time.time()

    # Open video
    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        print("❌ Error: Could not open video")
        return False

    # Get properties
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    duration = total_frames / fps

    print(f"📊 Duration: {duration/60:.1f} minutes ({duration:.1f}s)")
    print(f"📐 Resolution: {width}x{height}")
    print(f"🎞️  FPS: {fps:.1f}")
    print(f"📦 Total frames: {total_frames:,}")

    # Analyze video with heavy sampling for speed
    print(f"\n🔍 Analyzing video (sampling every 5 seconds)...")

    segments = []
    sample_interval = int(fps * 5)  # Sample every 5 seconds
    prev_gray = None

    for frame_idx in range(0, total_frames, sample_interval):
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
        ret, frame = cap.read()

        if not ret:
            break

        # Downscale for analysis
        small = cv2.resize(frame, (320, 240))
        gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)

        if prev_gray is not None:
            # Calculate motion
            diff = cv2.absdiff(prev_gray, gray)
            motion_score = np.mean(diff)

            timestamp = frame_idx / fps
            segments.append({
                'time': timestamp,
                'motion': motion_score,
                'frame': frame_idx
            })

        prev_gray = gray

        # Progress
        if frame_idx % (sample_interval * 10) == 0:
            progress = (frame_idx / total_frames) * 100
            print(f"  Progress: {progress:.0f}%")

    cap.release()

    print(f"✅ Found {len(segments)} segments")

    # Sort by motion score (higher = more interesting)
    segments.sort(key=lambda x: x['motion'], reverse=True)

    # Select top segments to fill target duration
    selected = []
    total_selected = 0
    segment_duration = 5  # Each segment is 5 seconds

    for seg in segments:
        if total_selected + segment_duration <= target_duration:
            selected.append(seg)
            total_selected += segment_duration

        if total_selected >= target_duration:
            break

    # Sort selected by time
    selected.sort(key=lambda x: x['time'])

    print(f"\n✂️  Selected {len(selected)} segments ({total_selected}s total)")

    # Create output video using ffmpeg to preserve audio
    print(f"\n🎥 Creating highlight video with audio...")

    import subprocess
    import os

    # Create temp directory for segments
    temp_dir = "temp_segments"
    os.makedirs(temp_dir, exist_ok=True)

    # Extract each segment with audio using ffmpeg
    segment_files = []
    for i, seg in enumerate(selected):
        start_time = seg['time']
        segment_file = f"{temp_dir}/segment_{i:03d}.mp4"

        cmd = [
            'ffmpeg', '-y',
            '-ss', str(start_time),
            '-i', input_path,
            '-t', str(segment_duration),
            '-c', 'copy',
            '-avoid_negative_ts', '1',
            segment_file
        ]

        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        segment_files.append(segment_file)

        progress = ((i + 1) / len(selected)) * 100
        print(f"  Extracting: {progress:.0f}%")

    # Create concat file
    concat_file = f"{temp_dir}/concat.txt"
    with open(concat_file, 'w') as f:
        for seg_file in segment_files:
            f.write(f"file '{os.path.basename(seg_file)}'\n")

    # Concatenate all segments with audio
    print(f"  Merging segments...")
    output_abs_path = os.path.abspath(output_path)
    cmd = [
        'ffmpeg', '-y',
        '-f', 'concat',
        '-safe', '0',
        '-i', 'concat.txt',
        '-c', 'copy',
        output_abs_path
    ]
    result = subprocess.run(cmd, cwd=temp_dir, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  ⚠️  Warning: ffmpeg concat had issues: {result.stderr[:200]}")

    # Cleanup temp files
    import shutil
    shutil.rmtree(temp_dir)

    processing_time = time.time() - start_time

    print(f"\n✅ Complete!")
    print(f"⏱️  Processing time: {processing_time:.1f}s ({processing_time/60:.1f} min)")
    print(f"📦 Output: {output_path}")
    print(f"📊 Compression: {duration:.0f}s → {total_selected}s ({duration/total_selected:.1f}x)")

    return True

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python fast_process.py INPUT_VIDEO [OUTPUT_VIDEO] [DURATION]")
        sys.exit(1)

    input_video = sys.argv[1]
    output_video = sys.argv[2] if len(sys.argv) > 2 else 'highlights_fast.mp4'
    target_duration = int(sys.argv[3]) if len(sys.argv) > 3 else 180

    fast_process_video(input_video, output_video, target_duration)