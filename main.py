import pygame  # 游戏引擎库
import random  # 用来随机生成柱子的位置
import os      # 用来设置排行榜文件路径

# ============================================================
# 1. 游戏常量(设置)
# ============================================================
# 把"魔法数字"放在最上面,方便以后调整
WINDOW_WIDTH = 400          # 窗口宽度(像素)
WINDOW_HEIGHT = 600         # 窗口高度
FPS = 60                    # 每秒帧数(画面流畅度)
 
# colour (R, G, B)
SKY_BLUE = (135, 206, 235)  # sky_blue
WHITE = (255, 255, 255)     # word_white
BLACK = (0, 0, 0)           # word_black

# ui colours
PANEL_BG = (255, 250, 235)
PANEL_BORDER = (70, 70, 70)
SHADOW = (90, 90, 90)
TITLE_BLUE = (35, 80, 130)
BUTTON_BG = (235, 235, 220)
BUTTON_BORDER = (90, 90, 90)

# Menu UI accent colours
AU_ACCENT = (95, 155, 210)        # Soft sky blue
AU_ACCENT_DARK = (55, 105, 160)
CN_ACCENT = (195, 55, 65)
CN_ACCENT_DARK = (135, 30, 40)
EG_ACCENT = (215, 165, 55)
EG_ACCENT_DARK = (155, 110, 30)

TAG_PINK = (240, 90, 110)
SUBTITLE_GREY = (95, 95, 105)
GRADIENT_TOP = (220, 235, 250)
GRADIENT_BOTTOM = (255, 215, 185)
INPUT_BG = (255, 255, 255)

# aus_theme
ROAD_GREY = (80, 80, 80)
ROAD_LINE = (245, 245, 245)
KANGAROO_BROWN = (150, 90, 40)
KANGAROO_DARK = (95, 55, 25)
POLE_GREY = (120, 120, 120)
BUTTON_BOX = (30, 30, 30)
RED_BUTTON = (220, 40, 40)
GREEN_BUTTON = (40, 180, 70)
OPERA_WHITE = (245, 245, 235)
KANGAROO_LIGHT = (205, 155, 95)  # light belly colour
KANGAROO_LIGHT = (205, 155, 105)   # belly colour
KANGAROO_NOSE = (35, 25, 20)

# china_theme
CHINA_SKY = (225, 245, 220)
MOUNTAIN_LIGHT = (150, 190, 150)
MOUNTAIN_DARK = (90, 140, 100)
BAMBOO_GREEN = (40, 150, 60)
BAMBOO_DARK = (20, 100, 40)
PANDA_WHITE = (245, 245, 245)
PANDA_BLACK = (20, 20, 20)

# egypt_theme
EGYPT_SKY = (245, 205, 120)
SAND = (220, 180, 95)
SAND_DARK = (180, 130, 60)
PYRAMID = (190, 145, 75)
PYRAMID_DARK = (130, 90, 45)
CAMEL_BROWN = (150, 95, 45)
CAMEL_DARK = (100, 60, 30)
MUMMY_BANDAGE = (230, 215, 180)
MUMMY_LINE = (130, 100, 70)
SUN_ORANGE = (255, 150, 50)

# 小鸟相关参数
BIRD_X = 80                 # 小鸟固定的 x 坐标(它只会上下动)
BIRD_SIZE = 30              # 小鸟的大小(正方形边长)
GRAVITY = 0.5               # 重力加速度(每帧速度增加多少)
JUMP_STRENGTH = -9          # 跳跃力度(负值表示向上)
 
# 柱子相关参数
PIPE_WIDTH = 60             # 柱子宽度
PIPE_GAP = 135             # 上下柱子之间的缝隙大小(给小鸟穿过)
PIPE_SPEED = 3              # 柱子向左移动的速度
PIPE_SPACING = 250          # 两根柱子之间的水平间距
 
# Leaderboard settings
# Theme settings
THEMES = {
    "Australia": {"name": "Australia","code": "AU"},
    "China": {"name": "China", "code": "CN"},
    "Egypt": {"name": "Egypt", "code": "EG"}
}

current_theme = THEMES["Australia"]

# Save leaderboard.txt in the same folder as this Python file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LEADERBOARD_FILE = os.path.join(BASE_DIR, "leaderboard.txt") 
# ============================================================
# 2. 初始化 PyGame
# ============================================================
pygame.init()  # 启动 pygame
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))  # 创建窗口
pygame.display.set_caption("World Jumper")  # 窗口标题
clock = pygame.time.Clock()  # 时钟,用来控制帧率
font = pygame.font.SysFont("Arial", 36, bold=True)  # 用于显示分数的字体
small_font = pygame.font.SysFont("Arial", 22, bold=True)  # 用于显示小文字
tiny_font = pygame.font.SysFont("Arial", 16, bold=True)  # 用于排行榜
title_font = pygame.font.SysFont("Arial", 44, bold=True)  # For big titles

# Load character images
KANGAROO_IMAGE_PATH = os.path.join(BASE_DIR, "kangaroo.png")

# Load images
def load_character_image(filename, size):
    """
    Load and resize a character image.
    If the image file is missing, return None so the game can still run.
    """
    image_path = os.path.join(BASE_DIR, filename)

    try:
        image = pygame.image.load(image_path).convert_alpha()
        image = pygame.transform.smoothscale(image, size)
        return image

    except FileNotFoundError:
        return None


