import cv2 as cv
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

'''
# INITIAL CONSTANTS
h = 20 # height of the game board in cells
w = 16 # width of the game board in cells
unit_size = 25 # cell size in pixels
bg_color = (200, 200, 200) # display background
game_bg_color = (0, 0, 0) # tetris game background
line_color = (255, 0, 0) # grid lines
x_offset, y_offset = 2, 2 # initial x, y of start of grid

# MAIN GAME MARIX
board_matrix = np.zeros((h, w), dtype=int)

# TETROMINOES
tetrominoes =   [np.array([[1, 1, 1, 1]]), 
                np.array([[1, 1], [1, 1]]), 
                np.array([[0, 1, 0], [1, 1, 1]]),
                np.array([[1, 0, 0], [1, 1, 1]]),
                np.array([[0, 0, 1], [1, 1, 1]]),
                np.array([[1, 1, 0], [0, 1, 1]]),
                np.array([[0, 1, 1], [1, 1, 0]])
                ]
block_colors = [
    (0, 255, 255),    # yellow
    (255, 0, 0),      # blue
    (0, 255, 0),      # green
    (0, 0, 255),      # red
    (255, 0, 255),    # purple
    (255, 255, 0),    # cyan
    (0, 165, 255)     # orange
]

# BOARD GAME

def display_board():
    global tetris_display
    tetris_display = np.full(((h + 2 * y_offset) * unit_size, (w + 2 * x_offset) * unit_size, 3), bg_color, dtype=np.uint8)
    cv.rectangle(tetris_display, (x_offset * unit_size, y_offset * unit_size), ((x_offset + w) * unit_size, (y_offset + h) * unit_size), game_bg_color, thickness=-1)

def draw_grid():
    for i in range (w + 1):
        cv.line(tetris_display, 
                ((x_offset + i) * unit_size, y_offset * unit_size), 
                ((x_offset + i) * unit_size, (y_offset + h) * unit_size), 
                line_color, thickness=1)
    for i in range (h + 1):
        cv.line(tetris_display, 
                (x_offset * unit_size, (y_offset + i) * unit_size), 
                ((x_offset + w) * unit_size, (y_offset + i) * unit_size), 
                line_color, thickness=1)

def draw_board_matrix(): # draw board matrix
    for row in range(h):
        for col in range(w):
            if board_matrix[row, col] != 0:
                top_left = ((x_offset + col) * unit_size, (y_offset + row) * unit_size)
                bottom_right = ((x_offset + col + 1) * unit_size, (y_offset + row + 1) * unit_size)
                color = block_colors[board_matrix[row, col] - 1]
                cv.rectangle(tetris_display, top_left, bottom_right, color, -1)

def draw_tetromino(tetromino, x, y, color_index): # draw current falling block
    for row in range(tetromino.shape[0]):
        for col in range(tetromino.shape[1]):
            if tetromino[row, col] == 1:
                top_left = ((x_offset + x + col) * unit_size, (y_offset + y + row) * unit_size)
                bottom_right = ((x_offset + x + col + 1) * unit_size, (y_offset + y + row + 1) * unit_size)
                cv.rectangle(tetris_display, top_left, bottom_right, block_colors[color_index], -1)

def collision(tetromino, x, y): # collision check
    for row in range(tetromino.shape[0]):
        for col in range(tetromino.shape[1]):
            if tetromino[row, col] == 1:
                board_x = x + col
                board_y = y + row
                if board_x < 0 or board_x >= w:
                    return True
                if board_y >= h:    # bottom collision
                    return True
                if board_matrix[board_y, board_x] != 0:     # block collision
                    return True
    return False

def place_tetromino(tetromino, x, y, color_index): # place tetromino on board
    for row in range(tetromino.shape[0]):
        for col in range(tetromino.shape[1]):
            if tetromino[row, col] == 1:
                board_matrix[y + row, x + col] = color_index + 1

def new_piece(): # random choice of new tetromino
    tetromino = tetrominoes[np.random.randint(len(tetrominoes))]
    x = (w - tetromino.shape[1])// 2
    y = 0
    color_index = np.random.randint(len(block_colors))
    return tetromino, x, y, color_index

'''

# GESTURE CONTROL
base_options = python.BaseOptions(model_asset_path='hand_landmarker.task')
options = vision.HandLandmarkerOptions(base_options=base_options, num_hands=2)
detector = vision.HandLandmarker.create_from_options(options)

mp_hands = mp.tasks.vision.HandLandmarksConnections 
mp_drawing = mp.tasks.vision.drawing_utils 
mp_drawing_styles = mp.tasks.vision.drawing_styles

MARGIN = 10
FONT_SIZE = 0.5
FONT_THICKNESS = 1
HANDEDNESS_TEXT_COLOR = (88, 205, 54)

def draw_landmarks_on_image(rgb_image, detection_result):
    annotated_image = np.copy(rgb_image)
    hand_landmarks_list = detection_result.hand_landmarks
    handedness_list = detection_result.handedness
    height, width, _ = annotated_image.shape
    for idx in range(len(hand_landmarks_list)):
        hand_landmarks = hand_landmarks_list[idx]
        handedness = handedness_list[idx]
        mp_drawing.draw_landmarks(annotated_image, hand_landmarks, mp_hands.HAND_CONNECTIONS, mp_drawing_styles.get_default_hand_landmarks_style(), mp_drawing_styles.get_default_hand_connections_style())
        x_coordinates = [landmark.x for landmark in hand_landmarks]
        y_coordinates = [landmark.y for landmark in hand_landmarks]
        text_x = int(min(x_coordinates) * width)
        text_y = int(min(y_coordinates) * height) - MARGIN
        cv.putText(annotated_image, handedness[0].category_name, (text_x, text_y), cv.FONT_HERSHEY_DUPLEX, FONT_SIZE, HANDEDNESS_TEXT_COLOR, FONT_THICKNESS, cv.LINE_AA)
        for i, landmark in enumerate(hand_landmarks):
            px = int(landmark.x * width)
            py = int(landmark.y * height)
            cv.circle(annotated_image, (px, py), 4, (0, 255, 255), -1)
            coordinate_text = f"{i}: ({px}, {py})"
            cv.putText(annotated_image, coordinate_text, (px + 5, py - 5), cv.FONT_HERSHEY_SIMPLEX, 0.35, (255, 255, 255), 1)
    return annotated_image

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

'''
tetromino, x, y, color_index = new_piece()

# MAIN GAME LOOP
while True:

    display_board()
    draw_board_matrix()
    draw_tetromino(tetromino, x, y, color_index)
    draw_grid()
    cv.imshow('Tetris Display', tetris_display)

    key = cv.waitKeyEx(1000)
    if key == 2424832: # left
        if not collision(tetromino, x - 1, y):
            x -= 1
    elif key == 2555904: # right
        if not collision(tetromino, x + 1, y):
            x += 1
    elif key == 2490368: # up (rotate)
        rotated = np.rot90(tetromino, -1)
        if not collision(rotated, x, y):
            tetromino = rotated
    elif key == 2621440: # down
        if not collision(tetromino, x, y + 1):
            y += 1
    
    if not collision(tetromino, x, y + 1): # automatic fall
        y += 1
    else:
        place_tetromino(tetromino, x, y, color_index) # lock piece
        tetromino, x, y, color_index = new_piece() # continue with next piece

# cv.destroyAllWindows()
'''