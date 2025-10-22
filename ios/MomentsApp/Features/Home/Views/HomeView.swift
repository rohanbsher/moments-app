//
//  HomeView.swift
//  MomentsApp
//
//  Redesigned main home view with modern 2025 UX/UI
//

import SwiftUI
import Photos

struct HomeView: View {
    @State private var viewModel = UploadViewModel()
    @State private var showVideoPicker = false
    @State private var selectedVideoURL: URL?
    @State private var showPermissionAlert = false

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(spacing: Spacing.xxl) {
                    // Hero Section
                    heroSection

                    // Main Content
                    if viewModel.isActive {
                        processingView
                    } else if let videoURL = viewModel.downloadedVideoURL {
                        successView(videoURL: videoURL)
                    } else {
                        uploadSection
                        featureShowcase
                    }
                }
                .padding(.horizontal, Spacing.md)
                .padding(.bottom, Spacing.xxxl)
            }
            .background(Color.backgroundPrimary)
            .navigationBarTitleDisplayMode(.inline)
            .fullScreenCover(isPresented: $showVideoPicker) {
                VideoPicker(selectedVideoURL: $selectedVideoURL)
            }
            .onChange(of: selectedVideoURL) { oldValue, newValue in
                if let videoURL = newValue {
                    HapticManager.shared.medium()
                    Task {
                        await viewModel.uploadAndProcess(videoURL: videoURL)
                    }
                }
            }
            .alert("Error", isPresented: .constant(viewModel.errorMessage != nil)) {
                Button("OK") {
                    viewModel.errorMessage = nil
                    viewModel.detailedError = ""
                }
            } message: {
                Text(friendlyErrorMessage(viewModel.errorMessage ?? ""))
            }
            .alert("Photo Library Access Required", isPresented: $showPermissionAlert) {
                Button("Open Settings") {
                    if let settingsURL = URL(string: UIApplication.openSettingsURLString) {
                        UIApplication.shared.open(settingsURL)
                    }
                }
                Button("Cancel", role: .cancel) {}
            } message: {
                Text("Moments needs access to your photo library to select videos for creating highlights.")
            }
        }
    }

    // MARK: - Hero Section

    private var heroSection: some View {
        VStack(spacing: Spacing.md) {
            // AI Badge
            AIBadge(style: .large)
                .bounceIn()

            // App Icon & Title
            VStack(spacing: Spacing.xs) {
                Image(systemName: "wand.and.stars")
                    .font(.system(size: 64))
                    .foregroundStyle(LinearGradient.aiGradient)
                    .pulse()

                Text("Moments")
                    .font(.displayMedium)
                    .foregroundColor(.textPrimary)

                Text("AI finds your best video moments")
                    .font(.bodyMedium)
                    .foregroundColor(.textSecondary)
                    .multilineTextAlignment(.center)
            }
        }
        .padding(.top, Spacing.xxl)
    }

    // MARK: - Upload Section

    private var uploadSection: some View {
        Button {
            HapticManager.shared.light()
            requestPhotoLibraryPermission()
        } label: {
            VStack(spacing: Spacing.md) {
                ZStack {
                    // Gradient background
                    RoundedRectangle(cornerRadius: CornerRadius.extraLarge)
                        .fill(LinearGradient.aiGradient.opacity(0.1))
                        .frame(height: 200)

                    // Content
                    VStack(spacing: Spacing.sm) {
                        Image(systemName: "video.badge.plus")
                            .font(.system(size: 56))
                            .foregroundStyle(LinearGradient.aiGradient)

                        Text("Select Video")
                            .font(.headingMedium)
                            .foregroundColor(.textPrimary)

                        Text("Choose from your library")
                            .font(.captionLarge)
                            .foregroundColor(.textSecondary)
                    }
                }

                // Quick tips
                HStack(spacing: Spacing.md) {
                    tipBadge(icon: "face.smiling", text: "With people")
                    tipBadge(icon: "waveform", text: "With speech")
                    tipBadge(icon: "sparkles", text: "With action")
                }
            }
        }
        .buttonStyle(.plain)
    }

    private func tipBadge(icon: String, text: String) -> some View {
        HStack(spacing: Spacing.xxs) {
            Image(systemName: icon)
                .font(.system(size: 12))
            Text(text)
                .font(.captionSmall)
        }
        .foregroundColor(.textTertiary)
        .padding(.horizontal, Spacing.xs)
        .padding(.vertical, Spacing.xxs)
        .background(Color.backgroundSecondary)
        .cornerRadius(CornerRadius.small)
    }

    // MARK: - Feature Showcase

    private var featureShowcase: some View {
        VStack(alignment: .leading, spacing: Spacing.md) {
            Text("AI-Powered Analysis")
                .font(.headingMedium)
                .foregroundColor(.textPrimary)

            VStack(spacing: Spacing.sm) {
                FeatureCard.faceDetection
                FeatureCard.speechAnalysis
                FeatureCard.emotionAnalysis
            }
        }
    }

    // MARK: - Processing View

    private var processingView: some View {
        VStack(spacing: Spacing.xxl) {
            Spacer()

            // AI Brain Animation
            ZStack {
                // Outer glow
                Circle()
                    .fill(LinearGradient.aiGradient.opacity(0.2))
                    .frame(width: 160, height: 160)
                    .pulse()

                // Main circle with gradient
                Circle()
                    .fill(LinearGradient.aiGradient)
                    .frame(width: 120, height: 120)

                // Brain icon
                Image(systemName: "brain")
                    .font(.system(size: 48))
                    .foregroundColor(.white)
                    .float()
            }

            // Progress Info
            VStack(spacing: Spacing.sm) {
                Text(aiStatusMessage)
                    .font(.headingSmall)
                    .foregroundColor(.textPrimary)
                    .multilineTextAlignment(.center)

                Text(viewModel.progressText)
                    .font(.displaySmall)
                    .foregroundColor(.brandPrimary)
                    .bold()

                // Progress Bar
                GeometryReader { geometry in
                    ZStack(alignment: .leading) {
                        // Background
                        RoundedRectangle(cornerRadius: 4)
                            .fill(Color.backgroundSecondary)
                            .frame(height: 8)

                        // Progress
                        RoundedRectangle(cornerRadius: 4)
                            .fill(LinearGradient.aiGradient)
                            .frame(
                                width: geometry.size.width * progressValue,
                                height: 8
                            )
                            .animation(.smooth, value: progressValue)
                    }
                }
                .frame(height: 8)

                LoadingDotsView()
                    .padding(.top, Spacing.xs)
            }
            .padding(.horizontal, Spacing.xxl)

            Spacer()

            // Cancel Button
            Button {
                HapticManager.shared.light()
                viewModel.cancelProcessing()
            } label: {
                Text("Cancel")
                    .font(.labelLarge)
                    .foregroundColor(.textSecondary)
            }
        }
        .padding()
    }

    private var progressValue: Double {
        if viewModel.isUploading {
            return viewModel.uploadProgress
        } else {
            return Double(viewModel.processingProgress) / 100.0
        }
    }

    private var aiStatusMessage: String {
        if viewModel.isUploading {
            return "Uploading your video..."
        }

        let progress = viewModel.processingProgress
        if progress < 30 {
            return "AI analyzing scenes..."
        } else if progress < 60 {
            return "Detecting faces and emotions..."
        } else if progress < 90 {
            return "Finding best moments..."
        } else {
            return "Creating your highlight..."
        }
    }

    // MARK: - Success View

    private func successView(videoURL: URL) -> some View {
        VStack(spacing: Spacing.xxl) {
            Spacer()

            // Success Animation
            VStack(spacing: Spacing.lg) {
                ZStack {
                    Circle()
                        .fill(Color.success.opacity(0.1))
                        .frame(width: 120, height: 120)

                    Image(systemName: "checkmark.circle.fill")
                        .font(.system(size: 80))
                        .foregroundColor(.success)
                }
                .bounceIn()

                VStack(spacing: Spacing.xs) {
                    Text("Highlight Ready!")
                        .font(.displaySmall)
                        .foregroundColor(.textPrimary)

                    Text("AI found your best moments")
                        .font(.bodyMedium)
                        .foregroundColor(.textSecondary)
                }
            }

            Spacer()

            // Action Buttons
            VStack(spacing: Spacing.md) {
                NavigationLink {
                    ResultView(videoURL: videoURL)
                } label: {
                    HStack {
                        Image(systemName: "play.circle.fill")
                        Text("View Highlight")
                    }
                }
                .buttonStyle(PrimaryButtonStyle())
                .simultaneousGesture(TapGesture().onEnded {
                    HapticManager.shared.success()
                })

                Button {
                    HapticManager.shared.light()
                    viewModel.reset()
                    selectedVideoURL = nil
                } label: {
                    Text("Create Another")
                }
                .buttonStyle(SecondaryButtonStyle())
            }
        }
        .padding()
    }

    // MARK: - Helper Methods

    private func requestPhotoLibraryPermission() {
        let status = PHPhotoLibrary.authorizationStatus(for: .readWrite)

        switch status {
        case .authorized, .limited:
            showVideoPicker = true

        case .notDetermined:
            PHPhotoLibrary.requestAuthorization(for: .readWrite) { newStatus in
                DispatchQueue.main.async {
                    if newStatus == .authorized || newStatus == .limited {
                        showVideoPicker = true
                    } else {
                        showPermissionAlert = true
                    }
                }
            }

        case .denied, .restricted:
            showPermissionAlert = true

        @unknown default:
            showPermissionAlert = true
        }
    }

    private func friendlyErrorMessage(_ error: String) -> String {
        if error.contains("timed out") || error.contains("1001") {
            return "Couldn't connect to the server. Please check your WiFi connection and try again."
        } else if error.contains("1004") || error.contains("connect") {
            return "Server is not responding. Please make sure the backend is running and try again."
        } else if error.contains("decode") || error.contains("Decoding") {
            return "Received an unexpected response from the server. Please try again."
        } else if error.contains("401") || error.contains("403") {
            return "You don't have permission to access this resource."
        } else if error.contains("404") {
            return "The requested resource was not found."
        } else if error.contains("500") || error.contains("502") || error.contains("503") {
            return "The server encountered an error. Please try again later."
        } else {
            return "Something went wrong. Please try again."
        }
    }
}

#Preview {
    HomeView()
}
