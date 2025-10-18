"""Endpoints related to camera calibration steps."""

from fastapi import APIRouter, File, UploadFile
from fastapi.responses import JSONResponse

from camera import capture
import cv2
import numpy as np

from calibration import aruco
from config_manager import set_config, get_config
from app.core.storage import CAPTURE_IMAGE_PATH, GREEN_MAT_IMAGE_PATH, save_upload_file

router = APIRouter(prefix="/calibrate", tags=["Calibration"])


@router.post("/aruco")
async def calibrate_aruco(image: UploadFile = File(...)):
    try:
        image_data = await image.read()
        np_array = np.frombuffer(image_data, np.uint8)
        image = cv2.imdecode(np_array, cv2.IMREAD_COLOR)

        if image is None:
            raise ValueError("Failed to decode the image.")
        
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        det = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
        parameters = cv2.aruco.DetectorParameters()
        detector = cv2.aruco.ArucoDetector(det, parameters)
        corners, ids, rejected = detector.detectMarkers(gray)

        if ids is None or len(ids) == 0:
            return JSONResponse(
                status_code=404,
                content={
                    "status": "failed",
                    "message": "Calibration Failed. Marker not detected.",
                },
            )

        px_size = np.mean([cv2.norm(c[0][0] - c[0][2]) for c in corners])
        result = float((get_config("REF_ARUCO_MM") / 10) / px_size)

        set_config("CM_PER_PX", result)

        return {
            "status": "success",
            "message": "Calibration Success.",
            "result": result,
        }

    except Exception as exc:
        return JSONResponse(content={"message": str(exc)}, status_code=500)
