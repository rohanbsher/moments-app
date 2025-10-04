# Moments App - Complete Testing Checklist

**Date:** October 4, 2025
**Xcode Version:** 16.2
**iOS Target:** 17.0+
**Backend:** http://localhost:8000 ✅ RUNNING

---

## ✅ Pre-Test Setup Complete

- [x] Backend API running and healthy
- [x] All Swift files created (11 files)
- [x] Documentation complete
- [x] Code committed to GitHub

---

## 📋 Step-by-Step Testing Guide

### Phase 1: Xcode Project Setup (10 minutes)

#### Step 1.1: Open Xcode
```bash
open -a Xcode
```

#### Step 1.2: Create New Project
1. File → New → Project (or Cmd+Shift+N)
2. Select **iOS** → **App**
3. Click **Next**

#### Step 1.3: Configure Project
```
Product Name: MomentsApp
Team: <Select your team>
Organization Identifier: com.moments
Bundle Identifier: com.moments.MomentsApp
Interface: SwiftUI
Language: Swift
Storage: None
Include Tests: ☐ (unchecked for now)
```

4. Click **Next**
5. Save Location: `/Users/rohanbhandari/Desktop/Professional_Projects/ML_PROJECTS_AI/moments_app/ios/`
6. Click **Create**

#### Step 1.4: Delete Template Files
In Xcode Navigator (left panel):
1. Delete `ContentView.swift` (right-click → Delete → Move to Trash)
2. If `MomentsAppApp.swift` exists, delete it too

#### Step 1.5: Add Source Files
1. Right-click on "MomentsApp" folder (blue icon) in navigator
2. Select "Add Files to 'MomentsApp'..."
3. Navigate to: `/Users/rohanbhandari/Desktop/Professional_Projects/ML_PROJECTS_AI/moments_app/ios/MomentsApp/`
4. Select **ALL** items (Core, Features, MomentsApp.swift, Info.plist)
5. **IMPORTANT:**
   - ☐ Uncheck "Copy items if needed"
   - ☑ Check "Create groups"
   - ☑ Check target "MomentsApp"
6. Click **Add**

#### Step 1.6: Verify File Structure
Navigator should show:
```
MomentsApp
├── Core
│   ├── Models
│   │   ├── Job.swift
│   │   └── VideoConfig.swift
│   └── Services
│       └── APIClient.swift
├── Features
│   ├── Home
│   │   └── Views
│   │       └── HomeView.swift
│   ├── Upload
│   │   ├── ViewModels
│   │   │   └── UploadViewModel.swift
│   │   └── Views
│   │       └── VideoPicker.swift
│   └── Result
│       └── Views
│           └── ResultView.swift
├── MomentsApp.swift
└── Info.plist (may appear under project settings)
```

**✅ Checkpoint:** All Swift files visible in navigator

---

### Phase 2: Project Configuration (5 minutes)

#### Step 2.1: Set Deployment Target
1. Click on **MomentsApp** project (blue icon at top of navigator)
2. Select **MomentsApp** target (under TARGETS)
3. Go to **General** tab
4. Under "Minimum Deployments":
   - iOS: **17.0**

#### Step 2.2: Configure Info.plist
1. Select **MomentsApp** target → **Info** tab
2. Click **+** button to add keys:
   - Key: `NSPhotoLibraryUsageDescription`
   - Value: `We need access to your photo library to save highlights`
   - Type: String
3. Add another:
   - Key: `NSPhotoLibraryAddUsageDescription`
   - Value: `We need access to save your video highlights to your photo library`
   - Type: String
4. Add App Transport Security:
   - Key: `NSAppTransportSecurity`
   - Type: Dictionary
   - Expand it, click **+**:
     - Key: `NSAllowsArbitraryLoads`
     - Value: `NO`
     - Type: Boolean
   - Add another item under NSAppTransportSecurity:
     - Key: `NSExceptionDomains`
     - Type: Dictionary
     - Expand it, click **+**:
       - Key: `localhost`
       - Type: Dictionary
       - Expand localhost, click **+**:
         - Key: `NSExceptionAllowsInsecureHTTPLoads`
         - Value: `YES`
         - Type: Boolean

