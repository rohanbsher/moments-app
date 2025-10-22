//
//  AnimationConstants.swift
//  MomentsApp
//
//  Animation timings, curves, and utilities
//  Following iOS 2025 fluid motion guidelines
//

import SwiftUI

// MARK: - Animation Durations

struct AnimationDuration {
    // Standard durations
    static let instant: Double = 0.1
    static let fast: Double = 0.2
    static let normal: Double = 0.3
    static let slow: Double = 0.5
    static let verySlow: Double = 0.8

    // Specific use cases
    static let buttonTap: Double = fast
    static let cardAppear: Double = normal
    static let sheetPresentation: Double = normal
    static let pageTransition: Double = slow
}

// MARK: - Animation Curves

extension Animation {
    // Standard curves
    static let smooth = Animation.easeInOut(duration: AnimationDuration.normal)
    static let bouncy = Animation.spring(response: 0.3, dampingFraction: 0.7)
    static let snappy = Animation.spring(response: 0.2, dampingFraction: 0.8)
    static let gentle = Animation.easeInOut(duration: AnimationDuration.slow)

    // AI-specific animations
    static let aiPulse = Animation
        .easeInOut(duration: 1.5)
        .repeatForever(autoreverses: true)

    static let shimmer = Animation
        .linear(duration: 2.0)
        .repeatForever(autoreverses: false)

    static let float = Animation
        .easeInOut(duration: 3.0)
        .repeatForever(autoreverses: true)
}

// MARK: - Haptic Feedback

class HapticManager {
    static let shared = HapticManager()

    private init() {}

    func light() {
        let generator = UIImpactFeedbackGenerator(style: .light)
        generator.impactOccurred()
    }

    func medium() {
        let generator = UIImpactFeedbackGenerator(style: .medium)
        generator.impactOccurred()
    }

    func heavy() {
        let generator = UIImpactFeedbackGenerator(style: .heavy)
        generator.impactOccurred()
    }

    func success() {
        let generator = UINotificationFeedbackGenerator()
        generator.notificationOccurred(.success)
    }

    func error() {
        let generator = UINotificationFeedbackGenerator()
        generator.notificationOccurred(.error)
    }

    func warning() {
        let generator = UINotificationFeedbackGenerator()
        generator.notificationOccurred(.warning)
    }

    func selection() {
        let generator = UISelectionFeedbackGenerator()
        generator.selectionChanged()
    }
}

// MARK: - View Modifiers

struct ShimmerModifier: ViewModifier {
    @State private var phase: CGFloat = 0

    func body(content: Content) -> some View {
        content
            .overlay(
                LinearGradient.shimmerGradient
                    .offset(x: phase)
                    .mask(content)
            )
            .onAppear {
                withAnimation(.shimmer) {
                    phase = 400
                }
            }
    }
}

struct PulseModifier: ViewModifier {
    @State private var isPulsing = false

    func body(content: Content) -> some View {
        content
            .scaleEffect(isPulsing ? 1.05 : 1.0)
            .opacity(isPulsing ? 0.8 : 1.0)
            .onAppear {
                withAnimation(.aiPulse) {
                    isPulsing = true
                }
            }
    }
}

struct FloatModifier: ViewModifier {
    @State private var isFloating = false

    func body(content: Content) -> some View {
        content
            .offset(y: isFloating ? -10 : 0)
            .onAppear {
                withAnimation(.float) {
                    isFloating = true
                }
            }
    }
}

struct BounceModifier: ViewModifier {
    @State private var isBouncing = false

    func body(content: Content) -> some View {
        content
            .scaleEffect(isBouncing ? 1.0 : 0.8)
            .opacity(isBouncing ? 1.0 : 0.0)
            .onAppear {
                withAnimation(.bouncy) {
                    isBouncing = true
                }
            }
    }
}

// MARK: - View Extensions

extension View {
    /// Add shimmer animation effect
    func shimmer() -> some View {
        self.modifier(ShimmerModifier())
    }

    /// Add pulsing animation
    func pulse() -> some View {
        self.modifier(PulseModifier())
    }

    /// Add floating animation
    func float() -> some View {
        self.modifier(FloatModifier())
    }

    /// Add bounce-in animation
    func bounceIn() -> some View {
        self.modifier(BounceModifier())
    }

    /// Add tap haptic feedback
    func hapticFeedback(_ style: UIImpactFeedbackGenerator.FeedbackStyle = .light) -> some View {
        self.onTapGesture {
            let generator = UIImpactFeedbackGenerator(style: style)
            generator.impactOccurred()
        }
    }
}

// MARK: - Transition Styles

extension AnyTransition {
    static var slideAndFade: AnyTransition {
        .asymmetric(
            insertion: .move(edge: .trailing).combined(with: .opacity),
            removal: .move(edge: .leading).combined(with: .opacity)
        )
    }

    static var scaleAndFade: AnyTransition {
        .scale(scale: 0.8).combined(with: .opacity)
    }

    static var bottomSheet: AnyTransition {
        .move(edge: .bottom).combined(with: .opacity)
    }
}

// MARK: - Progress Animations

struct ProgressRingShape: Shape {
    var progress: Double

    var animatableData: Double {
        get { progress }
        set { progress = newValue }
    }

    func path(in rect: CGRect) -> Path {
        var path = Path()
        let center = CGPoint(x: rect.midX, y: rect.midY)
        let radius = min(rect.width, rect.height) / 2
        let startAngle = Angle(degrees: -90)
        let endAngle = Angle(degrees: -90 + (360 * progress))

        path.addArc(
            center: center,
            radius: radius,
            startAngle: startAngle,
            endAngle: endAngle,
            clockwise: false
        )

        return path
    }
}

// MARK: - Loading Animations

struct LoadingDotsView: View {
    @State private var animatingDot1 = false
    @State private var animatingDot2 = false
    @State private var animatingDot3 = false

    var body: some View {
        HStack(spacing: Spacing.xs) {
            Circle()
                .fill(Color.brandPrimary)
                .frame(width: 8, height: 8)
                .offset(y: animatingDot1 ? -8 : 0)
                .animation(
                    Animation.easeInOut(duration: 0.6)
                        .repeatForever(autoreverses: true),
                    value: animatingDot1
                )

            Circle()
                .fill(Color.brandPrimary)
                .frame(width: 8, height: 8)
                .offset(y: animatingDot2 ? -8 : 0)
                .animation(
                    Animation.easeInOut(duration: 0.6)
                        .repeatForever(autoreverses: true)
                        .delay(0.2),
                    value: animatingDot2
                )

            Circle()
                .fill(Color.brandPrimary)
                .frame(width: 8, height: 8)
                .offset(y: animatingDot3 ? -8 : 0)
                .animation(
                    Animation.easeInOut(duration: 0.6)
                        .repeatForever(autoreverses: true)
                        .delay(0.4),
                    value: animatingDot3
                )
        }
        .onAppear {
            animatingDot1 = true
            animatingDot2 = true
            animatingDot3 = true
        }
    }
}

// MARK: - Preview

#Preview {
    VStack(spacing: Spacing.xxl) {
        Text("Shimmer Effect")
            .font(.headingLarge)
            .shimmer()

        Text("Pulsing Effect")
            .font(.headingMedium)
            .pulse()

        Text("Floating Effect")
            .font(.headingSmall)
            .float()

        LoadingDotsView()

        Button("Haptic Button") {
            HapticManager.shared.success()
        }
        .primaryButtonStyle()
    }
    .padding()
}
