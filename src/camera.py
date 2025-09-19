import cv2

def open_camera():
    cap = cv2.VideoCapture(0)  # 0 = default webcam
    if not cap.isOpened():
        raise Exception("❌ Cannot open camera")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("❌ Failed to grab frame")
            break

        cv2.imshow("Camera Preview - Press Q to exit", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    open_camera()
