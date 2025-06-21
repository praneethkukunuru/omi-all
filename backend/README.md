# Simple Face Recognition System

A lightweight face recognition system that works reliably on macOS without dlib compatibility issues.

## Features

- Face capture and recognition using OpenCV
- Works with MacBook's built-in camera
- Avoids dlib/face_recognition compatibility issues
- Simple template matching for face recognition
- Real-time face detection and recognition

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Capture faces:
```bash
python simple_face_capture.py
```
- Press 'c' to capture a face
- Enter the person's name when prompted
- Capture multiple images per person for better recognition
- Press 'q' to quit

3. Run face recognition:
```bash
python simple_face_recognition.py
```
- The app will load saved faces and start real-time recognition
- Press 'q' to quit, 's' to save current frame

## How it Works

- **Face Capture**: Uses OpenCV's Haar Cascade for face detection and saves full frames
- **Face Recognition**: Loads saved images, detects faces, and uses template matching for recognition
- **Camera Selection**: Automatically selects the MacBook's built-in camera (index 0 or 1)

## File Structure

```
backend/
├── simple_face_capture.py    # Face capture application
├── simple_face_recognition.py # Face recognition application
└── known_faces/              # Directory for saved face images
    └── [person_name]/
        ├── [person_name]_[timestamp].jpg
        └── ...
```

## Troubleshooting

- **Camera not working**: Make sure to grant camera permissions to Terminal/VS Code
- **No faces detected**: Ensure good lighting and face is clearly visible
- **Recognition issues**: Capture more face images from different angles
- **Performance**: The app processes every 3rd frame for better performance 