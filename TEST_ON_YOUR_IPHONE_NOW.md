# 📱 Test Moments App on Your iPhone RIGHT NOW

## ⚠️ Important: Expo Go Won't Work

**Your Moments app is a native Swift/iOS app, NOT a React Native/Expo app.**
- ❌ Cannot use Expo Go (incompatible technologies)
- ✅ Use Xcode to install directly on your iPhone

---

## ✅ Quick Setup (15 Minutes)

### Step 1: Connect Your iPhone to Mac

```bash
# 1. Connect iPhone to Mac via USB cable
# 2. Unlock your iPhone
# 3. When prompted "Trust This Computer?" → Tap "Trust"
# 4. Enter your iPhone passcode
```

### Step 2: Open Xcode Project

```bash
cd ~/Desktop/Professional_Projects/ML_PROJECTS_AI/moments_app/ios
open MomentsApp.xcodeproj
```

**This will launch Xcode with the Moments project.**

### Step 3: Configure Code Signing in Xcode

1. **In Xcode, click on "MomentsApp" (blue icon) in left sidebar**
2. **Select "MomentsApp" target** (under TARGETS)
3. **Click "Signing & Capabilities" tab**
4. **Check "Automatically manage signing"**
5. **For "Team" dropdown:**
   - If you see your name → Select it
   - If it says "None" → Click "Add Account" → Sign in with your Apple ID
   - After signing in, select your Apple ID as Team

Xcode will automatically create a free development certificate and provisioning profile.

### Step 4: Select Your iPhone as Destination

1. **At the TOP of Xcode window, find the device dropdown**
   - It probably says "iPhone 16 Pro" or similar
2. **Click the dropdown**
3. **Look for your actual iPhone name** (e.g., "Rohan's iPhone")
4. **Select your physical iPhone**
   - It should show a 📱 icon next to it
   - May take a moment to prepare device

### Step 5: Build and Run on Your iPhone

```
Click the PLAY button (▶️) at top-left of Xcode
OR
Press: Cmd + R
```

**Wait for build to complete (~30 seconds)**

### Step 6: Trust Developer on iPhone (First Time Only)

**If this is your first time installing:**

1. App will install but show "Untrusted Developer" when you try to open it
2. On your iPhone: **Settings → General → VPN & Device Management**
3. Under "DEVELOPER APP", tap **your Apple ID email**
4. Tap **"Trust [Your Email]"**
5. Tap **"Trust"** in confirmation dialog
6. **Go back to home screen and launch Moments app**

### Step 7: Test the App!

✅ Backend is already running at: `http://192.168.0.8:8000`
✅ App is configured to use this IP address
✅ Your iPhone and Mac are on the same WiFi

**Now test:**
1. Open Moments app on your iPhone
2. Tap "Select Video"
3. Choose a video from your Photos
4. Watch it upload and process
5. See your highlight!

---

## 🎯 Your Setup is Ready

### Backend Status
```bash
# Backend is running at:
http://192.168.0.8:8000

# Test it's working:
curl http://192.168.0.8:8000/health
```

### iOS App Status
- ✅ Updated to use your Mac's IP (192.168.0.8)
- ✅ Built successfully
- ✅ Ready to install on your iPhone

### Requirements Met
- ✅ Mac and iPhone on same WiFi
- ✅ Backend running and accessible
- ✅ App configured with correct IP

---

## 🔧 Troubleshooting

### "Could not install app"

**Solution:**
```bash
# In Xcode:
# Product → Clean Build Folder (Shift+Cmd+K)
# Then Product → Run (Cmd+R)
```

### "iPhone is not available"

**Solution:**
1. Disconnect and reconnect USB cable
2. Unlock iPhone
3. In Xcode: Window → Devices and Simulators
4. Wait for iPhone to appear
5. Close window and try again

### "Failed to verify code signature"

**Solution:**
1. Xcode → Preferences → Accounts
2. Select your Apple ID
3. Click "Download Manual Profiles"
4. Try building again

### "Could not connect to backend"

**Check:**
```bash
# 1. Verify backend is running:
curl http://192.168.0.8:8000/health

# 2. Verify iPhone can reach Mac:
# On your iPhone, open Safari
# Go to: http://192.168.0.8:8000/health
# Should see: {"status":"healthy","service":"Moments API",...}
```

If Safari can't reach it:
```bash
# Check Mac firewall:
# System Settings → Network → Firewall
# Make sure it's OFF or allows port 8000
```

### "Untrusted Developer" persists

**Solution:**
1. Settings → General → VPN & Device Management
2. Make sure you're tapping YOUR email (not someone else's)
3. Tap Trust twice (once on the app, once in confirmation)

---

## 📋 Testing Checklist

Once app is running on your iPhone:

### Basic Tests
- [ ] App launches without crashing
- [ ] UI looks good on your iPhone screen
- [ ] Tap "Select Video" button
- [ ] Can access your Photos library
- [ ] Select a short video (10-30 sec recommended)
- [ ] Upload progress shows
- [ ] Processing status updates
- [ ] Download completes
- [ ] Can play the highlight video
- [ ] Share/Save buttons work

### Advanced Tests
- [ ] Try different video lengths
- [ ] Test with different Target Duration settings (15s/30s/60s)
- [ ] Test while walking around (WiFi range)
- [ ] Check battery usage
- [ ] Test multiple videos in a row

---

## 🚀 Next Steps After Testing

### If Everything Works ✅

1. **Gather feedback** - Note any bugs or issues
2. **Test on different WiFi** - Move around your house
3. **Deploy backend** to Railway for testing anywhere
4. **Set up TestFlight** for easier distribution

### Deploy Backend to Railway

Once local testing is good:

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login

# Deploy backend
cd ~/Desktop/Professional_Projects/ML_PROJECTS_AI/moments_app/backend
railway init
railway up

# Get your Railway URL
railway domain

# Update iOS app with Railway URL (in APIClient.swift)
# Then can test from anywhere!
```

---

## 📝 Quick Reference

### Your Network Setup
- **Mac IP:** 192.168.0.8
- **Backend URL:** http://192.168.0.8:8000
- **WiFi:** Both devices must be on same network

### Xcode Shortcuts
- **Build & Run:** Cmd+R
- **Stop:** Cmd+.
- **Clean:** Shift+Cmd+K
- **Devices:** Shift+Cmd+2

### iPhone Requirements
- iOS 17.0 or later
- Connected to same WiFi as Mac
- Developer mode enabled (automatic on first install)
- USB cable for initial installation

---

## 🎉 You're All Set!

**Everything is configured and ready. Just:**

1. Connect iPhone via USB
2. Open Xcode project
3. Select your iPhone
4. Click Run (▶️)
5. Trust developer on iPhone
6. Test the app!

**The app will work on your real iPhone, using your Mac's backend!**

No Expo Go needed - you're testing the actual native iOS app that will go to the App Store! 🚀
