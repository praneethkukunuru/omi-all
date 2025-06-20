import face_recognition
import os
import numpy as np

def test_face_loading():
    """Test if saved faces are being loaded correctly"""
    print("Testing Face Loading")
    print("=" * 30)
    
    faces_dir = "faces"
    if not os.path.exists(faces_dir):
        print(f"❌ {faces_dir} directory not found")
        return False
    
    face_files = [f for f in os.listdir(faces_dir) if f.endswith(('.jpg', '.jpeg', '.png'))]
    
    if not face_files:
        print(f"❌ No face images found in {faces_dir}")
        return False
    
    print(f"Found {len(face_files)} face images")
    
    for filename in face_files:
        name = os.path.splitext(filename)[0]
        image_path = os.path.join(faces_dir, filename)
        
        print(f"\nTesting: {filename}")
        
        try:
            # Load image
            image = face_recognition.load_image_file(image_path)
            print(f"  ✅ Image loaded successfully (shape: {image.shape})")
            
            # Detect faces
            face_locations = face_recognition.face_locations(image)
            print(f"  ✅ Face detection: {len(face_locations)} faces found")
            
            if len(face_locations) == 0:
                print(f"  ❌ No face detected in {filename}")
                continue
            
            # Get face encodings
            face_encodings = face_recognition.face_encodings(image, face_locations)
            print(f"  ✅ Face encoding: {len(face_encodings)} encodings created")
            
            if len(face_encodings) > 0:
                encoding = face_encodings[0]
                print(f"  ✅ Encoding shape: {encoding.shape}")
                print(f"  ✅ Encoding range: {encoding.min():.3f} to {encoding.max():.3f}")
                
                # Test self-comparison
                matches = face_recognition.compare_faces([encoding], encoding, tolerance=0.5)
                if matches[0]:
                    print(f"  ✅ Self-comparison test passed")
                else:
                    print(f"  ❌ Self-comparison test failed")
                    
            else:
                print(f"  ❌ Failed to create face encoding")
                
        except Exception as e:
            print(f"  ❌ Error processing {filename}: {e}")
    
    return True

if __name__ == "__main__":
    test_face_loading() 