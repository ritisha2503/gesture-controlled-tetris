import cv2 as cv
import numpy as np
import time

# INITIAL CONSTANTS
h = 20
w = 16
unit_size = 25
bg_color = (200, 200, 200)
game_bg_color = (0, 0, 0)
line_color = (255, 0, 0)

# TETROMINO SHAPES
tetrominoes = [np.array([[1, 1, 1, 1]]), 
np.array([[1, 1], [1, 1]]), 
np.array([[0, 1, 0], [1, 1, 1]]),
np.array([[1, 0, 0], [1, 1, 1]]),
np.array([[0, 0, 1], [1, 1, 1]]),
np.array([[1, 1, 0], [0, 1, 1]]),
np.array([[0, 1, 1], [1, 1, 0]])]

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

cv.imshow('Tetris Display', tetris_display)
cv.waitKey(0)
cv.destroyAllWindows()