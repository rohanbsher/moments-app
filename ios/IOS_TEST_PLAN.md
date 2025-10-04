# iOS App Testing Plan - Moments

## Prerequisites

✅ **Backend Running:** http://localhost:8000/health returns healthy
✅ **All Swift Files Created:** 11 Swift files in MomentsApp directory
✅ **Xcode Installed:** Version 15.0+ required
✅ **iOS Simulator:** iPhone 15 Pro (iOS 17.0+)

---

## Test Plan Overview

### Testing Phases

1. **API Testing** (Command Line) - Verify backend works
2. **Xcode Project Setup** - Create and configure project
3. **Build Testing** - Ensure code compiles
4. **UI Testing** (Simulator) - Test user interactions
5. **Integration Testing** - End-to-end video flow
6. **Error Handling** - Edge cases and failures

---

## Phase 1: API Testing (5 minutes)

### Test Backend Endpoints

```bash
cd /Users/rohanbhandari/Desktop/Professional_Projects/ML_PROJECTS_AI/moments_app

# 1. Health check
curl http://localhost:8000/health
# Expected: {"status":"healthy","version":"1.0.0","service":"Moments API"}

# 2. Root endpoint
curl http://localhost:8000/
# Expected: {"message":"Welcome to Moments API","version":"1.0.0","docs":"/docs","health":"/health"}

# 3. API docs
open http://localhost:8000/docs
# Expected: FastAPI Swagger UI opens in browser
```

### Test Upload Endpoint (with test video)

```bash
# Upload a test video
curl -X POST http://localhost:8000/api/v1/upload/video \
  -F "file=@test_sports_action.mp4" \
  -F "duration=30" \
  -F "min_segment=3" \
  -F "max_segment=10"

# Expected response:
# {
#   "job_id": "some-uuid",
#   "status": "queued",
#   "message": "Video uploaded successfully"
# }

# Save job_id for next step
export JOB_ID="<job-id-from-response>"

# Check status
curl http://localhost:8000/api/v1/jobs/$JOB_ID/status

# Expected: {"job_id":"...","status":"processing","progress":45,"message":"..."}

# Download (wait for completion first)
curl http://localhost:8000/api/v1/jobs/$JOB_ID/download -o test_highlight.mp4
```

**✅ Phase 1 Complete When:**
- Health endpoint returns 200 OK
- Upload returns job_id
- Status polling works
- Download returns video file

---

## Phase 2: Xcode Project Setup (10 minutes)

### Option A: Create Project via Xcode GUI

1. **Launch Xcode**
```bash
open -a Xcode
```

2. **Create New Project**
   - File → New → Project
   - iOS → App
   - Product Name: **MomentsApp**
   - Team: Select your team
   - Organization Identifier: **com.moments**
   - Interface: **SwiftUI**
   - Language: **Swift**
   - Save to: `/Users/rohanbhandari/Desktop/Professional_Projects/ML_PROJECTS_AI/moments_app/ios/`

3. **Delete Template Files**
   - Delete `ContentView.swift`
   - Delete `MomentsAppApp.swift` (if created)

4. **Add Source Files**
   - Right-click MomentsApp folder
   - Add Files to "MomentsApp"...
   - Select all files from `/Users/rohanbhandari/Desktop/Professional_Projects/ML_PROJECTS_AI/moments_app/ios/MomentsApp/`
   - **Uncheck** "Copy items if needed"
   - Select "Create groups"
   - Click Add

5. **Update Info.plist**
   - Select target → Info tab
   - Custom iOS Target Properties
   - Add entries from `Info.plist` file

### Option B: Use Existing Project Structure

If Xcode project already exists:

```bash
cd /Users/rohanbhandari/Desktop/Professional_Projects/ML_PROJECTS_AI/moments_app/ios
open MomentsApp.xcodeproj
```

**✅ Phase 2 Complete When:**
- Project opens without errors
- All Swift files visible in navigator
- Info.plist configured
- Target builds (Cmd+B)

---

## Phase 3: Build Testing (5 minutes)

### Test Compilation

1. **Select Simulator**
   - Top toolbar: Select "iPhone 15 Pro"
   - iOS 17.0 or later

2. **Clean Build Folder**
   ```
   Product → Clean Build Folder (Cmd+Shift+K)
   ```

3. **Build Project**
   ```
   Product → Build (Cmd+B)
   ```

### Expected Build Warnings/Errors

**If you see these errors:**

1. **"No such module 'Observation'"**
   - Fix: Set iOS Deployment Target to 17.0+
   - Target Settings → General → Minimum Deployments → 17.0

2. **"Cannot find 'PHPicker' in scope"**
   - Fix: Add `import PhotosUI` to VideoPicker.swift

3. **"Cannot find 'AVPlayer' in scope"**
   - Fix: Add `import AVKit` to ResultView.swift

4. **"Cannot find 'Photos' in scope"**
   - Fix: Add `import Photos` to ResultView.swift

**✅ Phase 3 Complete When:**
- Build succeeds with 0 errors
- May have warnings (acceptable)
- "Build Succeeded" message appears

---

## Phase 4: UI Testing (15 minutes)

