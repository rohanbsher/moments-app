#!/usr/bin/env python3
"""
Comprehensive Feature Test Suite for Moments App
Tests all core features end-to-end with the fixed audio preservation
"""

import requests
import time
import json
import subprocess
from pathlib import Path
from typing import Dict, Tuple

BASE_URL = "http://localhost:8000"

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

def print_warning(text):
    print(f"{Colors.WARNING}⚠️  {text}{Colors.END}")

def get_video_info(video_path: str) -> Dict:
    """Get detailed video properties including audio"""
    try:
        cmd = [
            'ffprobe', '-v', 'quiet', '-print_format', 'json',
            '-show_format', '-show_streams', video_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        data = json.loads(result.stdout)

        duration = float(data['format']['duration'])
        size_mb = int(data['format']['size']) / (1024 * 1024)

        video_stream = next((s for s in data['streams'] if s['codec_type'] == 'video'), None)
        audio_streams = [s for s in data['streams'] if s['codec_type'] == 'audio']

        if video_stream:
            width = video_stream.get('width', 0)
            height = video_stream.get('height', 0)
            fps = eval(video_stream.get('r_frame_rate', '0/1'))
            video_codec = video_stream.get('codec_name', 'unknown')
        else:
            width = height = fps = 0
            video_codec = 'none'

        has_audio = len(audio_streams) > 0
        audio_codecs = [s.get('codec_name', 'unknown') for s in audio_streams]

        return {
            'duration': duration,
            'size_mb': size_mb,
            'resolution': f"{width}x{height}",
            'fps': fps,
            'video_codec': video_codec,
            'has_audio': has_audio,
            'audio_codecs': audio_codecs,
            'audio_count': len(audio_streams)
        }
    except Exception as e:
        print_fail(f"Could not get video info: {e}")
        return None

def test_backend_health() -> bool:
    """Test 1: Backend health check"""
    print_header("TEST 1: Backend Health Check")

    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_success(f"Backend is healthy")
            print_info(f"Service: {data.get('service')}")
            print_info(f"Version: {data.get('version')}")
            return True
        else:
            print_fail(f"Backend returned {response.status_code}")
            return False
    except Exception as e:
        print_fail(f"Cannot reach backend: {e}")
        return False

def test_video_upload_and_processing(video_path: str, test_name: str, target_duration: int = 30) -> Tuple[bool, Dict]:
    """Test video upload and processing pipeline"""
    print_header(f"TEST: {test_name}")

    if not Path(video_path).exists():
        print_fail(f"Video not found: {video_path}")
        return False, {}

    # Get input info
    print_info("Analyzing input video...")
    input_info = get_video_info(video_path)
    if not input_info:
        return False, {}

    print(f"  Duration: {input_info['duration']:.1f}s")
    print(f"  Size: {input_info['size_mb']:.1f} MB")
    print(f"  Resolution: {input_info['resolution']}")
    print(f"  FPS: {input_info['fps']:.1f}")
    print(f"  Video Codec: {input_info['video_codec']}")
    print(f"  Has Audio: {input_info['has_audio']}")
    if input_info['has_audio']:
        print(f"  Audio Codecs: {', '.join(input_info['audio_codecs'])}")

    # Upload
    print_info("Uploading video...")
    upload_start = time.time()

    try:
        with open(video_path, 'rb') as f:
            response = requests.post(
                f"{BASE_URL}/api/v1/upload",
                files={'file': f},
                data={'target_duration': target_duration, 'quality': 'high'},
                timeout=300
            )

        upload_time = time.time() - upload_start

        if response.status_code != 200:
            print_fail(f"Upload failed: {response.status_code} - {response.text}")
            return False, {}

        job_id = response.json()['job_id']
        upload_speed = input_info['size_mb'] / upload_time
        print_success(f"Upload completed in {upload_time:.1f}s ({upload_speed:.1f} MB/s)")
        print_info(f"Job ID: {job_id}")

    except Exception as e:
        print_fail(f"Upload error: {e}")
        return False, {}

    # Monitor processing
    print_info("Processing video (AI analysis + FFmpeg composition)...")
    process_start = time.time()
    last_progress = -1

    while True:
        try:
            response = requests.get(f"{BASE_URL}/api/v1/jobs/{job_id}/status", timeout=10)
            if response.status_code != 200:
                print_fail(f"Status check failed: {response.status_code}")
                return False, {}

            data = response.json()
            status = data['status']
            progress = data['progress']
            message = data.get('message', '')

            if progress != last_progress:
                print(f"  [{progress:3d}%] {message:50s}", end='\r')
                last_progress = progress

            if status == 'completed':
                process_time = time.time() - process_start
                print(f"\n", end='')
                print_success(f"Processing completed in {process_time:.1f}s ({process_time/60:.1f} min)")
                break
            elif status == 'failed':
                print_fail(f"Processing failed: {data.get('error_message', 'Unknown error')}")
                return False, {}

            time.sleep(1)

        except Exception as e:
            print_fail(f"Status check error: {e}")
            return False, {}

    # Download
    print_info("Downloading result...")
    output_path = f"test_output_{test_name.replace(' ', '_')}.mp4"

    try:
        response = requests.get(
            f"{BASE_URL}/api/v1/jobs/{job_id}/download",
            stream=True,
            timeout=120
        )

        if response.status_code != 200:
            print_fail(f"Download failed: {response.status_code}")
            return False, {}

        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        print_success(f"Download completed: {output_path}")

    except Exception as e:
        print_fail(f"Download error: {e}")
        return False, {}

    # Validate output
    print_info("Validating output quality...")
    output_info = get_video_info(output_path)

    if not output_info:
        print_fail("Could not analyze output video")
        return False, {}

    print(f"  Duration: {output_info['duration']:.1f}s (target: {target_duration}s)")
    print(f"  Size: {output_info['size_mb']:.1f} MB")
    print(f"  Resolution: {output_info['resolution']}")
    print(f"  FPS: {output_info['fps']:.1f}")
    print(f"  Has Audio: {output_info['has_audio']}")
    if output_info['has_audio']:
        print(f"  Audio Codecs: {', '.join(output_info['audio_codecs'])}")

    # Quality checks
    print_info("Quality Assessment:")
    all_passed = True

    # Audio preservation check
    if input_info['has_audio']:
        if output_info['has_audio']:
            print_success("Audio preserved in output")
        else:
            print_fail("Audio MISSING in output (CRITICAL BUG!)")
            all_passed = False
    else:
        if not output_info['has_audio']:
            print_success("Video-only processing correct (no audio in input)")
        else:
            print_warning("Output has audio but input didn't?")

    # Duration check
    duration_ratio = abs(output_info['duration'] - target_duration) / target_duration
    if duration_ratio < 0.15:  # Within 15% of target
        print_success(f"Duration close to target ({output_info['duration']:.0f}s)")
    else:
        print_warning(f"Duration differs from target by {duration_ratio*100:.0f}%")

    # Resolution check
    if output_info['resolution'] == input_info['resolution']:
        print_success(f"Resolution maintained ({output_info['resolution']})")
    else:
        print_warning(f"Resolution changed: {input_info['resolution']} → {output_info['resolution']}")

    # Compression check
    compression = ((input_info['size_mb'] - output_info['size_mb']) / input_info['size_mb'] * 100)
    print_info(f"Compression: {compression:.1f}% size reduction")

    # Results summary
    results = {
        'test_name': test_name,
        'input': input_info,
        'output': output_info,
        'upload_time': upload_time,
        'processing_time': process_time,
        'total_time': upload_time + process_time,
        'compression': compression,
        'audio_preserved': input_info['has_audio'] == output_info['has_audio'],
        'passed': all_passed,
        'output_file': output_path
    }

    return all_passed, results

def test_error_handling() -> bool:
    """Test error handling with invalid requests"""
    print_header("TEST: Error Handling")

    all_passed = True

    # Test 1: Invalid job ID
    print_info("Testing invalid job ID...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/jobs/invalid-job-id/status")
        if response.status_code == 404:
            print_success("Correctly returns 404 for invalid job ID")
        else:
            print_fail(f"Expected 404, got {response.status_code}")
            all_passed = False
    except Exception as e:
        print_fail(f"Error handling test failed: {e}")
        all_passed = False

    # Test 2: Upload without file
    print_info("Testing upload without file...")
    try:
        response = requests.post(f"{BASE_URL}/api/v1/upload", data={'target_duration': 30})
        if response.status_code in [400, 422]:
            print_success("Correctly rejects upload without file")
        else:
            print_warning(f"Expected 400/422, got {response.status_code}")
    except Exception as e:
        print_fail(f"Error handling test failed: {e}")
        all_passed = False

    return all_passed

def main():
    """Run comprehensive test suite"""
    print_header("🎬 MOMENTS APP - COMPREHENSIVE FEATURE TEST SUITE")
    print_info("Testing all core features with audio preservation fix")

    all_results = []

    # Test 1: Backend health
    if not test_backend_health():
        print_fail("Backend health check failed - cannot proceed")
        return False

    # Test 2: Create test video with audio
    print_header("SETUP: Creating Test Videos")
    print_info("Creating synthetic test video with audio...")

    test_video = "test_with_audio_30s.mp4"
    subprocess.run([
        'ffmpeg', '-f', 'lavfi', '-i', 'testsrc=duration=30:size=1280x720:rate=30',
        '-f', 'lavfi', '-i', 'sine=frequency=440:duration=30',
        '-c:v', 'libx264', '-c:a', 'aac', '-shortest', test_video, '-y'
    ], capture_output=True, timeout=60)

    if Path(test_video).exists():
        print_success(f"Created test video: {test_video}")
    else:
        print_fail("Could not create test video")
        return False

    # Test 3: Small video processing
    passed, results = test_video_upload_and_processing(test_video, "Small Video (30s)", target_duration=15)
    all_results.append(results)

    # Test 4: Error handling
    error_test_passed = test_error_handling()

    # Test 5: Find and test with real videos if available
    print_header("SEARCHING FOR REAL TEST VIDEOS")
    real_videos_found = []

    for pattern in ['*singing*.mp4', '*meeting*.mp4', '*sports*.mp4', '*party*.mp4', '*nature*.mp4']:
        for video in Path('.').rglob(pattern):
            if video.stat().st_size > 1_000_000:  # > 1MB
                real_videos_found.append(str(video))
                break

    if real_videos_found:
        print_success(f"Found {len(real_videos_found)} real test videos")
        for video in real_videos_found[:2]:  # Test max 2 real videos
            video_name = Path(video).stem
            passed, results = test_video_upload_and_processing(video, f"Real Video: {video_name}", target_duration=60)
            all_results.append(results)
    else:
        print_info("No real test videos found (this is okay)")

    # Final Report
    print_header("📊 FINAL TEST REPORT")

    total_tests = len(all_results)
    passed_tests = sum(1 for r in all_results if r.get('passed', False))

    print(f"\nTotal Tests Run: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {total_tests - passed_tests}")

    print("\nDetailed Results:")
    for result in all_results:
        status = "✅ PASS" if result.get('passed') else "❌ FAIL"
        print(f"\n{status} - {result['test_name']}")
        print(f"  Upload: {result['upload_time']:.1f}s")
        print(f"  Processing: {result['processing_time']:.1f}s")
        print(f"  Total: {result['total_time']:.1f}s")
        print(f"  Audio Preserved: {'Yes' if result['audio_preserved'] else 'No'}")
        print(f"  Output: {result['output_file']}")

    # Save results
    with open('comprehensive_test_results.json', 'w') as f:
        json.dump({
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'total_tests': total_tests,
            'passed': passed_tests,
            'failed': total_tests - passed_tests,
            'error_handling_passed': error_test_passed,
            'results': all_results
        }, f, indent=2)

    print_info("\nResults saved to: comprehensive_test_results.json")

    # Final verdict
    if passed_tests == total_tests and error_test_passed:
        print_header("🎉 ALL TESTS PASSED!")
        print_success("The Moments app is working correctly with audio preservation!")
        print_info("✅ Backend API functional")
        print_info("✅ Video upload working")
        print_info("✅ Processing pipeline working")
        print_info("✅ Audio preservation working")
        print_info("✅ Download working")
        print_info("✅ Error handling working")
        print("\n🚀 Ready for deployment and user testing!")
        return True
    else:
        print_header("⚠️  SOME TESTS FAILED")
        print_warning("Review the results above to identify issues")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
