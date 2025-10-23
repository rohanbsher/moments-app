# iOS App Testing Guide - Moments

**Date:** October 6, 2025
**Status:** ✅ Ready for Testing
**Backend:** Running on `http://localhost:8000`

---

## 🎯 What You're Testing

You'll be testing the **complete end-to-end user experience** of the Moments app:

1. Selecting a video from your library
2. Uploading it to the backend
3. Watching the AI process it
4. Viewing and saving the generated highlight

---

## ✅ Pre-Testing Checklist

### Backend Status
- ✅ Backend running on `http://localhost:8000`
- ✅ Audio preservation working (FFmpeg-based)
- ✅ API tested and validated
- ✅ Health check passing

### iOS App Status
- ✅ Xcode project opened: `ios/MomentsApp.xcodeproj`
- ✅ Backend URL configured: `http://localhost:8000`
- ✅ Build succeeded
- ✅ Simulator ready (iPhone 16 Pro, iOS 18.3.1)

---

## 📱 How to Test in Xcode

### Step 1: Run the App

**In Xcode:**
1. The project should already be open (`MomentsApp.xcodeproj`)
2. Select **iPhone 16 Pro** (or any iPhone simulator) from the device dropdown at the top
3. Click the **Play button** (▶️) or press `Cmd + R`
4. Wait for the app to build and launch on the simulator

### Step 2: Add Test Videos to Simulator

You'll need some videos in the simulator's photo library to test with. Here are your options:

**Option A: Use Sample Videos (Recommended)**
1. When the simulator opens, drag and drop a video file directly onto the simulator window
2. Safari will open - click "Save Video"
3. The video will be saved to Photos

**Option B: Download Videos in Simulator**
1. Open Safari in the simulator
2. Search for "sample mp4 video" or use: https://sample-videos.com
3. Download a short video (5-30 seconds recommended for first test)
4. Save to Photos

**Option C: Use Your Test Videos**
I created a test video for you: `test_with_audio_30s.mp4` in the project root
- Drag this file onto the simulator
- Save it to Photos

### Step 3: Test the Complete User Flow

#### 3.1 Launch and Home Screen
- ✅ App launches without crashes
- ✅ "Create Highlight" button appears
- ✅ Clean, professional UI

#### 3.2 Select Video
1. Tap "Create Highlight"
2. Photo picker should open
3. Select a video from your library
4. Video should appear in preview

**Expected:** Video picker opens, you can select a video

#### 3.3 Configure and Upload
1. Adjust target duration slider (default 60 seconds)
2. Tap "Create Highlight" button
3. Upload progress bar should appear
4. Watch upload percentage increase

**Expected:**
- Upload starts immediately
- Progress bar updates (0% → 100%)
- Upload should complete in seconds for small videos

#### 3.4 Processing
1. After upload, status changes to "Processing"
2. Watch AI progress updates:
   - "Detecting scenes..."
   - "Analyzing motion..."
   - "Creating highlight..."
3. Progress bar updates in real-time

**Expected:**
- Real-time progress updates
- Smooth transitions between stages
- Processing completes (time varies by video size)

#### 3.5 View Result
1. When complete, "View Result" screen appears
2. Tap play button to watch highlight
3. **CRITICAL: Check if audio plays!** 🔊
4. Tap "Save to Photos" to save

**Expected:**
- Video plays smoothly
- **AUDIO IS PRESENT** (if original video had audio) ✅
- Video can be saved to Photos

---

## 🎬 What to Look For

### Must Work ✅
- [ ] App launches without crashing
- [ ] Can select video from Photos
- [ ] Upload progresses to 100%
- [ ] Processing completes successfully
- [ ] Result video plays
- [ ] **AUDIO IS PRESERVED** (critical!)
- [ ] Can save result to Photos

### Should Work Well ✅
- [ ] UI is smooth and responsive
- [ ] Progress updates are accurate
- [ ] Video quality is good
- [ ] Processing time is reasonable
- [ ] Error messages are clear (if any)

### Nice to Have ✅
- [ ] Animations are smooth
- [ ] Loading states look good
- [ ] Colors and design are appealing

---

## 🐛 Common Issues and Solutions

