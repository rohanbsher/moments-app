# End-to-End Testing Plan - Moments App

## Purpose
Comprehensive testing plan to verify all features work correctly after the UX/UI redesign, including resolving the IP address build cache issue.

---

## Pre-Test Requirements

### 1. Backend Status
- [ ] Backend running at `http://192.168.0.5:8000`
- [ ] Verify with: `curl http://192.168.0.5:8000/api/v1/health`
- [ ] Expected response: `{"status":"healthy"}`

### 2. Test Videos Ready
Prepare 3 test videos in your photo library:
- [ ] **Video 1**: Short clip with faces (10-30s)
- [ ] **Video 2**: Video with clear speech/dialogue (15-45s)
- [ ] **Video 3**: Action video (sports, dancing, movement) (20-60s)

### 3. iPhone Setup
- [ ] iPhone 16 Pro Max connected via USB
- [ ] Device unlocked
- [ ] Photo library access granted to Moments app
- [ ] WiFi connected to same network as backend (192.168.0.x)

---

## CRITICAL: Resolve Build Cache Issue

**Problem**: App is using cached build with old IP `192.168.0.11` instead of new IP `192.168.0.5`

**Solution**: Force clean build in Xcode

### Steps to Clean & Rebuild:

1. **Open Xcode Project**
   ```bash
   open ios/MomentsApp.xcodeproj
   ```

2. **Select Your iPhone**
   - Top toolbar: Select "iPhone 16 Pro Max (Rohan's)" from device dropdown

3. **Clean Build Folder** (⌘ + Shift + K)
   - Menu: Product → Clean Build Folder
   - Wait for "Clean Succeeded" message (3-5 seconds)

4. **Delete Derived Data** (Belt & Suspenders)
   - Menu: Xcode → Settings → Locations
   - Click arrow next to Derived Data path
   - Delete the `MomentsApp-*` folder
   - OR via terminal:
   ```bash
   rm -rf ~/Library/Developer/Xcode/DerivedData/MomentsApp-*
   ```

5. **Build & Run** (⌘ + R)
   - Menu: Product → Run
   - Watch for "Build Succeeded" then "Running on iPhone 16 Pro Max"
   - App will install fresh build with correct IP

6. **Verify IP Address** (CRITICAL CHECK)
   - In Xcode bottom panel, open "Console" output
   - Try uploading a test video
   - Look for network requests in console
   - MUST show: `http://192.168.0.5:8000` (NOT .11)
   - If still showing `.11`, repeat steps 3-5

---

## Testing Checklist

### Phase 1: Installation & Launch ✅

**Objective**: Verify app installs and launches with new design

- [ ] App installs without errors
- [ ] App icon appears on home screen
- [ ] App launches without crash
- [ ] Home screen loads within 2 seconds
- [ ] No error alerts on launch

**Success Criteria**: App opens to redesigned home screen with AI badge visible

---

### Phase 2: UI Components & Design 🎨

**Objective**: Verify all new UI components render correctly

#### Hero Section
- [ ] **AI Badge** appears at top with "AI-Powered" text
- [ ] **Shimmer animation** visible on AI badge (subtle wave effect)
- [ ] **Wand icon** (🪄) displays and pulses gently
- [ ] **"Moments"** title in large, bold, rounded font
- [ ] **"AI finds your best video moments"** subtitle visible

#### Upload Section
- [ ] **Gradient background card** visible (purple/blue tint)
- [ ] **"Select Video"** button with video+plus icon
- [ ] **Three tip badges** at bottom:
  - 😊 "With people"
  - 🎤 "With speech"
  - ✨ "With action"
- [ ] Card has subtle shadow

#### Feature Showcase
- [ ] **"AI-Powered Analysis"** section header
- [ ] **Three feature cards** displayed:
  1. **Face Detection** (blue gradient, smiling face icon)
  2. **Speech Analysis** (purple gradient, waveform icon)
  3. **Emotion Recognition** (pink gradient, heart icon)
