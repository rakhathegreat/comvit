"""Endpoints that handle image capture, landmarking, and streaming."""

import base64
import os
import uuid
import io

from fastapi import APIRouter, File, UploadFile
from fastapi.responses import JSONResponse, StreamingResponse

from camera import generate_frames, capture
from model.comvistunt import draw_landmarks, get_landmarks, get_height, get_weight, get_haz
from app.core.storage import CAPTURE_IMAGE_PATH, save_upload_file, LANDMARK_DIR, UPLOAD_DIR

from app.service.client import supabase

from config_manager import get_config

router = APIRouter(tags=["Media"])

async def upload_to_supabase(image, filename) -> str:
    client = await supabase()
    if not client:
        raise RuntimeError("Supabase client not ready")

    bucket = "temp"
    response = client.storage.from_(bucket).upload(filename, image, {"content-type": "image/png"})

    if response.path:
        return client.storage.from_(bucket).get_public_url(filename)

    raise RuntimeError("Upload failed – no path returned")

@router.post("/capture")
async def capture_image(gender: str, age: int, ref: str, image: UploadFile = File(...)):
    """Capture image and return the annotated landmark result."""

    try:
        # Read the uploaded image data
        image_data = await image.read()

        # Generate a unique filename for the uploaded image
        # filename = f"{uuid.uuid4()}.png" 
        filename = f"captured.png" 
        
        # Save the image to the server's local directory
        image_path = os.path.join(UPLOAD_DIR, filename)
        with open(image_path, "wb") as f:
            f.write(image_data)

        # Perform landmark detection and calculations
        landmarks = get_landmarks(image_path)
        result_image_path = draw_landmarks(image_path, landmarks, LANDMARK_DIR)
        height = get_height(landmarks, get_config('CM_PER_PX'))
        weight = get_weight(height)
        status = get_haz(height, str(gender), int(age))

        filename = f"{uuid.uuid4()}.png"

        # Upload the image to Supabase and get the public URL
        image_url = await upload_to_supabase("capture/landmark/draw-landmark.png", filename)

        return {
            "status": "success",
            "height": height,
            "weight": weight,
            "status": status,
            "filename": filename,
            "image_url": image_url
        }

    except Exception as exc:  # pragma: no cover - defensive coding
        return JSONResponse(content={"message": str(exc)}, status_code=500)