#### Step 2.3: Verify Signing
1. **Signing & Capabilities** tab
2. **Automatically manage signing**: ☑ Checked
3. **Team**: Select your team
4. **Bundle Identifier**: com.moments.MomentsApp

**✅ Checkpoint:** No signing errors shown

---

### Phase 3: Build Testing (5 minutes)

#### Step 3.1: Clean Build Folder
1. Product → Clean Build Folder (or Cmd+Shift+K)
2. Wait for completion

#### Step 3.2: Build Project
1. Select scheme: **MomentsApp** → **iPhone 15 Pro** (simulator)
2. Product → Build (or Cmd+B)
3. Wait for build to complete

#### Step 3.3: Expected Build Results

**✅ SUCCESS - If you see:**
```
Build Succeeded
```

**❌ ERRORS - Common Issues:**

**Error 1:** `No such module 'Observation'`
- **Fix:** Check deployment target is iOS 17.0+
- Go to General → Minimum Deployments → iOS 17.0

**Error 2:** `Cannot find 'PHPicker' in scope`
- **Fix:** This shouldn't happen (import is in file)
- If it does, check VideoPicker.swift has `import PhotosUI`

**Error 3:** `Cannot find 'AVPlayer' in scope`
- **Fix:** Check ResultView.swift has `import AVKit`

**Error 4:** File not found errors
- **Fix:** Right-click file → Show File Inspector
- Check "Target Membership" has MomentsApp checked

**✅ Checkpoint:** Build succeeds with 0 errors

---

### Phase 4: Simulator Testing (40 minutes)

#### Step 4.1: Launch App
1. Ensure simulator selected: **iPhone 15 Pro** (iOS 17.2+)
2. Product → Run (or Cmd+R)
3. Wait for simulator to boot and app to launch

**✅ Expected:** App launches, shows Moments home screen

#### Step 4.2: Add Test Video to Simulator

**Option A: Drag & Drop**
1. Locate test video: `/Users/rohanbhandari/Desktop/Professional_Projects/ML_PROJECTS_AI/moments_app/test_sports_action.mp4`
2. Drag the .mp4 file onto the simulator window
3. Simulator should show "Saving video..."

**Option B: Safari Method**
1. Open Safari in simulator
2. Go to a video URL or download test video
3. Save to Photos

**Verify:**
1. Open **Photos** app in simulator
2. Test video should appear
3. Can play video in Photos

**✅ Checkpoint:** Test video visible in simulator Photos

#### Step 4.3: Test Home Screen UI
Verify home screen shows:
- [ ] "Moments" title
- [ ] Wand/stars icon (blue)
- [ ] "Transform your videos into highlights" subtitle
- [ ] "Select Video" button (large, blue background)
- [ ] Settings section at bottom
- [ ] Target Duration picker (15s/30s/60s selected)
- [ ] Segment Length display (3s - 10s)

**Screenshot Location:** Take screenshot (Cmd+S in simulator)

#### Step 4.4: Test Video Selection
1. **Tap "Select Video"**
2. **Expected:** PHPicker sheet slides up from bottom
3. **Verify:**
   - [ ] "Recent" or "Videos" album shown
   - [ ] Test video visible with thumbnail
   - [ ] Can scroll through videos
4. **Tap test video to select**
5. **Expected:** Picker dismisses
6. **Expected:** Upload begins immediately

**✅ Checkpoint:** Video selection works, picker dismisses

#### Step 4.5: Test Upload Progress
After selecting video, verify:
- [ ] View changes to processing state
- [ ] Circular progress indicator appears
- [ ] Progress starts at 0%
- [ ] Progress updates (shows increasing %)
- [ ] "Uploading" text visible below percentage
- [ ] Status message: "Uploading video..."
- [ ] Cancel button visible

