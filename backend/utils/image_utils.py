import base64
import numpy as np
import cv2


def base64_to_image(base64_string: str):
    try:
        # Remove metadata if present (data:image/...;base64,)
        if "," in base64_string:
            base64_string = base64_string.split(",")[1]

        image_bytes = base64.b64decode(base64_string)
        np_arr = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        return image
    except Exception as e:
        print("Error decoding image:", str(e))
        return None