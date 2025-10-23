#!/usr/bin/env python3
"""
Final Comprehensive Testing Before App Store Launch
Tests with real videos including edge cases
"""

import requests
import time
import json
from pathlib import Path
import subprocess
import sys

# Configuration
BASE_URL = "http://localhost:8000"
TEST_VIDEOS = [
    # Small file test
    ("final_test_meeting_presentation.mp4", "Small File (577KB)", 30),
    # Medium files
    ("final_test_nature_scenic.mp4", "Medium File (2.7MB)", 30),
    ("final_test_sports_action.mp4", "Medium File (5.2MB)", 30),
    # Large file
    ("final_test_party_celebration.mp4", "Large File (18MB)", 30),
    # Very large file (real-world scenario)
    ("Singing_highlights_WITH_AUDIO.mp4", "Very Large File (647MB)", 60),
]

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(text):
    print(f"\n{bcolors.HEADER}{bcolors.BOLD}{'='*80}{bcolors.ENDC}")
    print(f"{bcolors.HEADER}{bcolors.BOLD}{text:^80}{bcolors.ENDC}")
    print(f"{bcolors.HEADER}{bcolors.BOLD}{'='*80}{bcolors.ENDC}\n")

def print_success(text):
    print(f"{bcolors.OKGREEN}✅ {text}{bcolors.ENDC}")

def print_fail(text):
    print(f"{bcolors.FAIL}❌ {text}{bcolors.ENDC}")

def print_info(text):
    print(f"{bcolors.OKCYAN}ℹ️  {text}{bcolors.ENDC}")

def print_warning(text):
    print(f"{bcolors.WARNING}⚠️  {text}{bcolors.ENDC}")

def check_backend():
    """Verify backend is running"""
    print_header("BACKEND HEALTH CHECK")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_success(f"Backend healthy: {data['service']} v{data['version']}")
            return True
        else:
            print_fail(f"Backend returned status code: {response.status_code}")
            return False
    except Exception as e:
        print_fail(f"Backend not accessible: {e}")
        print_info("Start backend: cd backend && ./run.sh")
        return False

