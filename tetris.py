import pygame
import random
import sys

pygame.init()
pygame.font.init()

# ------------------------- Global Variables ------------------------- #
s_width = 1200
s_height = 800
play_width = 300   # 10 columns * 30 pixels
play_height = 600  # 20 rows * 30 pixels
block_size = 30

top_left_x = (s_width - play_width) // 2
top_left_y = s_height - play_height - 50

# ------------------------- Themes & Difficulty ------------------------- #
# Two themes: "pastel" and "vibrant"
THEMES = {
    "pastel": [(48, 213, 200), (245, 105, 145), (99, 155, 255),
               (255, 255, 102), (255, 178, 102), (102, 255, 102),
               (204, 153, 255)],
    "vibrant": [(0, 255, 255), (255, 0, 255), (0, 0, 255),
                (255, 255, 0), (255, 165, 0), (0, 255, 0),
                (128, 0, 128)]
}

current_theme = "pastel"  # default theme
shape_colors = THEMES[current_theme]

# Difficulty levels determine the starting fall speed:
DIFFICULTY_SPEED = {
    "Easy": 0.35,
    "Medium": 0.27,
    "Hard": 0.18
}

# ------------------------- Tetris Shapes ------------------------- #
S = [['.....',
      '.....',
      '..00.',
      '.00..',
      '.....'],
     ['.....',
      '..0..',
      '..00.',
      '...0.',
      '.....']]

Z = [['.....',
      '.....',
      '.00..',
      '..00.',
      '.....'],
     ['.....',
      '..0..',
      '.00..',
      '.0...',
      '.....']]

I = [['..0..',
      '..0..',
      '..0..',
      '..0..',
      '.....'],
     ['.....',
      '0000.',
      '.....',
      '.....',
      '.....']]

O = [['.....',
      '.....',
      '.00..',
      '.00..',
      '.....']]

J = [['.....',
      '.0...',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..00.',
      '..0..',
      '..0..',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '...0.',
      '.....'],
     ['.....',
      '..0..',
      '..0..',
      '.00..',
      '.....']]

L = [['.....',
      '...0.',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..0..',
      '..0..',
      '..00.',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '.0...',
      '.....'],
     ['.....',
      '.00..',
      '..0..',
      '..0..',
      '.....']]

T = [['.....',
      '..0..',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..0..',
      '..00.',
      '..0..',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '..0..',
      '.....'],
     ['.....',
      '..0..',
      '.00..',
      '..0..',
      '.....']]

shapes = [S, Z, I, O, J, L, T]

# ------------------------- Classes ------------------------- #
class Piece:
    def __init__(self, x, y, shape):
        self.x = x
        self.y = y
        self.shape = shape
        self.color = shape_colors[shapes.index(shape)]
        self.rotation = 0

# ------------------------- Helper Functions ------------------------- #
def create_grid(locked_positions={}):
    """Creates a 20x10 grid with colors for locked positions."""
    grid = [[(0, 0, 0) for _ in range(10)] for _ in range(20)]
    
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            if (j, i) in locked_positions:
                grid[i][j] = locked_positions[(j, i)]
    return grid

def convert_shape_format(piece):
    """Converts the piece's shape into grid positions."""
    positions = []
    format = piece.shape[piece.rotation % len(piece.shape)]
    
    for i, line in enumerate(format):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':
                # Offset to center the shape (because our shapes are 5x5)
                positions.append((piece.x + j - 2, piece.y + i - 4))
    return positions

def valid_space(piece, grid):
    """Returns True if the piece is in a valid (empty) space on the grid."""
    accepted_positions = [[(j, i) for j in range(10) if grid[i][j] == (0, 0, 0)] for i in range(20)]
    accepted_positions = [pos for sub in accepted_positions for pos in sub]
    
    formatted = convert_shape_format(piece)
    
    for pos in formatted:
        if pos not in accepted_positions:
            if pos[1] > -1:
                return False
    return True

def check_lost(positions):
    """Returns True if any locked positions are above the visible grid."""
    for pos in positions:
        x, y = pos
        if y < 1:
            return True
    return False

def get_shape():
    """Returns a random new piece."""
    return Piece(5, 0, random.choice(shapes))

def draw_text(surface, text, size, color, pos):
    """Draws text (plain, without drop shadow) at the given position."""
    font = pygame.font.SysFont('comicsans', size, bold=True)
    label = font.render(text, True, color)
    surface.blit(label, pos)

def draw_grid(surface, grid):
    """Draws grid lines over the play area."""
    sx = top_left_x
    sy = top_left_y
    for i in range(len(grid)):
        pygame.draw.line(surface, (128, 128, 128), (sx, sy + i * block_size),
                         (sx + play_width, sy + i * block_size))
        for j in range(len(grid[i])):
            pygame.draw.line(surface, (128, 128, 128),
                             (sx + j * block_size, sy),
                             (sx + j * block_size, sy + play_height))

