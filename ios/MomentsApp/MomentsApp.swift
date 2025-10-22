//
//  MomentsApp.swift
//  MomentsApp
//
//  Main app entry point
//

import SwiftUI

@main
struct MomentsApp: App {
    init() {
        // Print app configuration on launch
        AppConfiguration.printConfiguration()
    }

    var body: some Scene {
        WindowGroup {
            HomeView()
        }
    }
}
