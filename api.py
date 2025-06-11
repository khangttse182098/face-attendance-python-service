from io import BytesIO
from fastapi import FastAPI, Response, UploadFile, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import face_recognition
import numpy as np
import shutil
import os
from database import SessionLocal
from models import DtUser

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change this to specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

KNOWN_FOLDER = "./known_faces"

@app.post("/verify")
async def verify_person(res: Response, name: str = Form(...), file: UploadFile = Form(...)):
    # Save to postgres
    db = SessionLocal()
    user_img: str
    try:    
        record = db.query(DtUser).filter(DtUser.user_name == name).first()

        if record:
            if record.face_img:    
                user_img = record.face_img
            else:
                res.status_code = 400
                return {
                    "message": "User hasn't uploaded reference image"
                }
        else:
            res.status_code = 400
            return {
                "message": "User doesn't exist in database"
            }
    finally:
        db.close()

    # Save the uploaded file temporarily
    # temp_path = f"./temp_upload.jpg"
    # with open(temp_path, "wb") as buffer:
    #     shutil.copyfileobj(file.file, buffer)
    user_img = BytesIO(user_img)

    # Encode uploaded face
    unknown_img = face_recognition.load_image_file(user_img)
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
    isMatch = bool(result[0])

    os.remove(temp_path)

    # Response
    return {
        "matched": isMatch,
        "distance": float(distance)
    }
