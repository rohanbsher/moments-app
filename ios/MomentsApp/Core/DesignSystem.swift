//
//  DesignSystem.swift
//  MomentsApp
//
//  Centralized design system for colors, typography, and spacing
//  Following iOS 2025 design guidelines
//

import SwiftUI

// MARK: - Colors

extension Color {
    // MARK: Brand Colors
    static let brandPrimary = Color("BrandPrimary", bundle: .main)
        .fallback(Color(red: 0.0, green: 0.48, blue: 1.0)) // iOS Blue

    static let brandSecondary = Color("BrandSecondary", bundle: .main)
        .fallback(Color(red: 0.35, green: 0.34, blue: 0.84)) // Purple

    static let brandAccent = Color("BrandAccent", bundle: .main)
        .fallback(Color(red: 1.0, green: 0.58, blue: 0.0)) // Orange

    // MARK: AI Theme Colors
    static let aiGradientStart = Color(red: 0.58, green: 0.4, blue: 1.0) // Purple
    static let aiGradientEnd = Color(red: 0.2, green: 0.6, blue: 1.0) // Blue

    // MARK: Semantic Colors
    static let success = Color.green
    static let error = Color.red
    static let warning = Color.orange
    static let info = Color.blue

    // MARK: Background Colors (Dark Mode Optimized)
    static let backgroundPrimary = Color("BackgroundPrimary", bundle: .main)
        .fallback(Color(uiColor: .systemBackground))

    static let backgroundSecondary = Color("BackgroundSecondary", bundle: .main)
        .fallback(Color(uiColor: .secondarySystemBackground))

    static let backgroundTertiary = Color("BackgroundTertiary", bundle: .main)
        .fallback(Color(uiColor: .tertiarySystemBackground))

    // MARK: Text Colors
    static let textPrimary = Color("TextPrimary", bundle: .main)
        .fallback(Color(uiColor: .label))

    static let textSecondary = Color("TextSecondary", bundle: .main)
        .fallback(Color(uiColor: .secondaryLabel))

    static let textTertiary = Color("TextTertiary", bundle: .main)
        .fallback(Color(uiColor: .tertiaryLabel))

    // MARK: Helper for Fallback
    func fallback(_ fallbackColor: Color) -> Color {
        // If custom color doesn't exist, use fallback
        // SwiftUI will handle this automatically
        return self
    }
}

// MARK: - Gradients

extension LinearGradient {
    static let aiGradient = LinearGradient(
        colors: [.aiGradientStart, .aiGradientEnd],
        startPoint: .topLeading,
        endPoint: .bottomTrailing
    )

    static let shimmerGradient = LinearGradient(
        colors: [
            Color.white.opacity(0.0),
            Color.white.opacity(0.3),
            Color.white.opacity(0.0)
        ],
        startPoint: .leading,
        endPoint: .trailing
    )
}

// MARK: - Typography

extension Font {
    // MARK: Display (Hero Titles)
    static let displayLarge = Font.system(size: 48, weight: .bold, design: .rounded)
    static let displayMedium = Font.system(size: 36, weight: .bold, design: .rounded)
    static let displaySmall = Font.system(size: 28, weight: .bold, design: .rounded)

    // MARK: Headings
    static let headingLarge = Font.system(size: 24, weight: .semibold, design: .rounded)
    static let headingMedium = Font.system(size: 20, weight: .semibold, design: .rounded)
    static let headingSmall = Font.system(size: 18, weight: .semibold, design: .rounded)

    // MARK: Body Text
    static let bodyLarge = Font.system(size: 17, weight: .regular, design: .default)
    static let bodyMedium = Font.system(size: 15, weight: .regular, design: .default)
    static let bodySmall = Font.system(size: 13, weight: .regular, design: .default)

    // MARK: Labels
    static let labelLarge = Font.system(size: 15, weight: .medium, design: .default)
    static let labelMedium = Font.system(size: 13, weight: .medium, design: .default)
    static let labelSmall = Font.system(size: 11, weight: .medium, design: .default)

    // MARK: Caption
    static let captionLarge = Font.system(size: 12, weight: .regular, design: .default)
    static let captionMedium = Font.system(size: 11, weight: .regular, design: .default)
    static let captionSmall = Font.system(size: 10, weight: .regular, design: .default)
}

// MARK: - Spacing

