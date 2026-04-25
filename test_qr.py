import requests
import base64
import cv2
import numpy as np

BASE_URL = "http://127.0.0.1:5000"


def get_qr(student_id):
    url = f"{BASE_URL}/generate-qr?student_id={student_id}"

    res = requests.get(url)

    if res.status_code != 200:
        print("Error:", res.json())
        return None

    data = res.json()
    return data


def display_and_save_qr(qr_base64, student_id):
    # Decode base64 → image
    qr_bytes = base64.b64decode(qr_base64)
    np_arr = np.frombuffer(qr_bytes, np.uint8)
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    if img is None:
        print("Failed to decode QR image")
        return

    # Save
    filename = f"qr_{student_id}.png"
    cv2.imwrite(filename, img)
    print(f"QR saved as {filename}")

    # Display
    cv2.imshow("QR Code", img)
    print("Press any key to close QR window...")
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def main():
    student_id = input("Enter student_id: ").strip()

    data = get_qr(student_id)

    if not data:
        return

    print("\n--- QR DATA ---")
    print("Student ID:", data["student_id"])
    print("QR Token:", data["qr_token"])

    display_and_save_qr(data["qr_image_base64"], student_id)


if __name__ == "__main__":
    main()