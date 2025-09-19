import cv2

print("Attempting to open camera...")
# We are trying to access the default webcam (index 0)
cap = cv2.VideoCapture(0) 

# Check if the camera opened successfully
if not cap.isOpened():
    print("\n--- FATAL ERROR ---")
    print("Could not open the camera.")
    print("\nTroubleshooting steps:")
    print("1. Make sure your webcam is connected and not being used by another app (Zoom, etc.).")
    print("2. Try changing cv2.VideoCapture(0) to cv2.VideoCapture(1) in the code.")
    exit()

print("\n✅ Camera opened successfully!")
print("A window should appear. Press the 'q' key on your keyboard to close it.")

frame_count = 0
while True:
    # Read a frame from the camera
    ret, frame = cap.read()
    
    # If 'ret' is False, it means we failed to get a frame
    if not ret:
        print(f"--- ERROR on frame {frame_count} ---")
        print("Failed to capture a frame. The camera might have disconnected.")
        break

    frame_count += 1
    
    # Display a frame counter on the video
    text = f'Frame Count: {frame_count}'
    cv2.putText(frame, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    
    # Show the frame in a window
    cv2.imshow('Camera Test | Press Q to Quit', frame)

    # Wait for the 'q' key to be pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

print("\nClosing camera...")
cap.release()
cv2.destroyAllWindows()