### Test 1: App Launch

1. **Run App**
   ```
   Product → Run (Cmd+R)
   ```

2. **Verify Home Screen**
   - [ ] App launches successfully
   - [ ] "Moments" title visible
   - [ ] Wand/stars icon displayed
   - [ ] "Select Video" button present
   - [ ] "Settings" section visible
   - [ ] Target duration selector shows 15s/30s/60s

**Screenshot:** Home screen with "Select Video" button

### Test 2: Video Picker

1. **Add Test Video to Simulator**
   ```bash
   # Drag test video onto simulator window
   # Or use Safari to download a video
   open -a Simulator
   ```

   Then drag `test_sports_action.mp4` onto simulator

2. **Open Photos App**
   - Verify video appears in Photos library

3. **Return to Moments App**
   - Tap "Select Video" button
   - [ ] PHPicker sheet appears
   - [ ] Test video visible in picker
   - [ ] Can select video
   - [ ] Picker dismisses after selection

**Screenshot:** PHPicker with video selected

### Test 3: Upload Progress

After selecting video:

1. **Verify Upload Phase**
   - [ ] Upload progress circle appears
   - [ ] Percentage updates (0% → 99%)
   - [ ] "Uploading" text visible
   - [ ] Status message updates
   - [ ] Can tap Cancel button

2. **Expected Timing**
   - Small video (<50MB): 5-10 seconds
   - Large video (>100MB): 20-30 seconds

**Screenshot:** Upload in progress at 45%

### Test 4: Processing Status

1. **Verify Processing Phase**
   - [ ] Upload completes (100%)
   - [ ] Status changes to "Processing"
   - [ ] Progress resets to 0%
   - [ ] Progress updates every 2 seconds
   - [ ] Status message shows scene analysis
   - [ ] Progress increases to 100%

2. **Expected Timing**
   - 30s video: ~2-3 seconds processing
   - 60s video: ~4-6 seconds processing

**Screenshot:** Processing at 67%

### Test 5: Completion & Result

1. **Verify Completion**
   - [ ] Green checkmark appears
   - [ ] "Highlight Ready!" message
   - [ ] "View Highlight" button visible
   - [ ] "Create Another" button visible

2. **View Result**
   - Tap "View Highlight"
   - [ ] ResultView appears
   - [ ] Video player loads
   - [ ] Video auto-plays
   - [ ] Video loops automatically
   - [ ] "Share Highlight" button visible
   - [ ] "Save to Photos" button visible

**Screenshot:** Result view with video playing

### Test 6: Video Playback

1. **Verify Playback**
   - [ ] Video plays smoothly
   - [ ] Can pause/play
   - [ ] Can scrub timeline
   - [ ] Audio plays (if present)
   - [ ] Video loops at end

**Screenshot:** Video mid-playback

### Test 7: Share Functionality

1. **Test Share**
   - Tap "Share Highlight" button
   - [ ] Share sheet appears
   - [ ] Video file included
   - [ ] Can share to AirDrop, Messages, etc.
   - [ ] Can cancel share sheet

**Screenshot:** Share sheet with options

### Test 8: Save to Photos

1. **Test Save**
   - Tap "Save to Photos" button
   - [ ] Permission alert appears (first time)
   - [ ] Grant permission
   - [ ] Success confirmation
   - [ ] Video appears in Photos app

2. **Verify in Photos**
   - Open Photos app
   - [ ] Highlight video saved
   - [ ] Video plays in Photos

**Screenshot:** Video in Photos library

### Test 9: Create Another

1. **Reset Flow**
   - Tap "Create Another" button
   - [ ] Returns to home screen
   - [ ] Previous result cleared
   - [ ] Can select new video
   - [ ] Process repeats successfully

---

## Phase 5: Integration Testing (20 minutes)

### Test Scenario 1: Quick Highlight (15s)

1. Configure: Target Duration = **15s**
2. Select: Short video (~1 minute)
3. **Expected Result:**
   - Upload: 5-10s
   - Processing: 6-8s
   - Output: ~15 second highlight
   - Contains 3-5 segments

### Test Scenario 2: Standard Highlight (30s)

1. Configure: Target Duration = **30s**
2. Select: Medium video (2-5 minutes)
3. **Expected Result:**
   - Upload: 10-20s
   - Processing: 12-20s
   - Output: ~30 second highlight
   - Contains 5-10 segments

### Test Scenario 3: Extended Highlight (60s)

1. Configure: Target Duration = **60s**
2. Select: Long video (5-10 minutes)
3. **Expected Result:**
   - Upload: 30-60s
   - Processing: 30-45s
   - Output: ~60 second highlight
   - Contains 10-15 segments

### Test Scenario 4: Multiple Videos

1. Complete full flow for video 1
2. Tap "Create Another"
3. Select video 2
4. Process completely
5. **Verify:**
   - [ ] First video not affected
   - [ ] Second video processes correctly
   - [ ] Both saved separately
   - [ ] No memory leaks

---

## Phase 6: Error Handling (15 minutes)

### Test 1: Network Error

