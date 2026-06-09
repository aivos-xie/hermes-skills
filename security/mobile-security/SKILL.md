---
name: mobile-security
version: 1.0.0
description: Mobile application security testing — Android/iOS static and dynamic analysis, instrumentation, and exploitation
tags: [security, mobile, android, ios, frida, apk, pentesting]
triggers:
  - mobile security
  - android pentest
  - ios pentest
  - APK analysis
  - Frida
  - mobile app testing
  - reverse engineer APK
  - app security
---

# Mobile Security Testing

## Tool Arsenal

| Tool | Purpose | Platform |
|------|---------|----------|
| MobSF | Automated mobile security framework | Android + iOS |
| Frida | Dynamic instrumentation toolkit | Android + iOS |
| Objection | Frida-powered mobile exploration | Android + iOS |
| apktool | APK decode/rebuild | Android |
| jadx | DEX → Java decompiler | Android |
| dex2jar | DEX → JAR converter | Android |
| Magisk | Systemless root + root hiding | Android |
| Xposed/LSPosed | Runtime hooking framework | Android |

---

## Environment Setup

### Prerequisites

```bash
# Install Java (required for most Android tools)
sudo apt install openjdk-17-jdk

# Install Android SDK tools
# Download command-line tools from https://developer.android.com/studio#cmdline-tools
wget https://dl.google.com/android/repository/commandlinetools-linux-11076708_latest.zip
unzip commandlinetools-linux-*.zip -d $HOME/android-sdk/cmdline-tools/latest

export ANDROID_HOME=$HOME/android-sdk
export PATH=$ANDROID_HOME/cmdline-tools/latest/bin:$ANDROID_HOME/platform-tools:$PATH

# Accept licenses and install platform tools
sdkmanager --licenses
sdkmanager "platform-tools" "build-tools;34.0.0"
```

---

## 1. MobSF (Mobile Security Framework)

**Repo:** https://github.com/MobSF/Mobile-Security-Framework-MobSF

Automated static and dynamic analysis for Android/iOS apps.

### Setup

```bash
# Docker (recommended)
docker pull opensecurity/mobsf:latest

# Or install locally
git clone https://github.com/MobSF/Mobile-Security-Framework-MobSF.git
cd MobSF
./setup.sh  # or setup.bat on Windows

# Python install
pip install -r requirements.txt
```

### Usage

```bash
# Start MobSF
docker run -it -p 8000:8000 opensecurity/mobsf:latest

# Or locally
python manage.py runserver 0.0.0.0:8000

# Upload APK/IPA via web UI at http://localhost:8000
# Or via CLI:
python -m mobsf.MobSF.main --file target.apk
```

### What MobSF Reports

- Permissions analysis
- Hardcoded secrets (API keys, certificates)
- Insecure data storage
- Weak cryptography usage
- Exported components (activities, services, receivers)
- Network security configuration
- Malware score heuristics

### Pitfalls

- Dynamic analysis requires an emulator — MobSF can spin up AVD automatically
- iOS analysis needs a macOS host for dynamic analysis (static works on Linux)
- Large APKs (>200MB) may timeout — increase `MobsfConfig.scan_timeout`

---

## 2. Frida — Dynamic Instrumentation

**Repo:** https://github.com/frida/frida

Inject JavaScript into native apps to hook functions, intercept calls, and modify behavior at runtime.

### Setup

```bash
# Install Frida tools
pip install frida-tools

# Verify version
frida --version

# Download frida-server for Android (match version!)
FRIDA_VERSION=$(frida --version)
wget "https://github.com/frida/frida/releases/download/${FRIDA_VERSION}/frida-server-${FRIDA_VERSION}-android-arm64.xz"
xz -d frida-server-*.xz
adb push frida-server-*-android-arm64 /data/local/tmp/frida-server
adb shell "chmod 755 /data/local/tmp/frida-server"
```

### Running Frida Server on Android

