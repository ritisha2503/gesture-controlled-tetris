import cv2 as cv
import numpy as np
from board_game import *
from gesture_control import *

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