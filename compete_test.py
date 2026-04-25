import cv2
import base64
import requests
import numpy as np

BASE_URL = "http://127.0.0.1:5000"


# ---------------- IMAGE CAPTURE ----------------
def capture_images(n=5):
    cap = cv2.VideoCapture(0)
    images = []

    print(f"\nCapture {n} images (SPACE to capture)")

    while len(images) < n:
        ret, frame = cap.read()
        if not ret:
            continue

        cv2.imshow("Capture", frame)
        key = cv2.waitKey(1)

        if key == 32:
            _, buffer = cv2.imencode('.jpg', frame)
            images.append(base64.b64encode(buffer).decode('utf-8'))
            print(f"Captured {len(images)}/{n}")

        elif key == 27:
            break

    cap.release()
    cv2.destroyAllWindows()
    return images


def capture_single():
    cap = cv2.VideoCapture(0)
    print("\nPress SPACE to capture face")

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        cv2.imshow("Capture Face", frame)
        key = cv2.waitKey(1)

        if key == 32:
            _, buffer = cv2.imencode('.jpg', frame)
            cap.release()
            cv2.destroyAllWindows()
            return base64.b64encode(buffer).decode('utf-8')

        elif key == 27:
            break

    cap.release()
    cv2.destroyAllWindows()
    return None


# ---------------- QR DISPLAY ----------------
def display_qr(qr_base64, student_id):
    qr_bytes = base64.b64decode(qr_base64)
    np_arr = np.frombuffer(qr_bytes, np.uint8)
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    filename = f"qr_{student_id}.png"
    cv2.imwrite(filename, img)
    print(f"\n✅ QR saved: {filename}")

    cv2.imshow("User QR", img)
    print("QR will close in 5 seconds...")
    cv2.waitKey(5000)
    cv2.destroyAllWindows()


# ---------------- QR SCANNER ----------------
def scan_qr():
    cap = cv2.VideoCapture(0)
    detector = cv2.QRCodeDetector()

    print("\nScan QR...")

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        data, _, _ = detector.detectAndDecode(frame)

        cv2.imshow("Scan QR", frame)

        if data:
            cap.release()
            cv2.destroyAllWindows()
            print(f"\nQR Detected: {data}")
            return data

        if cv2.waitKey(1) == 27:
            break

    cap.release()
    cv2.destroyAllWindows()
    return None


# ---------------- API CALLS ----------------
def register_user():
    print("\n=== NEW USER REGISTRATION ===")

    name = input("Enter name: ").strip()
    images = capture_images(5)

    res = requests.post(f"{BASE_URL}/register-user", json={
        "name": name,
        "images": images
    })

    data = res.json()
    print("\nRegister Response:", data)

    if not data.get("success"):
        return None

    return data["student_id"], data["qr_token"]


def generate_qr(student_id):
    res = requests.get(f"{BASE_URL}/generate-qr?student_id={student_id}")
    return res.json()


def verify_user(qr_token):
    image = capture_single()

    res = requests.post(f"{BASE_URL}/verify-user", json={
        "qr_token": qr_token,
        "image": image
    })

    data = res.json()
    print("\nVerify Result:", data)
    return data


# ---------------- MAIN ----------------
def main():
    print("""
1 → New User (Register + Auto Verify)
2 → Existing User (Scan QR + Verify)
""")

    choice = input("Select: ").strip()

    # -------- FLOW 1 --------
    if choice == "1":
        result = register_user()
        if not result:
            return

        student_id, qr_token = result

        qr_data = generate_qr(student_id)

        if "qr_image_base64" in qr_data:
            display_qr(qr_data["qr_image_base64"], student_id)

        print("\n➡️ Proceeding to verification...")
        verify_user(qr_token)

    # -------- FLOW 2 --------
    elif choice == "2":
        qr_token = scan_qr()

        if not qr_token:
            print("QR scan failed")
            return

        verify_user(qr_token)

    else:
        print("Invalid choice")


if __name__ == "__main__":
    main()