import cv2 as cv
import numpy as np
import time
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
            coordinate_text = f"{i} : ({px}, {py})"
            cv.putText(annotated_image, coordinate_text, (px + 5, py - 5), cv.FONT_HERSHEY_SIMPLEX, 0.35, (255, 255, 255), 1)
    return annotated_image, x_coordinates, y_coordinates


def gesture_detection(x_coordinates, y_coordinates, previous_x, previous_y):
    dx = x_coordinates[8] - previous_x[8]
    dy = y_coordinates[0] - previous_y[0]
    index_x = x_coordinates[8]
    index_up = y_coordinates[8] < y_coordinates[6]
    middle_up = y_coordinates[12] < y_coordinates[10]
    if index_up and middle_up:
        return "CCW_ROTATE"
    if index_up and not middle_up:
        return "CW_ROTATE"
    if index_x < 0.35:
        return "LEFT" 
    if index_x > 0.65:
        return "RIGHT"
    if dy > 0.015:
        return "DOWN"
    return None

# WEBCAM
cap = cv.VideoCapture(0)

previous_x, previous_y = [0] * 21, [0] * 21

last_gesture_time = 0
cooldown = 0.5

def get_gesture():
    global previous_x, previous_y, last_gesture_time

    if not cap.isOpened():
        print("Error: Could not open camera")
        return None, np.zeros((480, 640, 3), dtype=np.uint8)
    ret, frame = cap.read()
    if not ret:
        print("Error: Could not read frame")
        return None, np.zeros((480, 640, 3), dtype=np.uint8),  np.zeros((480, 640, 3), dtype=np.uint8)
    frame = cv.flip(frame, 1)
    rgb_frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
    detection_result = detector.detect(mp_image)
    if len(detection_result.hand_landmarks) == 0:
        previous_x[:], previous_y[:] = [0] * 21,  [0] * 21
        return None, cv.cvtColor(rgb_frame, cv.COLOR_RGB2BGR)
    annotated_image, x_coordinates, y_coordinates = draw_landmarks_on_image(rgb_frame, detection_result)
    gesture = gesture_detection(x_coordinates, y_coordinates, previous_x, previous_y)
    current_time = time.time()
    output_gesture = None
    if gesture and (current_time - last_gesture_time) > cooldown:
        output_gesture = gesture
        last_gesture_time = current_time
    webcam_frame = cv.cvtColor(annotated_image, cv.COLOR_RGB2BGR)
    cv.waitKey(1)
    previous_x, previous_y = x_coordinates.copy(), y_coordinates.copy()
    return output_gesture, webcam_frame

def cleanup():
    cap.release()