### Issue: "Cannot connect to server"
**Solution:**
1. Check backend is running: `curl http://localhost:8000/health`
2. Should return: `{"status":"healthy","version":"1.0.0","service":"Moments API"}`
3. If not, restart backend:
   ```bash
   cd backend
   python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

### Issue: No videos in Photos library
**Solution:**
1. Drag the test video (`test_with_audio_30s.mp4`) onto the simulator
2. Or download a sample video from Safari in the simulator

### Issue: App crashes on launch
**Solution:**
1. Clean build: In Xcode, go to Product → Clean Build Folder
2. Rebuild: Press Cmd + B
3. Run again: Press Cmd + R

### Issue: Build fails
**Solution:**
1. Close Xcode
2. Run: `xcodegen generate` in the `ios/` directory
3. Reopen Xcode and build again

### Issue: Upload gets stuck at 99%
**Solution:** This is normal! Wait a few seconds, the backend is processing the initial handshake.

### Issue: No audio in output (CRITICAL!)
**This should NOT happen anymore - the bug is fixed!**
If it does:
1. Stop the app
2. Check that the backend was restarted AFTER the FFmpeg fix
3. The backend logs should show: "Audio stream found" and "Building filter with audio preservation"

---

## 📊 Test Scenarios

### Scenario 1: Quick Test (5 minutes)
**Goal:** Verify basic functionality

1. Use `test_with_audio_30s.mp4` (30 seconds)
2. Target duration: 15 seconds
3. Upload → Process → View
4. **Check audio plays!**

**Expected Time:**
- Upload: < 1 second
- Processing: ~7 seconds
- Total: < 10 seconds

### Scenario 2: Real Video Test (10-15 minutes)
**Goal:** Test with actual user content

1. Use a real video from your iPhone (if testing on device)
2. Or download a 1-2 minute video with audio
3. Target duration: 60 seconds
4. Upload → Process → View → Save

**Expected Time:**
- Upload: 1-5 seconds (depends on size)
- Processing: 10-30 seconds
- Total: < 1 minute

### Scenario 3: Large Video Test (Optional)
**Goal:** Stress test with large file

1. Use a 5-10 minute video
2. Target duration: 60 seconds
3. Upload → Process → View

**Expected Time:**
- Upload: 5-15 seconds
- Processing: 30-120 seconds
- Total: 1-3 minutes

---

## 🎯 Success Criteria

**For the app to be considered "working":**

✅ **Critical (Must Pass):**
1. App launches without crashing
2. Can select and upload video
3. Processing completes successfully
4. **Output video has AUDIO** (if input had audio)
5. Result can be viewed and saved

✅ **Important (Should Pass):**
6. Upload progress is visible
7. Processing progress updates
8. UI is responsive
9. Processing time is reasonable (< 2 minutes for 1-minute video)

✅ **Nice to Have (Great if it works):**
10. Smooth animations
11. Professional UI design
12. Error handling is graceful

---

## 📝 What to Report

### If Everything Works
Tell me:
- ✅ "Everything works!"
- How long did processing take for your video?
- Was the audio preserved? (Critical!)
- Any UI/UX feedback?

### If Something Doesn't Work
Tell me:
- What step failed?
- What error message appeared (if any)?
- What were you doing when it failed?
- Screenshots help!

---

## 🎬 Sample Test Flow

**Here's exactly what you should see for a successful test:**

1. **Launch:** Moments app opens with "Create Highlight" button
2. **Select:** Photo picker opens → Select video → Preview appears
3. **Upload:** Tap "Create" → Progress bar: 0% → 50% → 100% (~1s for 30s video)
4. **Process:** Status: "Processing" → Progress updates → Completes (~7s for 30s video)
5. **Result:** Video player appears → Tap play → **Audio plays!** → Can save
6. **Success:** ✅ You now have a highlight video with audio!

---

## 🔍 Technical Details (For Reference)

### What the App Does
1. **Upload:** Sends video file to backend via multipart/form-data POST
2. **Poll:** Checks job status every 1 second via GET request
3. **Download:** Downloads processed video when ready via GET request
4. **Save:** Saves video to iOS Photos library

### Backend Processing (What You're Testing)
1. Scene detection (PySceneDetect)
2. Motion analysis (OpenCV optical flow)
3. Audio intelligence (volume detection, excitement scoring)
4. Diversity scoring (prevents repetitive clips)
5. **FFmpeg composition (preserves audio!)** ✅

### API Endpoints Being Called
- `POST /api/v1/upload` - Upload video
- `GET /api/v1/jobs/{job_id}/status` - Check progress
- `GET /api/v1/jobs/{job_id}/download` - Download result

---

## 🚀 Ready to Test!

**Everything is set up for you:**
- ✅ Backend running with audio preservation fix
- ✅ iOS app configured for localhost
- ✅ Xcode project ready to run
- ✅ Test videos available

**Just click Play (▶️) in Xcode and start testing!**

---

## 💡 Pro Tips

1. **Start small:** Use the 30-second test video first
2. **Check audio:** This is the most important thing to verify!
3. **Try different videos:** Test with various content (music, speech, nature sounds)
4. **Test the flow multiple times:** Make sure it's reliable
5. **Save some results:** You can compare multiple highlight versions

---

## 📞 Need Help?

**If something doesn't work:**
1. Check the backend logs (they're running in your terminal)
2. Check Xcode console for iOS errors (bottom panel in Xcode)
3. Try the "Common Issues" section above
4. Let me know what's happening!

---

**Happy Testing! 🎉**

Let me know how it goes and especially **confirm that audio is preserved** in the output!
