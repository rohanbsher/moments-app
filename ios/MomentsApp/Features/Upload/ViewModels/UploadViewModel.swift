//
//  UploadViewModel.swift
//  MomentsApp
//
//  ViewModel for video upload and processing
//

import Foundation
import Observation
import SwiftUI

@Observable
class UploadViewModel {
    // MARK: - State
    var uploadProgress: Double = 0.0
    var processingProgress: Int = 0
    var currentStatus: JobStatus = .pending
    var statusMessage: String = ""
    var errorMessage: String?
    var isUploading: Bool = false
    var isProcessing: Bool = false
    var jobId: String?
    var downloadedVideoURL: URL?
    var detailedError: String = ""  // For debugging

    // Configuration
    var videoConfig = VideoConfig.standard

    // Polling timer
    private var pollingTask: Task<Void, Never>?

    // MARK: - Upload and Process

    /// Upload video and start processing
    /// - Parameter videoURL: Local URL of video to upload
    func uploadAndProcess(videoURL: URL) async {
        print("📤 UploadViewModel: uploadAndProcess called with: \(videoURL)")

        // Reset state
        resetState()
        print("📤 UploadViewModel: State reset complete")

        do {
            // Upload phase
            print("📤 UploadViewModel: Starting upload phase...")

            await MainActor.run {
                self.isUploading = true
                self.statusMessage = "Uploading video..."
            }

            print("📤 UploadViewModel: Calling APIClient.uploadVideo...")

            let uploadedJobId = try await APIClient.shared.uploadVideo(
                videoURL: videoURL,
                config: videoConfig
            ) { [weak self] progress in
                Task { @MainActor in
                    self?.uploadProgress = progress
                    print("📊 Upload progress: \(Int(progress * 100))%")
                }
            }

            print("✅ UploadViewModel: Upload complete! Job ID: \(uploadedJobId)")

            await MainActor.run {
                self.jobId = uploadedJobId
                self.isUploading = false
                self.isProcessing = true
                self.statusMessage = "Processing video..."
            }

            print("📤 UploadViewModel: Starting polling...")

            // Start polling for status
            startPolling(jobId: uploadedJobId)

        } catch {
            print("❌ UploadViewModel: Upload failed with error: \(error)")
            print("❌ Error description: \(error.localizedDescription)")

            let detailedMsg = "Error: \(error)\nDescription: \(error.localizedDescription)"

            await MainActor.run {
                self.errorMessage = error.localizedDescription
                self.detailedError = detailedMsg
                self.isUploading = false
                self.isProcessing = false
                self.statusMessage = "Upload failed: \(error.localizedDescription)"
            }
        }
    }

    // MARK: - Status Polling

    private func startPolling(jobId: String) {
        pollingTask?.cancel()

        pollingTask = Task {
            while !Task.isCancelled {
                do {
                    let status = try await APIClient.shared.checkStatus(jobId: jobId)

                    await MainActor.run {
                        self.currentStatus = status.status
                        self.processingProgress = status.progress
                        self.statusMessage = status.message ?? "Processing..."

                        if let error = status.errorMessage {
                            self.errorMessage = error
                        }
                    }

                    // Check if completed
                    if status.status == .completed {
                        await handleCompletion(jobId: jobId)
                        break
                    } else if status.status == .failed {
                        await MainActor.run {
                            self.isProcessing = false
                            self.errorMessage = status.errorMessage ?? "Processing failed"
                        }
                        break
                    }

                    // Poll every 2 seconds
                    try await Task.sleep(nanoseconds: 2_000_000_000)

                } catch {
                    if !Task.isCancelled {
                        await MainActor.run {
                            self.errorMessage = error.localizedDescription
                            self.isProcessing = false
                        }
                    }
                    break
                }
            }
        }
    }

    private func handleCompletion(jobId: String) async {
        do {
            // Download processed video
            await MainActor.run {
                self.statusMessage = "Downloading highlight..."
            }

            let videoURL = try await APIClient.shared.downloadVideo(jobId: jobId)

            await MainActor.run {
                self.downloadedVideoURL = videoURL
                self.isProcessing = false
                self.statusMessage = "Complete!"
            }

        } catch {
            await MainActor.run {
                self.errorMessage = error.localizedDescription
                self.isProcessing = false
                self.statusMessage = "Download failed"
            }
        }
    }

    // MARK: - Cancel

    func cancelProcessing() {
        pollingTask?.cancel()
        pollingTask = nil

        isUploading = false
        isProcessing = false
        statusMessage = "Cancelled"
    }

    // MARK: - Reset

    private func resetState() {
        uploadProgress = 0.0
        processingProgress = 0
        currentStatus = .pending
        statusMessage = ""
        errorMessage = nil
        isUploading = false
        isProcessing = false
        jobId = nil
        downloadedVideoURL = nil
        pollingTask?.cancel()
        pollingTask = nil
    }

    func reset() {
        resetState()
    }

    // MARK: - Computed Properties

    var isActive: Bool {
        isUploading || isProcessing
    }

    var progressText: String {
        if isUploading {
            return "\(Int(uploadProgress * 100))%"
        } else if isProcessing {
            return "\(processingProgress)%"
        }
        return ""
    }

    deinit {
        pollingTask?.cancel()
    }
}
