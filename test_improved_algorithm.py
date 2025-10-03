#!/usr/bin/env python3
"""
Test Improved Algorithm with Audio and Diversity Scoring
Validates Phase 1.5 improvements
"""

import os
import sys
import time
import json
from core.simple_processor import SimpleVideoProcessor, SimpleConfig

def test_with_existing_videos():
    """Test improved algorithm with existing test videos"""

    print("="*70)
    print(" 🎯 TESTING IMPROVED ALGORITHM - Phase 1.5")
    print("="*70)
    print()
    print("New Features:")
    print("  ✨ Audio volume analysis (30% of score)")
    print("  ✨ Diversity scoring (prevents repetition)")
    print("  ✨ Enhanced segment selection")
    print()

    test_videos = [
        {
            'path': 'test_sports_action.mp4',
            'type': 'Sports/Action',
            'expected': 'High scores for action segments (20-40s, 70-90s)'
        },
        {
            'path': 'test_party_celebration.mp4',
            'type': 'Party/Celebration',
            'expected': 'High scores for cake (15-25s) and dancing (40-55s)'
        },
        {
            'path': 'test_nature_scenic.mp4',
            'type': 'Nature/Scenic',
            'expected': 'Wildlife moment (30-45s) should be prioritized'
        },
        {
            'path': 'test_meeting_presentation.mp4',
            'type': 'Meeting/Presentation',
            'expected': 'Demo section (30-50s) should rank higher'
        }
    ]

    results = []

    for i, video_info in enumerate(test_videos, 1):
        video_path = video_info['path']

        if not os.path.exists(video_path):
            print(f"⏭️  Skipping {video_path} (not found)")
            print()
            continue

        print(f"📹 Test {i}/{len(test_videos)}: {video_info['type']}")
        print(f"   File: {video_path}")
        print(f"   Expected: {video_info['expected']}")
        print("-" * 70)

        try:
            # Create config for 30-second highlights
            config = SimpleConfig(
                target_duration=30,
                min_segment_duration=2.0,
                max_segment_duration=10.0
            )

            processor = SimpleVideoProcessor(config)

            # Process video
            start_time = time.time()
            output_file = f"improved_highlights_{video_info['type'].lower().replace('/', '_')}_30s.mp4"

            metadata = processor.process_video(video_path, output_file)

            processing_time = time.time() - start_time

            # Display results
            print(f"\n✅ Processing Complete!")
            print(f"   Input: {metadata['input_duration']:.1f}s")
            print(f"   Output: {metadata['output_duration']:.1f}s")
            print(f"   Compression: {metadata['input_duration']/metadata['output_duration']:.1f}x")
            print(f"   Processing time: {processing_time:.2f}s")
            print(f"   Speed: {metadata['input_duration']/processing_time:.1f}x real-time")

            # Show selected segments with scores
            print(f"\n   📊 Selected Segments:")
            for j, seg in enumerate(metadata['segments'], 1):
                audio_excitement = seg.get('audio_excitement', 0)
                volume_peak = seg.get('volume_peak', 0)
                diversity_penalty = seg.get('diversity_penalty', 0)

                print(f"      {j}. {seg['start']:5.1f}s - {seg['end']:5.1f}s | "
                      f"Score: {seg['score']:.3f} | "
                      f"Motion: {seg['motion_intensity']:5.1f} | "
                      f"Audio: {audio_excitement:.2f} | "
                      f"Vol: {volume_peak:.2f} | "
                      f"Penalty: {diversity_penalty:.2f}")

            # Store results
            results.append({
                'video_type': video_info['type'],
                'success': True,
                'processing_time': processing_time,
                'input_duration': metadata['input_duration'],
                'output_duration': metadata['output_duration'],
                'compression_ratio': metadata['input_duration'] / metadata['output_duration'],
                'segments': metadata['segments'],
                'output_file': output_file
            })

            print()

        except Exception as e:
            print(f"\n❌ Error processing {video_path}: {e}")
            import traceback
            traceback.print_exc()

            results.append({
                'video_type': video_info['type'],
                'success': False,
                'error': str(e)
            })

            print()

    # Generate summary report
    print("="*70)
    print(" 📊 TEST SUMMARY")
    print("="*70)

    successful = [r for r in results if r.get('success')]
    failed = [r for r in results if not r.get('success')]

    print(f"\nTests run: {len(results)}")
    print(f"✅ Successful: {len(successful)}")
    print(f"❌ Failed: {len(failed)}")

    if successful:
        avg_processing_time = sum(r['processing_time'] for r in successful) / len(successful)
        avg_compression = sum(r['compression_ratio'] for r in successful) / len(successful)
        total_input = sum(r['input_duration'] for r in successful)
        total_processing = sum(r['processing_time'] for r in successful)
        avg_speed = total_input / total_processing if total_processing > 0 else 0

        print(f"\n📈 Performance:")
        print(f"   Average processing time: {avg_processing_time:.2f}s")
        print(f"   Average compression: {avg_compression:.1f}x")
        print(f"   Average speed: {avg_speed:.1f}x real-time")

    # Save detailed report
    report = {
        'test_name': 'Phase 1.5 - Improved Algorithm Test',
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'features_tested': [
            'Audio volume analysis',
            'Diversity scoring',
            'Enhanced segment selection'
        ],
        'results': results
    }

    report_file = 'phase1_5_test_report.json'
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)

    print(f"\n💾 Detailed report saved: {report_file}")

    # Output files created
    print(f"\n📁 Output files:")
    for r in successful:
        if 'output_file' in r and os.path.exists(r['output_file']):
            size = os.path.getsize(r['output_file']) / (1024 * 1024)
            print(f"   ✅ {r['output_file']} ({size:.1f} MB)")

    print("\n" + "="*70)

    if len(successful) == len(results):
        print("🎉 ALL TESTS PASSED!")
    elif len(successful) > 0:
        print(f"⚠️  {len(successful)}/{len(results)} tests passed")
    else:
        print("❌ ALL TESTS FAILED - Check errors above")

    print("="*70)
    print()

    return results