def load_obstacle_image(filename, crop_top=0, crop_bottom=0, crop_left=0, crop_right=0):
    """
    Load an obstacle image and crop extra empty space around it.
    """
    image_path = os.path.join(BASE_DIR, filename)

    try:
        image = pygame.image.load(image_path).convert_alpha()

        # First crop transparent padding
        rect = image.get_bounding_rect()
        if rect.width > 0 and rect.height > 0:
            image = image.subsurface(rect).copy()

        # Then manually crop extra space if needed
        w, h = image.get_size()

        crop_rect = pygame.Rect(
            crop_left,
            crop_top,
            w - crop_left - crop_right,
            h - crop_top - crop_bottom
        )

        image = image.subsurface(crop_rect).copy()

        return image

    except FileNotFoundError:
        return None

start_bg_image = load_character_image("start_bg.png", (WINDOW_WIDTH, WINDOW_HEIGHT))

kangaroo_image = load_character_image("kangaroo.png", (58, 58))
panda_image = load_character_image("panda.png", (58, 58))
camel_image = load_character_image("camel.png", (64, 58))

australia_obstacle_image = load_obstacle_image("australia_obstacle.png", crop_top=120, crop_bottom=120, crop_left=5, crop_right=5)
egypt_obstacle_image = load_obstacle_image("egypt_obstacle.png", crop_top=120, crop_bottom=220, crop_left=80, crop_right=80)
china_obstacle_image = load_obstacle_image("china_obstacle.png", crop_top=220, crop_bottom=120, crop_left=240, crop_right=240)

australia_bg_image = load_character_image("australia_bg.png", (WINDOW_WIDTH, WINDOW_HEIGHT))
china_bg_image = load_character_image("china_bg.png", (WINDOW_WIDTH, WINDOW_HEIGHT))
egypt_bg_image = load_character_image("egypt_bg.png", (WINDOW_WIDTH, WINDOW_HEIGHT))
# ===========================================================40
# 3. 游戏状态变量
# ============================================================
# Player object
player = None
 
# 柱子列表 - 每根柱子是一个字典 {"x": 横坐标, "gap_y": 缝隙中心y, "passed": 是否已经过}
pipes = []
 
# 游戏分数
score = 0
 
# 游戏状态:True=进行中,False=游戏结束
game_running = False

start_screen = True
selecting_theme = False
entering_name = False # input name
player_name = ""
# Used to prevent saving the same score many times after game over
score_saved = False 
# ============================================================
# 4. 辅助函数
# ============================================================ 
 
def reset_game():
    """Reset the game to the starting state."""
    global player, pipes, score, game_running, score_saved

    player = Player()
    pipes = [Obstacle(WINDOW_WIDTH + 100)]  # first obstacle starts outside the screen
    score = 0
    game_running = True
    score_saved = False

def load_leaderboard():
    """
    Read all saved scores from leaderboard.txt.
    Return a list of dictionaries.
    """
    records = []

    try:
        with open(LEADERBOARD_FILE, "r") as file:
            for line in file:
                line = line.strip()

                if line == "":
                    continue

                try:
                    name, theme, score_text = line.split(",")
                    records.append({"name": name, "theme": theme, "score": int(score_text)})
                except ValueError:
                    # Skip broken lines instead of crashing the game
                    continue

    except FileNotFoundError:
        # First time running the game, so no leaderboard file exists yet
        return []

    return records


def save_score(name, theme, final_score):
    """
    Save the player's score into leaderboard.txt.
    Only the top 10 scores will be kept in the file.
    """
    safe_name = name.replace(",", " ").strip()

    if safe_name == "":
        safe_name = "Player"

    # 1. Load old scores
    records = load_leaderboard()

    # 2. Add the new score
    records.append({
        "name": safe_name,
        "theme": theme,
        "score": final_score
    })

    # 3. Sort from highest score to lowest score
    records.sort(key=lambda record: record["score"], reverse=True)

    # 4. Keep only top 10 records
    top_records = records[:10]

    # 5. Rewrite the file with only top 10 records
    with open(LEADERBOARD_FILE, "w") as file:
        for record in top_records:
            file.write(f"{record['name']},{record['theme']},{record['score']}\n")

def draw_start_screen():
    """
    Draw the opening start screen.
    The background image already contains the title and design.
    Only keep one blinking start instruction.
    """
    # Draw start background image
    if start_bg_image is not None:
        screen.blit(start_bg_image, (0, 0))
    else:
        draw_gradient_background((215, 235, 250), (170, 205, 235))



    # Blinking start text
    if pygame.time.get_ticks() // 500 % 2 == 0:
        draw_center_text(
            "Press SPACE to start",
            small_font,
            (60, 60, 60),
            WINDOW_WIDTH // 2 + 2,
            502
        )
        draw_center_text(
            "Press SPACE to start",
            small_font,
            WHITE,
            WINDOW_WIDTH // 2,
            500
        )

def get_top_scores():
    """
    Return the top 10 scores from highest to lowest.
    """
    records = load_leaderboard()
    records.sort(key=lambda record: record["score"], reverse=True)
    return records[:10]


def end_game():
    """
    End the game and save the player's score once.
    """
    global game_running, score_saved

    game_running = False

    if not score_saved:
        save_score(player_name, current_theme["name"], score)
        score_saved = True

def draw_australia_background():
    """
    绘制澳洲主题背景:
    蓝天、马路、白色虚线和简单的悉尼歌剧院剪影。
    """
    if australia_bg_image is not None:
        screen.blit(australia_bg_image, (0, 0))
        return
    
    # 天空
    screen.fill(SKY_BLUE)

    # 简单太阳
    pygame.draw.circle(screen, (255, 220, 80), (330, 70), 35)

    # 悉尼歌剧院简化版
    base_y = WINDOW_HEIGHT - 95
    pygame.draw.polygon(screen, OPERA_WHITE, [(235, base_y), (260, base_y - 55), (285, base_y)])
    pygame.draw.polygon(screen, OPERA_WHITE, [(270, base_y), (300, base_y - 70), (330, base_y)])
    pygame.draw.polygon(screen, OPERA_WHITE, [(305, base_y), (330, base_y - 45), (355, base_y)])
    pygame.draw.rect(screen, (180, 180, 170), (230, base_y, 130, 8))

    # 马路
    pygame.draw.rect(screen, ROAD_GREY, (0, WINDOW_HEIGHT - 90, WINDOW_WIDTH, 90))

    # 马路白色虚线
    for x in range(0, WINDOW_WIDTH, 80):
        pygame.draw.rect(screen, ROAD_LINE, (x, WINDOW_HEIGHT - 48, 45, 6))

