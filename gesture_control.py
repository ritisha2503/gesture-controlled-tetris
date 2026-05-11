import cv2 as cv
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# HAND LANDMARKER SETUP
base_options = python.BaseOptions(model_asset_path='hand_landmarker.task')
options = vision.HandLandmarkerOptions(base_options=base_options, num_hands=2)
detector = vision.HandLandmarker.create_from_options(options)

# MEDIAPIPE DRAWING
mp_hands = mp.tasks.vision.HandLandmarksConnections 
mp_drawing = mp.tasks.vision.drawing_utils 
mp_drawing_styles = mp.tasks.vision.drawing_styles

# TEXT SETTINGS
MARGIN = 10
FONT_SIZE = 0.5
FONT_THICKNESS = 1
HANDEDNESS_TEXT_COLOR = (88, 205, 54)

# LANDMARK NAMES
landmark_names = [
    "WRIST",
    "THUMB_CMC",
    "THUMB_MCP",
    "THUMB_IP",
    "THUMB_TIP",
    "INDEX_FINGER_MCP",
    "INDEX_FINGER_PIP",
    "INDEX_FINGER_DIP",
    "INDEX_FINGER_TIP",
    "MIDDLE_FINGER_MCP",
    "MIDDLE_FINGER_PIP",
    "MIDDLE_FINGER_DIP",
    "MIDDLE_FINGER_TIP",
    "RING_FINGER_MCP",
    "RING_FINGER_PIP",
    "RING_FINGER_DIP",
    "RING_FINGER_TIP",
    "PINKY_MCP",
    "PINKY_PIP",
    "PINKY_DIP",
    "PINKY_TIP"
]

# DRAW FUNCTION
def draw_landmarks_on_image(rgb_image, detection_result):
    annotated_image = np.copy(rgb_image)
    hand_landmarks_list = detection_result.hand_landmarks
    handedness_list = detection_result.handedness
    height, width, _ = annotated_image.shape
    # LOOP THROUGH ALL HANDS
    for idx in range(len(hand_landmarks_list)):
        hand_landmarks = hand_landmarks_list[idx]
        handedness = handedness_list[idx]
        # DRAW CONNECTIONS
        mp_drawing.draw_landmarks(annotated_image, hand_landmarks, mp_hands.HAND_CONNECTIONS, mp_drawing_styles.get_default_hand_landmarks_style(), mp_drawing_styles.get_default_hand_connections_style())
        x_coordinates = [landmark.x for landmark in hand_landmarks]
        y_coordinates = [landmark.y for landmark in hand_landmarks]
        text_x = int(min(x_coordinates) * width)
        text_y = int(min(y_coordinates) * height) - MARGIN
        cv.putText(annotated_image, handedness[0].category_name, (text_x, text_y), cv.FONT_HERSHEY_DUPLEX, FONT_SIZE, HANDEDNESS_TEXT_COLOR, FONT_THICKNESS, cv.LINE_AA)
        # DRAW ALL 21 POINT COORDINATES
        for i, landmark in enumerate(hand_landmarks):
            px = int(landmark.x * width)
            py = int(landmark.y * height)
            cv.circle(annotated_image, (px, py), 4, (0, 255, 255), -1)
            coordinate_text = f"{i}: {landmark_names[i]} : ({px}, {py})"
            cv.putText(annotated_image, coordinate_text, (px + 5, py - 5), cv.FONT_HERSHEY_SIMPLEX, 0.35, (255, 255, 255), 1)
    return annotated_image

# WEBCAM
cap = cv.VideoCapture(0)
if not cap.isOpened():
    print("Error: Could not open camera")
    exit()
while True:
    ret, frame = cap.read()
    if not ret:
        print("Error: Could not read frame")
        break
    frame = cv.flip(frame, 1)
    rgb_frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
    detection_result = detector.detect(mp_image)
    annotated_image = draw_landmarks_on_image(rgb_frame, detection_result)
    cv.imshow('Hand Landmarks', cv.cvtColor(annotated_image, cv.COLOR_RGB2BGR))
    if cv.waitKey(1) == ord('q'):
        break

cap.release()
cv.destroyAllWindows()