#!/bin/bash

echo "🔍 Checking for connected iPhone..."

# Find connected iPhone
DEVICE_ID=$(xcrun xctrace list devices 2>&1 | grep "Rohan's iPhone" | grep -o '([A-F0-9-]*' | tr -d '(')

if [ -z "$DEVICE_ID" ]; then
    echo "❌ iPhone not found!"
    echo ""
    echo "Please make sure:"
    echo "1. Your iPhone is connected via USB"
    echo "2. Your iPhone is unlocked"
    echo "3. You tapped 'Trust' when iPhone asked 'Trust This Computer?'"
    echo ""
    exit 1
fi

echo "✅ Found: Rohan's iPhone ($DEVICE_ID)"
echo ""
echo "🔨 Building for physical device..."
echo ""

# Build for the physical device
xcodebuild \
    -project MomentsApp.xcodeproj \
    -scheme MomentsApp \
    -destination "id=$DEVICE_ID" \
    clean build \
    CODE_SIGN_IDENTITY="" \
    CODE_SIGNING_REQUIRED=NO \
    CODE_SIGNING_ALLOWED=NO

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Build succeeded!"
    echo ""
    echo "Now installing on your iPhone..."
    echo ""

    # Find the built app
    APP_PATH=$(find ~/Library/Developer/Xcode/DerivedData -name "MomentsApp.app" -path "*/Build/Products/Debug-iphoneos/*" -type d 2>/dev/null | head -1)

    if [ -n "$APP_PATH" ]; then
        echo "Found app at: $APP_PATH"
        echo ""
        echo "⚠️  To install on your iPhone:"
        echo "1. Open Xcode"
        echo "2. At the top, click the device dropdown"
        echo "3. Select 'Rohan's iPhone' (not simulator!)"
        echo "4. Click the Play button (▶️)"
        echo ""
        echo "First time setup:"
        echo "- Xcode will ask you to sign in with your Apple ID"
        echo "- Go to Signing & Capabilities tab and select your Apple ID as Team"
        echo "- Click Play again"
    fi
else
    echo ""
    echo "❌ Build failed"
    echo ""
    echo "This might be due to code signing requirements."
    echo "Please open Xcode and:"
    echo "1. Click MomentsApp (blue icon) in left sidebar"
    echo "2. Select MomentsApp under TARGETS"
    echo "3. Click 'Signing & Capabilities' tab"
    echo "4. Check 'Automatically manage signing'"
    echo "5. Select your Apple ID under 'Team'"
    echo "6. Click Play button at top"
fi
