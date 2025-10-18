import cv2
import numpy as np
from typing import Optional 
from config_manager import get_config, set_config

def aruco(image) -> Optional[float]:
    image = cv2.imread(image)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    det = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
    parameters = cv2.aruco.DetectorParameters()
    detector = cv2.aruco.ArucoDetector(det, parameters)
    corners, ids, rejected = detector.detectMarkers(gray)

    if ids is None:
        return None
    
    px_size = np.mean([cv2.norm(c[0][0]-c[0][2]) for c in corners])

    cv2.aruco.drawDetectedMarkers(image, corners, ids)
    file_path = "uploads/calibration/aruco.png"
    cv2.imwrite(file_path, image)

    return [float((get_config("REF_ARUCO_MM")/10) / px_size), file_path]
