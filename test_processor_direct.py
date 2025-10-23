#!/usr/bin/env python3
import sys
from pathlib import Path
import subprocess
import json

sys.path.insert(0, str(Path(__file__).parent))
from core.simple_processor import SimpleVideoProcessor, SimpleConfig

def check_audio(path):
    cmd = ['ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_streams', path]
    result = subprocess.run(cmd, capture_output=True, text=True)
    data = json.loads(result.stdout)
    audio = [s for s in data['streams'] if s['codec_type'] == 'audio']
    return len(audio) > 0, [s['codec_name'] for s in audio]

input_video = "test_video_with_audio.mp4"
output_video = "test_processor_output.mp4"

print(f"Input: {input_video}")
has_audio, codecs = check_audio(input_video)
print(f"  Has audio: {has_audio}, codecs: {codecs}")

config = SimpleConfig(target_duration=15, max_segment_duration=5.0)
processor = SimpleVideoProcessor(config)

print("\nProcessing...")
result = processor.process_video(input_video, output_video)

print(f"\n✅ Processing complete in {result['processing_time']:.1f}s")
print(f"Output: {output_video}")
has_audio_out, codecs_out = check_audio(output_video)
print(f"  Has audio: {has_audio_out}, codecs: {codecs_out}")

if has_audio_out:
    print("\n🎉 SUCCESS! FFmpeg preserved audio!")
else:
    print("\n❌ FAILED! Audio missing in output!")
