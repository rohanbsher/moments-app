//
//  Job.swift
//  MomentsApp
//
//  Model for video processing job
//

import Foundation

// MARK: - Job Status
enum JobStatus: String, Codable {
    case pending = "pending"
    case queued = "queued"
    case processing = "processing"
    case completed = "completed"
    case failed = "failed"
}

// MARK: - Job Model
struct Job: Codable, Identifiable {
    let id: String
    let userId: String?
    let originalFilename: String
    let uploadPath: String
    let outputPath: String?
    let duration: Double?
    let fileSize: Int?
    let config: JobConfig?
    let targetDuration: Int
    let status: JobStatus
    let progress: Int
    let errorMessage: String?
    let segmentsSelected: Int?
    let processingTime: Double?
    let resultMetadata: JobMetadata?
    let createdAt: Date
    let updatedAt: Date
    let completedAt: Date?

    enum CodingKeys: String, CodingKey {
        case id
        case userId = "user_id"
        case originalFilename = "original_filename"
        case uploadPath = "upload_path"
        case outputPath = "output_path"
        case duration
        case fileSize = "file_size"
        case config
        case targetDuration = "target_duration"
        case status
        case progress
        case errorMessage = "error_message"
        case segmentsSelected = "segments_selected"
        case processingTime = "processing_time"
        case resultMetadata = "result_metadata"
        case createdAt = "created_at"
        case updatedAt = "updated_at"
        case completedAt = "completed_at"
    }
}

// MARK: - Job Config
struct JobConfig: Codable {
    let targetDuration: Int
    let minSegmentDuration: Int
    let maxSegmentDuration: Int

    enum CodingKeys: String, CodingKey {
        case targetDuration = "target_duration"
        case minSegmentDuration = "min_segment_duration"
        case maxSegmentDuration = "max_segment_duration"
    }
}

// MARK: - Job Metadata
struct JobMetadata: Codable {
    let totalSegments: Int?
    let selectedSegments: Int?
    let averageScore: Double?
    let processingSteps: [String]?

    enum CodingKeys: String, CodingKey {
        case totalSegments = "total_segments"
        case selectedSegments = "selected_segments"
        case averageScore = "average_score"
        case processingSteps = "processing_steps"
    }
}

// MARK: - API Response Models

struct UploadResponse: Codable {
    let jobId: String
    let status: String
    let message: String

    enum CodingKeys: String, CodingKey {
        case jobId = "job_id"
        case status
        case message
    }
}

struct StatusResponse: Codable {
    let jobId: String
    let status: JobStatus
    let progress: Int
    let message: String?
    let outputPath: String?
    let errorMessage: String?

    enum CodingKeys: String, CodingKey {
        case jobId = "job_id"
        case status
        case progress
        case message
        case outputPath = "output_path"
        case errorMessage = "error_message"
    }
}
