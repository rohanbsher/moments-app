//
//  Environment.swift
//  MomentsApp
//
//  Environment configuration for different build configurations
//

import Foundation

enum Environment {
    case development
    case staging
    case production

    // MARK: - Current Environment

    static var current: Environment {
        #if DEBUG
        return .development
        #elseif STAGING
        return .staging
        #else
        return .production
        #endif
    }

    // MARK: - Configuration

    var apiBaseURL: String {
        switch self {
        case .development:
            // Local development - change this to your Mac's IP address
            // Find with: ifconfig | grep "inet " | grep -v 127.0.0.1
            return ProcessInfo.processInfo.environment["API_BASE_URL"]
                   ?? "http://192.168.0.5:8000"

        case .staging:
            // Railway staging environment
            return "https://moments-staging.up.railway.app"

        case .production:
            // Railway production environment
            return "https://moments-api.up.railway.app"
        }
    }

    var apiTimeout: TimeInterval {
        switch self {
        case .development:
            return 300 // 5 minutes for debugging
        case .staging:
            return 180 // 3 minutes
        case .production:
            return 120 // 2 minutes
        }
    }

    var isDebugMode: Bool {
        switch self {
        case .development, .staging:
            return true
        case .production:
            return false
        }
    }

    var logLevel: LogLevel {
        switch self {
        case .development:
            return .verbose
        case .staging:
            return .info
        case .production:
            return .error
        }
    }

    // MARK: - Feature Flags

    var enableAnalytics: Bool {
        switch self {
        case .development:
            return false // No analytics in dev
        case .staging:
            return true // Test analytics in staging
        case .production:
            return true
        }
    }

    var enableCrashReporting: Bool {
        switch self {
        case .development:
            return false
        case .staging, .production:
            return true
        }
    }

    // MARK: - Display

    var displayName: String {
        switch self {
        case .development:
            return "DEV"
        case .staging:
            return "STAGING"
        case .production:
            return "PROD"
        }
    }

    var badgeColor: String {
        switch self {
        case .development:
            return "green"
        case .staging:
            return "orange"
        case .production:
            return "red"
        }
    }
}

// MARK: - Log Level

enum LogLevel: Int {
    case verbose = 0
    case info = 1
    case warning = 2
    case error = 3

    var emoji: String {
        switch self {
        case .verbose:
            return "💬"
        case .info:
            return "ℹ️"
        case .warning:
            return "⚠️"
        case .error:
            return "❌"
        }
    }
}

// MARK: - Logger Helper

struct Logger {
    static func log(
        _ message: String,
        level: LogLevel = .info,
        file: String = #file,
        function: String = #function,
        line: Int = #line
    ) {
        guard level.rawValue >= Environment.current.logLevel.rawValue else {
            return
        }

        let fileName = (file as NSString).lastPathComponent
        let timestamp = DateFormatter.localizedString(
            from: Date(),
            dateStyle: .none,
            timeStyle: .medium
        )

        print("\(level.emoji) [\(timestamp)] [\(fileName):\(line)] \(message)")
    }

    static func verbose(_ message: String, file: String = #file, function: String = #function, line: Int = #line) {
        log(message, level: .verbose, file: file, function: function, line: line)
    }

    static func info(_ message: String, file: String = #file, function: String = #function, line: Int = #line) {
        log(message, level: .info, file: file, function: function, line: line)
    }

    static func warning(_ message: String, file: String = #file, function: String = #function, line: Int = #line) {
        log(message, level: .warning, file: file, function: function, line: line)
    }

    static func error(_ message: String, file: String = #file, function: String = #function, line: Int = #line) {
        log(message, level: .error, file: file, function: function, line: line)
    }
}

// MARK: - Configuration Helper

struct AppConfiguration {
    static let environment = Environment.current
    static let apiBaseURL = environment.apiBaseURL
    static let apiTimeout = environment.apiTimeout
    static let isDebugMode = environment.isDebugMode

    // App metadata
    static let appVersion: String = {
        Bundle.main.infoDictionary?["CFBundleShortVersionString"] as? String ?? "1.0.0"
    }()

    static let buildNumber: String = {
        Bundle.main.infoDictionary?["CFBundleVersion"] as? String ?? "1"
    }()

    static var fullVersion: String {
        "\(appVersion) (\(buildNumber))"
    }

    // Device info
    static let deviceModel: String = {
        var systemInfo = utsname()
        uname(&systemInfo)
        let modelCode = withUnsafePointer(to: &systemInfo.machine) {
            $0.withMemoryRebound(to: CChar.self, capacity: 1) {
                String(validatingUTF8: $0)
            }
        }
        return modelCode ?? "Unknown"
    }()

    static let osVersion: String = {
        "\(UIDevice.current.systemName) \(UIDevice.current.systemVersion)"
    }()

    // Print configuration on app launch
    static func printConfiguration() {
        print("=" * 60)
        print("🎬 Moments App Configuration")
        print("=" * 60)
        print("📱 App Version: \(fullVersion)")
        print("🌍 Environment: \(environment.displayName)")
        print("🌐 API Base URL: \(apiBaseURL)")
        print("🐛 Debug Mode: \(isDebugMode)")
        print("📊 Analytics: \(environment.enableAnalytics ? "Enabled" : "Disabled")")
        print("💥 Crash Reporting: \(environment.enableCrashReporting ? "Enabled" : "Disabled")")
        print("📱 Device: \(deviceModel)")
        print("📱 OS: \(osVersion)")
        print("=" * 60)
    }
}
