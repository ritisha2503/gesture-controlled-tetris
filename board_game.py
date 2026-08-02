import cv2 as cv
import numpy as np

# ============================================================================
# CONSTANTS & CONFIGURATION
# ============================================================================

# Board dimensions
h = 20  # height in cells
w = 10  # width in cells
unit_size = 32  # cell size in pixels

# Layout dimensions
MARGIN = 15
LEFT_PANEL_WIDTH = 260
CAMERA_PANEL_WIDTH = 360
CAMERA_PANEL_HEIGHT = 320
SCREEN_WIDTH = LEFT_PANEL_WIDTH + MARGIN + (w * unit_size) + MARGIN + CAMERA_PANEL_WIDTH + MARGIN
SCREEN_HEIGHT = max((h * unit_size) + (2 * MARGIN), CAMERA_PANEL_HEIGHT + (2 * MARGIN))

# Game board positioning
GAME_AREA_X = LEFT_PANEL_WIDTH + MARGIN
GAME_AREA_Y = MARGIN

# Camera positioning
CAMERA_X = GAME_AREA_X + (w * unit_size) + MARGIN
CAMERA_Y = MARGIN

# Display canvas
DISPLAY_HEIGHT = max((h * unit_size) + (2 * MARGIN), CAMERA_PANEL_HEIGHT + (2 * MARGIN))
DISPLAY_WIDTH = LEFT_PANEL_WIDTH + MARGIN + (w * unit_size) + MARGIN + CAMERA_PANEL_WIDTH + MARGIN

# Color palette - dark theme with good contrast
COLOR_BG_PRIMARY = (20, 20, 20)           # Dark background
COLOR_BG_SECONDARY = (28, 28, 28)         # Slightly lighter for panels
COLOR_ACCENT = (56, 165, 238)             # Bright blue accent
COLOR_TEXT_PRIMARY = (240, 240, 240)      # Light text
COLOR_TEXT_SECONDARY = (180, 180, 180)    # Dimmer text
COLOR_GRID = (50, 50, 50)                 # Grid lines
COLOR_BORDER = (70, 70, 70)               # Borders
COLOR_DANGER = (255, 80, 80)              # Red for warnings

# Tetromino colors - vibrant and distinct
TETRIS_COLORS = [
    (0, 240, 240),      # Cyan (I)
    (240, 240, 0),      # Yellow (O)
    (240, 160, 0),      # Orange (T)
    (240, 0, 0),        # Red (S)
    (0, 240, 0),        # Green (Z)
    (240, 0, 240),      # Magenta (J)
    (0, 160, 240)       # Blue (L)
]

# Font settings
FONT_MAIN = cv.FONT_HERSHEY_SIMPLEX
FONT_MONO = cv.FONT_HERSHEY_DUPLEX
FONT_THICK = 1
FONT_THIN = 0.5

# ============================================================================
# GLOBAL STATE
# ============================================================================

board_matrix = np.zeros((h, w), dtype=int)
tetris_display = None

# Tetrominoes with spawn rotations
TETROMINOES = [
    np.array([[1, 1, 1, 1]]),                    # I
    np.array([[1, 1], [1, 1]]),                  # O
    np.array([[0, 1, 0], [1, 1, 1]]),            # T
    np.array([[1, 0, 0], [1, 1, 1]]),            # S
    np.array([[0, 0, 1], [1, 1, 1]]),            # Z
    np.array([[1, 1, 0], [0, 1, 1]]),            # J
    np.array([[0, 1, 1], [1, 1, 0]])             # L
]

# ============================================================================
# RENDERING FUNCTIONS
# ============================================================================

def create_canvas():
    """Create a fresh display canvas"""
    global tetris_display
    tetris_display = np.full((DISPLAY_HEIGHT, DISPLAY_WIDTH, 3), COLOR_BG_PRIMARY, dtype=np.uint8)


def draw_panel_background(x1, y1, x2, y2, title=None):
    """Draw a panel with background, border, and optional title"""
    # Background
    cv.rectangle(tetris_display, (x1, y1), (x2, y2), COLOR_BG_SECONDARY, -1)
    # Border
    cv.rectangle(tetris_display, (x1, y1), (x2, y2), COLOR_BORDER, 2)
    
    # Title bar if provided
    if title:
        title_height = 32
        cv.rectangle(tetris_display, (x1, y1), (x2, y1 + title_height), COLOR_ACCENT, -1)
        cv.putText(tetris_display, title, (x1 + 12, y1 + 22), FONT_MAIN, 
                    0.7, COLOR_BG_PRIMARY, 2)