```bash
# Start frida-server (requires root)
adb shell "su -c '/data/local/tmp/frida-server -D &'"

# Verify connection
frida-ps -U  # List processes on USB device
frida-ps -Ua  # List all applications
```

### Basic Usage

```bash
# Attach to running app
frida -U -n com.target.app -l hook.js

# Spawn app with instrumentation
frida -U -f com.target.app -l hook.js --no-pause

# List running apps
frida-ps -Ua
```

### Common Frida Scripts

#### Bypass SSL Pinning

```javascript
// ssl-bypass.js
Java.perform(function() {
    // TrustManager bypass
    var TrustManager = Java.registerClass({
        name: 'com.custom.BypassTrustManager',
        implements: [Java.use('javax.net.ssl.X509TrustManager')],
        methods: {
            checkClientTrusted: function(chain, authType) {},
            checkServerTrusted: function(chain, authType) {},
            getAcceptedIssuers: function() { return []; }
        }
    });

    var SSLContext = Java.use('javax.net.ssl.SSLContext');
    var ctx = SSLContext.getInstance('TLS');
    ctx.init(null, [TrustManager.$new()], null);

    // Override OkHttp certificate pinner
    try {
        var CertificatePinner = Java.use('okhttp3.CertificatePinner');
        CertificatePinner.check.overload('java.lang.String', 'java.util.List').implementation = function() {
            console.log('[+] SSL Pinning bypassed (OkHttp)');
        };
    } catch(e) {}

    // Override WebViewClient
    try {
        var WebViewClient = Java.use('android.webkit.WebViewClient');
        WebViewClient.onReceivedSslError.implementation = function(view, handler, error) {
            handler.proceed();
            console.log('[+] SSL error bypassed (WebView)');
        };
    } catch(e) {}
});
```

#### Hook Crypto Functions

```javascript
// crypto-hook.js
Java.perform(function() {
    // Hook AES encryption
    var Cipher = Java.use('javax.crypto.Cipher');
    Cipher.doFinal.overload('[B').implementation = function(input) {
        console.log('[Cipher.doFinal] Algorithm: ' + this.getAlgorithm());
        console.log('[Cipher.doFinal] Input: ' + bytesToHex(input));
        var result = this.doFinal(input);
        console.log('[Cipher.doFinal] Output: ' + bytesToHex(result));
        return result;
    };

    // Hook SharedPreferences (often stores secrets)
    var SharedPreferencesImpl = Java.use('android.app.SharedPreferencesImpl');
    SharedPreferencesImpl.getString.implementation = function(key, defValue) {
        var value = this.getString(key, defValue);
        console.log('[SharedPrefs] ' + key + ' = ' + value);
        return value;
    };
});

function bytesToHex(bytes) {
    var hex = [];
    for (var i = 0; i < bytes.length; i++) {
        hex.push(('0' + (bytes[i] & 0xFF).toString(16)).slice(-2));
    }
    return hex.join('');
});
```

#### Enumerate Loaded Classes

```javascript
// enum-classes.js
Java.perform(function() {
    Java.enumerateLoadedClasses({
        onMatch: function(className) {
            if (className.includes('target') || className.includes('auth') || className.includes('token')) {
                console.log('[Class] ' + className);
            }
        },
        onComplete: function() {
            console.log('[*] Enumeration complete');
        }
    });
});
```

### Pitfalls

- frida-server version MUST match frida-tools version exactly
- Some apps detect Frida — use `frida-server` renamed + Magisk Hide
- ART runtime changes between Android versions can break hooks
- Use `--runtime=v8` for better compatibility: `frida -U -f com.app -l hook.js --runtime=v8`

---

## 3. Objection — Mobile Exploration

**Repo:** https://github.com/sensepost/objection

Frida-powered runtime mobile exploration without needing to write JavaScript.

### Setup

```bash
pip install objection
```

### Usage

