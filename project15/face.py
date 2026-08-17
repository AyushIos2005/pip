import cv2

# Load the Haar Cascade for face detection
face_cap = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

# Open webcam
video = cv2.VideoCapture(0)

while True:
    ret, frame = video.read()

    if not ret:
        print("Failed to access webcam.")
        break

    # Convert frame to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect faces
    faces = face_cap.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(40, 40)
    )

    # Draw rectangles around faces
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

    # Show the frame
    cv2.imshow("Face Detection", frame)

    # Press 'v' to quit
    if cv2.waitKey(1) & 0xFF == ord('v'):
        break

# Release resources
video.release()
cv2.destroyAllWindows()