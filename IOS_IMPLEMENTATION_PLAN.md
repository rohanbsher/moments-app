# iOS App Implementation Plan - Detailed Analysis

**Date:** October 3, 2025
**Current Status:** Backend API Complete, Ready for iOS Development
**Goal:** Build production-ready iOS app and launch on App Store

---

## 🎯 Current Architecture Analysis

### What We Have (Backend)

✅ **REST API (Phase 2 - Complete)**
```
Endpoints Available:
- POST /api/v1/upload          → Upload video, get job_id
- GET /api/v1/jobs/{id}/status → Poll job status (0-100% progress)
- GET /api/v1/jobs/{id}        → Get detailed job info
- GET /api/v1/jobs/{id}/download → Download processed video
- DELETE /api/v1/jobs/{id}     → Cancel job
- GET /api/v1/upload/formats   → Get supported formats
```

✅ **Processing Algorithm (Phase 1.5 - Complete)**
```
Features:
- Scene detection (PySceneDetect)
- Motion analysis (optical flow)
- Audio analysis (NumPy-based, no dependencies)
- Diversity scoring (prevents repetition)
- Performance: 10-15x real-time
```

✅ **Infrastructure**
```
Current Setup:
- Local server (localhost:8000)
- SQLite database
- Local file storage
- Background task processing

Production Ready:
- Can deploy to Railway/Render
- Can migrate to PostgreSQL
- Can add S3/R2 cloud storage
- Can add Redis for scaling
```

### What We Need (iOS)

❌ **iOS App** - Not started yet
❌ **Video Upload** - Need SwiftUI implementation
❌ **Status Polling** - Need iOS timer/polling logic
❌ **Result Display** - Need AVPlayer integration
❌ **Monetization** - Need StoreKit 2 setup
❌ **App Store Assets** - Need design and screenshots

---

## 📱 iOS App Architecture Design

### Technology Stack

**Language & Framework:**
- Swift 5.9+ (latest)
- SwiftUI (declarative UI)
- iOS 16.0+ minimum (PhotosUI, StoreKit 2)

**Key Frameworks:**
```swift
import SwiftUI           // UI framework
import PhotosUI          // Video picker
import AVFoundation      // Video playback
import AVKit            // Video player UI
import StoreKit         // Subscriptions
```

**Architecture Pattern:**
```
MVVM (Model-View-ViewModel)
- Models: Data structures (Job, Video, Config)
- Views: SwiftUI views (ContentView, UploadView, ResultView)
- ViewModels: Business logic (@Observable classes)
- Services: API client, Storage manager
```

### App Structure

```
MomentsApp/
├── App/
│   ├── MomentsApp.swift           # App entry point
│   └── AppDelegate.swift          # Lifecycle management
│
├── Models/
│   ├── Job.swift                  # Job data model
│   ├── VideoConfig.swift          # Processing configuration
│   └── UploadResponse.swift       # API responses
│
├── ViewModels/
│   ├── VideoPickerViewModel.swift # Video selection logic
│   ├── UploadViewModel.swift      # Upload & processing
│   └── SubscriptionViewModel.swift # StoreKit logic
│
├── Views/
│   ├── HomeView.swift             # Main screen
│   ├── VideoPickerView.swift     # PHPickerViewController wrapper
│   ├── UploadProgressView.swift  # Progress UI
│   ├── ProcessingView.swift      # Status polling UI
│   ├── ResultView.swift           # AVPlayer preview
│   └── PaywallView.swift          # Subscription UI
│
├── Services/
│   ├── APIClient.swift            # URLSession networking
│   ├── StorageManager.swift      # Local cache, UserDefaults
│   └── SubscriptionManager.swift # StoreKit integration
│
└── Resources/
    ├── Assets.xcassets            # Images, colors
    └── Info.plist                 # App configuration
```

---

## 🔌 API Integration Strategy

### 1. API Client Implementation

**Purpose:** Handle all networking with the backend API

