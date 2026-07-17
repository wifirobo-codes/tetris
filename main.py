import pygame
import random
import os
import sys

pygame.init()
pygame.mixer.init()

def make_block(color):

    img = BLOCK.copy()

    tint = pygame.Surface(img.get_size(), pygame.SRCALPHA)
    tint.fill(color)

    img.blit(tint, (0,0), special_flags=pygame.BLEND_RGBA_MULT)

    return img

def fit(img,w,h):

    iw,ih=img.get_size()

    s=min(w/iw,h/ih)

    return pygame.transform.smoothscale(
        img,
        (int(iw*s),int(ih*s))
    )

COLORS = {
    0:(0,255,255),      # I
    1:(255,255,0),      # O
    2:(170,0,255),      # T
    3:(0,0,255),        # J
    4:(255,140,0),      # L
    5:(0,255,0),        # S
    6:(255,0,0)         # Z
}

# ---------------------------------
# WINDOW
# ---------------------------------

WIDTH = 800
HEIGHT = 640
FPS = 60

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tetris")

clock = pygame.time.Clock()

# ---------------------------------
# BOARD
# ---------------------------------

COLS = 10
ROWS = 20

CELL = 32

CELL = 32

BOARD_WIDTH = CELL * 10
BOARD_HEIGHT = CELL * 20

BOARD_X = (WIDTH - 220 - BOARD_WIDTH) // 2
BOARD_Y = (HEIGHT - BOARD_HEIGHT) // 2

SIDE_X = BOARD_X + BOARD_WIDTH + 40

# ---------------------------------
# COLORS
# ---------------------------------

WHITE = (255,255,255)
BLACK = (0,0,0)
CYAN = (0,255,255)
GREEN = (0,255,0)

# ---------------------------------
# ASSET PATHS
# ---------------------------------

def get_resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

GFX = get_resource_path("assets/Graphics")
SFX = get_resource_path("assets/Audio")

# ---------------------------------
# IMAGE LOADER
# ---------------------------------

def load_image(name, size=None):

    img = pygame.image.load(os.path.join(GFX, name)).convert_alpha()

    if size:
        img = pygame.transform.smoothscale(img, size)

    return img

# ---------------------------------
# LOAD IMAGES
# ---------------------------------

BLOCK = load_image("unit.png",(CELL,CELL))

PAUSE_IMG = load_image("pause.png")
GAMEOVER_IMG = load_image("gameOver.png")
CONTROL_IMG = load_image("keysControl.png")

PAUSE_IMG = fit(PAUSE_IMG,300,120)
GAMEOVER_IMG = fit(GAMEOVER_IMG,350,180)
CONTROL_IMG = fit(CONTROL_IMG,340,220)

# ---------------------------------
# LOAD SOUNDS
# ---------------------------------

pygame.mixer.music.load(os.path.join(SFX,"bg-music.mp3"))
pygame.mixer.music.play(-1)

move_left_sound = pygame.mixer.Sound(os.path.join(SFX,"blockMoveLeft.wav"))
move_right_sound = pygame.mixer.Sound(os.path.join(SFX,"blockMoveRight.wav"))
rotate_sound = pygame.mixer.Sound(os.path.join(SFX,"blockRotate.wav"))
line_sound = pygame.mixer.Sound(os.path.join(SFX,"lineKill.wav"))
gameover_sound = pygame.mixer.Sound(os.path.join(SFX,"gameOver.wav"))

# ---------------------------------
# SIMPLE FONT
# ---------------------------------

font = pygame.font.SysFont("Consolas",28)
small = pygame.font.SysFont("Consolas",20)

# ---------------------------------
# TETROMINOES
# ---------------------------------

SHAPES = [

[[1,1,1,1]],

[[1,1],
 [1,1]],

[[0,1,0],
 [1,1,1]],

[[1,0,0],
 [1,1,1]],

[[0,0,1],
 [1,1,1]],

[[1,1,0],
 [0,1,1]],

[[0,1,1],
 [1,1,0]]

]

# ---------------------------------
# PIECE CLASS
# ---------------------------------

class Piece:

    def __init__(self, shape=None):

        if shape is None:
            self.index = random.randrange(len(SHAPES))
            self.shape = SHAPES[self.index]
            self.image = make_block(COLORS[self.index])

        else:
            self.shape = shape
            self.index = SHAPES.index(shape)
            self.image = make_block(COLORS[self.index])

        self.x = 3
        self.y = 0

    def cells(self):

        cells=[]

        for y,row in enumerate(self.shape):
            for x,val in enumerate(row):
                if val:
                    cells.append((self.x+x,self.y+y))

        return cells

    def rotate(self):

        rows=len(self.shape)
        cols=len(self.shape[0])

        new=[]

        for x in range(cols):

            row=[]

            for y in range(rows-1,-1,-1):

                row.append(self.shape[y][x])

            new.append(row)

        self.shape=new