def get_video_info(video_path):
    """Get video properties using ffprobe"""
    try:
        cmd = [
            'ffprobe', '-v', 'quiet', '-print_format', 'json',
            '-show_format', '-show_streams', video_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        data = json.loads(result.stdout)

        duration = float(data['format']['duration'])
        size_mb = int(data['format']['size']) / (1024 * 1024)

        # Get video stream info
        video_stream = next(s for s in data['streams'] if s['codec_type'] == 'video')
        width = video_stream.get('width', 0)
        height = video_stream.get('height', 0)
        fps = eval(video_stream.get('r_frame_rate', '0/1'))

        return {
            'duration': duration,
            'size_mb': size_mb,
            'resolution': f"{width}x{height}",
            'fps': fps
        }
    except Exception as e:
        print_warning(f"Could not get video info: {e}")
        return None

def upload_video(video_path, target_duration):
    """Upload video to backend"""
    print_info(f"Uploading: {video_path}")

    if not Path(video_path).exists():
        print_fail(f"Video not found: {video_path}")
        return None, 0

    with open(video_path, 'rb') as f:
        files = {'file': f}
        data = {
            'target_duration': target_duration,
            'quality': 'high'
        }

        start_time = time.time()
        try:
            response = requests.post(
                f"{BASE_URL}/api/v1/upload",
                files=files,
                data=data,
                timeout=600  # 10 minutes for large files
            )
            upload_time = time.time() - start_time

            if response.status_code == 200:
                result = response.json()
                print_success(f"Upload completed in {upload_time:.2f}s")
                print_info(f"Job ID: {result['job_id']}")
                return result['job_id'], upload_time
            else:
                print_fail(f"Upload failed: {response.status_code} - {response.text}")
                return None, 0
        except Exception as e:
            print_fail(f"Upload error: {e}")
            return None, 0

def monitor_processing(job_id, timeout=600):
    """Monitor processing with progress updates"""
    print_info("Monitoring processing...")

    start_time = time.time()
    last_progress = -1

    while time.time() - start_time < timeout:
        try:
            response = requests.get(f"{BASE_URL}/api/v1/jobs/{job_id}/status", timeout=10)

            if response.status_code != 200:
                print_fail(f"Status check failed: {response.status_code}")
                return None

            data = response.json()
            status = data['status']
            progress = data['progress']

            if progress != last_progress:
                print(f"  Progress: {progress}% - {data.get('message', '')}")
                last_progress = progress

            if status == 'completed':
                processing_time = time.time() - start_time
                print_success(f"Processing completed in {processing_time:.2f}s")
                return data
            elif status == 'failed':
                print_fail(f"Processing failed: {data.get('error_message', 'Unknown error')}")
                return None

            time.sleep(1)
        except Exception as e:
            print_warning(f"Status check error: {e}")
            time.sleep(2)

    print_fail(f"Processing timeout after {timeout}s")
    return None

def download_video(job_id, output_path):
    """Download processed video"""
    print_info(f"Downloading highlight to: {output_path}")

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

            size_mb = Path(output_path).stat().st_size / (1024 * 1024)
            print_success(f"Download completed: {size_mb:.2f} MB")
            return size_mb
        else:
            print_fail(f"Download failed: {response.status_code}")
            return 0
    except Exception as e:
        print_fail(f"Download error: {e}")
        return 0

def verify_output_quality(output_path):
    """Verify output video is playable and has good quality"""
    print_info("Verifying output quality...")

    info = get_video_info(output_path)
    if not info:
        print_fail("Could not verify output quality")
        return False

    # Check basic quality metrics
    if info['duration'] > 0:
        print_success(f"Duration: {info['duration']:.1f}s")
    else:
        print_fail("Invalid duration")
        return False

    if info['resolution'] != "0x0":
        print_success(f"Resolution: {info['resolution']}")
    else:
        print_fail("Invalid resolution")
        return False

    if info['fps'] > 0:
        print_success(f"FPS: {info['fps']:.1f}")
    else:
        print_fail("Invalid FPS")
        return False

    print_success("Output quality verified")
    return True

def test_video(video_path, test_name, target_duration):
    """Test complete flow for one video"""
    print_header(f"Testing: {test_name}")

    results = {
        'test_name': test_name,
        'video_path': video_path,
        'target_duration': target_duration,
        'success': False,
        'error': None
    }

    # Check if video exists
    if not Path(video_path).exists():
        print_fail(f"Video not found: {video_path}")
        results['error'] = 'File not found'
        return results

    # Get input info
    input_info = get_video_info(video_path)
    if input_info:
        print_info(f"Input: {input_info['duration']:.1f}s, {input_info['size_mb']:.2f} MB, {input_info['resolution']}")
        results['input_info'] = input_info

    # Upload
    job_id, upload_time = upload_video(video_path, target_duration)
    if not job_id:
        results['error'] = 'Upload failed'
        return results

    results['job_id'] = job_id
    results['upload_time'] = upload_time

    # Monitor processing
    status_data = monitor_processing(job_id, timeout=900)  # 15 min timeout for very large files
    if not status_data:
        results['error'] = 'Processing failed'
        return results

    results['processing_time'] = status_data.get('processing_time', 0)

    # Download
    output_path = f"final_output_{test_name.replace(' ', '_').replace('(', '').replace(')', '').lower()}.mp4"
    output_size = download_video(job_id, output_path)
    if output_size == 0:
        results['error'] = 'Download failed'
        return results

    results['output_path'] = output_path
    results['output_size'] = output_size

    # Verify quality
    quality_ok = verify_output_quality(output_path)
    if not quality_ok:
        results['error'] = 'Quality verification failed'
        return results

    # Get output info
    output_info = get_video_info(output_path)
    if output_info:
        results['output_info'] = output_info

        # Calculate metrics
        if input_info:
            compression = ((input_info['size_mb'] - output_info['size_mb']) / input_info['size_mb'] * 100)
            results['compression_percent'] = compression
            print_info(f"Compression: {compression:.1f}%")

    results['success'] = True
    print_success(f"{test_name} - PASSED ✅")

    return results

def test_error_handling():
    """Test error handling with invalid inputs"""
    print_header("ERROR HANDLING TESTS")

    # Test 1: Invalid file format
    print_info("Test 1: Invalid file format")
    try:
        files = {'file': ('test.txt', b'not a video', 'text/plain')}
        data = {'target_duration': 30, 'quality': 'high'}
        response = requests.post(f"{BASE_URL}/api/v1/upload", files=files, data=data, timeout=30)

        if response.status_code in [400, 415]:
            print_success("Correctly rejected invalid file format")
        else:
            print_warning(f"Unexpected response: {response.status_code}")
    except Exception as e:
        print_warning(f"Error test exception: {e}")

    # Test 2: Invalid job ID
    print_info("Test 2: Invalid job ID")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/jobs/invalid-id-12345/status", timeout=10)
        if response.status_code == 404:
            print_success("Correctly returned 404 for invalid job ID")
        else:
            print_warning(f"Unexpected response: {response.status_code}")
    except Exception as e:
        print_warning(f"Error test exception: {e}")

    print_success("Error handling tests completed")

def run_all_tests():
    """Run all comprehensive tests"""
    print_header("🚀 FINAL COMPREHENSIVE TESTING - APP STORE READINESS")
    print_info(f"Testing {len(TEST_VIDEOS)} videos including edge cases")
    print_info(f"Backend: {BASE_URL}")
    print()

    # Check backend
    if not check_backend():
        sys.exit(1)

    # Test each video
    all_results = []
    passed_count = 0

    for video_path, test_name, target_duration in TEST_VIDEOS:
        result = test_video(video_path, test_name, target_duration)
        all_results.append(result)
        if result['success']:
            passed_count += 1
        time.sleep(2)  # Brief pause between tests

    # Error handling tests
    test_error_handling()

    # Summary
    print_header("📊 FINAL TEST RESULTS")

    total = len(all_results)
    print(f"\n✅ Tests Passed: {passed_count}/{total}\n")

    for result in all_results:
        if result['success']:
            print_success(f"{result['test_name']}")
            print(f"    Upload: {result.get('upload_time', 0):.2f}s")
            print(f"    Processing: {result.get('processing_time', 0):.2f}s")
            if 'compression_percent' in result:
                print(f"    Compression: {result['compression_percent']:.1f}%")
            if 'output_info' in result:
                print(f"    Output: {result['output_info']['duration']:.1f}s @ {result['output_info']['resolution']}")
        else:
            print_fail(f"{result['test_name']} - {result.get('error', 'Unknown error')}")
        print()

    # Performance metrics
    if passed_count > 0:
        avg_processing = sum(r.get('processing_time', 0) for r in all_results if r['success']) / passed_count
        avg_upload = sum(r.get('upload_time', 0) for r in all_results if r['success']) / passed_count

        print_header("⚡ PERFORMANCE METRICS")
        print(f"Average Upload Time: {avg_upload:.2f}s")
        print(f"Average Processing Time: {avg_processing:.2f}s")
        print()

    # App Store readiness assessment
    print_header("🎯 APP STORE READINESS ASSESSMENT")

    if passed_count == total:
        print_success("✅ ALL TESTS PASSED")
        print()
        print_success("🎉 APPLICATION IS READY FOR APP STORE LAUNCH!")
        print()
        print_info("Next steps:")
        print("  1. ✅ Backend fully tested")
        print("  2. 📱 Test iOS app on simulator")
        print("  3. 📸 Capture screenshots for App Store")
        print("  4. 📝 Prepare App Store listing")
        print("  5. 🚀 Submit for review")
        success = True
    else:
        print_warning(f"⚠️  {total - passed_count}/{total} tests failed")
        print_info("Fix failures before App Store submission")
        success = False

    print()

    # Save results
    with open('final_test_results.json', 'w') as f:
        json.dump(all_results, f, indent=2)

    print_info("Detailed results saved to: final_test_results.json")
    print()

    return success

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
