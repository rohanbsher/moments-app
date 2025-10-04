# iOS App Setup Guide - Moments

## Project Structure Created

```
ios/MomentsApp/
├── Core/
│   ├── Models/
│   │   ├── Job.swift                    ✅ Job model with status tracking
│   │   └── VideoConfig.swift            ✅ Video processing configuration
│   └── Services/
│       └── APIClient.swift              ✅ Complete API client with multipart upload
├── Features/
│   ├── Home/Views/
│   │   └── HomeView.swift               ✅ Main app interface
│   ├── Upload/
│   │   ├── ViewModels/
│   │   │   └── UploadViewModel.swift    ✅ Upload logic and state management
│   │   └── Views/
│   │       └── VideoPicker.swift        ✅ PHPicker video selector
│   └── Result/Views/
│       └── ResultView.swift             ✅ Video playback and sharing
├── MomentsApp.swift                      ✅ App entry point
└── Info.plist                            ✅ Permissions and App Transport Security

```

## Step 1: Create Xcode Project

### Option A: Command Line (Recommended for Quick Setup)

```bash
cd /Users/rohanbhandari/Desktop/Professional_Projects/ML_PROJECTS_AI/moments_app/ios

# Create Xcode project
xcodebuild -project MomentsApp.xcodeproj \
  -scheme MomentsApp \
  -sdk iphonesimulator \
  -destination 'platform=iOS Simulator,name=iPhone 15 Pro'
```

### Option B: Xcode GUI (Recommended for Full Control)

1. Open Xcode
2. File → New → Project
3. Choose "iOS" → "App"
4. Settings:
   - **Product Name:** MomentsApp
   - **Team:** Select your Apple Developer team
   - **Organization Identifier:** com.yourdomain (e.g., com.moments)
   - **Interface:** SwiftUI
   - **Language:** Swift
   - **Minimum Deployments:** iOS 17.0
5. Save location: `/Users/rohanbhandari/Desktop/Professional_Projects/ML_PROJECTS_AI/moments_app/ios/`

## Step 2: Add Source Files to Xcode

1. Delete the default `ContentView.swift` and `MomentsAppApp.swift` (if created by template)

2. **Add all Swift files:**
   - Right-click on "MomentsApp" folder in Xcode
   - Select "Add Files to 'MomentsApp'..."
   - Navigate to `/Users/rohanbhandari/Desktop/Professional_Projects/ML_PROJECTS_AI/moments_app/ios/MomentsApp/`
   - Select all `.swift` files and folders
   - Ensure "Copy items if needed" is **unchecked** (files are already in place)
   - Ensure "Create groups" is selected
   - Click "Add"

3. **Add Info.plist:**
   - Select the MomentsApp target
   - Go to "Info" tab
   - Click "Custom iOS Target Properties"
   - Right-click → "Open As" → "Source Code"
   - Replace with contents from `Info.plist` file

## Step 3: Configure Project Settings

### General Tab
- **Display Name:** Moments
- **Bundle Identifier:** com.yourdomain.MomentsApp
- **Version:** 1.0
- **Build:** 1
- **Deployment Target:** iOS 17.0

### Signing & Capabilities
- **Team:** Select your Apple Developer team
- **Signing Certificate:** Automatic

**Add Capabilities:**
- Click "+ Capability"
- Add "App Transport Security" (already in Info.plist)

### Build Settings
- **Swift Language Version:** Swift 5
- **Optimization Level:** -Onone (Debug), -O (Release)

## Step 4: Update API Base URL

### For Localhost Testing (Current):
No changes needed - already configured for `http://localhost:8000`

### For Production (After Railway Deployment):
Edit `Core/Services/APIClient.swift`:

```swift
// Line 14 - Change from:
private let baseURL = "http://localhost:8000"

// To:
private let baseURL = "https://moments-app-production.up.railway.app"
```

## Step 5: Run the App

### Using Xcode Simulator

1. Select simulator: iPhone 15 Pro
2. Click ▶️ Run button (or Cmd+R)
3. Wait for build to complete
4. App should launch in simulator

### Verify Backend is Running

Before testing upload, ensure backend is running:

```bash
cd /Users/rohanbhandari/Desktop/Professional_Projects/ML_PROJECTS_AI/moments_app/backend
./run.sh
```

Backend should be at `http://localhost:8000`

## Step 6: Testing the App

### Test Flow:

1. **Launch App**
   - Should see "Moments" home screen
   - "Select Video" button visible

2. **Pick a Video**
   - Tap "Select Video"
   - Choose a video from simulator's photo library
   - If no videos, add one via: Simulator → Photos app → drag video file

3. **Upload & Processing**
   - Upload progress shows 0-100%
   - Processing begins automatically
   - Status updates every 2 seconds
   - Progress shown as percentage