# ---------------------------------
# BOARD
# ---------------------------------

board=[[0 for _ in range(COLS)] for _ in range(ROWS)]

current=Piece()
next_piece=Piece()

score=0
lines=0
level=1

fall_timer=0
fall_speed=600

running=True

MENU=0
PLAY=1
PAUSE=2
GAMEOVER=3

state=MENU

# ---------------------------------
# COLLISION
# ---------------------------------

def valid(piece):

    for x, y in piece.cells():

        if x < 0 or x >= COLS:
            return False

        if y >= ROWS:
            return False

        if y >= 0 and board[y][x]:
            return False

    return True


# ---------------------------------
# LOCK PIECE
# ---------------------------------

def lock_piece(piece):

    global current, next_piece, state

    for x, y in piece.cells():

        if y < 0:
            state = GAMEOVER
            gameover_sound.play()
            return

        board[y][x] = piece.index + 1

    clear_lines()

    current = next_piece
    next_piece = Piece()

    if not valid(current):
        state = GAMEOVER
        gameover_sound.play()

# ---------------------------------
# CLEAR LINES
# ---------------------------------

def clear_lines():

    global board
    global score
    global lines
    global level
    global fall_speed

    new_board = []
    cleared = 0

    for row in board:

        if 0 not in row:
            cleared += 1
        else:
            new_board.append(row)

    while len(new_board) < ROWS:
        new_board.insert(0, [0] * COLS)

    board = new_board

    if cleared > 0:

        line_sound.play()

        lines += cleared

        score += [0, 100, 300, 500, 800][cleared] * level

        level = lines // 10 + 1

        fall_speed = max(80, 600 - (level - 1) * 40)


# ---------------------------------
# MOVE
# ---------------------------------

def move(dx):

    current.x += dx

    if not valid(current):
        current.x -= dx
        return

    if dx < 0:
        move_left_sound.play()

    if dx > 0:
        move_right_sound.play()


# ---------------------------------
# ROTATE
# ---------------------------------

def rotate():

    old = [row[:] for row in current.shape]

    current.rotate()

    if not valid(current):
        current.shape = old
    else:
        rotate_sound.play()


# ---------------------------------
# SOFT DROP
# ---------------------------------

def soft_drop():

    current.y += 1

    if not valid(current):

        current.y -= 1

        lock_piece(current)


# ---------------------------------
# HARD DROP
# ---------------------------------

def hard_drop():

    while True:

        current.y += 1

        if not valid(current):

            current.y -= 1

            lock_piece(current)

            break


# ---------------------------------
# GHOST PIECE
# ---------------------------------

def ghost_y():

    test = Piece()

    test.shape = [row[:] for row in current.shape]

    test.x = current.x
    test.y = current.y

    while True:

        test.y += 1

        if not valid(test):

            test.y -= 1

            return test.y


# ---------------------------------
# RESTART GAME
# ---------------------------------

def reset_game():

    global board
    global current
    global next_piece
    global score
    global level
    global lines
    global fall_speed
    global state

    board = [[0] * COLS for _ in range(ROWS)]

    current = Piece()
    next_piece = Piece()

    score = 0
    level = 1
    lines = 0

    fall_speed = 600

    state = PLAY
    
# ---------------------------------
# DRAW TEXT
# ---------------------------------

def draw_text(text, x, y, color=WHITE, use_small=False):
    img = small.render(str(text), True, color) if use_small else font.render(str(text), True, color)
    screen.blit(img, (x, y))


# ---------------------------------
# DRAW PIECE
# ---------------------------------

def draw_piece(piece):

    for x, y in piece.cells():

        if y >= 0:
            screen.blit(
                piece.image,
                (
                    BOARD_X + x * CELL,
                    BOARD_Y + y * CELL
                )
            )


# ---------------------------------
# DRAW GHOST PIECE
# ---------------------------------

def draw_ghost():

    gy = ghost_y()

    ghost = pygame.Surface((CELL, CELL), pygame.SRCALPHA)
    ghost.fill((255, 255, 255, 70))

    for yy, row in enumerate(current.shape):
        for xx, value in enumerate(row):

            if value:

                screen.blit(
                    ghost,
                    (
                        BOARD_X + (current.x + xx) * CELL,
                        BOARD_Y + (gy + yy) * CELL
                    )
                )


# ---------------------------------
# DRAW LOCKED BLOCKS
# ---------------------------------

