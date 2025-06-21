import cv2
import numpy as np
import os
from pathlib import Path
import time

class SimpleFaceRecognition:
    def __init__(self, faces_dir="known_faces"):
        self.faces_dir = Path(faces_dir)
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.known_faces = {}
        self.load_known_faces()
        
    def load_known_faces(self):
        """Load known faces from the faces directory"""
        if not self.faces_dir.exists():
            print(f"Faces directory {self.faces_dir} not found!")
            return
            
        print(f"Loading faces from {self.faces_dir}...")
        
        for person_dir in self.faces_dir.iterdir():
            if person_dir.is_dir():
                person_name = person_dir.name
                face_images = []
                
                for img_file in person_dir.glob("*.jpg"):
                    img = cv2.imread(str(img_file))
                    if img is not None:
                        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                        faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
                        
                        if len(faces) > 0:
                            # Use the first detected face
                            x, y, w, h = faces[0]
                            face_roi = gray[y:y+h, x:x+w]
                            face_roi = cv2.resize(face_roi, (100, 100))  # Standardize size
                            face_images.append(face_roi)
                
                if face_images:
                    self.known_faces[person_name] = face_images
                    print(f"  ✅ Loaded {len(face_images)} face(s) for {person_name}")
        
        print(f"Loaded {len(self.known_faces)} known people")
    
    def detect_faces(self, frame):
        """Detect faces in the frame"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
        return faces, gray
    
    def compare_faces(self, face_roi, known_faces):
        """Compare a face ROI with known faces using template matching"""
        best_match = None
        best_score = 0
        
        face_roi = cv2.resize(face_roi, (100, 100))
        
        for person_name, person_faces in known_faces.items():
            for known_face in person_faces:
                # Use template matching
                result = cv2.matchTemplate(face_roi, known_face, cv2.TM_CCOEFF_NORMED)
                score = np.max(result)
                
                if score > best_score:
                    best_score = score
                    best_match = person_name
        
        return best_match, best_score
    
    def recognize_faces(self, frame):
        """Recognize faces in the frame"""
        faces, gray = self.detect_faces(frame)
        results = []
        
        for (x, y, w, h) in faces:
            face_roi = gray[y:y+h, x:x+w]
            
            if len(self.known_faces) > 0:
                person_name, confidence = self.compare_faces(face_roi, self.known_faces)
                
                if confidence > 0.6:  # Threshold for recognition
                    results.append((x, y, w, h, person_name, confidence))
                else:
                    results.append((x, y, w, h, "Unknown", confidence))
            else:
                results.append((x, y, w, h, "No known faces", 0.0))
        
        return results

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

def main():
    print("Simple Face Recognition App Started")
    print("Press 'q' to quit, 's' to save current frame")
    
    # Initialize face recognition
    recognizer = SimpleFaceRecognition()
    
    if not recognizer.known_faces:
        print("No known faces found! Please run simple_face_capture.py first to capture faces.")
        return
    
    # Get camera
    cap = get_macbook_camera()
    
    if not cap.isOpened():
        print("Error: Could not open camera")
        return
    
    # Set camera properties for better performance
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    cap.set(cv2.CAP_PROP_FPS, 30)
    
    frame_count = 0
    start_time = time.time()
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Error: Could not read frame")
                break
            
            # Process every 3rd frame for better performance
            frame_count += 1
            if frame_count % 3 != 0:
                continue
            
            # Recognize faces
            results = recognizer.recognize_faces(frame)
            
            # Draw results
            for (x, y, w, h, name, confidence) in results:
                # Draw rectangle around face
                color = (0, 255, 0) if name != "Unknown" and name != "No known faces" else (0, 0, 255)
                cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
                
                # Draw label
                label = f"{name} ({confidence:.2f})"
                cv2.putText(frame, label, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
            
            # Calculate and display FPS
            elapsed_time = time.time() - start_time
            if elapsed_time > 0:
                fps = frame_count / elapsed_time
                cv2.putText(frame, f"FPS: {fps:.1f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            
            # Display frame
            cv2.imshow('Simple Face Recognition', frame)
            
            # Handle key presses
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s'):
                timestamp = int(time.time())
                filename = f"captured_frame_{timestamp}.jpg"
                cv2.imwrite(filename, frame)
                print(f"Saved frame as {filename}")
    
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    
    finally:
        cap.release()
        cv2.destroyAllWindows()
        print("Face recognition stopped")

if __name__ == "__main__":
    main() 