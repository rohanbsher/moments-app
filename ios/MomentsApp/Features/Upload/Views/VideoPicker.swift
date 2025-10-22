//
//  VideoPicker.swift
//  MomentsApp
//
//  Video picker using PhotosUI/PHPicker with iOS 18 compatibility
//

import SwiftUI
import PhotosUI
import Photos

struct VideoPicker: UIViewControllerRepresentable {
    @Binding var selectedVideoURL: URL?
    @Environment(\.dismiss) private var dismiss

    func makeUIViewController(context: Context) -> PHPickerViewController {
        print("📸 VideoPicker: Creating PHPickerViewController")

        // Simple configuration for iOS 18 compatibility
        var configuration = PHPickerConfiguration()
        configuration.filter = .videos  // Only videos
        configuration.selectionLimit = 1  // Single selection
        configuration.preferredAssetRepresentationMode = .current

        let picker = PHPickerViewController(configuration: configuration)
        picker.delegate = context.coordinator

        print("✅ VideoPicker: PHPickerViewController created successfully")

        return picker
    }

    func updateUIViewController(_ uiViewController: PHPickerViewController, context: Context) {
        // No updates needed
    }

    func makeCoordinator() -> Coordinator {
        Coordinator(self)
    }

    class Coordinator: NSObject, PHPickerViewControllerDelegate {
        let parent: VideoPicker

        init(_ parent: VideoPicker) {
            self.parent = parent
            print("📸 VideoPicker.Coordinator: Initialized")
        }

        func picker(_ picker: PHPickerViewController, didFinishPicking results: [PHPickerResult]) {
            print("📹 VideoPicker: didFinishPicking called with \(results.count) results")

            // Dismiss picker first
            picker.dismiss(animated: true)

            guard let result = results.first else {
                print("⚠️ VideoPicker: User cancelled or no results selected")
                return
            }

            print("📹 VideoPicker: Result selected, checking for movie type...")
            print("📹 VideoPicker: Item provider: \(result.itemProvider)")

            // Check if can load file representation
            if result.itemProvider.hasItemConformingToTypeIdentifier(UTType.movie.identifier) {
                print("✅ VideoPicker: Movie type confirmed, loading file...")

                result.itemProvider.loadFileRepresentation(forTypeIdentifier: UTType.movie.identifier) { url, error in
                    if let error = error {
                        print("❌ VideoPicker: Error loading video: \(error)")
                        print("❌ VideoPicker: Error details: \(error.localizedDescription)")
                        return
                    }

                    guard let url = url else {
                        print("❌ VideoPicker: No URL received from item provider")
                        return
                    }

                    print("📹 VideoPicker: Video loaded from: \(url)")
                    print("📹 VideoPicker: File exists: \(FileManager.default.fileExists(atPath: url.path))")

                    // Copy to temporary location
                    let tempURL = FileManager.default.temporaryDirectory
                        .appendingPathComponent(UUID().uuidString)
                        .appendingPathExtension("mp4")

                    print("📹 VideoPicker: Copying to temp location: \(tempURL)")

                    do {
                        // Ensure destination doesn't exist
                        if FileManager.default.fileExists(atPath: tempURL.path) {
                            try FileManager.default.removeItem(at: tempURL)
                        }

                        // Copy file to temp location
                        try FileManager.default.copyItem(at: url, to: tempURL)

                        let fileSize = try FileManager.default.attributesOfItem(atPath: tempURL.path)[.size] as? Int ?? 0
                        print("✅ VideoPicker: Video copied successfully!")
                        print("📹 VideoPicker: File size: \(fileSize) bytes (\(Double(fileSize) / 1_000_000) MB)")

                        // Set the URL on main thread
                        DispatchQueue.main.async {
                            print("📹 VideoPicker: Setting selectedVideoURL on main thread")
                            self.parent.selectedVideoURL = tempURL
                            print("✅ VideoPicker: selectedVideoURL set successfully!")
                        }
                    } catch {
                        print("❌ VideoPicker: Error copying video: \(error)")
                        print("❌ VideoPicker: Error details: \(error.localizedDescription)")
                    }
                }
            } else if result.itemProvider.hasItemConformingToTypeIdentifier(UTType.quickTimeMovie.identifier) {
                // Try QuickTime format as fallback
                print("📹 VideoPicker: Trying QuickTime movie format...")

                result.itemProvider.loadFileRepresentation(forTypeIdentifier: UTType.quickTimeMovie.identifier) { url, error in
                    if let error = error {
                        print("❌ VideoPicker: Error loading QuickTime video: \(error)")
                        return
                    }

                    guard let url = url else {
                        print("❌ VideoPicker: No URL received for QuickTime")
                        return
                    }

                    let tempURL = FileManager.default.temporaryDirectory
                        .appendingPathComponent(UUID().uuidString)
                        .appendingPathExtension("mov")

                    do {
                        try FileManager.default.copyItem(at: url, to: tempURL)
                        print("✅ VideoPicker: QuickTime video copied successfully!")

                        DispatchQueue.main.async {
                            self.parent.selectedVideoURL = tempURL
                        }
                    } catch {
                        print("❌ VideoPicker: Error copying QuickTime video: \(error)")
                    }
                }
            } else {
                print("❌ VideoPicker: Selected item is not a video!")
                print("❌ VideoPicker: Available types: \(result.itemProvider.registeredTypeIdentifiers)")
            }
        }
    }
}
