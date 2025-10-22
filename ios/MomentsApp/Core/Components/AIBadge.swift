//
//  AIBadge.swift
//  MomentsApp
//
//  AI-powered badge with shimmer animation
//

import SwiftUI

struct AIBadge: View {
    var style: Style = .large

    enum Style {
        case large
        case small

        var fontSize: Font {
            switch self {
            case .large: return .labelLarge
            case .small: return .labelSmall
            }
        }

        var iconSize: CGFloat {
            switch self {
            case .large: return 16
            case .small: return 12
            }
        }

        var padding: EdgeInsets {
            switch self {
            case .large: return EdgeInsets(top: 8, leading: 12, bottom: 8, trailing: 12)
            case .small: return EdgeInsets(top: 4, leading: 8, bottom: 4, trailing: 8)
            }
        }
    }

    var body: some View {
        HStack(spacing: Spacing.xxs) {
            Image(systemName: "sparkles")
                .font(.system(size: style.iconSize))

            Text("AI-Powered")
                .font(style.fontSize)
        }
        .foregroundColor(.white)
        .padding(style.padding)
        .background(
            LinearGradient.aiGradient
                .opacity(0.9)
        )
        .cornerRadius(CornerRadius.large)
        .shadow(
            color: Color.aiGradientStart.opacity(0.3),
            radius: 8,
            x: 0,
            y: 4
        )
        .shimmer()
    }
}

#Preview {
    VStack(spacing: Spacing.lg) {
        AIBadge(style: .large)
        AIBadge(style: .small)
    }
    .padding()
    .background(Color.backgroundPrimary)
}