def draw_stat_line(x, y, label, value, label_color=COLOR_TEXT_SECONDARY):
    """Draw a label-value pair"""
    # Label
    cv.putText(tetris_display, label, (x, y), FONT_MAIN, 0.6, label_color, 1)
    # Value
    cv.putText(tetris_display, str(value), (x, y + 28), FONT_MONO, 0.8, 
                COLOR_TEXT_PRIMARY, 2)


def display_board(score, level=1, lines_cleared=0, camera_frame=None):
    """Create main display with all UI elements"""
    global tetris_display
    
    create_canvas()
    
    # ========== LEFT PANEL: INFO ==========
    left_x1, left_y1 = MARGIN, MARGIN
    left_x2, left_y2 = left_x1 + LEFT_PANEL_WIDTH, DISPLAY_HEIGHT - MARGIN
    
    draw_panel_background(left_x1, left_y1, left_x2, left_y2, "TETRIS")
    
    # Stats in left panel
    stat_x = left_x1 + 15
    stat_y = left_y1 + 50
    
    draw_stat_line(stat_x, stat_y, "SCORE", score)
    draw_stat_line(stat_x, stat_y + 70, "LEVEL", level)
    draw_stat_line(stat_x, stat_y + 140, "LINES", lines_cleared)
    
    # Controls guide
    guide_y = stat_y + 210
    cv.putText(tetris_display, "CONTROLS", (stat_x, guide_y), FONT_MAIN, 
                0.55, COLOR_ACCENT, 1)
    
    controls = [
        "LEFT: Move",
        "RIGHT: Move",
        "DOWN: Drop",
        "CW: Rotate",
        "CCW: Rotate"
    ]
    
    for i, control in enumerate(controls):
        cv.putText(tetris_display, control, (stat_x, guide_y + 25 + (i * 22)), 
                    FONT_MAIN, 0.45, COLOR_TEXT_SECONDARY, 1)
    
    # ========== CENTER: GAME BOARD ==========
    board_x1 = GAME_AREA_X
    board_y1 = GAME_AREA_Y
    board_x2 = board_x1 + (w * unit_size)
    board_y2 = board_y1 + (h * unit_size)
    
    # Background
    cv.rectangle(tetris_display, (board_x1, board_y1), (board_x2, board_y2), 
                    (0, 0, 0), -1)
    # Border
    cv.rectangle(tetris_display, (board_x1, board_y1), (board_x2, board_y2), 
                    COLOR_ACCENT, 3)
    
    # ========== RIGHT PANEL: CAMERA ==========
    if camera_frame is not None:
        cam_x1 = CAMERA_X
        cam_y1 = CAMERA_Y
        cam_x2 = cam_x1 + CAMERA_PANEL_WIDTH
        cam_y2 = cam_y1 + CAMERA_PANEL_HEIGHT
        
        # Panel background and border
        cv.rectangle(tetris_display, (cam_x1, cam_y1), (cam_x2, cam_y2), 
                        COLOR_BG_SECONDARY, -1)
        cv.rectangle(tetris_display, (cam_x1, cam_y1), (cam_x2, cam_y2), 
                        COLOR_BORDER, 2)
        
        # Title
        cv.rectangle(tetris_display, (cam_x1, cam_y1), (cam_x2, cam_y1 + 32), 
                        COLOR_ACCENT, -1)
        cv.putText(tetris_display, "CAMERA", (cam_x1 + 12, cam_y1 + 22), FONT_MAIN, 
                    0.7, COLOR_BG_PRIMARY, 2)
        
        # Resize and embed camera feed
        camera_resized = cv.resize(camera_frame, (CAMERA_PANEL_WIDTH - 4, CAMERA_PANEL_HEIGHT - 36))
        tetris_display[cam_y1 + 34:cam_y1 + 34 + CAMERA_PANEL_HEIGHT - 36, 
                        cam_x1 + 2:cam_x1 + 2 + CAMERA_PANEL_WIDTH - 4] = camera_resized
    
    return tetris_display


def draw_grid():
    """Draw the game board grid"""
    board_x1 = GAME_AREA_X
    board_y1 = GAME_AREA_Y
    
    # Vertical lines
    for i in range(w + 1):
        x = board_x1 + (i * unit_size)
        cv.line(tetris_display, (x, board_y1), (x, board_y1 + (h * unit_size)), 
                COLOR_GRID, 1)
    
    # Horizontal lines
    for i in range(h + 1):
        y = board_y1 + (i * unit_size)
        cv.line(tetris_display, (board_x1, y), (board_x1 + (w * unit_size), y), 
                COLOR_GRID, 1)


