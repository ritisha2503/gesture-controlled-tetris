import cv2 as cv
import numpy as np
import time
import keyboard

# INITIAL CONSTANTS
h = 20 # height of the game board in cells
w = 16 # width of the game board in cells
unit_size = 25 # cell size in pixels
bg_color = (200, 200, 200) # display background
game_bg_color = (0, 0, 0) # tetris game background
line_color = (255, 0, 0) # grid lines
x_offset, y_offset = 2, 2 # initial x, y of start of grid
board_matrix = np.zeros((h, w), dtype=int) # game board matrix

# TETROMINO SHAPES
tetrominoes =   [np.array([[1, 1, 1, 1]]), 
                np.array([[1, 1], [1, 1]]), 
                np.array([[0, 1, 0], [1, 1, 1]]),
                np.array([[1, 0, 0], [1, 1, 1]]),
                np.array([[0, 0, 1], [1, 1, 1]]),
                np.array([[1, 1, 0], [0, 1, 1]]),
                np.array([[0, 1, 1], [1, 1, 0]])
                ]


# GAME FUNCTIONS
def rotate(tetromino, clockwise=True):
    if clockwise:
        return np.rot90(tetromino, -1)
    else:
        return np.rot90(tetromino, 1)

def draw_block(tetromino, start_x, start_y, color):
    for row in range(tetromino.shape[0]):
        for col in range(tetromino.shape[1]):
            if tetromino[row, col] == 1:
                top_left = ((start_x + col) * unit_size, (start_y + row) * unit_size)
                bottom_right = ((start_x + col + 1) * unit_size, (start_y + row + 1) * unit_size)
                cv.rectangle(tetris_display, top_left, bottom_right, color, thickness=-1)


# KEYBOARD CONTROLS
def on_press(event):
    if event.name == 'left':
        print("Left arrow pressed")
    elif event.name == 'right':
        print("Right arrow pressed")
    elif event.name == 'up':
        print("Up arrow pressed")
    elif event.name == 'down':
        print("Down arrow pressed")
keyboard.on_press(on_press)

# BOARD GAME
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

choice = np.random.randint(0, len(tetrominoes)) # random tetromino

xi = np.random.randint(x_offset, x_offset + w - tetrominoes[choice].shape[1] + 1) # random x position for the tetromino
yi = y_offset # start at the top of the board

for i in range (h - tetrominoes[choice].shape[0]):
    draw_block(tetrominoes[choice], xi, yi + i, (0, 255, 0))
    draw_grid()
    cv.imshow('Tetris Display', tetris_display)
    cv.waitKey(2000)
    keyboard.on_press(on_press)
    draw_block(tetrominoes[choice], xi, yi + i, (0, 0, 0))