**Monitor progress:**
- Progress should reach ~99% within 5-30 seconds (depending on video size)
- Then briefly show 100%

**Expected Timing:**
- Small video (<50MB): 5-10 seconds
- Test video (~30MB): 10-15 seconds

**✅ Checkpoint:** Upload completes, shows 100%

#### Step 4.6: Test Processing Status
After upload completes (100%), verify:
- [ ] Status changes from "Uploading" to "Processing"
- [ ] Progress resets to 0%
- [ ] Status message changes (e.g., "Analyzing scene 1 of 50")
- [ ] Progress updates every ~2 seconds
- [ ] Percentage increases gradually
- [ ] Status messages update with scene numbers

**Expected Timing:**
- 30s video: ~2-4 seconds processing
- 60s video: ~4-8 seconds processing
- Progress: 0% → 25% → 50% → 75% → 100%

**Status Messages to Watch For:**
- "Analyzing scene X of Y"
- "Detecting motion..."
- "Analyzing audio..."
- "Selecting highlights..."
- "Creating highlight reel..."

**✅ Checkpoint:** Processing completes, reaches 100%

#### Step 4.7: Test Completion State
After processing completes, verify:
- [ ] Green checkmark icon appears
- [ ] "Highlight Ready!" message
- [ ] "View Highlight" button (blue, full width)
- [ ] "Create Another" button (text only, below)

**Screenshot Location:** Capture completion screen

**✅ Checkpoint:** Completion screen displays correctly

#### Step 4.8: Test Result View
1. **Tap "View Highlight"**
2. **Expected:** Navigates to ResultView
3. **Verify:**
   - [ ] Navigation bar shows "Your Highlight"
   - [ ] Video player loads (may show loading spinner briefly)
   - [ ] Video begins playing automatically
   - [ ] Video has playback controls (play/pause, scrubber)
   - [ ] "Share Highlight" button (blue, full width)
   - [ ] "Save to Photos" button (light blue background)

**✅ Checkpoint:** Result view appears with video player

#### Step 4.9: Test Video Playback
While video is playing:
- [ ] Video plays smoothly (no stuttering)
- [ ] Audio plays (if present in highlight)
- [ ] Can pause/play by tapping video
- [ ] Can scrub to different positions
- [ ] Video loops automatically when finished
- [ ] Loop is seamless (no pause between loops)

**Verify Video Content:**
- [ ] Video shows selected highlights (not full original)
- [ ] Duration is approximately target (30s if default)
- [ ] Transitions between segments are smooth

**✅ Checkpoint:** Video playback works correctly

#### Step 4.10: Test Share Functionality
1. **Tap "Share Highlight"**
2. **Expected:** iOS share sheet appears from bottom
3. **Verify share sheet shows:**
   - [ ] Video file icon/preview
   - [ ] AirDrop option (if available)
   - [ ] Messages option
   - [ ] Mail option
   - [ ] Other sharing apps
4. **Test:**
   - [ ] Can select AirDrop (if available)
   - [ ] Can select Messages (should open Messages with video)
   - [ ] Can cancel share sheet
5. **Tap "Cancel" or tap outside sheet**
6. **Expected:** Returns to ResultView

**✅ Checkpoint:** Share sheet works correctly

#### Step 4.11: Test Save to Photos
1. **Tap "Save to Photos"**
2. **Expected (First Time):** Permission alert appears
   - Alert text: "MomentsApp Would Like to Access Your Photos"
   - Shows our usage description
3. **Tap "Allow" or "OK"**
4. **Expected:**
   - Permission granted
   - Video saves to Photos
   - May show brief success message (check console)
5. **Verify in Photos App:**
   - Open **Photos** app in simulator
   - Go to "Recents"
   - [ ] Highlight video appears (separate from original test video)
   - [ ] Video has current date/time
   - [ ] Video plays in Photos app

