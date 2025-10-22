#!/bin/bash
# Install Moments app to iPhone
# Run this script when iPhone is unlocked and connected

echo "🔍 Checking for connected iPhone..."
xcrun devicectl list devices | grep "iPhone"

echo ""
echo "📱 Installing app to iPhone..."
echo "⚠️ Make sure your iPhone is:"
echo "   1. Unlocked"
echo "   2. Connected via cable or WiFi"
echo "   3. Trust this computer is confirmed"
echo ""

APP_PATH="/Users/rohanbhandari/Library/Developer/Xcode/DerivedData/MomentsApp-dfekgfptbbkmdofuoxjvbtkvfzqg/Build/Products/Debug-iphoneos/MomentsApp.app"
DEVICE_ID="00008140-001129442E84801C"

if [ ! -d "$APP_PATH" ]; then
    echo "❌ App not found at: $APP_PATH"
    echo "Building app first..."
    cd "$(dirname "$0")"
    xcodebuild -project MomentsApp.xcodeproj -scheme MomentsApp -configuration Debug -sdk iphoneos CODE_SIGN_IDENTITY="Apple Development" DEVELOPMENT_TEAM=NYMNM2UCQ8 -allowProvisioningUpdates build

    if [ $? -ne 0 ]; then
        echo "❌ Build failed"
        exit 1
    fi
fi

echo "✅ App built successfully"
echo ""
echo "📲 Installing to iPhone..."

xcrun devicectl device install app --device $DEVICE_ID "$APP_PATH"

if [ $? -eq 0 ]; then
    echo "✅ App installed successfully!"
    echo ""
    echo "🚀 Launching app..."
    xcrun devicectl device process launch --device $DEVICE_ID com.rohanbhandari.moments
    echo ""
    echo "✅ App launched! Check your iPhone."
    echo ""
    echo "📋 Next steps:"
    echo "   1. Open Moments app on iPhone"
    echo "   2. Tap 'Select Video'"
    echo "   3. Choose a short video (30s-1min)"
    echo "   4. Watch it upload and process"
    echo ""
    echo "Backend is running at: http://192.168.0.5:8000"
else
    echo "❌ Installation failed"
    echo "⚠️ Make sure iPhone is unlocked and trusted"
    exit 1
fi