- [ ] Each card shows:
  - Circular icon with gradient
  - Title text
  - Description text (2 lines max)

**Success Criteria**: All components match the design in UX_UI_REDESIGN_COMPLETE.md, colors are vibrant, animations are smooth

---

### Phase 3: Animations & Micro-Interactions ✨

**Objective**: Verify all animations work smoothly at 60fps

#### On Launch
- [ ] **AI Badge** bounces in when screen appears
- [ ] **Wand icon** pulses continuously (scale 1.0 → 1.05)
- [ ] **Shimmer** sweeps across AI badge every 2 seconds

#### Tap Interactions
- [ ] **Select Video button** tap:
  - Light haptic feedback felt
  - No visual lag
  - Photo picker opens immediately
- [ ] **Cancel button** (during processing):
  - Light haptic feedback
  - Processing stops immediately

#### Performance Check
- [ ] Scrolling is smooth (no stuttering)
- [ ] No animation frame drops
- [ ] No UI lag when tapping buttons
- [ ] Dark mode colors look correct (pure black background)

**Success Criteria**: All animations are smooth, haptic feedback is immediate, no performance issues

---

### Phase 4: Upload Flow 📤

**Objective**: Test complete video upload and processing flow

#### Test Case 1: Upload Video with Faces

1. **Start Upload**
   - [ ] Tap "Select Video" button
   - [ ] Haptic feedback occurs
   - [ ] Photo picker opens

2. **Select Video**
   - [ ] Choose test video with faces
   - [ ] Photo picker closes automatically
   - [ ] Home screen transitions to processing view

3. **Processing View Appears**
   - [ ] **AI Brain animation** visible:
     - Outer pulsing glow circle (160px)
     - Inner gradient circle (120px)
     - Brain icon (🧠) floating up/down
   - [ ] **Status message** updates dynamically:
     - 0-30%: "AI analyzing scenes..."
     - 30-60%: "Detecting faces and emotions..."
     - 60-90%: "Finding best moments..."
     - 90-100%: "Creating your highlight..."
   - [ ] **Progress percentage** updates (0% → 100%)
   - [ ] **Progress bar** animates smoothly (gradient fill)
   - [ ] **Loading dots** animate (bounce up/down)
   - [ ] **Cancel button** visible at bottom

4. **Backend Communication**
   - [ ] Upload completes (check Xcode console: `Status Code: 200`)
   - [ ] Job ID received (console: `Job ID: abc123...`)
   - [ ] Polling starts every 2 seconds
   - [ ] Progress updates reflect backend status

5. **Processing Completes**
   - [ ] View transitions to success screen
   - [ ] Success haptic feedback occurs (stronger vibration)

6. **Success Screen**
   - [ ] **Green checkmark** in circle bounces in
   - [ ] **"Highlight Ready!"** title
   - [ ] **"AI found your best moments"** subtitle
   - [ ] **"View Highlight"** button (primary style, gradient)
   - [ ] **"Create Another"** button (secondary style, gray)

7. **View Result**
   - [ ] Tap "View Highlight" button
   - [ ] Success haptic feedback
   - [ ] Navigation to ResultView
   - [ ] Video player loads
   - [ ] Highlight plays automatically
   - [ ] Video has sound (if original had audio)
   - [ ] Back button returns to home

**Success Criteria**:
- Complete flow works without errors
- All status messages appear correctly
- Progress updates smoothly
- Highlight video plays successfully
- Network requests use `192.168.0.5:8000` (NOT .11)

---

#### Test Case 2: Upload Video with Speech

Repeat Phase 4 steps with test video containing dialogue.

**Additional Checks**:
- [ ] Status message "Finding best moments..." appears
- [ ] Backend logs show speech detection working
- [ ] Highlight includes speech-heavy segments

---

#### Test Case 3: Upload Action Video

Repeat Phase 4 steps with action/sports video.