def draw_well():
    # Draw background of the well
    pygame.draw.rect(screen, (0, 0, 0), (BOARD_X, BOARD_Y, BOARD_WIDTH, BOARD_HEIGHT))
    # Draw border
    pygame.draw.rect(screen, WHITE, (BOARD_X, BOARD_Y, BOARD_WIDTH, BOARD_HEIGHT), 2)

def draw_board():
    # Replace the WELL blit with the function call
    draw_well()

    for y in range(ROWS):
        for x in range(COLS):
            if board[y][x]:
                color = COLORS[board[y][x] - 1]
                screen.blit(
                    make_block(color),
                    (
                        BOARD_X + x * CELL,
                        BOARD_Y + y * CELL
                    )
                )

# ---------------------------------
# DRAW NEXT PIECE
# ---------------------------------

def draw_next():

    draw_text("NEXT", SIDE_X, 30)

    start_x = SIDE_X
    start_y = 80

    for y, row in enumerate(next_piece.shape):
        for x, value in enumerate(row):

            if value:

                screen.blit(
                    next_piece.image,
                    (
                        start_x + x * CELL,
                        start_y + y * CELL
                    )
                )


# ---------------------------------
# DRAW SCORE
# ---------------------------------

def draw_stats():

    draw_text("Score", SIDE_X, 220)
    draw_text(score, SIDE_X, 255)

    draw_text("Lines", SIDE_X, 320)
    draw_text(lines, SIDE_X, 355)

    draw_text("Level", SIDE_X, 420)
    draw_text(level, SIDE_X, 455)


# ---------------------------------
# CENTER IMAGE
# ---------------------------------

def draw_center(image, y):

    x = (WIDTH - image.get_width()) // 2
    screen.blit(image, (x, y))


# ---------------------------------
# DRAW MENU
# ---------------------------------

def draw_menu():

    screen.fill(BLACK)

    draw_text("TETRIS", WIDTH // 2 - 70, 50)

    draw_center(CONTROL_IMG, 140)

    draw_text("Press ENTER", WIDTH // 2 - 90, 560)


# ---------------------------------
# DRAW PAUSE
# ---------------------------------

def draw_pause():

    draw_center(PAUSE_IMG, 150)


# ---------------------------------
# DRAW GAME OVER
# ---------------------------------

def draw_game_over():
    
    screen.fill(BLACK)
    
    draw_center(GAMEOVER_IMG, 120)

    draw_text(f"Score : {score}", WIDTH // 2 - 70, 330)

    draw_text("Press R to Restart", WIDTH // 2 - 120, 390)


# ---------------------------------
# DRAW GAME
# ---------------------------------

def draw_game():

    screen.fill((20, 20, 20))

    draw_board()

    draw_ghost()

    draw_piece(current)

    draw_next()

    draw_stats()
    
# ---------------------------------
# MAIN LOOP
# ---------------------------------

while running:

    dt = clock.tick(FPS)
    fall_timer += dt

    # ----------------------------
    # EVENTS
    # ----------------------------

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:

            # ---------------- MENU ----------------

            if state == MENU:

                if event.key == pygame.K_RETURN:
                    reset_game()

            # ---------------- PLAY ----------------

            elif state == PLAY:

                if event.key == pygame.K_LEFT:
                    move(-1)

                elif event.key == pygame.K_RIGHT:
                    move(1)

                elif event.key == pygame.K_DOWN:
                    soft_drop()

                elif event.key == pygame.K_UP:
                    rotate()

                elif event.key == pygame.K_SPACE:
                    hard_drop()

                elif event.key == pygame.K_p:
                    state = PAUSE

                elif event.key == pygame.K_ESCAPE:
                    running = False

            # ---------------- PAUSE ----------------

            elif state == PAUSE:

                if event.key == pygame.K_p:
                    state = PLAY

                elif event.key == pygame.K_ESCAPE:
                    running = False

            # ---------------- GAME OVER ----------------

            elif state == GAMEOVER:

                if event.key == pygame.K_r:
                    reset_game()

                elif event.key == pygame.K_ESCAPE:
                    running = False

    # ----------------------------
    # AUTO FALL
    # ----------------------------

    if state == PLAY:

        if fall_timer >= fall_speed:

            fall_timer = 0

            current.y += 1

            if not valid(current):

                current.y -= 1

                lock_piece(current)

    # ----------------------------
    # DRAW
    # ----------------------------

    if state == MENU:

        draw_menu()

    elif state == PLAY:

        draw_game()

    elif state == PAUSE:

        draw_game()
        draw_pause()

    elif state == GAMEOVER:

        draw_game()
        draw_game_over()

    pygame.display.flip()

pygame.quit()
sys.exit()