def draw_china_background():
    """
    Draw a simple Chinese ink-style mountain background.
    """
    if china_bg_image is not None:
        screen.blit(china_bg_image, (0, 0))
        return
    screen.fill(CHINA_SKY)

    # distant mountains
    pygame.draw.polygon(screen, MOUNTAIN_LIGHT, [(0, 360), (90, 230), (180, 360)])
    pygame.draw.polygon(screen, MOUNTAIN_LIGHT, [(120, 360), (230, 210), (340, 360)])
    pygame.draw.polygon(screen, MOUNTAIN_LIGHT, [(260, 360), (360, 240), (440, 360)])

    # front mountains
    pygame.draw.polygon(screen, MOUNTAIN_DARK, [(0, 430), (120, 280), (240, 430)])
    pygame.draw.polygon(screen, MOUNTAIN_DARK, [(180, 430), (310, 260), (430, 430)])

    # ground
    pygame.draw.rect(screen, (120, 170, 110), (0, WINDOW_HEIGHT - 90, WINDOW_WIDTH, 90))

    # simple mist lines
    for y in [150, 190, 230]:
        pygame.draw.line(screen, (200, 220, 200), (30, y), (370, y), 2)

def draw_egypt_background():
    """
    Draw an Egypt desert background with sun and pyramids.
    """
    if egypt_bg_image is not None:
        screen.blit(egypt_bg_image, (0, 0))
        return
    screen.fill(EGYPT_SKY)

    # sun
    pygame.draw.circle(screen, SUN_ORANGE, (330, 80), 40)

    # distant pyramids
    pygame.draw.polygon(screen, PYRAMID, [(30, 420), (130, 240), (230, 420)])
    pygame.draw.polygon(screen, PYRAMID_DARK, [(130, 240), (230, 420), (160, 420)])

    pygame.draw.polygon(screen, PYRAMID, [(180, 430), (290, 260), (400, 430)])
    pygame.draw.polygon(screen, PYRAMID_DARK, [(290, 260), (400, 430), (330, 430)])

    # desert ground
    pygame.draw.rect(screen, SAND, (0, WINDOW_HEIGHT - 90, WINDOW_WIDTH, 90))

    # simple sand lines
    for x in range(0, WINDOW_WIDTH, 80):
        pygame.draw.arc(screen, SAND_DARK, (x, WINDOW_HEIGHT - 75, 90, 30), 0, 3.14, 2)

def draw_obstacle_image(image, rect, image_width, image_offset, align_bottom=False):
    """
    Draw an obstacle image without squeezing its height.
    The image keeps its original ratio and is clipped to the obstacle rectangle.
    """
    original_width, original_height = image.get_size()

    scale_ratio = image_width / original_width
    scaled_height = int(original_height * scale_ratio)

    scaled_image = pygame.transform.smoothscale(
        image,
        (image_width, scaled_height)
    )

    image_x = rect.x - image_offset

    old_clip = screen.get_clip()
    screen.set_clip(pygame.Rect(image_x, rect.y, image_width, rect.height))

    if align_bottom:
        y = rect.bottom - scaled_height
        while y > rect.y:
            screen.blit(scaled_image, (image_x, y))
            y -= scaled_height
        screen.blit(scaled_image, (image_x, y))
    else:
        y = rect.y
        while y < rect.bottom:
            screen.blit(scaled_image, (image_x, y))
            y += scaled_height

    screen.set_clip(old_clip)

def draw_crossing_pole(top_rect, bottom_rect):
    """
    Draw Australia obstacle.
    If australia_obstacle.png exists, use the image.
    Otherwise, draw the original hand-drawn crossing pole.
    """
    if australia_obstacle_image is not None:
        # Keep this small so the pole is not too wide
        image_width = top_rect.width - 4
        image_offset = 0

        if top_rect.height > 0:
            draw_obstacle_image(
                australia_obstacle_image,
                top_rect,
                image_width,
                image_offset,
                align_bottom=True
            )

        if bottom_rect.height > 0:
            draw_obstacle_image(
                australia_obstacle_image,
                bottom_rect,
                image_width,
                image_offset,
                align_bottom=False
            )

        return

    # Fallback: original simple crossing pole
    pygame.draw.rect(screen, POLE_GREY, top_rect)
    pygame.draw.rect(screen, POLE_GREY, bottom_rect)

    pygame.draw.rect(screen, BLACK, top_rect, 2)
    pygame.draw.rect(screen, BLACK, bottom_rect, 2)

    if top_rect.height > 65:
        box_x = top_rect.x + 10
        box_y = top_rect.bottom - 55
        pygame.draw.rect(screen, BUTTON_BOX, (box_x, box_y, 40, 35))
        pygame.draw.circle(screen, RED_BUTTON, (box_x + 20, box_y + 18), 8)

    if bottom_rect.height > 65:
        box_x = bottom_rect.x + 10
        box_y = bottom_rect.y + 20
        pygame.draw.rect(screen, BUTTON_BOX, (box_x, box_y, 40, 35))
        pygame.draw.circle(screen, GREEN_BUTTON, (box_x + 20, box_y + 18), 8)

