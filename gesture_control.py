import cv2 as cv
import numpy as np
import time
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# ============================================================================
# MEDIAPIPE SETUP
# ============================================================================

base_options = python.BaseOptions(model_asset_path='hand_landmarker.task')
options = vision.HandLandmarkerOptions(base_options=base_options, num_hands=1)
detector = vision.HandLandmarker.create_from_options(options)

mp_hands = mp.tasks.vision.HandLandmarksConnections
mp_drawing = mp.tasks.vision.drawing_utils
mp_drawing_styles = mp.tasks.vision.drawing_styles

# ============================================================================
# GESTURE PARAMETERS
# ============================================================================

# Landmark indices (MediaPipe hand landmarks)
WRIST = 0
THUMB_TIP = 4
INDEX_TIP = 8
MIDDLE_TIP = 12
RING_TIP = 16
PINKY_TIP = 20

# Thresholds for gesture detection
HAND_X_LEFT_THRESHOLD = 0.35      # Left side of screen
HAND_X_RIGHT_THRESHOLD = 0.65     # Right side of screen
HAND_X_CENTER_MIN = 0.35
HAND_X_CENTER_MAX = 0.65

# Gesture cooldown (prevent spam)
GESTURE_COOLDOWN = 0.3  # seconds

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def calculate_distance(point1, point2):
    """Calculate Euclidean distance between two points"""
    return np.sqrt((point1.x - point2.x) ** 2 + (point1.y - point2.y) ** 2)


def is_finger_extended(tip, pip, mcp):
    """Check if a finger is extended (tip is above pip)"""
    return tip.y < pip.y


def count_extended_fingers(landmarks):
    """Count how many fingers are extended"""
    extended = 0
    
    # Thumb (different logic - check x position)
    if landmarks[THUMB_TIP].x < landmarks[4 - 1].x:  # 3 is MCP
        extended += 1
    
    # Other fingers (check if tip is above MCP)
    fingers = [(INDEX_TIP, 6), (MIDDLE_TIP, 10), (RING_TIP, 14), (PINKY_TIP, 18)]
    for tip_idx, mcp_idx in fingers:
        if is_finger_extended(landmarks[tip_idx], landmarks[tip_idx - 2], landmarks[mcp_idx]):
            extended += 1
    
    return extended


def is_peace_sign(landmarks):
    """Detect peace/victory sign: index and middle fingers extended, others folded"""
    index_extended = is_finger_extended(landmarks[INDEX_TIP], landmarks[6], landmarks[5])
    middle_extended = is_finger_extended(landmarks[MIDDLE_TIP], landmarks[10], landmarks[9])
    ring_folded = not is_finger_extended(landmarks[RING_TIP], landmarks[14], landmarks[13])
    pinky_folded = not is_finger_extended(landmarks[PINKY_TIP], landmarks[18], landmarks[17])
    
    return index_extended and middle_extended and ring_folded and pinky_folded


def is_fist(landmarks):
    """Detect closed fist: all fingers folded"""
    extended_count = count_extended_fingers(landmarks)
    return extended_count <= 1  # Only thumb might be slightly out


def is_open_palm(landmarks):
    """Detect open palm: all fingers extended"""
    extended_count = count_extended_fingers(landmarks)
    return extended_count >= 4


def get_hand_position(landmarks):
    """Get average x position of hand (0.0 = left, 1.0 = right)"""
    return landmarks[WRIST].x


def get_hand_height_change(landmarks, previous_landmarks):
    """Get vertical movement of wrist (positive = moving down)"""
    if previous_landmarks is None:
        return 0
    return landmarks[WRIST].y - previous_landmarks[WRIST].y


# ============================================================================
# DRAWING FUNCTIONS
# ============================================================================

