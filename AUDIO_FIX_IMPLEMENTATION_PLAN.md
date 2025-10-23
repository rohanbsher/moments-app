# Audio Preservation - Implementation Plan

**Priority:** 🔴 CRITICAL
**Estimated Time:** 2-3 hours
**Status:** Ready to implement

---

## 🎯 Objective

**Replace OpenCV-based video composition with FFmpeg to preserve audio tracks in highlight videos.**

---

## 🔍 Current Implementation Analysis

### Problem Location
**File:** `core/simple_processor.py`
**Function:** `_create_output_video()` (lines 310-341)

### Current Approach (BROKEN)
```python
def _create_output_video(self, input_path, segments, output_path):
    # Uses OpenCV VideoWriter
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    for segment in segments:
        # Writes ONLY video frames
        out.write(frame)  # ❌ No audio!

    out.release()
```

**Why It Fails:**
- `cv2.VideoWriter` only handles video frames
- No audio stream support
- No codec flexibility
- Poor MP4 encoding (uses old 'mp4v')

---

## ✅ New Implementation Strategy

### Approach: FFmpeg Filter Complex

**Use FFmpeg's `filter_complex` to:**
1. Extract specific time ranges from input (with audio)
2. Concatenate multiple segments preserving both video and audio
3. Encode with modern codecs (H.264 + AAC)
4. Create proper MP4 container

### Technical Advantages
- ✅ Preserves audio streams
- ✅ Better video quality (libx264)
- ✅ Standard AAC audio encoding
- ✅ Proper MP4 muxing
- ✅ Faster processing (hardware acceleration)
- ✅ Frame-accurate trimming

---

## 🏗️ Implementation Design

### New Function: `_create_output_video_with_audio()`

```python
def _create_output_video_with_audio(self, input_path: str, segments: List[Dict], output_path: str):
    """Create output video WITH AUDIO using FFmpeg"""

    if not segments:
        raise ValueError("No segments to process")

    # Step 1: Check if input has audio
    has_audio = self._check_audio_stream(input_path)

    # Step 2: Build filter_complex command
    if has_audio:
        filter_complex = self._build_filter_complex_with_audio(segments)
        output_map = ['-map', '[outv]', '-map', '[outa]']
    else:
        filter_complex = self._build_filter_complex_video_only(segments)
        output_map = ['-map', '[outv]']

    # Step 3: Execute FFmpeg
    cmd = [
        'ffmpeg',
        '-i', input_path,
        '-filter_complex', filter_complex,
        *output_map,
        '-c:v', 'libx264',
        '-preset', 'medium',  # Balance speed/quality
        '-crf', '23',         # Quality (18-28, lower=better)
        '-c:a', 'aac',
        '-b:a', '192k',       # Audio bitrate
        '-y',                 # Overwrite output
        output_path
    ]

    self._run_ffmpeg(cmd)
```

### Helper Functions

**1. Check Audio Stream**
```python
def _check_audio_stream(self, video_path: str) -> bool:
    """Check if video has audio stream"""
    cmd = [
        'ffprobe', '-v', 'quiet',
        '-print_format', 'json',
        '-show_streams',
        video_path
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    data = json.loads(result.stdout)

    return any(s['codec_type'] == 'audio' for s in data.get('streams', []))
```

**2. Build Filter Complex (with Audio)**
```python
def _build_filter_complex_with_audio(self, segments: List[Dict]) -> str:
    """Build FFmpeg filter_complex for segments with audio"""

    filter_parts = []

    for i, segment in enumerate(segments):
        start = segment['start']
        duration = min(
            segment['end'] - segment['start'],
            self.config.max_segment_duration
        )

        # Video trim
        filter_parts.append(
            f"[0:v]trim=start={start}:duration={duration},"
            f"setpts=PTS-STARTPTS[v{i}]"
        )

        # Audio trim
        filter_parts.append(
            f"[0:a]atrim=start={start}:duration={duration},"
            f"asetpts=PTS-STARTPTS[a{i}]"
        )

    # Concatenate video streams
    video_inputs = ''.join(f"[v{i}]" for i in range(len(segments)))
    video_concat = f"{video_inputs}concat=n={len(segments)}:v=1:a=0[outv]"

    # Concatenate audio streams
    audio_inputs = ''.join(f"[a{i}]" for i in range(len(segments)))
    audio_concat = f"{audio_inputs}concat=n={len(segments)}:v=0:a=1[outa]"

    # Combine
    filter_complex = ';'.join(filter_parts) + ';' + video_concat + ';' + audio_concat

    return filter_complex
```

**3. Build Filter Complex (Video Only)**
```python
def _build_filter_complex_video_only(self, segments: List[Dict]) -> str:
    """Build FFmpeg filter_complex for video-only segments"""

    filter_parts = []

    for i, segment in enumerate(segments):
        start = segment['start']
        duration = min(
            segment['end'] - segment['start'],
            self.config.max_segment_duration
        )

        filter_parts.append(
            f"[0:v]trim=start={start}:duration={duration},"
            f"setpts=PTS-STARTPTS[v{i}]"
        )

    # Concatenate
    video_inputs = ''.join(f"[v{i}]" for i in range(len(segments)))
    video_concat = f"{video_inputs}concat=n={len(segments)}:v=1:a=0[outv]"

    filter_complex = ';'.join(filter_parts) + ';' + video_concat

    return filter_complex
```