**✅ Checkpoint:** Save to Photos works

#### Step 4.12: Test "Create Another"
1. **Navigate back to ResultView** (if not there)
2. **Tap "Create Another"**
3. **Expected:**
   - [ ] Returns to home screen
   - [ ] Previous result is cleared
   - [ ] Progress indicators reset
   - [ ] "Select Video" button visible again
   - [ ] Can select a new video
   - [ ] Process repeats successfully

**✅ Checkpoint:** Create Another resets state correctly

---

### Phase 5: Advanced Testing (30 minutes)

#### Test 5.1: Different Target Durations

**Test 15-Second Highlight:**
1. On home screen, select **15s** in picker
2. Select test video
3. Upload and process
4. **Verify:**
   - [ ] Resulting video is ~15 seconds
   - [ ] Contains 3-5 segments
5. **✅ Expected:** ~15s highlight created

**Test 60-Second Highlight:**
1. Tap "Create Another"
2. Select **60s** in picker
3. Select test video (or different one)
4. Upload and process
5. **Verify:**
   - [ ] Resulting video is ~60 seconds
   - [ ] Contains 10-15 segments
6. **✅ Expected:** ~60s highlight created

#### Test 5.2: Cancel During Upload
1. Select video to upload
2. **Wait until upload is at ~50%**
3. **Tap "Cancel"**
4. **Verify:**
   - [ ] Upload stops immediately
   - [ ] Progress indicator disappears
   - [ ] Status changes to "Cancelled"
   - [ ] Returns to home screen or shows error
   - [ ] Can select new video
5. **✅ Expected:** Cancel works, no errors

#### Test 5.3: Cancel During Processing
1. Select and upload video
2. **Wait until processing is at ~50%**
3. **Tap "Cancel"**
4. **Verify:**
   - [ ] Processing stops
   - [ ] Polling stops (status stops updating)
   - [ ] Status changes to "Cancelled"
   - [ ] Can select new video
5. **✅ Expected:** Cancel works, can retry

#### Test 5.4: Multiple Videos Sequentially
1. **Upload video 1** (complete full flow)
2. **Save result to Photos**
3. **Tap "Create Another"**
4. **Upload video 2** (different video if possible)
5. **Complete full flow again**
6. **Verify:**
   - [ ] Both videos process successfully
   - [ ] Both highlights saved separately
   - [ ] No interference between jobs
   - [ ] App remains stable (no crashes)
7. **✅ Expected:** Multiple uploads work

#### Test 5.5: Error Handling - Stop Backend
1. **In terminal, stop backend:**
   ```bash
   # Find backend process
   ps aux | grep uvicorn
   # Kill it
   pkill -f uvicorn
   ```
2. **In app, try to upload video**
3. **Expected:**
   - [ ] Upload fails
   - [ ] Error alert appears
   - [ ] Error message is clear (e.g., "Network error", "Could not connect")
   - [ ] Can dismiss alert
   - [ ] App doesn't crash
4. **Restart backend:**
   ```bash
   cd /Users/rohanbhandari/Desktop/Professional_Projects/ML_PROJECTS_AI/moments_app/backend
   ./run.sh
   ```
5. **Try upload again**
6. **Expected:**
   - [ ] Upload works after restart
7. **✅ Expected:** Error handling works

---

### Phase 6: Performance & Quality (15 minutes)

#### Test 6.1: Memory Usage
1. Open **Debug Navigator** in Xcode (Cmd+7)
2. Look at **Memory** gauge while:
   - Uploading video
   - Processing video
   - Playing video
   - After completing 3 videos
3. **Verify:**
   - [ ] Memory usage reasonable (<500MB)
   - [ ] No memory leaks (memory returns to baseline after reset)
   - [ ] No warnings in console about memory

**✅ Expected:** Stable memory usage

