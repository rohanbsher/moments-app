//
//  VideoConfig.swift
//  MomentsApp
//
//  Configuration for video processing
//

import Foundation

struct VideoConfig {
    var targetDuration: Int = 30  // seconds
    var minSegmentDuration: Int = 3
    var maxSegmentDuration: Int = 10

    // Computed property for form data
    var formData: [String: String] {
        return [
            "target_duration": String(targetDuration),
            "quality": "high"
        ]
    }
}

// Preset configurations
extension VideoConfig {
    static let quick = VideoConfig(
        targetDuration: 15,
        minSegmentDuration: 2,
        maxSegmentDuration: 5
    )

    static let standard = VideoConfig(
        targetDuration: 30,
        minSegmentDuration: 3,
        maxSegmentDuration: 10
    )

    static let extended = VideoConfig(
        targetDuration: 60,
        minSegmentDuration: 5,
        maxSegmentDuration: 15
    )
}
