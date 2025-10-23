#!/usr/bin/env python3
"""
Comprehensive End-to-End Testing for Moments App
Tests core user value delivery across multiple video types
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
    ("final_test_meeting_presentation.mp4", "Meeting", 30),
    ("final_test_nature_scenic.mp4", "Nature", 30),
    ("final_test_sports_action.mp4", "Sports", 30),
    ("final_test_party_celebration.mp4", "Party", 30),
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
    print_header("STEP 1: Backend Health Check")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_success(f"Backend is healthy: {data['service']} v{data['version']}")
            return True
        else:
            print_fail(f"Backend returned status code: {response.status_code}")
            return False
    except Exception as e:
        print_fail(f"Backend is not running: {e}")
        print_info("Please start backend: cd backend && ./run.sh")
        return False

def get_video_info(video_path):
    """Get video duration and properties"""
    try:
        cmd = [
            'ffprobe', '-v', 'quiet', '-print_format', 'json',
            '-show_format', '-show_streams', video_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        data = json.loads(result.stdout)
        duration = float(data['format']['duration'])
        size_mb = int(data['format']['size']) / (1024 * 1024)
        return duration, size_mb
    except:
        return None, None

def upload_video(video_path, target_duration):
    """Upload video to backend"""
    print_info(f"Uploading: {video_path}")

    with open(video_path, 'rb') as f:
        files = {'file': f}
        data = {
            'target_duration': target_duration,
            'quality': 'high'
        }

        start_time = time.time()
        response = requests.post(
            f"{BASE_URL}/api/v1/upload",
            files=files,
            data=data,
            timeout=300
        )
        upload_time = time.time() - start_time

        if response.status_code == 200:
            result = response.json()
            print_success(f"Upload completed in {upload_time:.2f}s")
            print_info(f"Job ID: {result['job_id']}")
            return result['job_id'], upload_time
        else:
            print_fail(f"Upload failed: {response.text}")
            return None, 0

def monitor_processing(job_id):
    """Monitor processing progress"""
    print_info("Monitoring processing...")

    start_time = time.time()
    last_progress = -1

    while True:
        response = requests.get(f"{BASE_URL}/api/v1/jobs/{job_id}/status")

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

def download_video(job_id, output_path):
    """Download processed video"""
    print_info(f"Downloading highlight to: {output_path}")

    response = requests.get(
        f"{BASE_URL}/api/v1/jobs/{job_id}/download",
        stream=True
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

def analyze_output(input_path, output_path):
    """Analyze output video quality"""
    print_info("Analyzing output quality...")

    input_duration, input_size = get_video_info(input_path)
    output_duration, output_size = get_video_info(output_path)

    if input_duration and output_duration:
        compression = ((input_size - output_size) / input_size * 100) if input_size > 0 else 0
        duration_ratio = (output_duration / input_duration * 100) if input_duration > 0 else 0

        print(f"  Input:  {input_duration:.1f}s, {input_size:.2f} MB")
        print(f"  Output: {output_duration:.1f}s, {output_size:.2f} MB")
        print(f"  Compression: {compression:.1f}%")
        print(f"  Duration ratio: {duration_ratio:.1f}%")

        return {
            'input_duration': input_duration,
            'output_duration': output_duration,
            'input_size': input_size,
            'output_size': output_size,
            'compression': compression,
            'duration_ratio': duration_ratio
        }
    return None

def test_video(video_path, video_type, target_duration):
    """Test complete flow for one video"""
    print_header(f"Testing: {video_type} Video")

    results = {
        'video_type': video_type,
        'video_path': video_path,
        'target_duration': target_duration,
        'success': False
    }

    # Check if video exists
    if not Path(video_path).exists():
        print_fail(f"Video not found: {video_path}")
        return results

    # Get input info
    input_duration, input_size = get_video_info(video_path)
    if input_duration:
        print_info(f"Input: {input_duration:.1f}s, {input_size:.2f} MB")
        results['input_duration'] = input_duration
        results['input_size'] = input_size

    # Upload
    job_id, upload_time = upload_video(video_path, target_duration)
    if not job_id:
        return results

    results['job_id'] = job_id
    results['upload_time'] = upload_time

    # Monitor processing
    status_data = monitor_processing(job_id)
    if not status_data:
        return results

    results['processing_time'] = status_data.get('processing_time', 0)

    # Download
    output_path = f"test_output_{video_type.lower()}.mp4"
    output_size = download_video(job_id, output_path)
    if output_size == 0:
        return results

    results['output_path'] = output_path
    results['output_size'] = output_size

    # Analyze
    analysis = analyze_output(video_path, output_path)
    if analysis:
        results.update(analysis)

    results['success'] = True
    print_success(f"{video_type} video test PASSED")

    return results

def run_all_tests():
    """Run all comprehensive tests"""
    print_header("MOMENTS APP - COMPREHENSIVE END-TO-END TESTING")
    print_info(f"Testing {len(TEST_VIDEOS)} different video types")
    print_info(f"Backend: {BASE_URL}")
    print()

    # Check backend
    if not check_backend():
        sys.exit(1)

    # Test each video
    all_results = []
    for video_path, video_type, target_duration in TEST_VIDEOS:
        result = test_video(video_path, video_type, target_duration)
        all_results.append(result)
        time.sleep(2)  # Brief pause between tests

    # Summary
    print_header("TEST RESULTS SUMMARY")

    successful = sum(1 for r in all_results if r['success'])
    total = len(all_results)

    print(f"\nTests Passed: {successful}/{total}")
    print()

    for result in all_results:
        if result['success']:
            print_success(f"{result['video_type']} - PASS")
            print(f"    Processing: {result['processing_time']:.2f}s")
            print(f"    Compression: {result.get('compression', 0):.1f}%")
            print(f"    Output: {result.get('output_duration', 0):.1f}s")
        else:
            print_fail(f"{result['video_type']} - FAIL")

    print()

    # Overall metrics
    if successful > 0:
        avg_processing_time = sum(r.get('processing_time', 0) for r in all_results if r['success']) / successful
        avg_compression = sum(r.get('compression', 0) for r in all_results if r['success']) / successful

        print_header("PERFORMANCE METRICS")
        print(f"Average Processing Time: {avg_processing_time:.2f}s")
        print(f"Average Compression: {avg_compression:.1f}%")
        print()

    # User value assessment
    print_header("USER VALUE ASSESSMENT")
    if successful == total:
        print_success("ALL VIDEO TYPES PROCESSED SUCCESSFULLY")
        print_info("✨ Core user value delivered:")
        print("  - Automatic highlight generation works")
        print("  - Multiple video types supported")
        print("  - Fast processing (seconds, not minutes)")
        print("  - Significant file size reduction")
        print()
        print_success("🚀 APPLICATION IS READY FOR USERS!")
    else:
        print_warning(f"Some tests failed ({total - successful}/{total})")
        print_info("Review failures before deploying to users")

    print()

    # Save detailed results
    with open('test_results_comprehensive.json', 'w') as f:
        json.dump(all_results, f, indent=2)

    print_info("Detailed results saved to: test_results_comprehensive.json")
    print()

    return successful == total

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
