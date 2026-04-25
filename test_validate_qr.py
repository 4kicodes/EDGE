import cv2
import requests

URL = "http://127.0.0.1:5000/validate-qr"


def scan_qr():
    cap = cv2.VideoCapture(0)
    detector = cv2.QRCodeDetector()

    print("Scanning QR... Press ESC to exit")

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        data, bbox, _ = detector.detectAndDecode(frame)

        if bbox is not None:
            # Draw box around QR
            for i in range(len(bbox)):
                pt1 = tuple(map(int, bbox[i][0]))
                pt2 = tuple(map(int, bbox[(i + 1) % len(bbox)][0]))
                cv2.line(frame, pt1, pt2, (0, 255, 0), 2)

        if data:
            print("\nQR Detected:", data)
            cap.release()
            cv2.destroyAllWindows()
            return data

        cv2.imshow("QR Scanner", frame)

        if cv2.waitKey(1) == 27:  # ESC
            break

    cap.release()
    cv2.destroyAllWindows()
    return None


def validate_qr(qr_token):
    res = requests.post(URL, json={"qr_token": qr_token})

    print("\n--- RESPONSE ---")
    print(res.json())


def main():
    qr_token = scan_qr()

    if not qr_token:
        print("No QR detected")
        return

    validate_qr(qr_token)


if __name__ == "__main__":
    main()