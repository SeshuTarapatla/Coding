# Android Emulator

## Installation
1. Download [command line-tools](https://developer.android.com/studio#command-tools) from Android studio site: [🔗](https://developer.android.com/studio#:~:text=Command%20line%20tools%20only).
2. Create a folder `C:\Android` and extract the cmdline-tools folder to it.
3. Create a folder named `latest` just after cmdline-tools folder.
4. Add bin folder to path.

## Setup
1. Required packages
```ps
sdkmanager --update #optional
sdkmanager --list   #list all installable packages
sdkmanager --install "platform-tools" "emulator" "system-images;android-36;google_apis_playstore;x86_64"
```
2. AVD creation
```ps
avdmanager list device #list all available devices
avdmanager create avd -n "emulator" -k "system-images;android-36;google_apis_playstore;x86_64" -d "pixel_9_pro"
echo "hw.keyboard=yes" >> "$env:USERPROFILE\.android\avd\emulator.avd\config.ini"
```

## Start/Stop
1. Add `C:\Android\emulator` to path before starting
```ps
emulator -avd emulator
```