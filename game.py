import cv2 as cv
import numpy as np
import time
from board_game import *
from gesture_control import get_gesture, cleanup


def main():
    tetromino, x, y, color_index = new_piece()
    score = 0
    fall_time = time.time()
    fall_speed = 0.5 # seconds per cell fall

    # MAIN GAME LOOP
    while True:

        tetris_display = display_board(score)
        gesture, webcam_frame = get_gesture()
        webcam_frame = cv.resize(webcam_frame, (webcam_width, webcam_height))
        tetris_display[webcam_y1:webcam_y2, webcam_x1:webcam_x2] = webcam_frame
        draw_board_matrix()
        draw_tetromino(tetromino, x, y, color_index)
        draw_grid()
        cv.imshow('Tetris Display', tetris_display)
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
                lines = clear_lines()
                if lines > 0:
                    score += lines * 100
                tetromino, x, y, color_index = new_piece() # continue with next piece
                if collision(tetromino, x, y):
                    cv.putText(tetris_display, "GAME OVER", (7*unit_size, 12*unit_size), cv.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 5)
                    cv.imshow('Tetris Display', tetris_display)
                    cv.waitKey(5000)
                    break
            fall_time = current_time
        cv.imshow('Tetris Display', tetris_display)
        if cv.waitKey(1) == ord('q'):
            break

    cleanup()
    cv.destroyAllWindows()