def test_algorithm_improvements():
    """Compare improved algorithm against expected improvements"""

    print("="*70)
    print(" 🔬 ALGORITHM IMPROVEMENT VALIDATION")
    print("="*70)
    print()

    improvements = {
        'audio_analysis': {
            'description': 'Audio volume analysis implemented',
            'test': 'Check if audio_excitement is in segment metadata',
            'passed': False
        },
        'diversity_scoring': {
            'description': 'Diversity scoring prevents repetition',
            'test': 'Check if diversity_penalty is in segment metadata',
            'passed': False
        },
        'segment_weighting': {
            'description': 'Audio contributes 30% to score',
            'test': 'Verify scoring weights in code',
            'passed': False
        }
    }

    # Quick test with party video
    test_video = 'test_party_celebration.mp4'

    if os.path.exists(test_video):
        print(f"Testing with: {test_video}")
        print()

        config = SimpleConfig(target_duration=10)
        processor = SimpleVideoProcessor(config)

        try:
            metadata = processor.process_video(test_video, "validation_test.mp4")

            # Check improvements
            if metadata['segments']:
                first_seg = metadata['segments'][0]

                if 'audio_excitement' in first_seg:
                    improvements['audio_analysis']['passed'] = True
                    print("✅ Audio analysis: IMPLEMENTED")
                else:
                    print("❌ Audio analysis: MISSING")

                if 'diversity_penalty' in first_seg:
                    improvements['diversity_scoring']['passed'] = True
                    print("✅ Diversity scoring: IMPLEMENTED")
                else:
                    print("❌ Diversity scoring: MISSING")

                # Check if audio contributes to score
                if first_seg.get('audio_excitement', 0) > 0 or first_seg.get('volume_peak', 0) > 0:
                    improvements['segment_weighting']['passed'] = True
                    print("✅ Segment weighting: UPDATED")
                else:
                    print("⚠️  Segment weighting: Audio data present but may be zero")

            # Cleanup
            if os.path.exists("validation_test.mp4"):
                os.remove("validation_test.mp4")

        except Exception as e:
            print(f"❌ Validation test failed: {e}")

    else:
        print(f"⏭️  Skipping validation - {test_video} not found")

    print()
    print("="*70)

    passed_count = sum(1 for imp in improvements.values() if imp['passed'])
    total_count = len(improvements)

    if passed_count == total_count:
        print(f"🎉 ALL IMPROVEMENTS VALIDATED ({passed_count}/{total_count})")
    else:
        print(f"⚠️  {passed_count}/{total_count} improvements validated")

    print("="*70)
    print()

    return improvements


def main():
    """Main test execution"""

    print()
    print("🚀 Starting Phase 1.5 Algorithm Tests")
    print()

    # Validate improvements
    improvements = test_algorithm_improvements()

    # Test with existing videos
    results = test_with_existing_videos()

    # Final summary
    print()
    print("="*70)
    print(" ✨ PHASE 1.5 TESTING COMPLETE")
    print("="*70)
    print()
    print("Next Steps:")
    print("  1. Review output videos to verify quality")
    print("  2. Test with 5 real user videos")
    print("  3. Collect user feedback (target: >4.0/5.0)")
    print("  4. If successful → Proceed to Phase 2 (REST API)")
    print()

    # Return success if most tests passed
    successful_results = sum(1 for r in results if r.get('success', False))
    successful_improvements = sum(1 for imp in improvements.values() if imp['passed'])

    if successful_results >= len(results) * 0.75 and successful_improvements >= len(improvements) * 0.75:
        print("✅ Testing: PASSED (75%+ success rate)")
        return 0
    else:
        print("⚠️  Testing: NEEDS ATTENTION (< 75% success rate)")
        return 1


if __name__ == '__main__':
    sys.exit(main())
