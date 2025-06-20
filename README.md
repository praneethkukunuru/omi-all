# Omi Audio Receiver iOS App

This iOS app receives real-time audio data from Omi devices via webhook connections.

## Features

- Real-time audio streaming from Omi devices
- Webhook endpoint to receive audio data
- Audio playback and visualization
- Background processing support
- Local audio file storage

## Setup Instructions

1. **Configure Omi Device:**
   - Open the Omi app on your device
   - Go to Settings → Developer Mode
   - Set the "Realtime audio bytes" webhook URL to your server endpoint
   - Configure the frequency (e.g., every 10 seconds)

2. **Deploy the Webhook Server:**
   - The app includes a simple webhook server
   - Deploy to a cloud service or use ngrok for local testing
   - Update the webhook URL in your Omi app settings

3. **Run the iOS App:**
   - Open the project in Xcode
   - Build and run on your device
   - The app will start listening for audio data

## Architecture

- **iOS App**: SwiftUI-based interface for audio playback and management
- **Webhook Server**: Receives audio data from Omi devices
- **Audio Processing**: Handles raw audio bytes and converts to playable format
- **Storage**: Local file system for audio recordings

## Requirements

- iOS 15.0+
- Xcode 14.0+
- Swift 5.7+
- Active internet connection for webhook communication 