def draw_background(surface):
    """Draws a vertical gradient background."""
    top_color = (10, 10, 30)
    bottom_color = (50, 50, 100)
    for i in range(s_height):
        ratio = i / s_height
        r = int(top_color[0] * (1 - ratio) + bottom_color[0] * ratio)
        g = int(top_color[1] * (1 - ratio) + bottom_color[1] * ratio)
        b = int(top_color[2] * (1 - ratio) + bottom_color[2] * ratio)
        pygame.draw.line(surface, (r, g, b), (0, i), (s_width, i))

def draw_window(surface, grid, score=0, high_score=0):
    """Renders the entire game window (background, grid, scores, and control text)."""
    draw_background(surface)
    
    # Title at top-center
    title = "TETRIS"
    title_font = pygame.font.SysFont('comicsans', 60, bold=True)
    title_label = title_font.render(title, True, (255, 255, 255))
    surface.blit(title_label, (top_left_x + play_width / 2 - title_label.get_width() / 2, 20))
    
    # Left panel for Score and Controls
    panel_x = 50
    draw_text(surface, f"Score: {score}", 30, (255, 255, 255), (panel_x, 150))
    draw_text(surface, f"High Score: {high_score}", 30, (255, 255, 255), (panel_x, 190))
    
    # Draw controls information (arranged normally)
    controls = [
        "Controls:",
        "Move Left: ← or A",
        "Move Right: → or D",
        "Drop: ↓ or S",
        "Rotate: ↑ or W",
        "Pause: P"
    ]
    for i, line in enumerate(controls):
        draw_text(surface, line, 24, (200, 200, 200), (panel_x, 250 + i * 30))
    
    # Draw play area grid
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            pygame.draw.rect(surface, grid[i][j],
                             (top_left_x + j * block_size,
                              top_left_y + i * block_size,
                              block_size, block_size), 0)
    
    draw_grid(surface, grid)
    pygame.draw.rect(surface, (255, 255, 255), (top_left_x, top_left_y, play_width, play_height), 4)

def draw_next_shape(piece, surface):
    """Displays the next piece in a preview box with label 'Next Figure:'."""
    sx = top_left_x + play_width + 50
    sy = top_left_y + play_height / 2 - 100
    
    # Label for next piece
    draw_text(surface, "Next Figure:", 30, (255, 255, 255), (sx, sy - 40))
    
    format = piece.shape[piece.rotation % len(piece.shape)]
    
    for i, line in enumerate(format):
        for j, column in enumerate(list(line)):
            if column == '0':
                pygame.draw.rect(surface, piece.color,
                                 (sx + j * block_size - 30, sy + i * block_size - 30,
                                  block_size, block_size), 0)

def update_high_score(new_score):
    """Reads and updates the high score stored in a text file."""
    high_score = new_score
    try:
        with open('high_score.txt', 'r') as f:
            high_score = int(f.read())
    except:
        high_score = 0
    if new_score > high_score:
        high_score = new_score
        with open('high_score.txt', 'w') as f:
            f.write(str(high_score))
    return high_score

