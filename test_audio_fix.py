#!/usr/bin/env python3
"""Quick test to verify audio preservation with FFmpeg implementation"""

import requests
import time
import json
from pathlib import Path
import subprocess

BASE_URL = "http://localhost:8000"

def get_video_info(video_path):
    """Get audio stream info"""
    try:
        cmd = [
            'ffprobe', '-v', 'quiet', '-print_format', 'json',
            '-show_streams', video_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        data = json.loads(result.stdout)

        has_audio = any(s.get('codec_type') == 'audio' for s in data.get('streams', []))
        audio_codec = next(
            (s.get('codec_name') for s in data.get('streams', []) if s.get('codec_type') == 'audio'),
            'none'
        )

        return {'has_audio': has_audio, 'audio_codec': audio_codec}
    except:
        return {'has_audio': False, 'audio_codec': 'error'}

# Find a test video
test_video = None
for path in Path('.').rglob('*inging*.mp4'):
    if path.stat().st_size > 1000000:  # > 1MB
        test_video = str(path)
        break

if not test_video:
    print("❌ No test video found")
    exit(1)

print(f"Testing with: {test_video}")
input_info = get_video_info(test_video)
print(f"Input - Has Audio: {input_info['has_audio']}, Codec: {input_info['audio_codec']}")

# Upload
print("\nUploading...")
with open(test_video, 'rb') as f:
    response = requests.post(
        f"{BASE_URL}/api/v1/upload",
        files={'file': f},
        data={'target_duration': 30, 'quality': 'high'},
        timeout=300
    )

if response.status_code != 200:
    print(f"❌ Upload failed: {response.status_code}")
    exit(1)

job_id = response.json()['job_id']
print(f"✅ Uploaded - Job ID: {job_id}")

# Wait for processing
print("\nProcessing...")
while True:
    response = requests.get(f"{BASE_URL}/api/v1/jobs/{job_id}/status")
    data = response.json()
    status = data['status']
    progress = data['progress']

    print(f"  [{progress:3d}%] {data.get('message', '')}         ", end='\r')

    if status == 'completed':
        print("\n✅ Processing complete!")
        break
    elif status == 'failed':
        print(f"\n❌ Failed: {data.get('error_message')}")
        exit(1)

    time.sleep(1)

# Download and check audio
print("\nDownloading...")
response = requests.get(f"{BASE_URL}/api/v1/jobs/{job_id}/download", stream=True)
output_path = "test_audio_output.mp4"

with open(output_path, 'wb') as f:
    for chunk in response.iter_content(chunk_size=8192):
        f.write(chunk)

output_info = get_video_info(output_path)
print(f"\nOutput - Has Audio: {output_info['has_audio']}, Codec: {output_info['audio_codec']}")

# Result
print("\n" + "="*60)
if output_info['has_audio']:
    print("✅ SUCCESS! Audio preserved in output!")
    print(f"   Audio codec: {output_info['audio_codec']}")
else:
    print("❌ FAILED! Audio still missing from output!")
print("="*60)
