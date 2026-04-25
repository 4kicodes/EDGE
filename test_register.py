import cv2
import base64
import requests

URL = "http://127.0.0.1:5000/register-user"


def capture_images(num_images=5):
    cap = cv2.VideoCapture(0)
    images = []

    print("Press SPACE to capture image. ESC to exit.")

    while len(images) < num_images:
        ret, frame = cap.read()
        if not ret:
            continue

        cv2.imshow("Capture", frame)

        key = cv2.waitKey(1)

        if key == 27:  # ESC
            break
        elif key == 32:  # SPACE
            _, buffer = cv2.imencode('.jpg', frame)
            img_base64 = base64.b64encode(buffer).decode('utf-8')
            images.append(img_base64)
            print(f"Captured {len(images)}/{num_images}")

    cap.release()
    cv2.destroyAllWindows()

    return images


def register():
    name = input("Enter name: ").strip()

    if not name:
        print("Name is required")
        return

    images = capture_images(5)

    if len(images) < 5:
        print("Registration aborted: not enough images")
        return

    payload = {
        "name": name,
        "images": images
    }

    res = requests.post(URL, json=payload)

    try:
        data = res.json()
    except Exception:
        print("Invalid response from server")
        return

    print("\n--- RESPONSE ---")
    print(data)

    if data.get("success"):
        print("\nRegistration successful")
        print("Student ID:", data.get("student_id"))
        print("QR Token:", data.get("qr_token"))
    else:
        print("\nRegistration failed:", data.get("message") or data.get("error"))


if __name__ == "__main__":
    register()