```swift
// Services/APIClient.swift

import Foundation

class APIClient {
    static let shared = APIClient()

    // Configuration
    private let baseURL = "http://localhost:8000" // Dev
    // private let baseURL = "https://api.moments.app" // Production

    // MARK: - Upload Video

    func uploadVideo(
        videoURL: URL,
        targetDuration: Int = 30,
        quality: String = "high",
        onProgress: @escaping (Double) -> Void
    ) async throws -> String {
        let url = URL(string: "\(baseURL)/api/v1/upload")!
        var request = URLRequest(url: url)
        request.httpMethod = "POST"

        // Create multipart form data
        let boundary = UUID().uuidString
        request.setValue("multipart/form-data; boundary=\(boundary)",
                        forHTTPHeaderField: "Content-Type")

        let body = createMultipartBody(
            videoURL: videoURL,
            targetDuration: targetDuration,
            quality: quality,
            boundary: boundary
        )

        // Upload with progress tracking
        let (data, response) = try await URLSession.shared.upload(
            for: request,
            from: body
        ) { progress in
            onProgress(Double(progress.completedUnitCount) /
                      Double(progress.totalUnitCount))
        }

        guard let httpResponse = response as? HTTPURLResponse,
              httpResponse.statusCode == 200 else {
            throw APIError.uploadFailed
        }

        let uploadResponse = try JSONDecoder().decode(
            UploadResponse.self,
            from: data
        )

        return uploadResponse.jobId
    }

    // MARK: - Poll Job Status

    func getJobStatus(jobId: String) async throws -> JobStatus {
        let url = URL(string: "\(baseURL)/api/v1/jobs/\(jobId)/status")!
        let (data, _) = try await URLSession.shared.data(from: url)
        return try JSONDecoder().decode(JobStatus.self, from: data)
    }

    // MARK: - Download Result

    func downloadResult(jobId: String) async throws -> URL {
        let url = URL(string: "\(baseURL)/api/v1/jobs/\(jobId)/download")!
        let (localURL, _) = try await URLSession.shared.download(from: url)

        // Move to permanent location
        let documentsURL = FileManager.default.urls(
            for: .documentDirectory,
            in: .userDomainMask
        )[0]
        let destinationURL = documentsURL.appendingPathComponent(
            "highlight_\(jobId).mp4"
        )

        try FileManager.default.moveItem(at: localURL, to: destinationURL)
        return destinationURL
    }
}

// MARK: - Models

struct UploadResponse: Codable {
    let jobId: String
    let message: String
    let estimatedTime: Int?

    enum CodingKeys: String, CodingKey {
        case jobId = "job_id"
        case message
        case estimatedTime = "estimated_time"
    }
}

struct JobStatus: Codable {
    let jobId: String
    let status: Status
    let progress: Int
    let message: String?
    let resultUrl: String?

    enum Status: String, Codable {
        case pending, processing, completed, failed, cancelled
    }

    enum CodingKeys: String, CodingKey {
        case jobId = "job_id"
        case status, progress, message
        case resultUrl = "result_url"
    }
}

enum APIError: Error {
    case uploadFailed
    case invalidResponse
    case networkError
}
```

### 2. Upload Flow Implementation

**Purpose:** Manage video upload and processing workflow

