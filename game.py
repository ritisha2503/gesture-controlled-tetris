import cv2 as cv
import numpy as np
from board_game import *
from gesture_control import get_gesture
import time

tetromino, x, y, color_index = new_piece()

fall_time = time.time()
fall_speed = 0.5 # seconds per cell fall

# MAIN GAME LOOP
while True:

    tetris_display = display_board()
    draw_board_matrix()
    draw_tetromino(tetromino, x, y, color_index)
    draw_grid()
    cv.imshow('Tetris Display', tetris_display)

    gesture = get_gesture()
    if gesture:
        print(gesture)
    if gesture == "LEFT":
        if not collision(tetromino, x - 1, y):
            x -= 1
    elif gesture == "RIGHT":
        if not collision(tetromino, x + 1, y):
            x += 1
    elif gesture == "CW_ROTATE": # clockwise rotate
        rotated = np.rot90(tetromino, -1)
        if not collision(rotated, x, y):
            tetromino = rotated
    elif gesture == "CCW_ROTATE": # counterclockwise rotate
        rotated = np.rot90(tetromino, 1)
        if not collision(rotated, x, y):
            tetromino = rotated
    elif gesture == "DOWN":
        if not collision(tetromino, x, y + 1):
            y += 1
    current_time = time.time()
    if current_time - fall_time > fall_speed:
        if not collision(tetromino, x, y + 1): # automatic fall
            y += 1
        else:
            place_tetromino(tetromino, x, y, color_index) # lock piece
            tetromino, x, y, color_index = new_piece() # continue with next piece
        fall_time = current_time