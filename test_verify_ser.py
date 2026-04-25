import cv2
import base64
import requests

URL = "http://127.0.0.1:5000/verify-user"

QR_TOKEN = "f1c004b5-0664-48e1-b017-d6fa423d214b"


def capture_image():
    cap = cv2.VideoCapture(0)

    print("Press SPACE to capture image")

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        cv2.imshow("Verify", frame)

        key = cv2.waitKey(1)

        if key == 32:  # SPACE
            _, buffer = cv2.imencode('.jpg', frame)
            img_base64 = base64.b64encode(buffer).decode('utf-8')
            break

    cap.release()
    cv2.destroyAllWindows()

    return img_base64


def verify():
    image = capture_image()

    payload = {
        "qr_token": QR_TOKEN,
        "image": image
    }

    res = requests.post(URL, json=payload)

    print("\n--- VERIFY RESPONSE ---")
    print(res.json())


if __name__ == "__main__":
    verify()