**Additional Checks**:
- [ ] Motion detection works (backend logs)
- [ ] Highlight captures high-motion moments

---

### Phase 5: Error Handling 🚨

**Objective**: Verify friendly error messages appear instead of technical jargon

#### Test Case 1: Backend Offline

1. **Stop Backend**
   ```bash
   # In terminal where backend is running, press Ctrl+C
   ```

2. **Try Upload**
   - [ ] Select video in app
   - [ ] Error alert appears
   - [ ] **Friendly message shown**: "Server is not responding. Please make sure the backend is running and try again."
   - [ ] **NOT technical**: No "NSURLErrorDomain" or "Code=-1004"
   - [ ] Tap "OK" to dismiss
   - [ ] Returns to home screen (idle state)

**Success Criteria**: User sees helpful, actionable error message

---

#### Test Case 2: Network Timeout

1. **Enable Airplane Mode** on iPhone
2. **Try Upload**
   - [ ] Select video
   - [ ] Wait for timeout
   - [ ] **Friendly message**: "Couldn't connect to the server. Please check your WiFi connection and try again."
   - [ ] No technical error codes visible

3. **Disable Airplane Mode**
4. **Retry Upload**
   - [ ] Works normally after WiFi reconnects

**Success Criteria**: Clear guidance for network issues

---

#### Test Case 3: Photo Library Permission Denied

1. **Revoke Permission**
   - Settings → Moments → Photos → None

2. **Tap Select Video**
   - [ ] Permission alert appears: "Photo Library Access Required"
   - [ ] Message: "Moments needs access to your photo library..."
   - [ ] Two buttons: "Open Settings" / "Cancel"

3. **Grant Permission**
   - [ ] Tap "Open Settings"
   - [ ] Re-enable photo access
   - [ ] Return to app
   - [ ] Try upload again - works

**Success Criteria**: Clear permission flow with helpful messaging

---

### Phase 6: State Management 🔄

**Objective**: Verify app handles state transitions correctly

#### Test: Create Multiple Highlights

1. **First Upload**
   - [ ] Upload video, wait for success
   - [ ] Tap "Create Another"
   - [ ] Light haptic feedback
   - [ ] Returns to idle home screen
   - [ ] All state reset (no leftover progress)

2. **Second Upload**
   - [ ] Repeat upload with different video
   - [ ] Processing starts fresh at 0%
   - [ ] Completes successfully

3. **Navigation**
   - [ ] From success screen, tap "View Highlight"
   - [ ] Navigate to ResultView
   - [ ] Tap back button
   - [ ] Returns to success screen (not home)
   - [ ] Tap "Create Another" to reset

**Success Criteria**: State transitions are clean, no stuck progress indicators

---

#### Test: Cancel During Processing

1. **Start Upload**
   - [ ] Select video
   - [ ] Processing begins

2. **Cancel Mid-Processing**
   - [ ] Wait until ~40% progress
   - [ ] Tap "Cancel" button
   - [ ] Light haptic feedback
   - [ ] Processing stops immediately
   - [ ] Returns to idle home screen
   - [ ] No error message shown

3. **Retry Upload**
   - [ ] Upload same video again
   - [ ] Processes normally from 0%

**Success Criteria**: Cancel works reliably, no lingering state

---

### Phase 7: Accessibility & Polish ♿️

**Objective**: Verify accessibility features work

#### Dynamic Type
1. **Change Text Size**
   - Settings → Display & Brightness → Text Size
   - [ ] Move slider to largest size
   - [ ] Return to Moments app
   - [ ] All text scales appropriately
   - [ ] No text cutoff or overlap
   - [ ] Layout adjusts correctly

#### VoiceOver
1. **Enable VoiceOver**
   - Settings → Accessibility → VoiceOver → On
2. **Navigate App**
   - [ ] "Select Video" button is readable
   - [ ] Feature cards have meaningful labels
   - [ ] Progress updates are announced
   - [ ] Error messages are read aloud

