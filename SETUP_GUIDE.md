# Omi Audio Receiver - Setup Guide

This guide will help you set up the Omi Audio Receiver iOS app to receive real-time audio data from your Omi devices.

## Prerequisites

- macOS with Xcode 14.0 or later
- iOS device (iPhone/iPad) running iOS 15.0 or later
- Omi device (listening device)
- Omi mobile app installed on your device
- Internet connection

## Step 1: Build and Run the iOS App

1. **Open the project in Xcode:**
   ```bash
   open OmiAudioReceiver.xcodeproj
   ```

2. **Select your device:**
   - Connect your iOS device to your Mac
   - In Xcode, select your device as the target
   - Make sure your device is trusted and has developer mode enabled

3. **Build and run:**
   - Press `Cmd + R` or click the Run button
   - The app should install and launch on your device

## Step 2: Configure Network Access

The app needs to receive webhook requests from your Omi device. You have two options:

### Option A: Local Network (Same WiFi)

If your iPhone and Omi device are on the same WiFi network:

1. **Get your iPhone's IP address:**
   - Open Settings → WiFi
   - Tap the (i) icon next to your network
   - Note the IP address (e.g., 192.168.1.100)

2. **Use the local webhook URL:**
   - The app will display the webhook URL automatically
   - It should look like: `http://192.168.1.100:8080/audio`

### Option B: Public Internet (Recommended)

For more reliable connectivity, use ngrok to create a public tunnel:

1. **Install ngrok:**
   ```bash
   brew install ngrok
   ```

2. **Run the deployment script:**
   ```bash
   ./deploy.sh
   ```

3. **Use the public webhook URL:**
   - The script will provide a URL like: `https://abc123.ngrok.io/audio`
   - This URL will work from anywhere on the internet

## Step 3: Configure Your Omi Device

1. **Open the Omi app on your device**

2. **Enable Developer Mode:**
   - Go to Settings
   - Find and enable "Developer Mode"

3. **Configure the webhook:**
   - In Developer Mode, find "Realtime audio bytes"
   - Set the webhook URL to the one from Step 2
   - Configure the frequency (e.g., every 10 seconds)

4. **Test the connection:**
   - Start speaking to your Omi device
   - You should see audio files appear in the iOS app

## Step 4: Using the App

### Main Interface

- **Status Indicator:** Shows if the webhook server is running
- **Webhook URL:** Displays the current webhook endpoint
- **Audio Files List:** Shows all received audio recordings
- **Setup Instructions:** Access the setup guide

### Audio Playback

- **Play Button:** Tap to play an audio file
- **Stop Button:** Tap to stop playback
- **File Information:** Shows filename, date, and duration

### File Management

- Audio files are automatically saved to the app's documents directory
- Files are named with timestamps for easy identification
- The app loads existing files when launched

## Troubleshooting

### App Won't Start

- Check that your device is running iOS 15.0 or later
- Make sure you have a valid developer certificate
- Try cleaning the build folder (Cmd + Shift + K)

### No Audio Files Received

1. **Check webhook status:**
   - Ensure the app shows "Webhook Active"
   - Verify the webhook URL is correct

2. **Check network connectivity:**
   - Make sure both devices are on the same network (for local setup)
   - Verify ngrok tunnel is running (for public setup)

3. **Check Omi device settings:**
   - Confirm the webhook URL is set correctly
   - Verify the frequency is not set too high

4. **Check firewall settings:**
   - Ensure port 8080 is not blocked
   - Try using the public ngrok URL instead

### Audio Files Won't Play

- Check that your device's volume is turned up
- Ensure the audio file was saved correctly
- Try restarting the app

### Performance Issues

- Reduce the webhook frequency in the Omi app
- Close other apps to free up memory
- Restart the app if it becomes unresponsive

## Advanced Configuration

### Custom Port

To change the webhook server port, edit `WebhookServer.swift`:

```swift
private let port: UInt16 = 8080  // Change this value
```

### Audio Format

The app currently supports:
- Sample rates: 8000Hz, 16000Hz
- Format: 16-bit PCM
- Channels: Mono
- Container: WAV

### Storage Location

Audio files are stored in:
```
/var/mobile/Containers/Data/Application/[APP_ID]/Documents/AudioFiles/
```

## Security Considerations

- The webhook server accepts connections from any IP address
- Consider implementing authentication for production use
- Audio files are stored locally on the device
- No data is transmitted to external servers (except ngrok)

## Support

If you encounter issues:

1. Check the Xcode console for error messages
2. Verify all network settings
3. Try restarting both the app and your Omi device
4. Check the ngrok logs if using the public tunnel

## Next Steps

Once you have the basic audio reception working, you can:

1. **Add audio processing:** Implement speech-to-text, audio analysis, etc.
2. **Cloud storage:** Upload audio files to cloud services
3. **Real-time transcription:** Add live transcription capabilities
4. **Audio visualization:** Add waveform or spectrogram displays
5. **Integration:** Connect with other services via the audio data

Happy coding! 🎉 