def draw_board_matrix():
    """Render placed blocks"""
    board_x1 = GAME_AREA_X
    board_y1 = GAME_AREA_Y
    
    for row in range(h):
        for col in range(w):
            if board_matrix[row, col] != 0:
                x = board_x1 + (col * unit_size)
                y = board_y1 + (row * unit_size)
                
                color_idx = board_matrix[row, col] - 1
                color = TETRIS_COLORS[color_idx % len(TETRIS_COLORS)]
                
                # Draw block with subtle border
                cv.rectangle(tetris_display, (x + 2, y + 2), 
                            (x + unit_size - 2, y + unit_size - 2), color, -1)
                cv.rectangle(tetris_display, (x + 2, y + 2), 
                            (x + unit_size - 2, y + unit_size - 2), 
                            (255, 255, 255), 1)


def draw_tetromino(tetromino, x, y, color_index):
    """Render the falling piece"""
    board_x1 = GAME_AREA_X
    board_y1 = GAME_AREA_Y
    
    color = TETRIS_COLORS[color_index % len(TETRIS_COLORS)]
    
    for row in range(tetromino.shape[0]):
        for col in range(tetromino.shape[1]):
            if tetromino[row, col] == 1:
                block_x = board_x1 + ((x + col) * unit_size)
                block_y = board_y1 + ((y + row) * unit_size)
                
                # Draw with slight transparency effect (bright border)
                cv.rectangle(tetris_display, (block_x + 2, block_y + 2), 
                            (block_x + unit_size - 2, block_y + unit_size - 2), 
                            color, -1)
                cv.rectangle(tetris_display, (block_x + 2, block_y + 2), 
                            (block_x + unit_size - 2, block_y + unit_size - 2), 
                            (255, 255, 255), 2)


def draw_game_over(score, level):
    """Draw game over screen overlay"""
    # Semi-transparent overlay
    overlay = tetris_display.copy()
    cv.rectangle(overlay, (0, 0), (DISPLAY_WIDTH, DISPLAY_HEIGHT), 
                (0, 0, 0), -1)
    cv.addWeighted(overlay, 0.7, tetris_display, 0.3, 0, tetris_display)
    
    # Text
    text_y = DISPLAY_HEIGHT // 2 - 40
    cv.putText(tetris_display, "GAME OVER", (DISPLAY_WIDTH // 2 - 120, text_y), 
                FONT_MAIN, 2, COLOR_DANGER, 3)
    
    cv.putText(tetris_display, f"Final Score: {score}", 
               (DISPLAY_WIDTH // 2 - 100, text_y + 60), FONT_MAIN, 1.2, 
                COLOR_TEXT_PRIMARY, 2)
    
    cv.putText(tetris_display, f"Level: {level}", 
               (DISPLAY_WIDTH // 2 - 70, text_y + 100), FONT_MAIN, 1.2, 
                COLOR_TEXT_PRIMARY, 2)


# ============================================================================
# GAME LOGIC
# ============================================================================

def collision(tetromino, x, y):
    """Check for collisions with walls, floor, and blocks"""
    for row in range(tetromino.shape[0]):
        for col in range(tetromino.shape[1]):
            if tetromino[row, col] == 1:
                board_x = x + col
                board_y = y + row
                
                # Wall collision
                if board_x < 0 or board_x >= w:
                    return True
                # Bottom collision
                if board_y >= h:
                    return True
                # Block collision
                if board_y >= 0 and board_matrix[board_y, board_x] != 0:
                    return True
    
    return False


def place_tetromino(tetromino, x, y, color_index):
    """Lock piece to board"""
    for row in range(tetromino.shape[0]):
        for col in range(tetromino.shape[1]):
            if tetromino[row, col] == 1:
                board_y = y + row
                board_x = x + col
                
                if 0 <= board_y < h and 0 <= board_x < w:
                    board_matrix[board_y, board_x] = color_index + 1


def clear_lines():
    """Clear completed rows and return count"""
    global board_matrix
    
    full_rows = []
    for row in range(h):
        if np.all(board_matrix[row] != 0):
            full_rows.append(row)
    
    # Delete from bottom to top to maintain indices
    for row in sorted(full_rows, reverse=True):
        board_matrix = np.delete(board_matrix, row, axis=0)
        new_row = np.zeros((1, w), dtype=int)
        board_matrix = np.vstack((new_row, board_matrix))
    
    return len(full_rows)


def new_piece():
    """Spawn a random tetromino at the top center"""
    piece_idx = np.random.randint(len(TETROMINOES))
    tetromino = TETROMINOES[piece_idx].copy()
    x = (w - tetromino.shape[1]) // 2
    y = 0
    color_idx = piece_idx
    
    return tetromino, x, y, color_idx