def draw_landmarks_on_image(rgb_image, detection_result):
    """Draw hand landmarks and skeleton on image"""
    annotated_image = np.copy(rgb_image)
    hand_landmarks_list = detection_result.hand_landmarks
    handedness_list = detection_result.handedness
    height, width, _ = annotated_image.shape
    
    if len(hand_landmarks_list) == 0:
        return annotated_image, None
    
    # Draw for first hand only (we only detect 1 hand)
    hand_landmarks = hand_landmarks_list[0]
    handedness = handedness_list[0]
    
    # Draw hand skeleton
    mp_drawing.draw_landmarks(
        annotated_image, 
        hand_landmarks, 
        mp_hands.HAND_CONNECTIONS,
        mp_drawing_styles.get_default_hand_landmarks_style(),
        mp_drawing_styles.get_default_hand_connections_style()
    )
    
    # Draw hand label
    x_coords = [lm.x for lm in hand_landmarks]
    y_coords = [lm.y for lm in hand_landmarks]
    text_x = int(min(x_coords) * width)
    text_y = int(min(y_coords) * height) - 15
    cv.putText(annotated_image, f"{handedness[0].category_name}", 
               (text_x, text_y), cv.FONT_HERSHEY_DUPLEX, 0.7, (88, 205, 54), 2)
    
    return annotated_image, hand_landmarks


# ============================================================================
# GESTURE DETECTION
# ============================================================================

def gesture_detection(landmarks, previous_landmarks, hand_x, hand_y_delta):
    """
    Detect gestures based on hand position and finger configuration.
    
    Gestures:
    - LEFT: Fist on left side of screen
    - RIGHT: Fist on right side of screen
    - DOWN: Open palm or moving hand downward
    - CW_ROTATE: Peace sign (2 fingers up)
    - CCW_ROTATE: Open palm + moving up (all fingers)
    """
    
    fist = is_fist(landmarks)
    palm = is_open_palm(landmarks)
    peace = is_peace_sign(landmarks)
    
    # Rotation gestures (based on finger configuration, position-independent)
    if peace:
        # Peace sign = clockwise rotation
        return "CW_ROTATE"
    
    if palm and hand_y_delta < -0.03:
        # Open palm moving upward = counter-clockwise rotation
        return "CCW_ROTATE"
    
    # Movement gestures (based on hand position)
    if fist:
        if hand_x < HAND_X_LEFT_THRESHOLD:
            return "LEFT"
        elif hand_x > HAND_X_RIGHT_THRESHOLD:
            return "RIGHT"
    
    # Drop gesture (open palm or quick downward movement)
    if palm and hand_y_delta > 0.025:
        return "DOWN"
    
    return None


# ============================================================================
# WEBCAM & GESTURE CAPTURE
# ============================================================================

cap = cv.VideoCapture(0)
previous_landmarks = None
last_gesture_time = 0


def get_gesture():
    """
    Capture camera frame and detect hand gesture.
    Returns: (gesture_string, annotated_frame)
    """
    global previous_landmarks, last_gesture_time
    
    if not cap.isOpened():
        print("Error: Could not open camera")
        return None, np.zeros((480, 640, 3), dtype=np.uint8)
    
    ret, frame = cap.read()
    if not ret:
        print("Error: Could not read frame")
        return None, np.zeros((480, 640, 3), dtype=np.uint8)
    
    # Flip for selfie view
    frame = cv.flip(frame, 1)
    rgb_frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
    
    # Detect hand landmarks
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
    detection_result = detector.detect(mp_image)
    
    # Draw landmarks
    annotated_image, landmarks = draw_landmarks_on_image(rgb_frame, detection_result)
    
    # If no hand detected, reset and return
    if landmarks is None:
        previous_landmarks = None
        webcam_frame = cv.cvtColor(annotated_image, cv.COLOR_RGB2BGR)
        return None, webcam_frame
    
    # Calculate hand metrics
    hand_x = landmarks[WRIST].x
    hand_y_delta = get_hand_height_change(landmarks, previous_landmarks)
    
    # Detect gesture
    gesture = gesture_detection(landmarks, previous_landmarks, hand_x, hand_y_delta)
    
    # Apply cooldown to prevent rapid firing
    current_time = time.time()
    output_gesture = None
    if gesture and (current_time - last_gesture_time) > GESTURE_COOLDOWN:
        output_gesture = gesture
        last_gesture_time = current_time
        
        # Draw detected gesture on screen
        cv.putText(annotated_image, f"GESTURE: {gesture}", (20, 50),
                   cv.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 2)
    
    # Convert back to BGR for display
    webcam_frame = cv.cvtColor(annotated_image, cv.COLOR_RGB2BGR)
    
    # Update previous landmarks
    previous_landmarks = landmarks
    
    return output_gesture, webcam_frame


def cleanup():
    """Release camera resources"""
    cap.release()