def draw_bamboo(top_rect, bottom_rect):
    """
    Draw bamboo obstacles for the China theme.
    If china_obstacle.png exists, use the image.
    Otherwise, draw simple bamboo with pygame shapes.
    """
    if china_obstacle_image is not None:
        image_width = top_rect.width + 40
        image_offset = 20

        if top_rect.height > 0:
            draw_obstacle_image(
                china_obstacle_image,
                top_rect,
                image_width,
                image_offset,
                align_bottom=True
            )

        if bottom_rect.height > 0:
            draw_obstacle_image(
                china_obstacle_image,
                bottom_rect,
                image_width,
                image_offset,
                align_bottom=False
            )

        return

    # Fallback: old hand-drawn bamboo
    pygame.draw.rect(screen, BAMBOO_GREEN, top_rect)
    pygame.draw.rect(screen, BAMBOO_GREEN, bottom_rect)

    pygame.draw.rect(screen, BAMBOO_DARK, top_rect, 3)
    pygame.draw.rect(screen, BAMBOO_DARK, bottom_rect, 3)

    y = top_rect.y
    while y < top_rect.y + top_rect.height:
        pygame.draw.line(screen, BAMBOO_DARK, (top_rect.x, y), (top_rect.x + top_rect.width, y), 3)
        y += 35

    y = bottom_rect.y
    while y < bottom_rect.y + bottom_rect.height:
        pygame.draw.line(screen, BAMBOO_DARK, (bottom_rect.x, y), (bottom_rect.x + bottom_rect.width, y), 3)
        y += 35


def draw_kangaroo(x, y):
    """
    Draw the kangaroo player.
    If kangaroo.png exists, use the image.
    Otherwise, draw a simple fallback kangaroo.
    """
    x = int(x)
    y = int(y)

    if kangaroo_image is not None:
        # Draw kangaroo image
        screen.blit(kangaroo_image, (x - 14, y - 18))
    else:
        # Fallback if image is missing
        pygame.draw.ellipse(screen, KANGAROO_BROWN, (x + 2, y + 16, 30, 22))
        pygame.draw.line(screen, KANGAROO_DARK, (x + 7, y + 28), (x - 18, y + 38), 6)
        pygame.draw.ellipse(screen, KANGAROO_BROWN, (x + 27, y + 5, 17, 13))
        pygame.draw.circle(screen, BLACK, (x + 38, y + 10), 2)

def draw_panda(x, y):
    """
    Draw the panda player.
    If panda.png exists, use the image.
    Otherwise, draw a simple fallback panda.
    """
    x = int(x)
    y = int(y)

    if panda_image is not None:
        # Draw panda image
        screen.blit(panda_image, (x - 14, y - 18))
    else:
        # Fallback simple panda
        pygame.draw.circle(screen, PANDA_BLACK, (x + 8, y + 6), 7)
        pygame.draw.circle(screen, PANDA_BLACK, (x + 25, y + 6), 7)

        pygame.draw.circle(screen, PANDA_WHITE, (x + 17, y + 17), 17)
        pygame.draw.circle(screen, BLACK, (x + 17, y + 17), 17, 2)

        pygame.draw.circle(screen, PANDA_BLACK, (x + 10, y + 15), 5)
        pygame.draw.circle(screen, PANDA_BLACK, (x + 24, y + 15), 5)

        pygame.draw.circle(screen, WHITE, (x + 10, y + 15), 2)
        pygame.draw.circle(screen, WHITE, (x + 24, y + 15), 2)

        pygame.draw.circle(screen, PANDA_BLACK, (x + 17, y + 24), 3)

        pygame.draw.ellipse(screen, PANDA_WHITE, (x + 3, y + 28, 28, 22))
        pygame.draw.ellipse(screen, BLACK, (x + 3, y + 28, 28, 22), 2)

def draw_camel(x, y):
    """
    Draw the camel player.
    If camel.png exists, use the image.
    Otherwise, draw a simple fallback camel.
    """
    x = int(x)
    y = int(y)

    if camel_image is not None:
        # Draw camel image
        screen.blit(camel_image, (x - 16, y - 18))
    else:
        # Fallback simple camel
        pygame.draw.ellipse(screen, CAMEL_BROWN, (x + 2, y + 18, 34, 18))
        pygame.draw.circle(screen, CAMEL_BROWN, (x + 18, y + 17), 10)

        pygame.draw.rect(screen, CAMEL_BROWN, (x + 31, y + 8, 7, 20))
        pygame.draw.circle(screen, CAMEL_BROWN, (x + 42, y + 8), 8)

        pygame.draw.rect(screen, CAMEL_DARK, (x + 8, y + 33, 5, 16))
        pygame.draw.rect(screen, CAMEL_DARK, (x + 25, y + 33, 5, 16))

        pygame.draw.circle(screen, BLACK, (x + 44, y + 6), 2)


def draw_mummy_pole(top_rect, bottom_rect):
    """
    Draw Egypt obstacle.
    If egypt_obstacle.png exists, use the image.
    Otherwise, draw a simple mummy-wrapped pole with pygame shapes.
    """
    if egypt_obstacle_image is not None:
        # Egypt image looks better when it is slightly wider than the collision rect
        image_width = top_rect.width + 60
        image_offset = 30

        # Top obstacle
        if top_rect.height > 0:
            top_image = pygame.transform.smoothscale(
                egypt_obstacle_image,
                (image_width, top_rect.height)
            )
            screen.blit(top_image, (top_rect.x - image_offset, top_rect.y))

        # Bottom obstacle
        if bottom_rect.height > 0:
            bottom_image = pygame.transform.smoothscale(
                egypt_obstacle_image,
                (image_width, bottom_rect.height)
            )
            screen.blit(bottom_image, (bottom_rect.x - image_offset, bottom_rect.y))

        return

    # Fallback only runs if the PNG is missing
    pygame.draw.rect(screen, MUMMY_BANDAGE, top_rect)
    pygame.draw.rect(screen, MUMMY_BANDAGE, bottom_rect)

    pygame.draw.rect(screen, MUMMY_LINE, top_rect, 3)
    pygame.draw.rect(screen, MUMMY_LINE, bottom_rect, 3)

    y = top_rect.y
    while y < top_rect.y + top_rect.height:
        pygame.draw.line(
            screen,
            MUMMY_LINE,
            (top_rect.x, y),
            (top_rect.x + top_rect.width, y + 20),
            3
        )
        y += 35

    y = bottom_rect.y
    while y < bottom_rect.y + bottom_rect.height:
        pygame.draw.line(
            screen,
            MUMMY_LINE,
            (bottom_rect.x, y),
            (bottom_rect.x + bottom_rect.width, y + 20),
            3
        )
        y += 35

