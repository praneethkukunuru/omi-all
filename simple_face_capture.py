import cv2
import os
from pathlib import Path
import time

def get_macbook_camera():
    """Get the MacBook's built-in camera, avoiding Continuity Camera"""
    cap = cv2.VideoCapture(0)
    
    # Try to get camera info
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    print(f"Using camera at index 0 (resolution: {width}x{height})")
    
    # If this looks like Continuity Camera (usually lower resolution), try index 1
    if width < 1280 or height < 720:
        cap.release()
        cap = cv2.VideoCapture(1)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        print(f"Switched to camera at index 1 (resolution: {width}x{height})")
    
    return cap

def capture_faces():
    """Capture face images for training"""
    print("Face Capture App Started")
    print("Press 'c' to capture a face, 'q' to quit")
    print("Enter the person's name when prompted")
    
    # Create faces directory
    faces_dir = Path("known_faces")
    faces_dir.mkdir(exist_ok=True)
    
    # Get camera
    cap = get_macbook_camera()
    
    if not cap.isOpened():
        print("Error: Could not open camera")
        return
    
    # Set camera properties
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    cap.set(cv2.CAP_PROP_FPS, 30)
    
    # Load face detection model
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    
    current_person = None
    capture_count = 0
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Error: Could not read frame")
                break
            
            # Detect faces
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)
            
            # Draw face detection rectangles
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            
            # Add status text
            status = f"Person: {current_person or 'None'} | Captures: {capture_count}"
            cv2.putText(frame, status, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            if current_person:
                cv2.putText(frame, f"Press 'c' to capture for {current_person}", (10, 60), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            else:
                cv2.putText(frame, "Enter person name and press 'c' to capture", (10, 60), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            
            # Display frame
            cv2.imshow('Face Capture', frame)
            
            # Handle key presses
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('c'):
                if len(faces) == 0:
                    print("No face detected! Please position your face in the camera.")
                    continue
                
                if current_person is None:
                    # Get person name
                    person_name = input("Enter person name: ").strip()
                    if not person_name:
                        print("Please enter a valid name")
                        continue
                    current_person = person_name
                
                # Create person directory
                person_dir = faces_dir / current_person
                person_dir.mkdir(exist_ok=True)
                
                # Save face image
                timestamp = int(time.time())
                filename = f"{current_person}_{timestamp}.jpg"
                filepath = person_dir / filename
                
                # Save the full frame (we'll crop it during recognition)
                cv2.imwrite(str(filepath), frame)
                capture_count += 1
                
                print(f"Captured face {capture_count} for {current_person}: {filename}")
                
                # Ask if they want to capture more for this person
                if capture_count >= 5:
                    more = input(f"Captured {capture_count} images for {current_person}. Capture more? (y/n): ").lower()
                    if more != 'y':
                        current_person = None
                        capture_count = 0
                        print("Ready for next person...")
    
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    
    finally:
        cap.release()
        cv2.destroyAllWindows()
        print("Face capture stopped")

if __name__ == "__main__":
    capture_faces() 