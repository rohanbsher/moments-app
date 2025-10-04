//
//  ResultView.swift
//  MomentsApp
//
//  View for displaying and sharing processed highlights
//

import SwiftUI
import AVKit

struct ResultView: View {
    let videoURL: URL

    @State private var player: AVPlayer?
    @State private var showShareSheet = false

    var body: some View {
        VStack(spacing: 20) {
            // Video player
            if let player = player {
                VideoPlayer(player: player)
                    .frame(height: 400)
                    .cornerRadius(16)
                    .onAppear {
                        player.play()
                    }
            } else {
                Rectangle()
                    .fill(Color.gray.opacity(0.2))
                    .frame(height: 400)
                    .cornerRadius(16)
                    .overlay {
                        ProgressView()
                    }
            }

            // Actions
            VStack(spacing: 16) {
                // Share button
                Button {
                    showShareSheet = true
                } label: {
                    HStack {
                        Image(systemName: "square.and.arrow.up")
                        Text("Share Highlight")
                    }
                    .font(.title3.bold())
                    .foregroundColor(.white)
                    .frame(maxWidth: .infinity)
                    .frame(height: 56)
                    .background(Color.blue)
                    .cornerRadius(16)
                }

                // Save to Photos button
                Button {
                    saveToPhotos()
                } label: {
                    HStack {
                        Image(systemName: "square.and.arrow.down")
                        Text("Save to Photos")
                    }
                    .font(.body)
                    .foregroundColor(.blue)
                    .frame(maxWidth: .infinity)
                    .frame(height: 50)
                    .background(Color.blue.opacity(0.1))
                    .cornerRadius(12)
                }
            }
            .padding(.horizontal)

            Spacer()
        }
        .padding()
        .navigationTitle("Your Highlight")
        .navigationBarTitleDisplayMode(.inline)
        .onAppear {
            setupPlayer()
        }
        .onDisappear {
            player?.pause()
        }
        .sheet(isPresented: $showShareSheet) {
            ShareSheet(items: [videoURL])
        }
    }

    private func setupPlayer() {
        player = AVPlayer(url: videoURL)
        // Loop video
        NotificationCenter.default.addObserver(
            forName: .AVPlayerItemDidPlayToEndTime,
            object: player?.currentItem,
            queue: .main
        ) { _ in
            player?.seek(to: .zero)
            player?.play()
        }
    }

    private func saveToPhotos() {
        // Request permission and save
        PHPhotoLibrary.requestAuthorization { status in
            guard status == .authorized else { return }

            PHPhotoLibrary.shared().performChanges({
                PHAssetCreationRequest.creationRequestForAssetFromVideo(atFileURL: videoURL)
            }) { success, error in
                DispatchQueue.main.async {
                    if success {
                        // Show success alert
                        print("Saved to Photos")
                    } else if let error = error {
                        print("Error saving: \(error)")
                    }
                }
            }
        }
    }
}

// MARK: - Share Sheet

struct ShareSheet: UIViewControllerRepresentable {
    let items: [Any]

    func makeUIViewController(context: Context) -> UIActivityViewController {
        UIActivityViewController(activityItems: items, applicationActivities: nil)
    }

    func updateUIViewController(_ uiViewController: UIActivityViewController, context: Context) {
        // No updates needed
    }
}

// Need to import Photos framework
import Photos

#Preview {
    NavigationStack {
        ResultView(videoURL: URL(fileURLWithPath: "/tmp/test.mp4"))
    }
}
