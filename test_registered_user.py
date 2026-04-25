import cv2
import requests
import base64
import numpy as np

BASE_URL = "http://127.0.0.1:5000"


# -------- QR SCAN --------
def scan_qr():
    cap = cv2.VideoCapture(0)
    detector = cv2.QRCodeDetector()

    print("Scanning QR...")

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        data, bbox, _ = detector.detectAndDecode(frame)

        if data:
            print("QR Detected:", data)
            cap.release()
            cv2.destroyAllWindows()
            return data

        cv2.imshow("Scan QR", frame)

        if cv2.waitKey(1) == 27:
            break

    cap.release()
    cv2.destroyAllWindows()
    return None


# -------- VALIDATE QR --------
def validate_qr(qr_token):
    res = requests.post(f"{BASE_URL}/validate-qr", json={"qr_token": qr_token})
    return res.json()


# -------- CAPTURE FACE --------
def capture_face():
    cap = cv2.VideoCapture(0)

    print("Press SPACE to capture face")

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        cv2.imshow("Capture Face", frame)

        key = cv2.waitKey(1)

        if key == 32:  # SPACE
            _, buffer = cv2.imencode(".jpg", frame)
            img_base64 = base64.b64encode(buffer).decode("utf-8")

            cap.release()
            cv2.destroyAllWindows()
            return img_base64

        elif key == 27:
            break

    cap.release()
    cv2.destroyAllWindows()
    return None


# -------- VERIFY USER --------
def verify_user(qr_token, image_base64):
    payload = {
        "qr_token": qr_token,
        "image": image_base64
    }

    res = requests.post(f"{BASE_URL}/verify-user", json=payload)
    return res.json()


# -------- MAIN FLOW --------
def main():
    # Step 1: Scan QR
    qr_token = scan_qr()
    if not qr_token:
        print("QR scan failed")
        return

    # Step 2: Validate QR
    qr_data = validate_qr(qr_token)

    if qr_data.get("status") != "VALID":
        print("Invalid QR")
        return

    print(f"Welcome {qr_data['name']}")

    # Step 3: Capture Face
    image_base64 = capture_face()
    if not image_base64:
        print("Face capture failed")
        return

    # Step 4: Verify
    result = verify_user(qr_token, image_base64)

    print("\n--- FINAL RESULT ---")
    print(result)


if __name__ == "__main__":
    main()