```swift
// ViewModels/UploadViewModel.swift

import SwiftUI
import Observation

@Observable
class UploadViewModel {
    // State
    var uploadProgress: Double = 0
    var processingProgress: Int = 0
    var currentStatus: JobStatus.Status = .pending
    var statusMessage: String = ""
    var errorMessage: String?
    var jobId: String?

    // Timer for polling
    private var pollingTimer: Timer?

    // MARK: - Upload & Process

    func uploadAndProcess(videoURL: URL) async {
        do {
            // 1. Upload video
            currentStatus = .pending
            statusMessage = "Uploading video..."

            let jobId = try await APIClient.shared.uploadVideo(
                videoURL: videoURL
            ) { progress in
                Task { @MainActor in
                    self.uploadProgress = progress
                }
            }

            self.jobId = jobId

            // 2. Start polling for status
            currentStatus = .processing
            statusMessage = "Processing video..."
            startPolling(jobId: jobId)

        } catch {
            errorMessage = "Upload failed: \(error.localizedDescription)"
        }
    }

    // MARK: - Status Polling

    private func startPolling(jobId: String) {
        pollingTimer = Timer.scheduledTimer(
            withTimeInterval: 2.0,
            repeats: true
        ) { [weak self] _ in
            Task {
                await self?.checkStatus(jobId: jobId)
            }
        }
    }

    private func checkStatus(jobId: String) async {
        do {
            let status = try await APIClient.shared.getJobStatus(jobId: jobId)

            await MainActor.run {
                self.currentStatus = status.status
                self.processingProgress = status.progress
                self.statusMessage = status.message ?? ""

                // Stop polling if completed or failed
                if status.status == .completed || status.status == .failed {
                    pollingTimer?.invalidate()
                    pollingTimer = nil
                }
            }
        } catch {
            await MainActor.run {
                errorMessage = "Status check failed: \(error.localizedDescription)"
            }
        }
    }

    // MARK: - Download Result

    func downloadResult() async -> URL? {
        guard let jobId = jobId else { return nil }

        do {
            statusMessage = "Downloading highlight..."
            let localURL = try await APIClient.shared.downloadResult(jobId: jobId)
            return localURL
        } catch {
            errorMessage = "Download failed: \(error.localizedDescription)"
            return nil
        }
    }
}
```

### 3. UI Implementation

**Purpose:** Build user-facing screens

```swift
// Views/ContentView.swift

import SwiftUI
import PhotosUI

struct ContentView: View {
    @State private var viewModel = UploadViewModel()
    @State private var selectedVideo: PhotosPickerItem?
    @State private var showingResult = false
    @State private var resultURL: URL?

    var body: some View {
        NavigationStack {
            VStack(spacing: 20) {
                // Header
                Text("Moments")
                    .font(.largeTitle.bold())

                Text("Create AI-powered highlights")
                    .foregroundStyle(.secondary)

                Spacer()

                // Video Picker
                PhotosPicker(
                    selection: $selectedVideo,
                    matching: .videos
                ) {
                    Label("Select Video", systemImage: "video.badge.plus")
                        .font(.headline)
                        .frame(maxWidth: .infinity)
                        .padding()
                        .background(.blue)
                        .foregroundStyle(.white)
                        .clipShape(RoundedRectangle(cornerRadius: 12))
                }
                .onChange(of: selectedVideo) { _, newValue in
                    Task {
                        await handleVideoSelection(newValue)
                    }
                }

                // Processing Status
                if viewModel.currentStatus == .processing {
                    VStack(spacing: 12) {
                        Text(viewModel.statusMessage)
                            .font(.headline)

                        ProgressView(value: Double(viewModel.processingProgress) / 100)

                        Text("\(viewModel.processingProgress)%")
                            .font(.caption)
                            .foregroundStyle(.secondary)
                    }
                    .padding()
                    .background(.ultraThinMaterial)
                    .clipShape(RoundedRectangle(cornerRadius: 12))
                }

                // Completed
                if viewModel.currentStatus == .completed {
                    Button {
                        Task {
                            resultURL = await viewModel.downloadResult()
                            showingResult = true
                        }
                    } label: {
                        Label("View Highlight", systemImage: "play.circle.fill")
                            .font(.headline)
                            .frame(maxWidth: .infinity)
                            .padding()
                            .background(.green)
                            .foregroundStyle(.white)
                            .clipShape(RoundedRectangle(cornerRadius: 12))
                    }
                }

                Spacer()
            }
            .padding()
            .navigationTitle("Home")
            .sheet(isPresented: $showingResult) {
                if let url = resultURL {
                    ResultView(videoURL: url)
                }
            }
        }
    }

    private func handleVideoSelection(_ item: PhotosPickerItem?) async {
        guard let item = item else { return }

        // Load video URL
        guard let videoURL = try? await item.loadTransferable(
            type: VideoTransferable.self
        )?.url else {
            return
        }

        // Start upload & processing
        await viewModel.uploadAndProcess(videoURL: videoURL)
    }
}

// Helper for transferable video
struct VideoTransferable: Transferable {
    let url: URL

    static var transferRepresentation: some TransferRepresentation {
        FileRepresentation(contentType: .movie) { video in
            SentTransferredFile(video.url)
        } importing: { received in
            let copy = FileManager.default.temporaryDirectory
                .appendingPathComponent(received.file.lastPathComponent)
            try FileManager.default.copyItem(at: received.file, to: copy)
            return Self(url: copy)
        }
    }
}
```