4. **View Result**
   - When complete, "Highlight Ready!" appears
   - Tap "View Highlight" to watch
   - Video plays in AVPlayer
   - Can share or save to Photos

### Expected Timings:
- **Upload:** ~10-30 seconds (depending on video size)
- **Processing:** 10-15x real-time (60s video → 4-6s processing)
- **Download:** ~5-10 seconds

## Troubleshooting

### Build Errors

**Error: "No such module 'Observation'"**
- **Fix:** Ensure deployment target is iOS 17.0+
- Go to Project Settings → General → Minimum Deployments → iOS 17.0

**Error: "Cannot find 'PHPicker' in scope"**
- **Fix:** Add `import PhotosUI` at top of file

**Error: "Cannot find 'AVPlayer' in scope"**
- **Fix:** Add `import AVKit` at top of file

### Runtime Errors

**Error: "Network request failed"**
- **Fix:** Ensure backend is running at `http://localhost:8000`
- Test: `curl http://localhost:8000/health`

**Error: "The resource could not be loaded because the App Transport Security policy requires the use of a secure connection"**
- **Fix:** Verify Info.plist has localhost exception
- Or use HTTPS production URL

**Error: "Video upload fails with 413"**
- **Fix:** Video too large (>5GB limit)
- Try smaller test video

### Video Picker Issues

**No videos appear in picker:**
- Add test videos to simulator:
  - Drag .mp4 file onto simulator
  - Or use Safari to download a video
  - Open Photos app to verify

## Architecture Overview

### MVVM Pattern

```
View → ViewModel → Service → API
 ↑        ↓
 └────────┘
   @Observable
```

### Data Flow

1. **Upload:**
   ```
   HomeView → VideoPicker → UploadViewModel.uploadAndProcess()
   → APIClient.uploadVideo() → Backend API
   ```

2. **Status Polling:**
   ```
   UploadViewModel.startPolling() → APIClient.checkStatus()
   → Update UI every 2s
   ```

3. **Download:**
   ```
   UploadViewModel.handleCompletion() → APIClient.downloadVideo()
   → Save to Documents → Display in ResultView
   ```

### State Management

Using **@Observable** (iOS 17+):
- No @Published needed
- No @StateObject/@ObservedObject
- Cleaner, more performant
- Automatic view updates

## Production Deployment Checklist

### Before App Store Submission:

- [ ] Change API baseURL to production Railway URL
- [ ] Remove localhost ATS exception from Info.plist
- [ ] Add proper app icon (1024x1024)
- [ ] Add launch screen
- [ ] Test on physical device
- [ ] Verify all permissions work
- [ ] Test video upload with cellular data
- [ ] Ensure video playback works
- [ ] Test share functionality
- [ ] Test save to Photos
- [ ] Add analytics (optional)
- [ ] Add crash reporting (optional)
- [ ] Update App Store metadata
- [ ] Create screenshots for App Store
- [ ] Submit for TestFlight beta

## API Endpoints Used

### 1. Upload Video
```
POST /api/v1/upload/video
Content-Type: multipart/form-data

Parameters:
- file: Video file (mp4/mov/avi)
- duration: Target duration (seconds)
- min_segment: Min segment length
- max_segment: Max segment length

Response:
{
  "job_id": "uuid",
  "status": "queued",
  "message": "Video uploaded successfully"
}
```

### 2. Check Status
```
GET /api/v1/jobs/{job_id}/status

Response:
{
  "job_id": "uuid",
  "status": "processing",
  "progress": 45,
  "message": "Analyzing scene 23 of 50"
}
```

### 3. Download Video
```
GET /api/v1/jobs/{job_id}/download

Response: Binary video file (mp4)
```

## Performance Optimization

### Current Implementation:
- ✅ Async/await for all network calls
- ✅ Progress tracking during upload
- ✅ Efficient polling (2s intervals)
- ✅ Video caching in Documents directory
- ✅ Automatic cleanup on reset

### Future Improvements:
- [ ] Background upload (URLSession background configuration)
- [ ] Push notifications for completion
- [ ] Video thumbnail generation
- [ ] Multiple video selection
- [ ] Batch processing
- [ ] Cloud storage integration (iCloud)

## Next Steps

### Phase 1: MVP Testing (Current)
1. ✅ Create all Swift files
2. ⏳ Setup Xcode project
3. ⏳ Test on simulator with localhost backend
4. ⏳ Verify upload → processing → download flow

### Phase 2: Production Ready
1. Deploy backend to Railway (get HTTPS URL)
2. Update API baseURL in APIClient
3. Test on physical device
4. Add proper error handling UI

### Phase 3: App Store
1. Add app icon and launch screen
2. Create App Store listing
3. Submit for review
4. Launch!

---

**Current Status:** All Swift code written ✅
**Next Action:** Create Xcode project and test on simulator
**Backend Required:** http://localhost:8000 (currently running ✅)