**4. Run FFmpeg**
```python
def _run_ffmpeg(self, cmd: List[str]):
    """Execute FFmpeg command with error handling"""

    try:
        logger.info(f"Running FFmpeg: {' '.join(cmd[:5])}...")

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
            timeout=600  # 10 min timeout
        )

        logger.info("FFmpeg completed successfully")

    except subprocess.CalledProcessError as e:
        logger.error(f"FFmpeg failed: {e.stderr}")
        raise RuntimeError(f"Video composition failed: {e.stderr}")

    except subprocess.TimeoutExpired:
        logger.error("FFmpeg timeout after 10 minutes")
        raise RuntimeError("Video composition timeout")
```

---

## 🔄 Migration Strategy

### Step 1: Add New Implementation (Parallel)
- Create new function `_create_output_video_with_audio()`
- Keep old function temporarily
- No breaking changes yet

### Step 2: Update Main Pipeline
```python
def process_video(self, input_path: str, output_path: str = None) -> Dict:
    # ... existing code ...

    # OLD: self._create_output_video(input_path, selected, output_path)
    # NEW:
    self._create_output_video_with_audio(input_path, selected, output_path)
```

### Step 3: Test Thoroughly
- Test with singing video (has audio)
- Test with all video types
- Test video-only files (no audio)
- Verify audio sync
- Check file sizes

### Step 4: Remove Old Implementation
- Delete `_create_output_video()` function
- Clean up unused imports
- Update documentation

---

## 📋 Implementation Checklist

### Code Changes
- [ ] Add `subprocess` and `json` imports (already present)
- [ ] Create `_check_audio_stream()` helper
- [ ] Create `_build_filter_complex_with_audio()` helper
- [ ] Create `_build_filter_complex_video_only()` helper
- [ ] Create `_run_ffmpeg()` helper
- [ ] Create `_create_output_video_with_audio()` main function
- [ ] Update `process_video()` to use new function
- [ ] Remove old `_create_output_video()` function

### Testing
- [ ] Test singing video (647MB, has audio)
- [ ] Verify audio is preserved
- [ ] Check audio-video sync
- [ ] Test meeting video (has speech)
- [ ] Test nature video (ambient audio)
- [ ] Test sports video (crowd noise)
- [ ] Test party video (music)
- [ ] Test video-only file (no audio stream)
- [ ] Performance comparison (before/after)

### Documentation
- [ ] Update function docstrings
- [ ] Add audio preservation notes
- [ ] Document FFmpeg requirements
- [ ] Update README if needed

---

## ⚠️ Edge Cases to Handle

### 1. No Audio Stream
**Scenario:** Input video has no audio track
**Solution:** Use video-only filter_complex
**Test:** Create test video with only video stream

### 2. Multiple Audio Streams
**Scenario:** Video has multiple audio tracks (rare)
**Solution:** Select first audio stream `[0:a:0]`
**Test:** If encountered, handle gracefully

### 3. Audio Codec Not AAC
**Scenario:** Input has MP3, PCM, or other codec
**Solution:** FFmpeg re-encodes to AAC automatically
**Test:** Various audio codecs

### 4. Very Short Segments
**Scenario:** Segment < 0.1 seconds
**Solution:** Already handled by min_segment_duration
**Test:** Edge case validation

### 5. FFmpeg Not Available
**Scenario:** FFmpeg not installed
**Solution:** Raise clear error with installation instructions
**Test:** Mock missing FFmpeg

---

## 🎯 Success Criteria

**Must Pass:**
- ✅ Singing video has audio in output
- ✅ Audio-video sync is perfect
- ✅ Audio quality is good (no distortion)
- ✅ All existing video types still work
- ✅ Processing time is acceptable
- ✅ File sizes are reasonable

**Quality Metrics:**
- Audio present: 100% (for videos with audio)
- Audio sync: < 100ms offset
- Audio quality: No perceptible degradation
- Processing time: < 2x slowdown vs current
- File size: Similar or better

---

## 📊 Expected Results

### Before (OpenCV)
- ❌ No audio in output
- ✅ Fast processing
- ⚠️ Poor video codec (mp4v)

### After (FFmpeg)
- ✅ Audio preserved
- ✅ Better video codec (H.264)
- ✅ AAC audio encoding
- ✅ Proper MP4 container
- ⚠️ Slightly slower (acceptable trade-off)

### Performance Estimate
- Small files (<10MB): +0.5s overhead
- Medium files (10-50MB): +1-2s overhead
- Large files (>50MB): +5-10s overhead
- Very large (647MB): +20-30s overhead

**Trade-off:** Worth it for audio preservation!

---

## 🚀 Deployment Plan

### Local Testing
1. Implement changes in `simple_processor.py`
2. Run comprehensive test suite
3. Verify all videos work with audio

### Staging
1. Deploy to test backend instance
2. Test with iOS app
3. End-to-end validation

### Production
1. Deploy to Railway
2. Monitor for errors
3. Check audio in user highlights

---

## 🔗 Dependencies

**System Requirements:**
- ✅ FFmpeg 4.0+ (we have 8.0)
- ✅ libx264 codec (available)
- ✅ AAC audio codec (available)
- ✅ Python subprocess module (built-in)

**Python Imports:**
- ✅ `subprocess` (standard library)
- ✅ `json` (standard library)
- ✅ Already imported in file

**No New Dependencies!** ✅

---

## 📝 Code Files to Modify

1. `core/simple_processor.py` (MAIN CHANGES)
   - Add helper functions
   - Replace video composition logic
   - Update imports if needed

2. `tests/scripts/test_singing_video.py` (VALIDATION)
   - Update to check for audio presence
   - Add audio quality validation

---

## ✅ Ready to Implement!

**All research complete. Implementation plan approved.**

**Next Step:** Begin coding the FFmpeg-based video composition!

---

**Created:** October 5, 2025
**Priority:** 🔴 CRITICAL
**Estimated Duration:** 2-3 hours
**Status:** READY FOR IMPLEMENTATION