---

## 💰 Monetization Implementation

### StoreKit 2 Integration

```swift
// Services/SubscriptionManager.swift

import StoreKit

@Observable
class SubscriptionManager {
    static let shared = SubscriptionManager()

    // Products
    private(set) var monthlySubscription: Product?
    private(set) var isSubscribed = false

    // Usage tracking
    private let usageKey = "monthly_video_count"
    private let maxFreeVideos = 3

    // MARK: - Setup

    func loadProducts() async {
        do {
            let products = try await Product.products(
                for: ["com.moments.pro.monthly"]
            )
            monthlySubscription = products.first

            // Check subscription status
            await updateSubscriptionStatus()
        } catch {
            print("Failed to load products: \(error)")
        }
    }

    // MARK: - Purchase

    func purchase() async throws {
        guard let product = monthlySubscription else {
            throw SubscriptionError.productNotFound
        }

        let result = try await product.purchase()

        switch result {
        case .success(let verification):
            switch verification {
            case .verified(let transaction):
                isSubscribed = true
                await transaction.finish()
            case .unverified:
                throw SubscriptionError.verificationFailed
            }
        case .userCancelled:
            throw SubscriptionError.cancelled
        case .pending:
            throw SubscriptionError.pending
        @unknown default:
            throw SubscriptionError.unknown
        }
    }

    // MARK: - Usage Tracking

    func canProcessVideo() -> Bool {
        if isSubscribed {
            return true
        }

        let count = UserDefaults.standard.integer(forKey: usageKey)
        return count < maxFreeVideos
    }

    func incrementUsage() {
        guard !isSubscribed else { return }

        let count = UserDefaults.standard.integer(forKey: usageKey)
        UserDefaults.standard.set(count + 1, forKey: usageKey)
    }

    func getRemainingVideos() -> Int {
        if isSubscribed {
            return Int.max
        }

        let count = UserDefaults.standard.integer(forKey: usageKey)
        return max(0, maxFreeVideos - count)
    }

    // MARK: - Private

    private func updateSubscriptionStatus() async {
        for await result in Transaction.currentEntitlements {
            guard case .verified(let transaction) = result else {
                continue
            }

            if transaction.productID == "com.moments.pro.monthly" {
                isSubscribed = true
                return
            }
        }

        isSubscribed = false
    }
}

enum SubscriptionError: Error {
    case productNotFound
    case verificationFailed
    case cancelled
    case pending
    case unknown
}
```

---

## 📊 Implementation Phases

### Phase 1: Foundation (Week 1)

**Goal:** Basic app structure and video selection

**Tasks:**
1. Create Xcode project
   - Bundle ID: com.yourname.moments
   - Deployment target: iOS 16.0+
   - SwiftUI lifecycle

2. Setup project structure
   - Create folders (Models, Views, ViewModels, Services)
   - Add Info.plist permissions
   - Configure capabilities

3. Implement video picker
   - PHPickerViewController integration
   - Video preview
   - File handling

**Deliverables:**
- Working video selection
- Basic navigation
- Project foundation

**Time Estimate:** 8-12 hours

---

### Phase 2: API Integration (Week 2)

