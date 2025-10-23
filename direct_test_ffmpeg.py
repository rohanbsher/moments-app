#!/usr/bin/env python3
"""Direct test of the simple_processor to verify FFmpeg implementation"""

import sys
import subprocess
import json
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))

from core.simple_processor import SimpleVideoProcessor, SimpleConfig

# Find a small test video
test_video = None
for path in Path('.').rglob('*singing*.mp4'):
    size = path.stat().st_size
    if 1_000_000 < size < 10_000_000:  # 1MB - 10MB
        test_video = str(path)
        break

if not test_video:
    # Find ANY video
    for path in Path('backend/storage/uploads').glob('*.mp4'):
        if path.stat().st_size < 50_000_000:  # < 50MB
            test_video = str(path)
            break

if not test_video:
    print("❌ No suitable test video found")
    sys.exit(1)

def check_audio(video_path):
    """Check if video has audio"""
    cmd = ['ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_streams', video_path]
    result = subprocess.run(cmd, capture_output=True, text=True)
    data = json.loads(result.stdout)
    audio_streams = [s for s in data.get('streams', []) if s.get('codec_type') == 'audio']
    return len(audio_streams) > 0, [s.get('codec_name') for s in audio_streams]

print(f"Testing with: {test_video}")
has_audio, codecs = check_audio(test_video)
print(f"Input audio: {has_audio}, codecs: {codecs}")

# Configure processor for SHORT output
config = SimpleConfig(
    target_duration=20,  # 20 seconds
    min_segment_duration=0.5,
    max_segment_duration=5.0
)

# Process
print("\nProcessing...")
processor = SimpleVideoProcessor(config)
output_path = "test_direct_output.mp4"

try:
    result = processor.process_video(test_video, output_path)
    print(f"\n✅ Processing complete!")
    print(f"   Processing time: {result['processing_time']:.1f}s")
    print(f"   Output duration: {result['output_duration']:.1f}s")
    print(f"   Segments selected: {result['segments_selected']}")

    # Check output audio
    has_audio_out, codecs_out = check_audio(output_path)
    print(f"\nOutput audio: {has_audio_out}, codecs: {codecs_out}")

    if has_audio and has_audio_out:
        print("\n🎉 SUCCESS! Audio preserved!")
    elif has_audio and not has_audio_out:
        print("\n❌ FAILED! Input had audio but output doesn't!")
    else:
        print("\n✅ Video-only processing works (no audio in input)")

except Exception as e:
    print(f"\n❌ Processing failed: {e}")
    import traceback
    traceback.print_exc()
