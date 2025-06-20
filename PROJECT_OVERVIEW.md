# Omi Audio Receiver - Project Overview

## Architecture

The Omi Audio Receiver is an iOS app that receives real-time audio data from Omi devices via webhook connections. The app consists of several key components:

### Core Components

#### 1. **OmiAudioReceiverApp.swift**
- Main app entry point
- Initializes and coordinates all components
- Manages app lifecycle

#### 2. **ContentView.swift**
- Main user interface
- Displays webhook status and audio files
- Provides audio playback controls
- Shows setup instructions

#### 3. **AudioManager.swift**
- Manages audio file storage and playback
- Handles AVAudioPlayer for audio playback
- Tracks playback progress and state
- Loads existing audio files on app launch

#### 4. **WebhookServer.swift**
- Implements HTTP server using Network framework
- Receives audio data from Omi devices
- Parses HTTP requests and query parameters
- Converts raw audio data to WAV files

#### 5. **AudioFile.swift**
- Data model for audio files
- Handles WAV header creation
- Manages file metadata (duration, sample rate, etc.)
- Provides formatted display properties

### Data Flow

```
Omi Device → Webhook Server → Audio Manager → UI
     ↓              ↓              ↓         ↓
  Audio Data → HTTP Request → Audio File → Display
```

1. **Omi Device** sends audio data via HTTP POST
2. **WebhookServer** receives and parses the request
3. **AudioFile** creates WAV file from raw data
4. **AudioManager** stores and manages the file
5. **ContentView** displays and allows playback

### Key Features

#### Real-time Audio Reception
- HTTP webhook server on port 8080
- Supports query parameters (sample_rate, uid)
- Handles raw audio data (16-bit PCM)
- Automatic WAV header generation

#### Audio Playback
- Native iOS audio playback
- Play/pause/stop controls
- Progress tracking
- Multiple file support

#### File Management
- Automatic file organization
- Timestamp-based naming
- Local storage in app documents
- Persistent file loading

#### User Interface
- Clean, modern SwiftUI interface
- Real-time status indicators
- Audio file list with metadata
- Setup instructions and troubleshooting

### Technical Specifications

#### Audio Format Support
- **Sample Rates:** 8000Hz, 16000Hz
- **Bit Depth:** 16-bit
- **Channels:** Mono
- **Container:** WAV
- **Encoding:** PCM

#### Network Requirements
- **Protocol:** HTTP/1.1
- **Method:** POST
- **Content-Type:** application/octet-stream
- **Port:** 8080 (configurable)

#### iOS Requirements
- **Minimum iOS:** 15.0
- **Architecture:** ARM64
- **Frameworks:** SwiftUI, AVFoundation, Network

### Security Considerations

#### Current Implementation
- No authentication (development only)
- Accepts connections from any IP
- Local file storage only
- No data transmission to external servers

#### Production Recommendations
- Implement API key authentication
- Add request validation
- Use HTTPS for webhook endpoints
- Implement rate limiting
- Add audio data encryption

### Deployment Options

#### Local Development
- Direct IP address access
- Same WiFi network required
- Simple setup, limited connectivity

#### Public Deployment
- ngrok tunnel for public access
- Works from anywhere
- Requires ngrok account
- More reliable connectivity

### Testing

#### Manual Testing
1. Run the iOS app
2. Configure Omi device webhook URL
3. Speak to Omi device
4. Verify audio files appear in app

#### Automated Testing
- Use `test_webhook.py` script
- Sends test audio data
- Verifies webhook functionality
- Helps with troubleshooting

### Future Enhancements

#### Audio Processing
- Speech-to-text integration
- Audio analysis and visualization
- Real-time transcription
- Voice activity detection

#### Cloud Integration
- Upload to cloud storage
- Multi-device sync
- Backup and restore
- Sharing capabilities

#### Advanced Features
- Audio filters and effects
- Multiple format support
- Background processing
- Push notifications

### File Structure

```
omi-all/
├── README.md                 # Project overview
├── SETUP_GUIDE.md           # Detailed setup instructions
├── PROJECT_OVERVIEW.md      # This file
├── deploy.sh                # Deployment script
├── test_webhook.py          # Webhook testing script
└── OmiAudioReceiver.xcodeproj/
    └── project.pbxproj      # Xcode project file
└── OmiAudioReceiver/
    ├── OmiAudioReceiverApp.swift    # Main app
    ├── ContentView.swift            # Main UI
    ├── AudioManager.swift           # Audio handling
    ├── WebhookServer.swift          # Webhook server
    ├── AudioFile.swift              # Data model
    ├── Info.plist                   # App configuration
    └── Assets.xcassets/             # App assets
```

### Development Workflow

1. **Setup:** Follow SETUP_GUIDE.md
2. **Development:** Use Xcode for iOS development
3. **Testing:** Use test_webhook.py for webhook testing
4. **Deployment:** Use deploy.sh for public access
5. **Debugging:** Check Xcode console and ngrok logs

### Troubleshooting

#### Common Issues
- Webhook not receiving data
- Audio files not playing
- Network connectivity problems
- App crashes or freezes

#### Debug Steps
1. Check webhook server status
2. Verify network connectivity
3. Test with test_webhook.py
4. Review Xcode console logs
5. Check ngrok tunnel status

This architecture provides a solid foundation for receiving and processing audio data from Omi devices, with room for future enhancements and integrations. 