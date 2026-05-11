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

# TETROMINO SHAPES
tetrominoes =   [np.array([[1, 1, 1, 1]]), 
                np.array([[1, 1], [1, 1]]), 
                np.array([[0, 1, 0], [1, 1, 1]]),
                np.array([[1, 0, 0], [1, 1, 1]]),
                np.array([[0, 0, 1], [1, 1, 1]]),
                np.array([[1, 1, 0], [0, 1, 1]]),
                np.array([[0, 1, 1], [1, 1, 0]])
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

def draw_block(tetromino, start_x, start_y, color):
    for row in range(tetromino.shape[0]):
        for col in range(tetromino.shape[1]):
            if tetromino[row, col] == 1:
                top_left = ((start_x + col) * unit_size, (start_y + row) * unit_size)
                bottom_right = ((start_x + col + 1) * unit_size, (start_y + row + 1) * unit_size)
                cv.rectangle(tetris_display, top_left, bottom_right, color, thickness=-1)


# NAVIGATION

def navigation(tetromino, x, y, key):
    if key == 2424832 and x > x_offset:
        return (tetromino, x - 1, y)
    elif key == 2555904 and x < (x_offset + w - tetromino.shape[1]):
        return (tetromino, x + 1, y)
    elif key == 2490368:
        return (np.rot90(tetromino, -1), x, y)
    elif key == 2621440 and y < (y_offset + h - tetromino.shape[0]):
        return (tetromino, x, y + 1)
    else:
        return (tetromino, x, y)


# random choice of tetromino and starting position
choice = np.random.randint(0, len(tetrominoes)) # random tetromino
xi = np.random.randint(x_offset, x_offset + w - tetrominoes[choice].shape[1] + 1) # random x position for the tetromino
yi = y_offset # start at the top of the board


tetromino = tetrominoes[choice]
x, y = xi, yi

while True:

    display_board()
    draw_block(tetromino, x, y, (0, 255, 0))
    draw_grid()
    cv.imshow('Tetris Display', tetris_display)
    key = cv.waitKeyEx(1000)
    tetromino, x, y = navigation(tetromino, x, y, key)
    y += 1

