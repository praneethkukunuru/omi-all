# Face Recognition App

A real-time face recognition application that uses YOLO for face detection and the face_recognition library for face recognition.

## Features

- Real-time face detection using YOLOv8
- Face recognition with known faces
- Live video feed from webcam
- Save captured frames
- Simple and easy to use

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `faces` directory and add face images:
```bash
mkdir faces
```

3. Add face images to the `faces` directory:
   - Use clear, front-facing photos
   - Name files as `person_name.jpg` (e.g., `john.jpg`, `sarah.png`)
   - Supported formats: JPG, JPEG, PNG

## Usage

Run the application:
```bash
python face_recognition_app.py
```

### Controls
- **q**: Quit the application
- **s**: Save current frame as image

### How it works

1. The app loads known faces from the `faces` directory
2. Opens your webcam for real-time video feed
3. Detects faces in each frame using YOLO
4. Recognizes detected faces by comparing with known faces
5. Displays bounding boxes and names on the video feed

## Requirements

- Python 3.8+
- Webcam
- Sufficient lighting for face detection

## Troubleshooting

- If no faces are detected, ensure good lighting
- If recognition is poor, use clearer reference images
- Make sure your webcam is working and accessible

## Performance

- Runs at ~15-30 FPS on most modern computers
- GPU acceleration available if CUDA is installed
- Memory usage scales with number of known faces 