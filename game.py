import cv2 as cv
import numpy as np
import time

# INITIAL CONSTANTS
h = 20 # height of the game board in cells
w = 16 # width of the game board in cells
unit_size = 25 # cell size in pixels
bg_color = (200, 200, 200) # display background
game_bg_color = (0, 0, 0) # tetris game background
line_color = (255, 0, 0) # grid lines
xi, yi = 2, 2 # initial x, y

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

# BOARD GAME
tetris_display = np.full(((h+4) * unit_size, (w + 4) * unit_size, 3), bg_color, dtype=np.uint8)
cv.rectangle(tetris_display, (2 * unit_size, 2 * unit_size), ((2 + w) * unit_size, (2 + h) * unit_size), game_bg_color, thickness=-1)
for i in range (w + 1):
    cv.line(tetris_display, 
            ((2 + i) * unit_size, 2 * unit_size), 
            ((2 + i) * unit_size, (2 + h) * unit_size), 
            line_color, thickness=1)
for i in range (h + 1):
    cv.line(tetris_display, 
            (2 * unit_size, (2 + i) * unit_size), 
            ((2 + w) * unit_size, (2 + i) * unit_size), 
            line_color, thickness=1)
draw_block(tetrominoes[0], xi, yi, (0, 255, 0)) # draw the first tetromino at the initial position
cv.imshow('Tetris Display', tetris_display)
cv.waitKey(0)
cv.destroyAllWindows()