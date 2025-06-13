from fastapi import FastAPI, Response, UploadFile, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import face_recognition

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
async def verify_person(res: Response, comparedImg: UploadFile = Form(...), refImg: UploadFile = Form(...)):
    # Encode compared image
    compared_img = face_recognition.load_image_file(comparedImg.file)
    compared_encodings = face_recognition.face_encodings(compared_img)

    # Encode reference image
    ref_img = face_recognition.load_image_file(refImg.file)
    ref_encodings = face_recognition.face_encodings(ref_img)

    if not compared_encodings:
        return JSONResponse(status_code=400, content={"detail": "No face detected in compared image."})
    if not ref_encodings: 
        return JSONResponse(status_code=400, content={"detail": "No face detected in reference image."})

    ref_encoding = ref_encodings[0]
    compared_encoding = compared_encodings[0]

    result = face_recognition.compare_faces([ref_encoding], compared_encoding, tolerance=0.5)
    distance = face_recognition.face_distance([ref_encoding], compared_encoding)[0]

    isMatch = bool(result[0])

    # Response
    return {
        "matched": isMatch,
        "distance": float(distance)
    }
