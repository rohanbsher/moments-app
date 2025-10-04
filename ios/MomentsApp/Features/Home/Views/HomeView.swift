//
//  HomeView.swift
//  MomentsApp
//
//  Main home view with upload interface
//

import SwiftUI

struct HomeView: View {
    @State private var viewModel = UploadViewModel()
    @State private var showVideoPicker = false
    @State private var selectedVideoURL: URL?
    @State private var showResult = false

    var body: some View {
        NavigationStack {
            VStack(spacing: 30) {
                // Header
                VStack(spacing: 8) {
                    Image(systemName: "wand.and.stars")
                        .font(.system(size: 60))
                        .foregroundStyle(.blue.gradient)

                    Text("Moments")
                        .font(.largeTitle.bold())

                    Text("Transform your videos into highlights")
                        .font(.subheadline)
                        .foregroundColor(.secondary)
                }
                .padding(.top, 60)

                Spacer()

                // Main content
                if viewModel.isActive {
                    // Processing view
                    processingView
                } else if let videoURL = viewModel.downloadedVideoURL {
                    // Success view
                    successView(videoURL: videoURL)
                } else {
                    // Upload view
                    uploadView
                }

                Spacer()

                // Configuration
                if !viewModel.isActive && viewModel.downloadedVideoURL == nil {
                    configurationView
                }
            }
            .padding()
            .navigationBarTitleDisplayMode(.inline)
            .sheet(isPresented: $showVideoPicker) {
                VideoPicker(selectedVideoURL: $selectedVideoURL)
            }
            .onChange(of: selectedVideoURL) { oldValue, newValue in
                if let videoURL = newValue {
                    Task {
                        await viewModel.uploadAndProcess(videoURL: videoURL)
                    }
                }
            }
            .alert("Error", isPresented: .constant(viewModel.errorMessage != nil)) {
                Button("OK") {
                    viewModel.errorMessage = nil
                }
            } message: {
                Text(viewModel.errorMessage ?? "")
            }
        }
    }

    // MARK: - Upload View

    private var uploadView: some View {
        VStack(spacing: 20) {
            Button {
                showVideoPicker = true
            } label: {
                VStack(spacing: 12) {
                    Image(systemName: "video.badge.plus")
                        .font(.system(size: 50))

                    Text("Select Video")
                        .font(.title3.bold())
                }
                .frame(maxWidth: .infinity)
                .frame(height: 200)
                .background(Color.blue.opacity(0.1))
                .foregroundColor(.blue)
                .cornerRadius(20)
            }
            .buttonStyle(.plain)

            Text("Choose a video to create highlights")
                .font(.caption)
                .foregroundColor(.secondary)
        }
    }

    // MARK: - Processing View

    private var processingView: some View {
        VStack(spacing: 24) {
            // Progress indicator
            ZStack {
                Circle()
                    .stroke(Color.gray.opacity(0.2), lineWidth: 10)
                    .frame(width: 120, height: 120)

                Circle()
                    .trim(from: 0, to: viewModel.isUploading ?
                          viewModel.uploadProgress :
                          Double(viewModel.processingProgress) / 100.0)
                    .stroke(Color.blue, style: StrokeStyle(lineWidth: 10, lineCap: .round))
                    .frame(width: 120, height: 120)
                    .rotationEffect(.degrees(-90))
                    .animation(.linear, value: viewModel.uploadProgress)
                    .animation(.linear, value: viewModel.processingProgress)

                VStack(spacing: 4) {
                    Text(viewModel.progressText)
                        .font(.title.bold())

                    Text(viewModel.isUploading ? "Uploading" : "Processing")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
            }

            // Status message
            Text(viewModel.statusMessage)
                .font(.body)
                .foregroundColor(.secondary)
                .multilineTextAlignment(.center)

            // Cancel button
            Button {
                viewModel.cancelProcessing()
            } label: {
                Text("Cancel")
                    .font(.body)
                    .foregroundColor(.red)
            }
        }
    }

    // MARK: - Success View

    private func successView(videoURL: URL) -> some View {
        VStack(spacing: 24) {
            Image(systemName: "checkmark.circle.fill")
                .font(.system(size: 60))
                .foregroundColor(.green)

            Text("Highlight Ready!")
                .font(.title2.bold())

            NavigationLink {
                ResultView(videoURL: videoURL)
            } label: {
                Text("View Highlight")
                    .font(.title3.bold())
                    .foregroundColor(.white)
                    .frame(maxWidth: .infinity)
                    .frame(height: 56)
                    .background(Color.blue)
                    .cornerRadius(16)
            }

            Button {
                viewModel.reset()
                selectedVideoURL = nil
            } label: {
                Text("Create Another")
                    .font(.body)
                    .foregroundColor(.blue)
            }
        }
    }

    // MARK: - Configuration View

    private var configurationView: some View {
        VStack(alignment: .leading, spacing: 16) {
            Text("Settings")
                .font(.headline)

            VStack(spacing: 12) {
                HStack {
                    Text("Target Duration")
                    Spacer()
                    Picker("", selection: $viewModel.videoConfig.targetDuration) {
                        Text("15s").tag(15)
                        Text("30s").tag(30)
                        Text("60s").tag(60)
                    }
                    .pickerStyle(.segmented)
                    .frame(width: 180)
                }

                Divider()

                HStack {
                    VStack(alignment: .leading) {
                        Text("Segment Length")
                            .font(.subheadline)
                        Text("\(viewModel.videoConfig.minSegmentDuration)s - \(viewModel.videoConfig.maxSegmentDuration)s")
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }
                    Spacer()
                }
            }
            .padding()
            .background(Color.gray.opacity(0.1))
            .cornerRadius(12)
        }
    }
}

#Preview {
    HomeView()
}
