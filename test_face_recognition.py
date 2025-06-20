import face_recognition
import os
import numpy as np

def test_face_recognition():
    """Test face recognition functionality"""
    print("Testing Face Recognition System")
    print("=" * 40)
    
    # Check if faces directory exists and has images
    faces_dir = "faces"
    if not os.path.exists(faces_dir):
        print(f"❌ {faces_dir} directory not found")
        return False
    
    face_files = [f for f in os.listdir(faces_dir) if f.endswith(('.jpg', '.jpeg', '.png'))]
    
    if not face_files:
        print(f"❌ No face images found in {faces_dir} directory")
        return False
    
    print(f"✅ Found {len(face_files)} face images")
    
    # Test loading faces
    known_face_encodings = []
    known_face_names = []
    
    for filename in face_files:
        name = os.path.splitext(filename)[0]
        image_path = os.path.join(faces_dir, filename)
        
        try:
            image = face_recognition.load_image_file(image_path)
            encodings = face_recognition.face_encodings(image)
            
            if encodings:
                encoding = encodings[0]
                known_face_encodings.append(encoding)
                known_face_names.append(name)
                print(f"✅ Loaded face: {name}")
            else:
                print(f"❌ No face detected in {filename}")
                
        except Exception as e:
            print(f"❌ Error loading {filename}: {e}")
    
    if not known_face_encodings:
        print("❌ No valid faces loaded")
        return False
    
    print(f"\n✅ Successfully loaded {len(known_face_names)} faces")
    print(f"Known faces: {', '.join(known_face_names)}")
    
    # Test face comparison
    if len(known_face_encodings) > 1:
        print("\nTesting face comparison...")
        # Compare first face with others
        test_encoding = known_face_encodings[0]
        test_name = known_face_names[0]
        
        for i, encoding in enumerate(known_face_encodings[1:], 1):
            match = face_recognition.compare_faces([test_encoding], encoding, tolerance=0.6)[0]
            other_name = known_face_names[i]
            print(f"Comparing {test_name} with {other_name}: {'✅ Match' if match else '❌ No match'}")
    
    print("\n🎉 Face recognition system is working correctly!")
    print("\nTo use the camera app:")
    print("1. Grant camera permissions in System Preferences > Security & Privacy > Camera")
    print("2. Run: python face_recognition_app.py")
    
    return True

if __name__ == "__main__":
    test_face_recognition() 