#### Dark Mode
- [ ] App uses pure black background (OLED optimized)
- [ ] Text is high contrast (white on black)
- [ ] Gradients are vibrant
- [ ] No light mode leakage

**Success Criteria**: App is fully accessible and polished

---

## Quick Verification Checklist

Use this for rapid testing after fixing the IP issue:

### 30-Second Smoke Test
1. [ ] App launches without crash
2. [ ] AI badge shimmer is visible
3. [ ] Wand icon pulses
4. [ ] Tap "Select Video" → photo picker opens
5. [ ] Select video → processing screen appears
6. [ ] Brain animation is active
7. [ ] Progress updates from 0% → 100%
8. [ ] Success screen appears
9. [ ] Tap "View Highlight" → video plays

**If all 9 pass**: Core functionality is working ✅

---

## Success Criteria Summary

### Must Pass (Critical)
- ✅ App installs with correct IP (192.168.0.5)
- ✅ Complete upload flow works (upload → process → success → view)
- ✅ Friendly error messages (no technical jargon)
- ✅ All animations are smooth (60fps)
- ✅ Haptic feedback on all interactions

### Should Pass (Important)
- ✅ All UI components match design
- ✅ Progress updates reflect backend status
- ✅ Cancel works reliably
- ✅ State management is clean
- ✅ Dark mode is optimized

### Nice to Have (Polish)
- ✅ VoiceOver works correctly
- ✅ Dynamic Type scales properly
- ✅ All 3 AI features work (face/speech/emotion)

---

## Troubleshooting Guide

### Issue: App still shows old IP (192.168.0.11)

**Solution**:
```bash
# Nuclear option - delete all Xcode caches
rm -rf ~/Library/Developer/Xcode/DerivedData/*
rm -rf ~/Library/Caches/com.apple.dt.Xcode

# Restart Xcode
killall Xcode
open ios/MomentsApp.xcodeproj

# Clean & rebuild
# In Xcode: Cmd+Shift+K, then Cmd+R
```

### Issue: Upload timeout even with correct IP

**Check**:
1. Backend is running: `curl http://192.168.0.5:8000/api/v1/health`
2. iPhone on same WiFi: Settings → WiFi → check network name
3. Firewall not blocking: System Settings → Firewall → ensure HTTP allowed

### Issue: Animations are laggy

**Check**:
1. Close other apps (free up memory)
2. Restart iPhone
3. Ensure Debug mode is disabled (use Release scheme in Xcode)

### Issue: No haptic feedback

**Check**:
1. iPhone Haptics enabled: Settings → Sounds & Haptics → System Haptics ON
2. Low Power Mode disabled: Settings → Battery → Low Power Mode OFF

---

## Testing Log Template

Date: ___________
Tester: Rohan
Device: iPhone 16 Pro Max, iOS 18.6.2
Backend: http://192.168.0.5:8000

| Test | Status | Notes |
|------|--------|-------|
| Clean build with correct IP | ⬜ Pass / ⬜ Fail | |
| UI components render | ⬜ Pass / ⬜ Fail | |
| Animations smooth | ⬜ Pass / ⬜ Fail | |
| Upload flow works | ⬜ Pass / ⬜ Fail | |
| Friendly errors | ⬜ Pass / ⬜ Fail | |
| Cancel works | ⬜ Pass / ⬜ Fail | |
| Create multiple highlights | ⬜ Pass / ⬜ Fail | |

**Overall Result**: ⬜ Ready for Production / ⬜ Needs Fixes

---

## Next Steps After Testing

### If All Tests Pass ✅
1. Document any minor issues found
2. Consider adding onboarding flow (Phase 2 feature)
3. Prepare for App Store submission

### If Tests Fail ❌
1. Document exact error messages
2. Check Xcode console for clues
3. Verify backend logs for API errors
4. Report issues with screenshots

---

**Ready to Start Testing!** 🚀

Begin with the "CRITICAL: Resolve Build Cache Issue" section, then work through phases 1-7.
