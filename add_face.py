import cv2
import os
import face_recognition
import numpy as np

def find_macbook_camera():
    """Find the MacBook's built-in camera, avoiding Continuity Camera"""
    # Try camera indices in order, but prefer index 0 for MacBook Pro
    camera_indices = [0, 1, 2, 3]
    
    for i in camera_indices:
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret and frame is not None:
                # Check if this looks like a MacBook camera (reasonable resolution)
                height, width = frame.shape[:2]
                # MacBook cameras typically have resolutions like 1280x720, 1920x1080
                # Avoid very high resolutions that might be Continuity Camera
                if 480 <= width <= 1920 and 360 <= height <= 1080:
                    print(f"Using MacBook camera at index {i} (resolution: {width}x{height})")
                    cap.release()
                    return i
                cap.release()
            else:
                cap.release()
    
    # Fallback to any working camera
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

def capture_and_average_face(name, num_images=7):
    camera_index = find_macbook_camera()
    if camera_index is None:
        print("Error: Could not find a working MacBook camera.")
        print("Please disconnect any iPhone or external cameras and try again.")
        return False
    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        print("Error: Could not open webcam")
        return False
    
    # Set camera properties to ensure we're using the built-in camera
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    cap.set(cv2.CAP_PROP_FPS, 30)
    
    print(f"Capturing {num_images} face images for: {name}")
    print("Press 'c' to capture, 'q' to quit. Make sure the video window is focused when pressing keys.")
    encodings = []
    captured = 0
    while captured < num_images:
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read frame")
            break
        rgb_frame = frame[:, :, ::-1]
        face_locations = face_recognition.face_locations(rgb_frame)
        for (top, right, bottom, left) in face_locations:
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
        cv2.putText(frame, f"Captured: {captured}/{num_images}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)
        cv2.imshow('Register Face', frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            print("Quitting registration.")
            cap.release()
            cv2.destroyAllWindows()
            return False
        elif key == ord('c'):
            if len(face_locations) == 1:
                # Use the simpler approach - get all encodings from the frame
                try:
                    all_encodings = face_recognition.face_encodings(rgb_frame)
                    if all_encodings:
                        encodings.append(all_encodings[0])
                        captured += 1
                        print(f"Captured image {captured}/{num_images}")
                    else:
                        print("Face detected but encoding failed. Try again.")
                except Exception as e:
                    print(f"Encoding error: {e}. Try again.")
            elif len(face_locations) == 0:
                print("No face detected. Please position your face in the camera.")
            else:
                print("Multiple faces detected. Please ensure only one face is visible.")
    cap.release()
    cv2.destroyAllWindows()
    if encodings:
        avg_encoding = np.mean(encodings, axis=0)
        faces_dir = "faces"
        if not os.path.exists(faces_dir):
            os.makedirs(faces_dir)
        np.save(os.path.join(faces_dir, f"{name}.npy"), avg_encoding)
        print(f"Averaged encoding saved as faces/{name}.npy")
        return True
    else:
        print("No encodings captured.")
        return False

def main():
    print("Face Registration Utility (Averaged)")
    print("=====================================")
    print("Note: This will use your MacBook's built-in camera.")
    print("Please disconnect any iPhone or external cameras if connected.")
    print()
    
    while True:
        name = input("Enter the person's name (or 'quit' to exit): ").strip()
        if name.lower() == 'quit':
            break
        if not name:
            print("Please enter a valid name.")
            continue
        if capture_and_average_face(name):
            print(f"Successfully registered face for {name}")
        else:
            print(f"Failed to register face for {name}")
        another = input("Register another face? (y/n): ").strip().lower()
        if another != 'y':
            break
    print("Face registration complete!")

if __name__ == "__main__":
    main() 