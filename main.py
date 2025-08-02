from fastapi import FastAPI, Response, UploadFile, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import face_recognition
import numpy as np
import cv2
import time

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def load_and_resize_image(file, scale=0.25):
    file_bytes = np.frombuffer(file.read(), np.uint8)
    image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
    small_image = cv2.resize(image, (0, 0), fx=scale, fy=scale)
    return image, small_image

@app.post("/check-multiple-face")
async def check_multiple_face(res: Response, img: UploadFile = Form(...)): 
    _, img_small = load_and_resize_image(img.file)
    img_locations = face_recognition.face_locations(img_small)
    if not img_locations:
        return JSONResponse(status_code=400, content={"error": "Không phát hiện khuôn mặt trong hình"})
    
    scale = 4  # since 0.25 used above
    img_locations = [(top*scale, right*scale, bottom*scale, left*scale) for (top, right, bottom, left) in img_locations] 

    if len(img_locations) > 1:
        return JSONResponse(status_code=400, content={"error": "Phát hiện nhiều hơn một khuôn mặt"})

@app.post("/verify")
async def verify_person(res: Response, comparedImg: UploadFile = Form(...), refImg: UploadFile = Form(...)):
    start_time = time.time()

    # Load and resize images
    ref_full, ref_small = load_and_resize_image(refImg.file)
    comp_full, comp_small = load_and_resize_image(comparedImg.file)

    # Get face locations on small images, scale back to original
    ref_locations = face_recognition.face_locations(ref_small)
    comp_locations = face_recognition.face_locations(comp_small)

    # throw error if multiple face detect
    if len(comp_locations) > 1: 
        return JSONResponse(status_code=400, content={"error": "Phát hiện nhiều hơn một khuôn mặt"})

    if not comp_locations:
        return JSONResponse(status_code=400, content={"error": "Không phát hiện khuôn mặt trong hình"})
    if not ref_locations:
        return JSONResponse(status_code=400, content={"error": "Không phát hiện khuôn mặt trong hình"})

    # Scale up face locations
    scale = 4  # since 0.25 used above
    ref_locations = [(top*scale, right*scale, bottom*scale, left*scale) for (top, right, bottom, left) in ref_locations]
    comp_locations = [(top*scale, right*scale, bottom*scale, left*scale) for (top, right, bottom, left) in comp_locations]

    # Encode faces using original resolution
    ref_encoding = face_recognition.face_encodings(ref_full, known_face_locations=[ref_locations[0]])[0]
    comp_encoding = face_recognition.face_encodings(comp_full, known_face_locations=[comp_locations[0]])[0]

    # Compare
    result = face_recognition.compare_faces([ref_encoding], comp_encoding, tolerance=0.5)
    distance = face_recognition.face_distance([ref_encoding], comp_encoding)[0]

    duration = round(time.time() - start_time, 3)

    if not bool(result[0]):
        return JSONResponse(status_code=400, content={"error": "Khuôn mặt không trùng khớp",
                                                      "matched": bool(result[0]),
                                                      "distance": float(distance), 
                                                      "processing_time_seconds": duration})

    return {
        "matched": bool(result[0]),
        "distance": float(distance),
        "processing_time_seconds": duration
    }
