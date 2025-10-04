//
//  APIClient.swift
//  MomentsApp
//
//  API client for communicating with Moments backend
//

import Foundation
import Observation

@Observable
class APIClient {
    static let shared = APIClient()

    // Base URL - using localhost for testing, will use Railway URL in production
    private let baseURL = "http://localhost:8000"

    private init() {}

    // MARK: - Upload Video

    /// Upload video to backend with progress tracking
    /// - Parameters:
    ///   - videoURL: Local URL of video file
    ///   - config: Video processing configuration
    ///   - onProgress: Callback for upload progress (0.0 to 1.0)
    /// - Returns: Job ID
    func uploadVideo(
        videoURL: URL,
        config: VideoConfig,
        onProgress: @escaping (Double) -> Void
    ) async throws -> String {
        let endpoint = "\(baseURL)/api/v1/upload/video"

        // Create multipart form data
        let boundary = "Boundary-\(UUID().uuidString)"
        var request = URLRequest(url: URL(string: endpoint)!)
        request.httpMethod = "POST"
        request.setValue("multipart/form-data; boundary=\(boundary)", forHTTPHeaderField: "Content-Type")

        // Build multipart body
        let httpBody = try createMultipartBody(
            videoURL: videoURL,
            config: config,
            boundary: boundary
        )

        // Upload with progress tracking
        let (data, response) = try await uploadWithProgress(
            request: request,
            data: httpBody,
            onProgress: onProgress
        )

        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIError.invalidResponse
        }

        guard httpResponse.statusCode == 200 else {
            throw APIError.serverError(statusCode: httpResponse.statusCode)
        }

        let uploadResponse = try JSONDecoder().decode(UploadResponse.self, from: data)
        return uploadResponse.jobId
    }

    // MARK: - Check Status

    /// Check processing status of a job
    /// - Parameter jobId: Job ID to check
    /// - Returns: Status response with progress
    func checkStatus(jobId: String) async throws -> StatusResponse {
        let endpoint = "\(baseURL)/api/v1/jobs/\(jobId)/status"

        guard let url = URL(string: endpoint) else {
            throw APIError.invalidURL
        }

        let (data, response) = try await URLSession.shared.data(from: url)

        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIError.invalidResponse
        }

        guard httpResponse.statusCode == 200 else {
            throw APIError.serverError(statusCode: httpResponse.statusCode)
        }

        return try JSONDecoder().decode(StatusResponse.self, from: data)
    }

    // MARK: - Download Video

    /// Download processed video
    /// - Parameter jobId: Job ID
    /// - Returns: Local URL of downloaded video
    func downloadVideo(jobId: String) async throws -> URL {
        let endpoint = "\(baseURL)/api/v1/jobs/\(jobId)/download"

        guard let url = URL(string: endpoint) else {
            throw APIError.invalidURL
        }

        let (tempURL, response) = try await URLSession.shared.download(from: url)

        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIError.invalidResponse
        }

        guard httpResponse.statusCode == 200 else {
            throw APIError.serverError(statusCode: httpResponse.statusCode)
        }

        // Move to permanent location
        let documentsURL = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask)[0]
        let destinationURL = documentsURL.appendingPathComponent("highlight_\(jobId).mp4")

        // Remove existing file if present
        try? FileManager.default.removeItem(at: destinationURL)

        try FileManager.default.moveItem(at: tempURL, to: destinationURL)

        return destinationURL
    }

    // MARK: - Private Helpers

    private func createMultipartBody(
        videoURL: URL,
        config: VideoConfig,
        boundary: String
    ) throws -> Data {
        var body = Data()

        // Add video file
        let videoData = try Data(contentsOf: videoURL)
        let filename = videoURL.lastPathComponent

        body.append("--\(boundary)\r\n".data(using: .utf8)!)
        body.append("Content-Disposition: form-data; name=\"file\"; filename=\"\(filename)\"\r\n".data(using: .utf8)!)
        body.append("Content-Type: video/mp4\r\n\r\n".data(using: .utf8)!)
        body.append(videoData)
        body.append("\r\n".data(using: .utf8)!)

        // Add configuration parameters
        for (key, value) in config.formData {
            body.append("--\(boundary)\r\n".data(using: .utf8)!)
            body.append("Content-Disposition: form-data; name=\"\(key)\"\r\n\r\n".data(using: .utf8)!)
            body.append("\(value)\r\n".data(using: .utf8)!)
        }

        // Final boundary
        body.append("--\(boundary)--\r\n".data(using: .utf8)!)

        return body
    }

    private func uploadWithProgress(
        request: URLRequest,
        data: Data,
        onProgress: @escaping (Double) -> Void
    ) async throws -> (Data, URLResponse) {
        var uploadRequest = request

        // Create upload task
        return try await withCheckedThrowingContinuation { continuation in
            let task = URLSession.shared.uploadTask(with: uploadRequest, from: data) { data, response, error in
                if let error = error {
                    continuation.resume(throwing: error)
                    return
                }

                guard let data = data, let response = response else {
                    continuation.resume(throwing: APIError.noData)
                    return
                }

                continuation.resume(returning: (data, response))
            }

            // Track progress (simplified - real implementation would use URLSessionDelegate)
            let timer = Timer.scheduledTimer(withTimeInterval: 0.1, repeats: true) { _ in
                let progress = Double(task.countOfBytesSent) / Double(data.count)
                DispatchQueue.main.async {
                    onProgress(min(progress, 0.99)) // Cap at 99% until complete
                }
            }

            task.resume()

            // Clean up timer when task completes
            Task {
                _ = try? await Task.sleep(nanoseconds: 100_000_000) // 0.1s
                while task.state == .running {
                    _ = try? await Task.sleep(nanoseconds: 100_000_000)
                }
                timer.invalidate()
                onProgress(1.0) // 100% when complete
            }
        }
    }
}

// MARK: - API Errors

enum APIError: LocalizedError {
    case invalidURL
    case invalidResponse
    case noData
    case serverError(statusCode: Int)
    case decodingError(Error)

    var errorDescription: String? {
        switch self {
        case .invalidURL:
            return "Invalid URL"
        case .invalidResponse:
            return "Invalid response from server"
        case .noData:
            return "No data received"
        case .serverError(let code):
            return "Server error: \(code)"
        case .decodingError(let error):
            return "Decoding error: \(error.localizedDescription)"
        }
    }
}