def draw_current_background():
    """Draw the background for the selected theme."""
    if current_theme["name"] == "Australia":
        draw_australia_background()
    elif current_theme["name"] == "China":
        draw_china_background()
    elif current_theme["name"] == "Egypt":
        draw_egypt_background()


def draw_current_player(x, y):
    """Draw the player for the selected theme."""
    if current_theme["name"] == "Australia":
        draw_kangaroo(x, y)
    elif current_theme["name"] == "China":
        draw_panda(x, y)
    elif current_theme["name"] == "Egypt":
        draw_camel(x, y)


def draw_current_obstacle(top_rect, bottom_rect):
    """Draw the obstacle for the selected theme."""
    if current_theme["name"] == "Australia":
        draw_crossing_pole(top_rect, bottom_rect)
    elif current_theme["name"] == "China":
        draw_bamboo(top_rect, bottom_rect)
    elif current_theme["name"] == "Egypt":
        draw_mummy_pole(top_rect, bottom_rect)

def draw_gradient_background(top_colour=GRADIENT_TOP, bottom_colour=GRADIENT_BOTTOM):
    """Draw a soft vertical gradient background for menu screens."""
    for y in range(WINDOW_HEIGHT):
        ratio = y / WINDOW_HEIGHT
        r = int(top_colour[0] + (bottom_colour[0] - top_colour[0]) * ratio)
        g = int(top_colour[1] + (bottom_colour[1] - top_colour[1]) * ratio)
        b = int(top_colour[2] + (bottom_colour[2] - top_colour[2]) * ratio)
        pygame.draw.line(screen, (r, g, b), (0, y), (WINDOW_WIDTH, y))

def draw_project_tag(center_x, y):
    """Draw a small pink badge that says 9001 FINAL PROJECT."""
    tag_text = tiny_font.render("COMP9001 FINAL PROJECT", True, WHITE)
    tag_w = tag_text.get_width() + 24
    tag_h = tag_text.get_height() + 10
    tag_x = center_x - tag_w // 2
    pygame.draw.rect(screen, TAG_PINK, (tag_x, y, tag_w, tag_h), border_radius=12)
    screen.blit(tag_text, (tag_x + 12, y + 5))

def draw_mini_icon(theme_key, cx, cy):
    """Draw a tiny icon representing a theme. Used on theme buttons."""
    cx, cy = int(cx), int(cy)
    if theme_key == "Australia":
        # Mini kangaroo head
        pygame.draw.polygon(screen, WHITE, [(cx - 6, cy - 6), (cx - 8, cy - 17), (cx - 2, cy - 6)])
        pygame.draw.polygon(screen, WHITE, [(cx + 2, cy - 6), (cx + 8, cy - 17), (cx + 6, cy - 6)])
        pygame.draw.circle(screen, WHITE, (cx, cy + 2), 12)
        pygame.draw.circle(screen, BLACK, (cx + 4, cy), 2)
    elif theme_key == "China":
        # Mini panda head
        pygame.draw.circle(screen, BLACK, (cx - 8, cy - 9), 5)
        pygame.draw.circle(screen, BLACK, (cx + 8, cy - 9), 5)
        pygame.draw.circle(screen, WHITE, (cx, cy + 2), 12)
        pygame.draw.circle(screen, BLACK, (cx - 5, cy), 3)
        pygame.draw.circle(screen, BLACK, (cx + 5, cy), 3)
        pygame.draw.circle(screen, BLACK, (cx, cy + 5), 2)
    elif theme_key == "Egypt":
        # Mini pyramid
        pygame.draw.polygon(screen, WHITE, [(cx, cy - 13), (cx - 14, cy + 11), (cx + 14, cy + 11)])
        pygame.draw.polygon(screen, (200, 200, 200),
                            [(cx, cy - 13), (cx, cy + 11), (cx + 14, cy + 11)])

