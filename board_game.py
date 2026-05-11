import cv2 as cv
import numpy as np

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

def display_board():
    tetris_display = np.full(((h + 2 * y_offset) * unit_size, (w + 2 * x_offset) * unit_size, 3), bg_color, dtype=np.uint8)
    cv.rectangle(tetris_display, (x_offset * unit_size, y_offset * unit_size), ((x_offset + w) * unit_size, (y_offset + h) * unit_size), game_bg_color, thickness=-1)
    return tetris_display

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