```bash
# Start exploration (requires frida-server running)
objection -g com.target.app explore

# Common commands inside objection:
# Memory
memory list modules
memory list exports libtarget.so
memory dump all output.bin

# Keychain (iOS)
ios keychain dump

# SSL Pinning
android sslpinning disable

# Root detection
android root disable

# Hooking
android hooking list classes
android hooking list class_methods com.target.app.ApiClient
android hooking watch class com.target.app.LoginActivity --dump-args --dump-return

# File system
file download /data/data/com.target.app/shared_prefs/config.xml

# Networking
android hooking watch class okhttp3.OkHttpClient --dump-args
```

### Pitfalls

- Objection is a convenience wrapper — for complex hooks, write raw Frida scripts
- Some `disable` commands (root, sslpinning) use known bypass patterns that modern apps detect
- Update frequently — Android API changes break objection hooks

---

## 4. Static Analysis Tools

### apktool — Decode and Rebuild APKs

```bash
# Install
sudo apt install apktool
# Or: brew install apktool

# Decode APK
apktool d target.apk -o target_decoded/

# Key files to examine:
# target_decoded/AndroidManifest.xml — permissions, components
# target_decoded/smali/ — smali bytecode
# target_decoded/res/ — resources
# target_decoded/assets/ — raw assets
# target_decoded/lib/ — native libraries

# Rebuild after modification
apktool b target_decoded/ -o target_modified.apk

# Sign the rebuilt APK
keytool -genkey -v -keystore test.keystore -alias test -keyalg RSA -keysize 2048 -validity 10000
jarsigner -verbose -sigalg SHA256withRSA -digestalg SHA-256 -keystore test.keystore target_modified.apk test
zipalign -v 4 target_modified.apk target_final.apk
```

### jadx — Java Decompiler

```bash
# Install
# Download from https://github.com/skylot/jadx/releases
wget https://github.com/skylot/jadx/releases/latest/download/jadx-1.5.1.zip
unzip jadx-*.zip -d jadx/

# GUI mode
./jadx/bin/jadx-gui target.apk

# CLI mode — decompile to directory
./jadx/bin/jadx target.apk -d output_java/

# Search for secrets
grep -rn "api_key\|apikey\|secret\|password\|token" output_java/
grep -rn "https\?://" output_java/ | grep -v "\.google\.\|android\.\|schemas\."
```

### dex2jar

```bash
# Install
# Download from https://github.com/pxb1988/dex2jar/releases
wget https://github.com/pxb1988/dex2jar/releases/latest/dex-tools-v2.4.zip
unzip dex-tools-v2.4.zip

# Convert
./dex2jar/d2j-dex2jar.sh target.apk -o target-dex2jar.jar

# Open in JD-GUI or decompile with jadx
```

### Useful Static Analysis Searches

```bash
# Find hardcoded secrets
grep -rn "AIza\|AKIA\|sk-\|pk_\|SG\.\|key\|secret\|password\|token" output_java/ --include="*.java"

# Find URLs and endpoints
grep -rnoP 'https?://[^\s"'"'"'<>]+' output_java/ | sort -u

# Find exported components (attack surface)
grep -A2 'exported="true"' target_decoded/AndroidManifest.xml

# Find deep links
grep -r "android:scheme" target_decoded/AndroidManifest.xml

# Find WebView JavaScript interfaces
grep -rn "addJavascriptInterface\|@JavascriptInterface" output_java/
```

---

## 5. Root Detection Bypass

### Magisk — Systemless Root

**Repo:** https://github.com/topjohnwu/Magisk

```bash
# Magisk provides systemless root — doesn't modify /system
# Flash via custom recovery or patch boot image

# 1. Extract boot.img from device
adb shell "su -c 'cat /dev/block/by-name/boot' > /sdcard/boot.img"
adb pull /sdcard/boot.img

# 2. Patch with Magisk Manager (on device)
# Install Magisk.apk → "Install" → "Select and Patch a File" → boot.img

# 3. Flash patched boot
adb push magisk_patched-*.img /sdcard/
fastboot flash boot magisk_patched-*.img

# 4. Configure DenyList (formerly MagiskHide)
# Magisk app → Settings → Configure DenyList → add target apps
```

### LSPosed — Xposed Framework

