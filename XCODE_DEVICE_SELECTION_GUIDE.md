# EXACT Steps to Run Moments on Your iPhone

**Your iPhone IS connected:** ✅ Rohan's iPhone (ID: 00008140-001129442E84801C)
**Problem:** Xcode needs code signing setup (one-time)

---

## 🎯 EXACT Visual Guide

### Step 1: Look at Top Left of Xcode

You should see this area:

```
[■] [▶︎]  MomentsApp > [Some Device Name]
```

The part that says **"[Some Device Name]"** - what does it say EXACTLY?

### Step 2: Click on That Device Name

Click directly on whatever text is there (probably says "iPhone 16 Pro" or similar)

### Step 3: In the Dropdown, Look for This EXACT Text:

```
Rohan's iPhone
```

It should be at the **VERY TOP** of the list, above a divider line.

**NOT "iPhone 16 Pro" (that's the simulator)**
**YES "Rohan's iPhone" (that's your actual device)**

### Step 4: Select "Rohan's iPhone"

Click on it. The top bar should now show:

```
[■] [▶︎]  MomentsApp > Rohan's iPhone
```

### Step 5: Set Up Code Signing (ONE TIME ONLY)

**In the left sidebar of Xcode:**

1. Click the **BLUE icon** at the very top (says "MomentsApp")
2. In the main area, under **TARGETS**, click **"MomentsApp"**
3. At the top of the main area, click the **"Signing & Capabilities"** tab
4. You'll see: **"Signing for MomentsApp requires a development team"**
5. Check the box: ☑️ **"Automatically manage signing"**
6. Under **"Team"**, you'll see a dropdown that says "None" or "Select a team"
7. **Click the Team dropdown**
8. Select **your Apple ID** (should show your email like rohan@...)
   - If you don't see your Apple ID:
     - Click **"Add an Account..."**
     - Sign in with your Apple ID (the one you use for iCloud/App Store)
     - Come back and select it

### Step 6: Click Play

1. Go back to the top left
2. Make sure it still says **"Rohan's iPhone"** (not simulator)
3. Click the **Play button (▶︎)**

### Step 7: First Time on iPhone

**Your iPhone will show a popup:**
- "Untrusted Developer"
- This is NORMAL for development apps

**On your iPhone:**
1. Go to: **Settings** app
2. **General**
3. **VPN & Device Management** (or "Profiles & Device Management")
4. You'll see your Apple ID listed
5. **Tap it**
6. **Tap "Trust [Your Name]"**
7. **Tap "Trust" again** to confirm

### Step 8: Launch the App

1. Go to your iPhone home screen
2. Find the **Moments** app icon
3. **Tap it**
4. App launches! 🎉

---

## 📸 If You Can Send Me Info

Can you tell me or take a screenshot of:

1. **What does the device dropdown in Xcode currently show?**
   - Does it say "iPhone 16 Pro" (simulator) or "Rohan's iPhone" (real device)?

2. **When you click it, do you see "Rohan's iPhone" at the top of the list?**

3. **When you go to Signing & Capabilities, what does it say under Team?**
   - "None"
   - Your Apple ID email
   - Something else?

---

## 🔑 Why This Is Required

- iOS **requires code signing** for all apps on physical devices
- Even for personal testing, you need to sign with your Apple ID
- This is Apple's security requirement - there's no way around it
- **Good news:** Your free Apple ID works! No paid developer account needed.

---

## ⚡ Once This Works (One-Time Setup)

After you set up code signing once:
- Future builds will be INSTANT
- Just click Play (▶︎) and it installs
- No more configuration needed

---

## 🎬 What Happens After It's Installed

1. App launches on your iPhone
2. You tap "Create Highlight"
3. Select a video from your Photos
4. Watch AI process it
5. **See if audio is preserved!** 🔊
6. Test the real value proposition!

---

**The device IS connected. We just need to configure code signing in Xcode. This is a one-time thing!**

Let me know what you see in Xcode and I'll guide you through the exact clicks.
