from fastapi import FastAPI, UploadFile, Form
from fastapi.responses import JSONResponse
import face_recognition
import numpy as np
import shutil
import os

app = FastAPI()

KNOWN_FOLDER = "./known_faces"

@app.post("/verify")
async def verify_person(name: str = Form(...), file: UploadFile = Form(...)):
    # Save the uploaded file temporarily
    temp_path = f"./temp_upload.jpg"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Encode uploaded face
    unknown_img = face_recognition.load_image_file(temp_path)
    unknown_encodings = face_recognition.face_encodings(unknown_img)

    if not unknown_encodings:
        return JSONResponse(status_code=400, content={"detail": "No face detected in uploaded image."})

    unknown_encoding = unknown_encodings[0]

    # Load known images for that name
    person_folder = os.path.join(KNOWN_FOLDER, name)
    print(f"person folder: {person_folder}")
    if not os.path.exists(person_folder):
        return JSONResponse(status_code=404, content={"detail": "Person not found in DB."})

    known_encodings = []
    for filename in os.listdir(person_folder):
        path = os.path.join(person_folder, filename)
        print(f"path: {path}")
        image = face_recognition.load_image_file(path)
        encs = face_recognition.face_encodings(image)
        if encs:
            known_encodings.append(encs[0])

    if not known_encodings:
        return JSONResponse(status_code=500, content={"detail": "No valid face encodings for this person."})

    # Average encoding
    avg_encoding = np.mean(known_encodings, axis=0)

    # Compare
    result = face_recognition.compare_faces([avg_encoding], unknown_encoding, tolerance=0.5)
    distance = face_recognition.face_distance([avg_encoding], unknown_encoding)[0]

    os.remove(temp_path)

    return {
        "matched": bool(result[0]),
        "distance": float(distance)
    }
