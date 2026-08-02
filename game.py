import cv2 as cv
import numpy as np
import time
from board_game import *
from gesture_control import get_gesture, cleanup


def main():
    tetromino, x, y, color_index = new_piece()
    score = 0
    level = 1
    lines_cleared = 0
    fall_time = time.time()
    fall_speed = 0.5
    
    # Set window to fullscreen
    cv.namedWindow('Tetris', cv.WINDOW_NORMAL)
    cv.resizeWindow('Tetris', SCREEN_WIDTH, SCREEN_HEIGHT)
    
    while True:
        # Get gesture and camera
        gesture, webcam_frame = get_gesture()
        
        # Render display
        tetris_display = display_board(score, level, lines_cleared, webcam_frame)
        
        # Handle gestures
        if gesture:
            print(f"Gesture: {gesture}")
        
        if gesture == "LEFT":
            if not collision(tetromino, x - 1, y):
                x -= 1
        elif gesture == "RIGHT":
            if not collision(tetromino, x + 1, y):
                x += 1
        elif gesture == "CW_ROTATE":
            rotated = np.rot90(tetromino, -1)
            if not collision(rotated, x, y):
                tetromino = rotated
        elif gesture == "CCW_ROTATE":
            rotated = np.rot90(tetromino, 1)
            if not collision(rotated, x, y):
                tetromino = rotated
        elif gesture == "DOWN":
            if not collision(tetromino, x, y + 1):
                y += 1
        
        # Draw game
        draw_board_matrix()
        draw_tetromino(tetromino, x, y, color_index)
        draw_grid()
        
        # Falling logic
        current_time = time.time()
        if current_time - fall_time > fall_speed:
            if not collision(tetromino, x, y + 1):
                y += 1
            else:
                place_tetromino(tetromino, x, y, color_index)
                
                lines = clear_lines()
                if lines > 0:
                    lines_cleared += lines
                    score += lines * 100
                    level = (lines_cleared // 10) + 1
                    fall_speed = max(0.1, 0.5 - (level * 0.05))
                    print(f"Lines: {lines_cleared} | Level: {level} | Score: {score}")
                
                tetromino, x, y, color_index = new_piece()
                
                if collision(tetromino, x, y):
                    draw_game_over(score, level)
                    cv.imshow('Tetris', tetris_display)
                    cv.waitKey(5000)
                    break
            
            fall_time = current_time
        
        # Display
        cv.imshow('Tetris', tetris_display)
        
        if cv.waitKey(1) == ord('q'):
            break
    
    cleanup()
    cv.destroyAllWindows()