def draw_theme_button(y, key_num, theme_key, theme_name, description, accent, accent_dark, icon_image=None):
    """Draw a single themed selection button."""
    btn_x = 45
    btn_w = 310
    btn_h = 78

    # Shadow
    pygame.draw.rect(screen, SHADOW, (btn_x + 4, y + 4, btn_w, btn_h), border_radius=14)
    # White card
    pygame.draw.rect(screen, WHITE, (btn_x, y, btn_w, btn_h), border_radius=14)
    # Coloured left panel (icon area)
    pygame.draw.rect(screen, accent, (btn_x, y, 70, btn_h),
                     border_top_left_radius=14, border_bottom_left_radius=14)
    # Outer border
    pygame.draw.rect(screen, accent_dark, (btn_x, y, btn_w, btn_h), 3, border_radius=14)

    # Icon
    if icon_image is not None:
        icon_size = 46
        icon = pygame.transform.smoothscale(icon_image, (icon_size, icon_size))
        icon_x = btn_x + 35 - icon_size // 2
        icon_y = y + btn_h // 2 - icon_size // 2
        screen.blit(icon, (icon_x, icon_y))
    else:
        draw_mini_icon(theme_key, btn_x + 35, y + btn_h // 2)

    # Number key badge (top right)
    badge_x = btn_x + btn_w - 28
    badge_y = y + btn_h // 2
    pygame.draw.circle(screen, accent, (badge_x, badge_y), 14)
    pygame.draw.circle(screen, accent_dark, (badge_x, badge_y), 14, 2)
    num_text = small_font.render(str(key_num), True, WHITE)
    screen.blit(num_text,
                (badge_x - num_text.get_width() // 2,
                 badge_y - num_text.get_height() // 2))

    # Theme name + description
    name_text = font.render(theme_name, True, BLACK)
    screen.blit(name_text, (btn_x + 90, y + (btn_h - name_text.get_height()) // 2))

def draw_panel(x, y, width, height):
    """
    Draw a simple panel with shadow and border.
    Used for menu screens.
    """
    # shadow
    pygame.draw.rect(screen, SHADOW, (x + 5, y + 5, width, height), border_radius=12)

    # main panel
    pygame.draw.rect(screen, PANEL_BG, (x, y, width, height), border_radius=12)
    pygame.draw.rect(screen, PANEL_BORDER, (x, y, width, height), 3, border_radius=12)

def draw_center_text(text, font_used, colour, center_x, y):
    """
    Draw text centered at a given x position.
    """
    text_surface = font_used.render(text, True, colour)
    screen.blit(text_surface, (center_x - text_surface.get_width() // 2, y))

class Player:
    """
    The player character.
    It stores the kangaroo's position and vertical speed.
    """

    def __init__(self):
        self.x = BIRD_X
        self.y = WINDOW_HEIGHT // 2
        self.velocity = 0

    def jump(self):
        """Make the kangaroo jump upward."""
        self.velocity = JUMP_STRENGTH

    def update(self):
        """Update the kangaroo's position using gravity."""
        self.velocity += GRAVITY
        self.y += self.velocity

        # Top boundary: the kangaroo cannot fly out of the screen
        if self.y < 0:
            self.y = 0
            self.velocity = 0

    def get_rect(self):
        """Return the rectangle used for collision detection."""
        return pygame.Rect(self.x, self.y, BIRD_SIZE, BIRD_SIZE)

    def draw(self):
        """Draw the kangaroo on the screen."""
        draw_current_player(self.x, self.y)

class Obstacle:
    """
    The obstacle that the player must avoid.
    It stores its own x position, gap position, and passed status.
    """

    def __init__(self, x_position):
        self.x = x_position
        self.gap_y = random.randint(100, WINDOW_HEIGHT - 100 - PIPE_GAP)
        self.passed = False

    def move(self):
        """Move the obstacle to the left."""
        self.x -= PIPE_SPEED

    def is_off_screen(self):
        """Check whether the obstacle has moved out of the screen."""
        return self.x + PIPE_WIDTH <= 0

    def get_rects(self):
        """
        Return the top and bottom rectangles for drawing.
        These are the original obstacle rectangles.
        """
        top_rect = pygame.Rect(
            self.x, 0,
            PIPE_WIDTH, self.gap_y
        )

        bottom_rect = pygame.Rect(
            self.x,
            self.gap_y + PIPE_GAP,
            PIPE_WIDTH,
            WINDOW_HEIGHT - self.gap_y - PIPE_GAP
        )

        return top_rect, bottom_rect

    def get_collision_rects(self):
        """
        Return rectangles used for collision detection.
        For Egypt, the collision box is matched to the wider obstacle image.
        """
        top_rect, bottom_rect = self.get_rects()

        if current_theme["name"] == "China":
            collision_width = 45
            
            top_collision = pygame.Rect(
                top_rect.x + (top_rect.width - collision_width) // 2,
                top_rect.y,
                collision_width,
                top_rect.height
            )
            
            bottom_collision = pygame.Rect(
                bottom_rect.x + (bottom_rect.width - collision_width) // 2,
                bottom_rect.y,
                collision_width,
                bottom_rect.height
            )

            return top_collision, bottom_collision

        if current_theme["name"] == "Egypt":
            collision_width = 45

            top_collision = pygame.Rect(
                top_rect.x + (top_rect.width - collision_width) // 2,
                top_rect.y,
                collision_width,
                top_rect.height
            )

            bottom_collision = pygame.Rect(
                bottom_rect.x + (bottom_rect.width - collision_width) // 2,
                bottom_rect.y,
                collision_width,
                bottom_rect.height
            )

            return top_collision, bottom_collision
        
        if current_theme["name"] == "Australia":
            collision_width = 45

            top_collision = pygame.Rect(
                top_rect.x + (top_rect.width - collision_width) // 2,
                top_rect.y,
                collision_width,
                top_rect.height
            )

            bottom_collision = pygame.Rect(
                bottom_rect.x + (bottom_rect.width - collision_width) // 2,
                bottom_rect.y,
                collision_width,
                bottom_rect.height
            )

            return top_collision, bottom_collision

        return top_rect, bottom_rect

    def draw(self):
        """Draw the obstacle."""
        top, bottom = self.get_rects()
        draw_current_obstacle(top, bottom)

def draw_theme_select_screen():
    """Theme selection screen with themed colour buttons."""
    draw_gradient_background()

    # Three themed buttons
    draw_theme_button(145, 1, "Australia", "Australia",
                      "Kangaroo · Opera House · Outback",
                      AU_ACCENT, AU_ACCENT_DARK, kangaroo_image)
    draw_theme_button(235, 2, "China", "China",
                      "Panda · Bamboo · Misty Mountains",
                      CN_ACCENT, CN_ACCENT_DARK, panda_image)
    draw_theme_button(325, 3, "Egypt", "Egypt",
                      "Camel · Pyramids · Desert Sun",
                      EG_ACCENT, EG_ACCENT_DARK, camel_image)

    # Footer hint
    if pygame.time.get_ticks() // 1200 % 2 == 0:
        draw_center_text(
            "Press 1, 2 or 3 to choose your adventure",
            tiny_font,
            BLACK,
            WINDOW_WIDTH // 2,
            465
        )

        draw_center_text(
            "Press SPACE to jump",
            tiny_font,
            BLACK,
            WINDOW_WIDTH // 2,
            495
        )

def get_current_theme_icon():
    """
    Return the character image for the selected theme.
    """
    if current_theme["name"] == "Australia":
        return kangaroo_image
    elif current_theme["name"] == "China":
        return panda_image
    elif current_theme["name"] == "Egypt":
        return camel_image

    return None

# name input function
def draw_name_input_screen():
    """Name input screen — background reflects the chosen theme colour."""
    # Get theme-specific colours
    if current_theme["name"] == "Australia":
        accent, accent_dark = AU_ACCENT, AU_ACCENT_DARK
        bg_top, bg_bot = (215, 235, 250), (160, 200, 235)
    elif current_theme["name"] == "China":
        accent, accent_dark = CN_ACCENT, CN_ACCENT_DARK
        bg_top, bg_bot = (230, 245, 230), (185, 220, 200)
    else:  # Egypt
        accent, accent_dark = EG_ACCENT, EG_ACCENT_DARK
        bg_top, bg_bot = (255, 235, 175), (235, 195, 120)

    draw_gradient_background(bg_top, bg_bot)

    # Chosen theme badge
    badge_w = 240
    badge_x = (WINDOW_WIDTH - badge_w) // 2
    badge_y = 155
    pygame.draw.rect(screen, accent, (badge_x, badge_y, badge_w, 52), border_radius=12)
    pygame.draw.rect(screen, accent_dark, (badge_x, badge_y, badge_w, 52), 3, border_radius=12)
    
    icon_image = get_current_theme_icon()

    if icon_image is not None:
        icon_size = 44
        icon = pygame.transform.smoothscale(icon_image, (icon_size, icon_size))

        icon_x = badge_x + 32 - icon_size // 2
        icon_y = badge_y + 26 - icon_size // 2

        screen.blit(icon, (icon_x, icon_y))
    else:
        draw_mini_icon(current_theme["name"], badge_x + 32, badge_y + 26)

    badge_text = small_font.render(f"{current_theme['name']} Theme", True, WHITE)
    screen.blit(badge_text, (badge_x + 65, badge_y + 14))

    # Prompt
    draw_center_text("Enter your name to start", small_font,
                     BLACK, WINDOW_WIDTH // 2, 240)

    # Input box
    box_w, box_h = 280, 52
    box_x = (WINDOW_WIDTH - box_w) // 2
    box_y = 290
    pygame.draw.rect(screen, SHADOW, (box_x + 3, box_y + 3, box_w, box_h), border_radius=10)
    pygame.draw.rect(screen, INPUT_BG, (box_x, box_y, box_w, box_h), border_radius=10)
    pygame.draw.rect(screen, accent, (box_x, box_y, box_w, box_h), 3, border_radius=10)

    # Blinking cursor
    cursor = "|" if pygame.time.get_ticks() // 500 % 2 == 0 else ""
    name_text = small_font.render(player_name + cursor, True, BLACK)
    screen.blit(name_text,
                (box_x + 15, box_y + (box_h - name_text.get_height()) // 2))

    # Character counter
    count_text = tiny_font.render(f"{len(player_name)}/12 characters",
                                  True, SUBTITLE_GREY)
    screen.blit(count_text, (box_x, box_y + box_h + 10))

    # Bottom hints
    draw_center_text("Press ENTER to start",
                     tiny_font, BLACK, WINDOW_WIDTH // 2, 400)
    draw_center_text("Press SPACE to jump during the game", tiny_font, 
                     BLACK, WINDOW_WIDTH // 2, 430)

def draw_game_over_screen():
    """
    Draw a simple game over screen with leaderboard and number controls.
    """
    # Main panel
    panel_x = 45
    panel_y = 115
    panel_w = 310
    panel_h = 420

    pygame.draw.rect(screen, SHADOW, (panel_x + 5, panel_y + 5, panel_w, panel_h), border_radius=18)
    pygame.draw.rect(screen, PANEL_BG, (panel_x, panel_y, panel_w, panel_h), border_radius=18)
    pygame.draw.rect(screen, PANEL_BORDER, (panel_x, panel_y, panel_w, panel_h), 3, border_radius=18)

    # Title
    draw_center_text("Game Over", font, TITLE_BLUE, WINDOW_WIDTH // 2, panel_y + 30)

    # Score
    draw_center_text(f"Score: {score}", small_font, BLACK, WINDOW_WIDTH // 2, panel_y + 85)

    # Leaderboard title
    draw_center_text("Top 5", small_font, BLACK, WINDOW_WIDTH // 2, panel_y + 135)

    # Leaderboard
    top_scores = get_top_scores()[:5]
    y_position = panel_y + 170

    if len(top_scores) == 0:
        draw_center_text("No scores yet", tiny_font, BLACK, WINDOW_WIDTH // 2, y_position)
    else:
        for index, record in enumerate(top_scores):
            rank_text = tiny_font.render(f"{index + 1}.", True, BLACK)
            name_text = tiny_font.render(record["name"], True, BLACK)
            score_text = tiny_font.render(str(record["score"]), True, BLACK)

            screen.blit(rank_text, (panel_x + 55, y_position))
            screen.blit(name_text, (panel_x + 90, y_position))
            screen.blit(score_text, (panel_x + panel_w - 75, y_position))

            y_position += 24

    # Bottom controls
    control_y = panel_y + panel_h - 55

    control_text = tiny_font.render("1 Replay     2 Theme     3 Quit", True, BLACK)
    screen.blit(
        control_text,
        (WINDOW_WIDTH // 2 - control_text.get_width() // 2, control_y)
    )

def draw_game_hud():
    """
    Draw simple in-game HUD.
    Left top shows player name and theme.
    Centre top shows score.
    """
    # left top: player name and theme
    player_text = small_font.render(f"{player_name} · {current_theme['code']}", True, BLACK)
    screen.blit(player_text, (35, 28))

    # centre top: score
    score_text = font.render(str(score), True, WHITE)

    # shadow for score
    score_shadow = font.render(str(score), True, (90, 90, 90))
    screen.blit(
        score_shadow,
        (WINDOW_WIDTH // 2 - score_shadow.get_width() // 2 + 2, 45 + 2)
    )

    screen.blit(
        score_text,
        (WINDOW_WIDTH // 2 - score_text.get_width() // 2, 45)
    )
# ============================================================
# 5. 主游戏循环
# ============================================================
# reset_game()  # 初始化游戏
 
# 这是游戏的"心脏" - 每秒钟跑 60 次
while True:
    # ----- 5.1 处理事件(键盘、关闭窗口等) -----
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            # 玩家点了关闭按钮
            pygame.quit()
            exit()
 
        if event.type == pygame.KEYDOWN:
                 
            if start_screen:
                if event.key == pygame.K_SPACE:
                        start_screen = False
                        selecting_theme = True

                 # Theme selection stage
            elif selecting_theme:
                if event.key == pygame.K_ESCAPE:
                    start_screen = True
                    selecting_theme = False
                    entering_name = False
                    player_name = ""

                elif event.key == pygame.K_1:
                     current_theme = THEMES["Australia"]
                     selecting_theme = False
                     entering_name = True
                     player_name = ""

                elif event.key == pygame.K_2:
                     current_theme = THEMES["China"]
                     selecting_theme = False
                     entering_name = True
                     player_name = ""
                
                elif event.key == pygame.K_3:
                     current_theme = THEMES["Egypt"]
                     selecting_theme = False
                     entering_name = True
                     player_name = ""

            elif entering_name:
                # 输入名字阶段
                if event.key == pygame.K_ESCAPE:
                    entering_name = False
                    selecting_theme = True
                    player_name = ""

                elif event.key == pygame.K_RETURN:
                    if player_name.strip() == "":
                        player_name = "Player"

                    entering_name = False
                    reset_game()

                elif event.key == pygame.K_BACKSPACE:
                    # 删除最后一个字符
                    player_name = player_name[:-1]

                else:
                    # 输入普通字符，限制名字长度，防止太长
                    if len(player_name) < 12 and event.unicode.isprintable():
                        player_name += event.unicode

            else:
                # 游戏阶段
                if game_running:
                    if event.key == pygame.K_SPACE:
                        player.jump()
                else:
                        # After game over, the player can replay, choose theme, or quit
                    if event.key == pygame.K_1:
                        reset_game()
                    elif event.key == pygame.K_2:
                        selecting_theme = True
                        entering_name = False
                        player_name = ""
                    elif event.key == pygame.K_3:
                        pygame.quit()
                        exit()
    
    # If the player is selecting theme, only draw the theme selection screen
    if start_screen:
        draw_start_screen()
        pygame.display.flip()
        clock.tick(FPS)
        continue

    if selecting_theme:
        draw_theme_select_screen()
        pygame.display.flip()
        clock.tick(FPS)
        continue

    # If the player is entering name, only draw the input screen
    if entering_name:
        draw_name_input_screen()
        pygame.display.flip()
        clock.tick(FPS)
        continue
    
    # ----- 5.2 更新游戏状态(只在游戏进行中) -----
    if game_running:
        # Update kangaroo position
        player.update()
 
        # 更新所有柱子的位置
        for pipe in pipes:
            pipe.move()
 
        # 生成新柱子:当最右边的柱子离右边界够远时
        if pipes[-1].x < WINDOW_WIDTH - PIPE_SPACING:
            pipes.append(Obstacle(WINDOW_WIDTH))
 
        # 移除已经飞出屏幕左侧的柱子(节省内存)
        pipes = [p for p in pipes if not p.is_off_screen()]
 
        # 检查小鸟是否通过柱子(得分判定)
        player_rect = player.get_rect()
        for pipe in pipes:
            # 当柱子完全在小鸟左边,且还没被记过分时,加分
            if not pipe.passed and pipe.x + PIPE_WIDTH < BIRD_X:
                pipe.passed = True
                score += 1
 
        # ----- 5.3 碰撞检测 -----
        # 撞到地面或天花板
        if player.y + BIRD_SIZE > WINDOW_HEIGHT:
            end_game()
 
        # 撞到柱子
        for pipe in pipes:
            top, bottom = pipe.get_collision_rects()
            if player_rect.colliderect(top) or player_rect.colliderect(bottom):
                end_game()
 
    # ----- 5.4 绘制画面(每一帧都要重画) -----
    # 1. 澳洲主题背景
    draw_current_background()
 
    # 2. 柱子
    for pipe in pipes:
        pipe.draw()

    # 3. 袋鼠角色；
    player.draw()

 
    # 4. 分数(左上角)
    draw_game_hud()
 
    # 5. 游戏结束提示
    if not game_running:
        draw_game_over_screen()
 
    # 6. 把绘制结果显示到屏幕上
    pygame.display.flip()
 
    # ----- 5.5 控制帧率 -----
    clock.tick(FPS)