**Goal:** Upload and status polling working

**Tasks:**
1. Implement APIClient
   - Upload endpoint
   - Status endpoint
   - Error handling

2. Build UploadViewModel
   - Upload logic
   - Progress tracking
   - Status polling

3. Create upload UI
   - Progress bars
   - Status messages
   - Error alerts

**Deliverables:**
- Working upload
- Status polling
- Error handling

**Time Estimate:** 12-16 hours

---

### Phase 3: Results & Download (Week 3)

**Goal:** Display and save highlights

**Tasks:**
1. Implement download
   - Result endpoint
   - Local file management

2. Build result view
   - AVPlayer integration
   - Playback controls
   - Share functionality

3. Add Photos integration
   - Save to library
   - Permission handling

**Deliverables:**
- Video playback
- Save to Photos
- Share sheet

**Time Estimate:** 8-12 hours

---

### Phase 4: Monetization (Week 4)

**Goal:** Subscriptions working

**Tasks:**
1. Setup StoreKit
   - Create products in App Store Connect
   - Implement SubscriptionManager
   - Receipt validation

2. Build paywall
   - Subscription UI
   - Pricing display
   - Purchase flow

3. Add usage tracking
   - Free video counter
   - Limit enforcement
   - Upgrade prompts

**Deliverables:**
- Working subscriptions
- Usage limits
- Paywall UI

**Time Estimate:** 12-16 hours

---

### Phase 5: Polish (Week 5-6)

**Goal:** Production ready

**Tasks:**
1. Onboarding
   - Welcome screens
   - Feature highlights
   - Permissions flow

2. Design
   - App icon
   - Launch screen
   - Color scheme
   - Typography

3. Testing
   - TestFlight beta
   - Bug fixes
   - Performance

**Deliverables:**
- Polished UI
- Onboarding flow
- Beta tested

**Time Estimate:** 16-20 hours

---

## 📋 Prerequisites & Setup

### Requirements

**Hardware:**
- Mac with macOS Sonoma+ (for Xcode 15)
- iPhone/iPad for testing (iOS 16+)

**Software:**
- Xcode 15.0+
- Apple Developer Account ($99/year)
- CocoaPods or SPM (for dependencies)

**Backend:**
- ✅ API running (already done!)
- Need: Deploy to production server
- Need: HTTPS endpoint

### Apple Developer Setup

1. **Create App ID**
   ```
   Identifier: com.yourname.moments
   Capabilities:
   - In-App Purchase
   - Push Notifications (future)
   ```

2. **Create Subscription Products**
   ```
   Product ID: com.moments.pro.monthly
   Price: $4.99/month
   Free trial: 7 days (optional)
   ```

3. **Generate Certificates**
   - Development certificate
   - Distribution certificate
   - Push notification certificate (future)

---

## 🚀 Deployment Checklist

### Backend Deployment

Before building iOS app, deploy backend:

- [ ] Deploy API to Railway/Render
- [ ] Setup PostgreSQL database
- [ ] Configure Cloudflare R2 storage
- [ ] Setup HTTPS with domain
- [ ] Test API endpoints remotely
- [ ] Update iOS app with production URL

### iOS App Store

- [ ] Complete app metadata
- [ ] Design app icon (1024x1024)
- [ ] Create screenshots (all sizes)
- [ ] Write app description
- [ ] Record preview video (optional)
- [ ] Setup privacy policy URL
- [ ] Configure age rating
- [ ] Submit for review

---

## 💡 Next Steps

**Immediate (This Week):**
1. Deploy backend to production server
2. Create Xcode project
3. Implement video picker
4. Test API integration locally

**Next Week:**
5. Build upload flow
6. Implement status polling
7. Test end-to-end workflow

**Following Weeks:**
8. Add result playback
9. Implement subscriptions
10. Polish and test
11. Submit to App Store

---

**Ready to start iOS development!** 🚀

The backend is solid, the roadmap is clear. Let's build the iOS app step by step.