```bash
# LSPosed requires Magisk (Zygisk)
# Install Zygisk-enabled Magisk first

# Install LSPosed module
# Download from: https://github.com/LSPosed/LSPosed/releases
# Flash via Magisk Manager

# Useful LSPosed modules:
# - JustTrustMe — bypass SSL pinning
# - RootCloak — hide root
# - XPrivacyLua — privacy controls
# - TrustMeAlready — bypass SSL certificate validation
```

---

## 6. APK Patching and Repackaging

### Add Frida Gadget to APK (No Root Required)

```bash
# 1. Decompile
apktool d target.apk -o target_out/

# 2. Download Frida gadget for target architecture
FRIDA_VERSION=$(frida --version)
wget "https://github.com/frida/frida/releases/download/${FRIDA_VERSION}/frida-gadget-${FRIDA_VERSION}-android-arm64.so.xz"
xz -d frida-gadget-*.so.xz
cp frida-gadget-*.so target_out/lib/arm64-v8a/libfrida-gadget.so

# 3. Inject load into smali — find Application class or main Activity
# Add to the constructor or attachBaseContext:
# const-string v0, "frida-gadget"
# invoke-static {v0}, Ljava/lang/System;->loadLibrary(Ljava/lang/String;)V

# Or inject into a static initializer of the main activity
# Edit target_out/smali/com/target/app/MainActivity.smali

# 4. Rebuild
apktool b target_out/ -o target_patched.apk

# 5. Sign
apksigner sign --ks test.keystore --ks-pass pass:password target_patched.apk

# 6. Install
adb install target_patched.apk
```

### Patch smali to Load Library

```smali
# Add to .locals of the target method (increase count by 1)
# Then insert:
const-string v0, "frida-gadget"
invoke-static {v0}, Ljava/lang/System;->loadLibrary(Ljava/lang/String;)V
```

---

## 7. iOS-Specific Notes

### Key Differences from Android

- Requires jailbroken device for dynamic analysis (checkra1n, palera1n)
- Frida works on jailbroken iOS — install via Cydia: `apt install re.frida.server`
- Use class-dump for Objective-C class extraction
- Use Clutch or frida-ios-dump for decrypted IPA extraction

```bash
# Install Frida on jailbroken iOS
ssh root@<device-ip>
apt update && apt install re.frida.server

# Dump decrypted IPA (alternative to Clutch)
python3 frida-ios-dump.py -l  # List apps
python3 frida-ios-dump.py com.target.app  # Dump
```

---

## 8. Complete Android Pentest Checklist

```
[ ] 1. Extract APK (adb pull, APKMirror, or apkpull)
[ ] 2. MobSF automated scan
[ ] 3. apktool decode → check AndroidManifest.xml
[ ] 4. jadx decompile → search for secrets, endpoints
[ ] 5. Check for hardcoded keys, tokens, passwords
[ ] 6. Analyze network security config
[ ] 7. Check for exported components (attack surface)
[ ] 8. Test deep links for injection
[ ] 9. Check WebView configurations (JavaScript enabled?)
[ ] 10. Set up Frida → test root detection bypass
[ ] 11. SSL pinning bypass → intercept traffic with Burp
[ ] 12. Test authentication (token storage, session management)
[ ] 13. Test data storage (SharedPrefs, SQLite, files)
[ ] 14. Test IPC (intents, content providers)
[ ] 15. If native code exists → RE with Ghidra + hooks
```

---

## Common Pitfalls

1. **Version mismatch** — Frida client/server versions must match exactly
2. **Emulator detection** — Many apps detect emulators. Use physical device or hide emulator artifacts
3. **64-bit only** — Some apps only have arm64 libs; 32-bit emulators won't work
4. **Split APKs** — Use `apkanalyzer` or Bundletool to handle Android App Bundles (.aab)
5. **Network security** — Android 7+ doesn't trust user CA by default; patch `network_security_config.xml`
6. **ProGuard/R8** — Obfuscated code is hard to read; focus on method signatures and string constants