# ------------------------- Animated Functions ------------------------- #
def create_piece_surface(shape_str, color, block_size):
    """
    Creates a surface for a given shape (using its 5x5 string representation)
    drawn in its minimal bounding box. Returns the Surface and its pivot.
    """
    blocks = []
    for i, line in enumerate(shape_str):
        for j, char in enumerate(line):
            if char == '0':
                blocks.append((i, j))
    if not blocks:
        return None, (0, 0)
    min_i = min(b[0] for b in blocks)
    max_i = max(b[0] for b in blocks)
    min_j = min(b[1] for b in blocks)
    max_j = max(b[1] for b in blocks)
    width = (max_j - min_j + 1) * block_size
    height = (max_i - min_i + 1) * block_size
    surface = pygame.Surface((width, height), pygame.SRCALPHA)
    for i, line in enumerate(shape_str):
        for j, char in enumerate(line):
            if char == '0':
                rect = pygame.Rect((j - min_j)*block_size, (i - min_i)*block_size, block_size, block_size)
                pygame.draw.rect(surface, color, rect)
                pygame.draw.rect(surface, (0, 0, 0), rect, 2)
    pivot = (width // 2, height // 2)
    return surface, pivot

def animate_rotation(win, piece, old_rotation, new_rotation, locked, grid, score, high_score):
    """
    Animates the piece rotating from old_rotation to new_rotation.
    This animation lasts 200ms.
    """
    duration = 200  # milliseconds
    start_time = pygame.time.get_ticks()
    # Create a surface for the piece in its old orientation
    piece_surface, _ = create_piece_surface(piece.shape[old_rotation], piece.color, block_size)
    
    # Compute piece position in pixels
    positions = []
    for i, line in enumerate(piece.shape[old_rotation]):
        for j, char in enumerate(line):
            if char == '0':
                positions.append((piece.x + j - 2, piece.y + i - 4))
    if positions:
        xs = [p[0] for p in positions]
        ys = [p[1] for p in positions]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        center_grid = (min_x + (max_x - min_x + 1) / 2, min_y + (max_y - min_y + 1) / 2)
    else:
        center_grid = (piece.x, piece.y)
    pivot_pixel = (top_left_x + center_grid[0] * block_size,
                   top_left_y + center_grid[1] * block_size)
    
    while True:
        current_time = pygame.time.get_ticks()
        elapsed = current_time - start_time
        progress = min(elapsed / duration, 1)
        angle = -90 * progress  # clockwise rotation
        rotated_image = pygame.transform.rotate(piece_surface, angle)
        rotated_rect = rotated_image.get_rect(center=pivot_pixel)
        
        temp_grid = create_grid(locked)
        draw_window(win, temp_grid, score, high_score)
        win.blit(rotated_image, rotated_rect.topleft)
        pygame.display.update()
        pygame.time.delay(20)
        if progress >= 1:
            break

def animate_row_clear(win, grid, row, score, high_score):
    """
    Animates a row clearing by fading it out over 300ms.
    """
    duration = 300  # milliseconds
    start_time = pygame.time.get_ticks()
    original_row = grid[row][:]
    while True:
        current_time = pygame.time.get_ticks()
        elapsed = current_time - start_time
        progress = elapsed / duration
        # Fade factor: from 1 to 0
        fade = max(1 - progress, 0)
        temp_grid = [r[:] for r in grid]
        for j in range(len(temp_grid[row])):
            orig_color = original_row[j]
            faded_color = (int(orig_color[0]*fade), int(orig_color[1]*fade), int(orig_color[2]*fade))
            temp_grid[row][j] = faded_color
        draw_window(win, temp_grid, score, high_score)
        pygame.display.update()
        pygame.time.delay(20)
        if elapsed >= duration:
            break

def clear_rows(grid, locked, win, score, high_score):
    """
    Checks for full rows, animates their clearing, and removes them.
    Returns the number of cleared rows.
    """
    cleared = 0
    rows_to_clear = []
    for i in range(len(grid)-1, -1, -1):
        row = grid[i]
        if (0, 0, 0) not in row:
            rows_to_clear.append(i)
    for row in rows_to_clear:
        animate_row_clear(win, grid, row, score, high_score)
        cleared += 1
        for j in range(len(grid[row])):
            try:
                del locked[(j, row)]
            except:
                continue
    if cleared > 0:
        for key in sorted(list(locked), key=lambda x: x[1])[::-1]:
            x, y = key
            shift = sum(1 for r in rows_to_clear if y < r)
            if shift > 0:
                newKey = (x, y + shift)
                locked[newKey] = locked.pop(key)
    return cleared

# ------------------------- Pause Functionality ------------------------- #
def pause_game(win, score, high_score):
    """Pauses the game until the player presses P again."""
    paused = True
    pause_font = pygame.font.SysFont('comicsans', 60, bold=True)
    pause_label = pause_font.render("PAUSED", True, (255, 255, 255))
    instruction = pygame.font.SysFont('comicsans', 30).render("Press P to resume", True, (200,200,200))
    while paused:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    paused = False
        # Redraw current game state (frozen)
        temp_grid = [[(0,0,0) for _ in range(10)] for _ in range(20)]
        draw_window(win, temp_grid, score, high_score)
        win.blit(pause_label, (top_left_x + play_width/2 - pause_label.get_width()/2,
                               top_left_y + play_height/2 - pause_label.get_height()/2))
        win.blit(instruction, (top_left_x + play_width/2 - instruction.get_width()/2,
                               top_left_y + play_height/2 + pause_label.get_height()/2))
        pygame.display.update()
        pygame.time.delay(50)

# ------------------------- Main Game Function ------------------------- #
def main(win, difficulty):
    locked_positions = {}
    grid = create_grid(locked_positions)
    
    change_piece = False
    run = True
    current_piece = get_shape()
    next_piece = get_shape()
    clock = pygame.time.Clock()
    fall_time = 0
    fall_speed = DIFFICULTY_SPEED[difficulty]
    level_time = 0
    score = 0
    
    while run:
        grid = create_grid(locked_positions)
        fall_time += clock.get_rawtime()
        level_time += clock.get_rawtime()
        clock.tick()
        
        # Increase difficulty over time (optional speed up)
        if level_time / 1000 > 5:
            level_time = 0
            if fall_speed > 0.12:
                fall_speed -= 0.005
        
        # Automatic piece falling
        if fall_time / 1000 > fall_speed:
            fall_time = 0
            current_piece.y += 1
            if not valid_space(current_piece, grid) and current_piece.y > 0:
                current_piece.y -= 1
                change_piece = True
        
        # Event handling (movement, rotation, pause)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                # Pause the game
                if event.key == pygame.K_p:
                    pause_game(win, score, update_high_score(score))
                # Move Left (Left arrow or A)
                if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    current_piece.x -= 1
                    if not valid_space(current_piece, grid):
                        current_piece.x += 1
                # Move Right (Right arrow or D)
                if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    current_piece.x += 1
                    if not valid_space(current_piece, grid):
                        current_piece.x -= 1
                # Move Down (Down arrow or S)
                if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    current_piece.y += 1
                    if not valid_space(current_piece, grid):
                        current_piece.y -= 1
                # Rotate (Up arrow or W)
                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    old_rotation = current_piece.rotation
                    current_piece.rotation = (current_piece.rotation + 1) % len(current_piece.shape)
                    if not valid_space(current_piece, grid):
                        current_piece.rotation = old_rotation
                    else:
                        animate_rotation(win, current_piece, old_rotation, current_piece.rotation,
                                         locked_positions, grid, score, update_high_score(score))
        
        shape_pos = convert_shape_format(current_piece)
        
        # Draw current piece onto grid
        for pos in shape_pos:
            x, y = pos
            if y > -1:
                grid[y][x] = current_piece.color
        
        # If piece has landed, lock it in place and load next piece
        if change_piece:
            for pos in shape_pos:
                locked_positions[(pos[0], pos[1])] = current_piece.color
            current_piece = next_piece
            next_piece = get_shape()
            change_piece = False
            cleared = clear_rows(grid, locked_positions, win, score, update_high_score(score))
            score += cleared * 10
        
        draw_window(win, grid, score, update_high_score(score))
        draw_next_shape(next_piece, win)
        pygame.display.update()
        
        if check_lost(locked_positions):
            draw_text(win, "YOU LOST!", 80, (255, 255, 255), (top_left_x + play_width/2 - 150, top_left_y + play_height/2 - 40))
            pygame.display.update()
            pygame.time.delay(1500)
            run = False

# ------------------------- Menu Functions ------------------------- #
def customization_menu(win):
    """Allows the player to toggle the color theme."""
    global current_theme, shape_colors
    run = True
    while run:
        win.fill((0, 0, 0))
        draw_text(win, "Customization", 60, (255, 255, 255), (s_width/2 - 180, 100))
        draw_text(win, f"Current Theme: {current_theme.capitalize()}", 40, (255, 255, 255), (s_width/2 - 180, 200))
        draw_text(win, "Press T to toggle theme", 30, (200, 200, 200), (s_width/2 - 180, 300))
        draw_text(win, "Press any other key to return", 30, (200, 200, 200), (s_width/2 - 180, 350))
        pygame.display.update()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_t:
                    # Toggle theme
                    current_theme = "vibrant" if current_theme == "pastel" else "pastel"
                    shape_colors = THEMES[current_theme]
                else:
                    run = False

def main_menu(win):
    """Displays the main menu and waits for user input."""
    run = True
    while run:
        win.fill((0, 0, 0))
        draw_text(win, "TETRIS", 80, (255, 255, 255), (s_width/2 - 150, 50))
        draw_text(win, "Select Difficulty:", 50, (255, 255, 255), (s_width/2 - 180, 180))
        draw_text(win, "1 - Easy", 40, (200, 200, 200), (s_width/2 - 150, 250))
        draw_text(win, "2 - Medium", 40, (200, 200, 200), (s_width/2 - 150, 300))
        draw_text(win, "3 - Hard", 40, (200, 200, 200), (s_width/2 - 150, 350))
        draw_text(win, "Press C for Customization", 40, (200, 200, 200), (s_width/2 - 180, 420))
        draw_text(win, "Press Q to Quit", 40, (200, 200, 200), (s_width/2 - 150, 470))
        pygame.display.update()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    main(win, "Easy")
                elif event.key == pygame.K_2:
                    main(win, "Medium")
                elif event.key == pygame.K_3:
                    main(win, "Hard")
                elif event.key == pygame.K_c:
                    customization_menu(win)
                elif event.key == pygame.K_q:
                    run = False
                    pygame.quit()
                    sys.exit()

# ------------------------- Entry Point ------------------------- #
win = pygame.display.set_mode((s_width, s_height))
pygame.display.set_caption('Tetris')
main_menu(win)