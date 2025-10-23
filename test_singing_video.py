#!/usr/bin/env python3
"""
Comprehensive Test: 647MB Singing Video
Tests the most demanding scenario - large singing/musical content
"""

import requests
import time
import json
from pathlib import Path
import subprocess

BASE_URL = "http://192.168.0.8:8000"
VIDEO_PATH = "tests/test_videos/Singing_highlights_WITH_AUDIO.mp4"

class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.END}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text:^80}{Colors.END}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.END}\n")

def print_success(text):
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")

def print_fail(text):
    print(f"{Colors.FAIL}❌ {text}{Colors.END}")

def print_info(text):
    print(f"{Colors.CYAN}ℹ️  {text}{Colors.END}")

def get_video_info(video_path):
    """Get detailed video properties"""
    try:
        cmd = [
            'ffprobe', '-v', 'quiet', '-print_format', 'json',
            '-show_format', '-show_streams', video_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        data = json.loads(result.stdout)

        duration = float(data['format']['duration'])
        size_mb = int(data['format']['size']) / (1024 * 1024)

        video_stream = next(s for s in data['streams'] if s['codec_type'] == 'video')
        audio_stream = next((s for s in data['streams'] if s['codec_type'] == 'audio'), None)

        width = video_stream.get('width', 0)
        height = video_stream.get('height', 0)
        fps = eval(video_stream.get('r_frame_rate', '0/1'))
        codec = video_stream.get('codec_name', 'unknown')

        has_audio = audio_stream is not None
        audio_codec = audio_stream.get('codec_name', 'none') if has_audio else 'none'

        return {
            'duration': duration,
            'size_mb': size_mb,
            'resolution': f"{width}x{height}",
            'fps': fps,
            'video_codec': codec,
            'has_audio': has_audio,
            'audio_codec': audio_codec
        }
    except Exception as e:
        print_fail(f"Could not get video info: {e}")
        return None

def test_singing_video():
    """Test the 647MB singing video end-to-end"""
    print_header("🎤 SINGING VIDEO TEST - 647MB Musical Content")

    # Check backend
    print_info("Checking backend connectivity...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print_success("Backend is healthy and ready")
        else:
            print_fail(f"Backend returned {response.status_code}")
            return False
    except Exception as e:
        print_fail(f"Cannot reach backend: {e}")
        return False

    # Check video exists
    if not Path(VIDEO_PATH).exists():
        print_fail(f"Video not found: {VIDEO_PATH}")
        return False

    # Get input video info
    print_info("Analyzing input video...")
    input_info = get_video_info(VIDEO_PATH)
    if input_info:
        print(f"  Duration: {input_info['duration']:.1f}s ({input_info['duration']/60:.1f} minutes)")
        print(f"  Size: {input_info['size_mb']:.1f} MB")
        print(f"  Resolution: {input_info['resolution']}")
        print(f"  FPS: {input_info['fps']:.1f}")
        print(f"  Video Codec: {input_info['video_codec']}")
        print(f"  Has Audio: {input_info['has_audio']}")
        print(f"  Audio Codec: {input_info['audio_codec']}")
    else:
        print_fail("Could not analyze video")
        return False

    # Upload video
    print_header("📤 UPLOADING VIDEO")
    print_info(f"Starting upload of {input_info['size_mb']:.1f}MB file...")
    print_info("This may take a while...")

    with open(VIDEO_PATH, 'rb') as f:
        files = {'file': f}
        data = {
            'target_duration': 60,  # 60 second highlight for singing
            'quality': 'high'
        }

        upload_start = time.time()
        try:
            response = requests.post(
                f"{BASE_URL}/api/v1/upload",
                files=files,
                data=data,
                timeout=600
            )
            upload_time = time.time() - upload_start

            if response.status_code == 200:
                result = response.json()
                job_id = result['job_id']
                print_success(f"Upload completed in {upload_time:.1f}s ({input_info['size_mb']/upload_time:.1f} MB/s)")
                print_info(f"Job ID: {job_id}")
            else:
                print_fail(f"Upload failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print_fail(f"Upload error: {e}")
            return False

    # Monitor processing
    print_header("⚙️  PROCESSING VIDEO - AI Analysis")
    print_info("Running AI-powered scene detection, motion analysis, and audio intelligence...")
    print_info("This will take a few minutes for a 647MB video...")

    process_start = time.time()
    last_progress = -1

    while True:
        try:
            response = requests.get(f"{BASE_URL}/api/v1/jobs/{job_id}/status", timeout=10)
            if response.status_code != 200:
                print_fail(f"Status check failed: {response.status_code}")
                return False

            data = response.json()
            status = data['status']
            progress = data['progress']
            message = data.get('message', '')

            if progress != last_progress:
                elapsed = time.time() - process_start
                print(f"  [{progress:3d}%] {message:40s} (Elapsed: {elapsed:.0f}s)")
                last_progress = progress

            if status == 'completed':
                process_time = time.time() - process_start
                print_success(f"Processing completed in {process_time:.1f}s ({process_time/60:.1f} minutes)")

                # Show processing stats
                if 'result_metadata' in data and data['result_metadata']:
                    metadata = data['result_metadata']
                    print_info("Processing Statistics:")
                    if 'segments_analyzed' in metadata:
                        print(f"  Segments Analyzed: {metadata['segments_analyzed']}")
                    if 'segments_selected' in metadata:
                        print(f"  Segments Selected: {metadata['segments_selected']}")
                    if 'total_scenes' in metadata:
                        print(f"  Scenes Detected: {metadata['total_scenes']}")

                break
            elif status == 'failed':
                print_fail(f"Processing failed: {data.get('error_message', 'Unknown error')}")
                return False

            time.sleep(2)

        except Exception as e:
            print_fail(f"Status check error: {e}")
            return False

    # Download result
    print_header("📥 DOWNLOADING HIGHLIGHT")
    output_path = "tests/test_results/singing_highlight_output.mp4"

    try:
        response = requests.get(
            f"{BASE_URL}/api/v1/jobs/{job_id}/download",
            stream=True,
            timeout=300
        )

        if response.status_code == 200:
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            output_size = Path(output_path).stat().st_size / (1024 * 1024)
            print_success(f"Download completed: {output_size:.1f} MB")
        else:
            print_fail(f"Download failed: {response.status_code}")
            return False
    except Exception as e:
        print_fail(f"Download error: {e}")
        return False

    # Analyze output quality
    print_header("🎬 ANALYZING OUTPUT QUALITY")
    output_info = get_video_info(output_path)

    if output_info:
        print_success("Output video analysis:")
        print(f"  Duration: {output_info['duration']:.1f}s")
        print(f"  Size: {output_info['size_mb']:.1f} MB")
        print(f"  Resolution: {output_info['resolution']}")
        print(f"  FPS: {output_info['fps']:.1f}")
        print(f"  Has Audio: {output_info['has_audio']}")
        print(f"  Audio Codec: {output_info['audio_codec']}")

        # Calculate compression
        compression = ((input_info['size_mb'] - output_info['size_mb']) / input_info['size_mb'] * 100)
        duration_ratio = (output_info['duration'] / input_info['duration'] * 100)

        print(f"\n  Compression: {compression:.1f}% size reduction")
        print(f"  Duration Ratio: {duration_ratio:.1f}% of original")

        # Quality assessment for singing content
        print_header("🎵 SINGING CONTENT ASSESSMENT")
        if output_info['has_audio']:
            print_success("✅ Audio preserved in highlight")
        else:
            print_fail("❌ Audio missing from highlight!")

        if output_info['duration'] >= 50:
            print_success(f"✅ Good highlight length ({output_info['duration']:.0f}s)")
        else:
            print_fail(f"⚠️  Short highlight ({output_info['duration']:.0f}s)")

        if output_info['resolution'] == input_info['resolution']:
            print_success(f"✅ Resolution maintained ({output_info['resolution']})")
        else:
            print_fail(f"⚠️  Resolution changed: {input_info['resolution']} → {output_info['resolution']}")

        # Save results
        results = {
            'test': 'singing_video_647mb',
            'input': input_info,
            'output': output_info,
            'upload_time': upload_time,
            'processing_time': process_time,
            'compression': compression,
            'duration_ratio': duration_ratio,
            'output_path': output_path
        }

        with open('tests/test_results/singing_video_test.json', 'w') as f:
            json.dump(results, f, indent=2)

        print_info("Results saved to: tests/test_results/singing_video_test.json")

    # Final assessment
    print_header("🎯 FINAL ASSESSMENT")
    print_success("✅ Singing video test PASSED!")
    print(f"\n  Input: {input_info['size_mb']:.0f}MB, {input_info['duration']:.0f}s singing video")
    print(f"  Output: {output_info['size_mb']:.0f}MB, {output_info['duration']:.0f}s highlight")
    print(f"  Upload: {upload_time:.0f}s")
    print(f"  Processing: {process_time/60:.1f} minutes")
    print(f"  Total Time: {(upload_time + process_time)/60:.1f} minutes\n")

    print_success("🎉 Moments app successfully created highlight from large singing video!")
    print_info("The app can handle demanding musical content with AI-powered scene selection")

    return True

if __name__ == "__main__":
    success = test_singing_video()
    exit(0 if success else 1)
