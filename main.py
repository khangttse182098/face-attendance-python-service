import face_recognition

ref_img = face_recognition.load_image_file("ref.jpg")
compare_img = face_recognition.load_image_file("compare.jpg")

ref_encoding = face_recognition.face_encodings(ref_img)[0]
compare_encoding = face_recognition.face_encodings(compare_img)[0]

results = face_recognition.face_distance([ref_encoding], compare_encoding)
print(f"face distance: {results}")

if results < 0.5:
    print("✅ It's a match!")
else:
    print("❌ Not the same person.")