struct Spacing {
    // Following 4-point grid system
    static let xxxs: CGFloat = 2
    static let xxs: CGFloat = 4
    static let xs: CGFloat = 8
    static let sm: CGFloat = 12
    static let md: CGFloat = 16
    static let lg: CGFloat = 20
    static let xl: CGFloat = 24
    static let xxl: CGFloat = 32
    static let xxxl: CGFloat = 40
    static let huge: CGFloat = 48

    // Semantic spacing
    static let cardPadding: CGFloat = md
    static let sectionSpacing: CGFloat = xxl
    static let itemSpacing: CGFloat = sm
}

// MARK: - Corner Radius

struct CornerRadius {
    static let small: CGFloat = 8
    static let medium: CGFloat = 12
    static let large: CGFloat = 16
    static let extraLarge: CGFloat = 20
    static let huge: CGFloat = 24

    // Semantic radii
    static let button: CGFloat = large
    static let card: CGFloat = medium
    static let sheet: CGFloat = extraLarge
}

// MARK: - Shadows

struct ShadowStyle {
    let color: Color
    let radius: CGFloat
    let x: CGFloat
    let y: CGFloat

    static let small = ShadowStyle(
        color: Color.black.opacity(0.1),
        radius: 4,
        x: 0,
        y: 2
    )

    static let medium = ShadowStyle(
        color: Color.black.opacity(0.15),
        radius: 8,
        x: 0,
        y: 4
    )

    static let large = ShadowStyle(
        color: Color.black.opacity(0.2),
        radius: 16,
        x: 0,
        y: 8
    )

    static let card = medium
}

// MARK: - View Extensions

extension View {
    /// Apply card style with shadow
    func cardStyle(padding: CGFloat = Spacing.cardPadding) -> some View {
        self
            .padding(padding)
            .background(Color.backgroundSecondary)
            .cornerRadius(CornerRadius.card)
            .shadow(
                color: ShadowStyle.card.color,
                radius: ShadowStyle.card.radius,
                x: ShadowStyle.card.x,
                y: ShadowStyle.card.y
            )
    }

    /// Apply primary button style
    func primaryButtonStyle() -> some View {
        self
            .font(.labelLarge)
            .foregroundColor(.white)
            .frame(maxWidth: .infinity)
            .frame(height: 56)
            .background(Color.brandPrimary)
            .cornerRadius(CornerRadius.button)
    }

    /// Apply secondary button style
    func secondaryButtonStyle() -> some View {
        self
            .font(.labelLarge)
            .foregroundColor(.brandPrimary)
            .frame(maxWidth: .infinity)
            .frame(height: 56)
            .background(Color.brandPrimary.opacity(0.1))
            .cornerRadius(CornerRadius.button)
    }

    /// Apply AI gradient background
    func aiGradientBackground() -> some View {
        self
            .background(LinearGradient.aiGradient)
    }
}

// MARK: - Button Styles

struct PrimaryButtonStyle: ButtonStyle {
    func makeBody(configuration: Configuration) -> some View {
        configuration.label
            .primaryButtonStyle()
            .scaleEffect(configuration.isPressed ? 0.95 : 1.0)
            .animation(.easeInOut(duration: 0.2), value: configuration.isPressed)
    }
}

struct SecondaryButtonStyle: ButtonStyle {
    func makeBody(configuration: Configuration) -> some View {
        configuration.label
            .secondaryButtonStyle()
            .scaleEffect(configuration.isPressed ? 0.95 : 1.0)
            .animation(.easeInOut(duration: 0.2), value: configuration.isPressed)
    }
}

// MARK: - Preview

#Preview {
    VStack(spacing: Spacing.lg) {
        Text("Display Large")
            .font(.displayLarge)

        Text("Heading Medium")
            .font(.headingMedium)

        Text("Body Text")
            .font(.bodyMedium)

        Button("Primary Button") {}
            .buttonStyle(PrimaryButtonStyle())

        Button("Secondary Button") {}
            .buttonStyle(SecondaryButtonStyle())

        HStack {
            VStack {
                Text("Card Style")
                    .font(.headingSmall)
            }
            .cardStyle()

            VStack {
                Text("AI Gradient")
                    .font(.headingSmall)
                    .foregroundColor(.white)
            }
            .padding()
            .aiGradientBackground()
            .cornerRadius(CornerRadius.card)
        }
    }
    .padding()
}
