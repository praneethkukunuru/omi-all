import cv2
import numpy as np
import face_recognition
import os
import time

class FaceRecognitionApp:
    def __init__(self):
        self.known_face_encodings = []
        self.known_face_names = []
        self.face_locations = []
        self.face_encodings = []
        self.face_names = []
        self.process_this_frame = True
        
        # Load known faces from the faces directory
        self.load_known_faces()
        
    def load_known_faces(self):
        """Load known faces from the faces directory"""
        faces_dir = "faces"
        if not os.path.exists(faces_dir):
            os.makedirs(faces_dir)
            print(f"Created {faces_dir} directory. Please add face .npy files there.")
            return
            
        for filename in os.listdir(faces_dir):
            if filename.endswith(".npy"):
                name = os.path.splitext(filename)[0]
                encoding_path = os.path.join(faces_dir, filename)
                
                try:
                    encoding = np.load(encoding_path)
                    if encoding.shape == (128,):
                        self.known_face_encodings.append(encoding)
                        self.known_face_names.append(name)
                        print(f"Loaded encoding for: {name}")
                    else:
                        print(f"Invalid encoding shape in {filename}")
                except Exception as e:
                    print(f"Error loading {filename}: {e}")
                    
        print(f"Loaded {len(self.known_face_names)} known faces")
    
    def find_macbook_camera(self):
        """Find the MacBook's built-in camera, avoiding Continuity Camera"""
        camera_indices = [0, 1, 2, 3]
        for i in camera_indices:
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                ret, frame = cap.read()
                if ret and frame is not None:
                    height, width = frame.shape[:2]
                    if 480 <= width <= 1920 and 360 <= height <= 1080:
                        print(f"Using MacBook camera at index {i} (resolution: {width}x{height})")
                        cap.release()
                        return i
                cap.release()
        for i in camera_indices:
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                ret, frame = cap.read()
                if ret:
                    print(f"Using fallback camera at index {i}")
                    cap.release()
                    return i
                cap.release()
        return None
    
    def detect_and_recognize_faces(self, frame):
        """Detect and recognize faces in the frame"""
        # Convert BGR to RGB
        rgb_frame = frame[:, :, ::-1]
        
        if self.process_this_frame:
            # Detect faces
            self.face_locations = face_recognition.face_locations(rgb_frame, model="hog")
            
            # Get face encodings one by one to avoid compatibility issues
            self.face_encodings = face_recognition.face_encodings(rgb_frame, self.face_locations)
            
            self.face_names = []
            for face_encoding in self.face_encodings:
                name = "Unknown"
                best_dist = 1.0
                for known_encoding, known_name in zip(self.known_face_encodings, self.known_face_names):
                    dist = np.linalg.norm(face_encoding - known_encoding)
                    if dist < 0.5 and dist < best_dist:
                        best_dist = dist
                        name = known_name
                self.face_names.append(name)
        
        self.process_this_frame = not self.process_this_frame
        
        return self.face_locations, self.face_names
    
    def draw_results(self, frame, face_locations, face_names):
        """Draw bounding boxes and names on the frame"""
        for (top, right, bottom, left), name in zip(face_locations, face_names):
            # Draw rectangle around face
            color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)
            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            
            # Draw label below face
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), color, cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, name, (left + 6, bottom - 6), font, 0.6, (255, 255, 255), 1)
            
        return frame
    
    def run(self):
        """Main application loop"""
        # Find MacBook Pro camera
        camera_index = self.find_macbook_camera()
        if camera_index is None:
            print("Error: Could not find a working MacBook camera.")
            print("Please disconnect any iPhone or external cameras and try again.")
            return
            
        video_capture = cv2.VideoCapture(camera_index)
        
        # Set camera properties for better performance
        video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        video_capture.set(cv2.CAP_PROP_FPS, 30)
        
        if not video_capture.isOpened():
            print("Error: Could not open video capture device")
            return
            
        print("Face Recognition App Started")
        print("Press 'q' to quit, 's' to save current frame")
        print(f"Looking for {len(self.known_face_names)} known faces: {', '.join(self.known_face_names)}")
        
        frame_count = 0
        while True:
            ret, frame = video_capture.read()
            if not ret:
                print("Error: Could not read frame")
                break
            
            # Process every other frame for better performance
            frame_count += 1
            if frame_count % 2 == 0:
                continue
                
            # Recognize faces
            face_locations, face_names = self.detect_and_recognize_faces(frame)
            
            # Draw results
            frame = self.draw_results(frame, face_locations, face_names)
            
            # Add status text
            status_text = f"Faces: {len(face_locations)} | Known: {sum(1 for name in face_names if name != 'Unknown')}"
            cv2.putText(frame, status_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            # Display frame
            cv2.imshow('Face Recognition', frame)
            
            # Handle key presses
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s'):
                # Save current frame
                timestamp = int(time.time())
                filename = f"captured_frame_{timestamp}.jpg"
                cv2.imwrite(filename, frame)
                print(f"Saved frame as {filename}")
                
        video_capture.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    app = FaceRecognitionApp()
    app.run()