#### Test 6.2: UI Responsiveness
1. During upload/processing:
   - [ ] UI remains responsive
   - [ ] Can tap Cancel button
   - [ ] Progress updates smoothly
   - [ ] No freezing or lag

**✅ Expected:** Smooth UI throughout

#### Test 6.3: Console Errors
1. Open **Debug Console** (Cmd+Shift+Y)
2. Review any errors or warnings
3. **Acceptable:**
   - Info logs about API calls
   - Debug logs about progress
4. **Not Acceptable:**
   - Crash logs
   - Thread warnings
   - Constraint errors

**✅ Expected:** No critical errors

---

## 📊 Test Results Summary

### Test Session Info
- **Date:** _____________
- **Tester:** _____________
- **Xcode:** 16.2
- **iOS:** _____________
- **Simulator:** iPhone 15 Pro

### Phase Results

#### Phase 1: Xcode Setup
- [ ] Project created successfully
- [ ] All files added correctly
- [ ] File structure correct
- **Issues:** _____________

#### Phase 2: Configuration
- [ ] Deployment target set to iOS 17.0
- [ ] Info.plist configured
- [ ] Signing configured
- **Issues:** _____________

#### Phase 3: Build
- [ ] Clean build successful
- [ ] Zero errors
- [ ] Warnings: _____________
- **Issues:** _____________

#### Phase 4: Core Functionality
- [ ] App launches
- [ ] Video selection works
- [ ] Upload progress tracks correctly
- [ ] Processing status updates
- [ ] Video downloads
- [ ] Playback works
- [ ] Share works
- [ ] Save to Photos works
- [ ] Create Another works
- **Issues:** _____________

#### Phase 5: Advanced Testing
- [ ] 15s highlight works
- [ ] 60s highlight works
- [ ] Cancel upload works
- [ ] Cancel processing works
- [ ] Multiple videos work
- [ ] Error handling works
- **Issues:** _____________

#### Phase 6: Performance
- [ ] Memory usage acceptable
- [ ] UI responsive
- [ ] No console errors
- **Issues:** _____________

### Critical Issues Found
1. _____________
2. _____________
3. _____________

### Non-Critical Issues
1. _____________
2. _____________

### Overall Assessment
- **Pass/Fail:** _____________
- **Ready for Production:** Yes / No
- **Blockers:** _____________
- **Next Steps:** _____________

---

## 🎯 Success Criteria

### Must Pass (Critical):
- ✅ App builds without errors
- ✅ App launches successfully
- ✅ Video upload completes
- ✅ Processing completes
- ✅ Video playback works
- ✅ No crashes during normal flow

### Should Pass (Important):
- ✅ Progress tracking accurate
- ✅ Status messages helpful
- ✅ Share functionality works
- ✅ Save to Photos works
- ✅ Error handling graceful

### Enhancement (Nice to Have):
- ✅ Smooth animations
- ✅ Fast processing
- ✅ Seamless video loops

---

## 📝 Notes for Tester

**Backend Must Be Running:**
```bash
# Check if running:
curl http://localhost:8000/health

# If not running:
cd backend && ./run.sh
```

**Simulator Tips:**
- Restart simulator if sluggish: Device → Erase All Content and Settings
- Add videos: Drag .mp4 files onto simulator window
- Screenshots: Cmd+S in simulator window
- Console logs: Xcode → View → Debug Area → Show Debug Area

**Common Issues:**
1. **"No videos" in picker** → Add videos to simulator Photos
2. **Upload fails** → Check backend is running
3. **App crashes** → Check console for errors, restart simulator
4. **Video won't play** → Verify video downloaded, check console

---

**Next Steps After Testing:**
1. Document all issues found
2. Fix critical bugs
3. Re-test failed scenarios
4. Deploy backend to Railway
5. Update API URL
6. Test on physical device
7. Prepare for App Store submission

---

**Testing Started:** __________
**Testing Completed:** __________
**Total Time:** __________
**Result:** PASS / FAIL / BLOCKED
