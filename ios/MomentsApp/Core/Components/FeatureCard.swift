//
//  FeatureCard.swift
//  MomentsApp
//
//  Card component for showcasing AI features
//

import SwiftUI

struct FeatureCard: View {
    let icon: String
    let title: String
    let description: String
    let gradient: LinearGradient

    init(
        icon: String,
        title: String,
        description: String,
        gradient: LinearGradient = LinearGradient.aiGradient
    ) {
        self.icon = icon
        self.title = title
        self.description = description
        self.gradient = gradient
    }

    var body: some View {
        VStack(alignment: .leading, spacing: Spacing.sm) {
            // Icon with gradient background
            ZStack {
                Circle()
                    .fill(gradient)
                    .frame(width: 48, height: 48)

                Image(systemName: icon)
                    .font(.system(size: 24))
                    .foregroundColor(.white)
            }

            VStack(alignment: .leading, spacing: Spacing.xxs) {
                Text(title)
                    .font(.headingSmall)
                    .foregroundColor(.textPrimary)

                Text(description)
                    .font(.captionLarge)
                    .foregroundColor(.textSecondary)
                    .lineLimit(2)
            }
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(Spacing.md)
        .background(Color.backgroundSecondary)
        .cornerRadius(CornerRadius.card)
        .shadow(
            color: ShadowStyle.small.color,
            radius: ShadowStyle.small.radius,
            x: ShadowStyle.small.x,
            y: ShadowStyle.small.y
        )
    }
}

// MARK: - Predefined Features

extension FeatureCard {
    static let faceDetection = FeatureCard(
        icon: "face.smiling",
        title: "Face Detection",
        description: "Finds and prioritizes people in your videos",
        gradient: LinearGradient(
            colors: [Color.blue, Color.cyan],
            startPoint: .topLeading,
            endPoint: .bottomTrailing
        )
    )

    static let emotionAnalysis = FeatureCard(
        icon: "heart.text.square",
        title: "Emotion Recognition",
        description: "Detects happy and exciting moments",
        gradient: LinearGradient(
            colors: [Color.pink, Color.red],
            startPoint: .topLeading,
            endPoint: .bottomTrailing
        )
    )

    static let speechAnalysis = FeatureCard(
        icon: "waveform",
        title: "Speech Analysis",
        description: "Identifies important keywords and dialogue",
        gradient: LinearGradient(
            colors: [Color.purple, Color.indigo],
            startPoint: .topLeading,
            endPoint: .bottomTrailing
        )
    )
}

#Preview {
    VStack(spacing: Spacing.md) {
        FeatureCard.faceDetection
        FeatureCard.emotionAnalysis
        FeatureCard.speechAnalysis
    }
    .padding()
    .background(Color.backgroundPrimary)
}