1. **Stop Backend**
```bash
# Kill backend server
pkill -f uvicorn
```

2. **Attempt Upload**
   - Select video
   - [ ] Upload fails
   - [ ] Error alert appears
   - [ ] Error message clear
   - [ ] Can dismiss error
   - [ ] Can retry after restarting backend

3. **Restart Backend**
```bash
cd backend && ./run.sh
```

### Test 2: Cancel During Upload

1. Start video upload
2. Tap "Cancel" at 50% progress
3. **Verify:**
   - [ ] Upload stops immediately
   - [ ] Progress resets
   - [ ] Status changes to "Cancelled"
   - [ ] Can select new video
   - [ ] No orphaned jobs

### Test 3: Cancel During Processing

1. Start processing
2. Tap "Cancel" at 50% processing
3. **Verify:**
   - [ ] Polling stops
   - [ ] Status changes to "Cancelled"
   - [ ] Can select new video
   - [ ] Backend job not affected (continues processing)

### Test 4: Large Video (>1GB)

1. Select very large video
2. **Verify:**
   - [ ] Upload works (may take minutes)
   - [ ] Progress accurate
   - [ ] Processing completes
   - [ ] Download succeeds
   - [ ] No memory issues

### Test 5: Unsupported Format

1. Try to select non-video file
2. **Verify:**
   - [ ] PHPicker only shows videos
   - [ ] Cannot select images
   - [ ] Cannot select documents

### Test 6: No Internet (Localhost Only)

1. Upload video (succeeds - localhost)
2. **Verify:**
   - [ ] Works on localhost even without internet
   - [ ] Cellular data not used
   - [ ] WiFi-only connection acceptable

---

## Test Results Template

### Test Session Info
- **Date:** _______________
- **Tester:** _______________
- **Xcode Version:** _______________
- **iOS Version:** _______________
- **Simulator:** _______________

### Phase 1: API Testing
- [ ] Health check passed
- [ ] Upload endpoint works
- [ ] Status polling works
- [ ] Download works
- **Issues:** _______________

### Phase 2: Xcode Setup
- [ ] Project created
- [ ] Files added
- [ ] Info.plist configured
- **Issues:** _______________

### Phase 3: Build Testing
- [ ] Clean build succeeds
- [ ] 0 errors
- [ ] Warnings (if any): _______________
- **Issues:** _______________

### Phase 4: UI Testing
- [ ] App launches
- [ ] Video picker works
- [ ] Upload progress displays
- [ ] Processing updates
- [ ] Result view shows
- [ ] Video playback works
- [ ] Share functionality works
- [ ] Save to Photos works
- [ ] Create Another works
- **Issues:** _______________

### Phase 5: Integration Testing
- [ ] Quick highlight (15s) ✓
- [ ] Standard highlight (30s) ✓
- [ ] Extended highlight (60s) ✓
- [ ] Multiple videos ✓
- **Issues:** _______________

### Phase 6: Error Handling
- [ ] Network error handled
- [ ] Cancel upload works
- [ ] Cancel processing works
- [ ] Large video supported
- [ ] Format validation works
- **Issues:** _______________

### Overall Assessment
- **Pass Rate:** ___/10 phases
- **Critical Issues:** _______________
- **Minor Issues:** _______________
- **Performance:** _______________
- **Recommendations:** _______________

---

## Success Criteria

### Must Pass (Critical):
- ✅ App builds without errors
- ✅ App launches successfully
- ✅ Video can be selected
- ✅ Upload completes
- ✅ Processing completes
- ✅ Highlight can be viewed
- ✅ No crashes during normal flow

### Should Pass (Important):
- ✅ Progress indicators accurate
- ✅ Status messages helpful
- ✅ Error messages clear
- ✅ Share functionality works
- ✅ Save to Photos works
- ✅ Cancel operations work

### Nice to Have (Enhanced):
- ✅ Animations smooth
- ✅ UI responsive
- ✅ Video loops seamlessly
- ✅ Multiple videos supported

---

## Known Limitations

1. **Localhost Only**
   - Currently works with http://localhost:8000
   - Will need HTTPS production URL for real device testing

2. **Simulator Only**
   - Camera not available in simulator
   - Use Photos library only
   - Physical device needed for camera testing

3. **Single Video**
   - One video at a time
   - Batch processing not yet supported

4. **No Background Upload**
   - Upload pauses if app backgrounds
   - Future: Add URLSession background configuration

5. **No Push Notifications**
   - Must stay in app to see completion
   - Future: Add APNs for remote notifications

---

## Next Steps After Testing

### If All Tests Pass:
1. Deploy backend to Railway
2. Update API baseURL to production
3. Test on physical iOS device
4. Add app icon and launch screen
5. Submit to TestFlight
6. Gather beta feedback
7. Submit to App Store

### If Tests Fail:
1. Document failures in test results
2. Review error logs
3. Fix critical issues first
4. Re-run failed tests
5. Iterate until all critical tests pass

---

**Current Status:** Ready for testing
**Backend:** http://localhost:8000 (running ✅)
**iOS Code:** All Swift files created ✅
**Next Action:** Create Xcode project and run Phase 1 tests
