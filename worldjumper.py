import pygame  
import random  
import os      

# ============================================================
# 1. 游戏常量(设置)
# ============================================================

WINDOW_WIDTH = 400          # 窗口宽度(像素)
WINDOW_HEIGHT = 600         # 窗口高度
FPS = 60                    # 每秒帧数(画面流畅度)
 
# colour (R, G, B)
SKY_BLUE = (135, 206, 235)  # sky_blue
WHITE = (255, 255, 255)     # word_white
BLACK = (0, 0, 0)           # word_black

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
PIPE_GAP = 150              # 上下柱子之间的缝隙大小(给小鸟穿过)
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
pygame.display.set_caption("Flappy USYD")  # 窗口标题
clock = pygame.time.Clock()  # 时钟,用来控制帧率
font = pygame.font.SysFont("Arial", 36, bold=True)  # 用于显示分数的字体
small_font = pygame.font.SysFont("Arial", 22, bold=True)  # 用于显示小文字
tiny_font = pygame.font.SysFont("Arial", 16, bold=True)  # 用于排行榜 
# ============================================================
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

selecting_theme = True
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
                    records.append({
                        "name": name,
                        "theme": theme,
                        "score": int(score_text)
                    })
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

def draw_crossing_pole(top_rect, bottom_rect):
    """
    绘制澳洲过马路按钮杆。
    这里仍然使用原来的 top_rect 和 bottom_rect，
    所以碰撞检测不用改。
    """
    # 上下障碍物主体
    pygame.draw.rect(screen, POLE_GREY, top_rect)
    pygame.draw.rect(screen, POLE_GREY, bottom_rect)

    # 边框，让障碍物更明显
    pygame.draw.rect(screen, BLACK, top_rect, 2)
    pygame.draw.rect(screen, BLACK, bottom_rect, 2)

    # 上方按钮盒
    if top_rect.height > 65:
        box_x = top_rect.x + 10
        box_y = top_rect.bottom - 55
        pygame.draw.rect(screen, BUTTON_BOX, (box_x, box_y, 40, 35))
        pygame.draw.circle(screen, RED_BUTTON, (box_x + 20, box_y + 18), 8)

    # 下方按钮盒
    if bottom_rect.height > 65:
        box_x = bottom_rect.x + 10
        box_y = bottom_rect.y + 20
        pygame.draw.rect(screen, BUTTON_BOX, (box_x, box_y, 40, 35))
        pygame.draw.circle(screen, GREEN_BUTTON, (box_x + 20, box_y + 18), 8)

def draw_bamboo(top_rect, bottom_rect):
    """
    Draw bamboo obstacles for the China theme.
    """
    pygame.draw.rect(screen, BAMBOO_GREEN, top_rect)
    pygame.draw.rect(screen, BAMBOO_GREEN, bottom_rect)

    pygame.draw.rect(screen, BAMBOO_DARK, top_rect, 3)
    pygame.draw.rect(screen, BAMBOO_DARK, bottom_rect, 3)

    # bamboo nodes for top obstacle
    y = top_rect.y
    while y < top_rect.y + top_rect.height:
        pygame.draw.line(screen, BAMBOO_DARK, (top_rect.x, y), (top_rect.x + top_rect.width, y), 3)
        y += 35

    # bamboo nodes for bottom obstacle
    y = bottom_rect.y
    while y < bottom_rect.y + bottom_rect.height:
        pygame.draw.line(screen, BAMBOO_DARK, (bottom_rect.x, y), (bottom_rect.x + bottom_rect.width, y), 3)
        y += 35


def draw_kangaroo(x, y):

    x = int(x)
    y = int(y)

    # 尾巴
    pygame.draw.line(screen, KANGAROO_DARK, (x + 6, y + 25), (x - 10, y + 35), 5)

    # 身体
    pygame.draw.ellipse(screen, KANGAROO_BROWN, (x + 3, y + 12, 25, 17))

    # 头
    pygame.draw.circle(screen, KANGAROO_BROWN, (x + 28, y + 10), 8)

    # 耳朵
    pygame.draw.polygon(screen, KANGAROO_BROWN, [(x + 24, y + 4), (x + 26, y - 8), (x + 30, y + 4)])
    pygame.draw.polygon(screen, KANGAROO_BROWN, [(x + 30, y + 5), (x + 35, y - 5), (x + 35, y + 7)])

    # 腿
    pygame.draw.rect(screen, KANGAROO_DARK, (x + 10, y + 25, 5, 13))
    pygame.draw.rect(screen, KANGAROO_DARK, (x + 20, y + 25, 5, 13))

    # 眼睛
    pygame.draw.circle(screen, BLACK, (x + 31, y + 8), 2)

def draw_panda(x, y):
    """
    Draw a simple panda character.
    """
    x = int(x)
    y = int(y)

    # ears
    pygame.draw.circle(screen, PANDA_BLACK, (x + 8, y + 6), 7)
    pygame.draw.circle(screen, PANDA_BLACK, (x + 25, y + 6), 7)

    # head
    pygame.draw.circle(screen, PANDA_WHITE, (x + 17, y + 17), 17)
    pygame.draw.circle(screen, BLACK, (x + 17, y + 17), 17, 2)

    # eye patches
    pygame.draw.circle(screen, PANDA_BLACK, (x + 10, y + 15), 5)
    pygame.draw.circle(screen, PANDA_BLACK, (x + 24, y + 15), 5)

    # eyes
    pygame.draw.circle(screen, WHITE, (x + 10, y + 15), 2)
    pygame.draw.circle(screen, WHITE, (x + 24, y + 15), 2)

    # nose
    pygame.draw.circle(screen, PANDA_BLACK, (x + 17, y + 24), 3)

    # body
    pygame.draw.ellipse(screen, PANDA_WHITE, (x + 3, y + 28, 28, 22))
    pygame.draw.ellipse(screen, BLACK, (x + 3, y + 28, 28, 22), 2)

def draw_camel(x, y):
    """
    Draw a simple camel character.
    """
    x = int(x)
    y = int(y)

    # body
    pygame.draw.ellipse(screen, CAMEL_BROWN, (x + 2, y + 18, 34, 18))

    # hump
    pygame.draw.circle(screen, CAMEL_BROWN, (x + 18, y + 17), 10)

    # neck
    pygame.draw.rect(screen, CAMEL_BROWN, (x + 31, y + 8, 7, 20))

    # head
    pygame.draw.circle(screen, CAMEL_BROWN, (x + 42, y + 8), 8)

    # legs
    pygame.draw.rect(screen, CAMEL_DARK, (x + 8, y + 33, 5, 16))
    pygame.draw.rect(screen, CAMEL_DARK, (x + 25, y + 33, 5, 16))

    # eye
    pygame.draw.circle(screen, BLACK, (x + 44, y + 6), 2)


def draw_mummy_pole(top_rect, bottom_rect):
    """
    Draw mummy-wrapped pole obstacles for the Egypt theme.
    """
    pygame.draw.rect(screen, MUMMY_BANDAGE, top_rect)
    pygame.draw.rect(screen, MUMMY_BANDAGE, bottom_rect)

    pygame.draw.rect(screen, MUMMY_LINE, top_rect, 3)
    pygame.draw.rect(screen, MUMMY_LINE, bottom_rect, 3)

    # bandage lines for top obstacle
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

    # bandage lines for bottom obstacle
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
    The obstacle that the kangaroo must avoid.
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
        """Return the top and bottom rectangles for drawing and collision."""
        top_pipe = pygame.Rect(
            self.x, 0,
            PIPE_WIDTH, self.gap_y
        )

        bottom_pipe = pygame.Rect(
            self.x, self.gap_y + PIPE_GAP,
            PIPE_WIDTH, WINDOW_HEIGHT - self.gap_y - PIPE_GAP
        )

        return top_pipe, bottom_pipe

    def draw(self):
        """Draw the obstacle."""
        top, bottom = self.get_rects()
        draw_current_obstacle(top, bottom)

def draw_theme_select_screen():
    """
    Draw the theme selection screen.
    The player chooses a country theme before entering their name.
    """
    draw_current_background()

    # White panel
    pygame.draw.rect(screen, WHITE, (35, 150, 330, 300))
    pygame.draw.rect(screen, BLACK, (35, 150, 330, 300), 3)

    title_text = font.render("Choose Theme", True, BLACK)
    aus_text = small_font.render("1. Australia - Kangaroo", True, BLACK)
    china_text = small_font.render("2. China - Panda", True, BLACK)
    egypt_text = small_font.render("3. Egypt - Camel", True, BLACK)
    help_text = tiny_font.render("Press 1, 2 or 3 to choose", True, BLACK)

    screen.blit(title_text, (WINDOW_WIDTH // 2 - title_text.get_width() // 2, 180))
    screen.blit(aus_text, (80, 260))
    screen.blit(china_text, (80, 310))
    screen.blit(egypt_text, (80, 360))
    screen.blit(help_text, (WINDOW_WIDTH // 2 - help_text.get_width() // 2, 405))

# name input function
def draw_name_input_screen():
    """
    Draw the name input screen before the game starts.
    The player types a name and presses Enter to start.
    """
    draw_current_background()

    # White panel
    pygame.draw.rect(screen, WHITE, (40, 175, 320, 235))
    pygame.draw.rect(screen, BLACK, (40, 175, 320, 235), 3)

    title_text = font.render("World Hop", True, BLACK)
    theme_text = small_font.render(f"{current_theme['name']} Theme", True, BLACK)
    prompt_text = small_font.render("Enter your name:", True, BLACK)
    help_text = small_font.render("Press ENTER to start", True, BLACK)

    screen.blit(title_text, (WINDOW_WIDTH // 2 - title_text.get_width() // 2, 200))
    screen.blit(theme_text, (WINDOW_WIDTH // 2 - theme_text.get_width() // 2, 240))
    screen.blit(prompt_text, (80, 280))

    # Input box
    input_box = pygame.Rect(80, 310, 240, 42)
    pygame.draw.rect(screen, (245, 245, 245), input_box)
    pygame.draw.rect(screen, BLACK, input_box, 2)

    # Blinking cursor
    cursor = ""
    if pygame.time.get_ticks() // 500 % 2 == 0:
        cursor = "|"

    name_text = small_font.render(player_name + cursor, True, BLACK)
    screen.blit(name_text, (input_box.x + 10, input_box.y + 10))

    screen.blit(help_text, (WINDOW_WIDTH // 2 - help_text.get_width() // 2, 370))

def draw_game_over_screen():
    """
    Draw game over message and top 10 leaderboard.
    """
    # Panel
    pygame.draw.rect(screen, WHITE, (35, 120, 330, 440))
    pygame.draw.rect(screen, BLACK, (35, 120, 330, 440), 3)

    over_text = font.render("Game Over!", True, BLACK)
    final_score_text = small_font.render(f"{player_name}'s score: {score}", True, BLACK)
    board_title = small_font.render("Top 10 Leaderboard", True, BLACK)
    replay_text = tiny_font.render("R - Replay", True, BLACK)
    theme_text = tiny_font.render("T - Choose Theme", True, BLACK)
    quit_text = tiny_font.render("Q - Quit", True, BLACK)

    screen.blit(over_text, (WINDOW_WIDTH // 2 - over_text.get_width() // 2, 140))
    screen.blit(final_score_text, (WINDOW_WIDTH // 2 - final_score_text.get_width() // 2, 185))
    screen.blit(board_title, (WINDOW_WIDTH // 2 - board_title.get_width() // 2, 225))

    top_scores = get_top_scores()

    if len(top_scores) == 0:
        no_score_text = tiny_font.render("No scores yet.", True, BLACK)
        screen.blit(no_score_text, (80, 265))
    else:
        y_position = 260

        for index, record in enumerate(top_scores):
            line = f"{index + 1}. {record['name']} - {record['theme']} - {record['score']}"
            line_text = tiny_font.render(line, True, BLACK)
            screen.blit(line_text, (65, y_position))
            y_position += 24

    screen.blit(replay_text, (70, 515))
    screen.blit(theme_text, (160, 515))
    screen.blit(quit_text, (285, 515))
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
            if selecting_theme:
                 # Theme selection stage
                 if event.key == pygame.K_1:
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
                if event.key == pygame.K_RETURN:
                    # 按 Enter 开始游戏
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
                    if event.key == pygame.K_r:
                        reset_game()
                    elif event.key == pygame.K_t:
                        selecting_theme = True
                        entering_name = False
                        player_name = ""
                    elif event.key == pygame.K_q:
                        pygame.quit()
                        exit()
    
    # If the player is selecting theme, only draw the theme selection screen
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
            top, bottom = pipe.get_rects()
            if player_rect.colliderect(top) or player_rect.colliderect(bottom):
                end_game()
 
    # ----- 5.4 绘制画面(每一帧都要重画) -----
    # 1. 澳洲主题背景
    draw_current_background()
 
    # 2. 柱子
    for pipe in pipes:
        pipe.draw()
    
    # 3. 袋鼠角色
    player.draw()

 
    # 4. 分数(左上角)
    player_text = small_font.render(f"{player_name} · {current_theme['code']}", True, BLACK)
    score_text = font.render(f"Score: {score}", True, BLACK)

    screen.blit(player_text, (10, 10))
    screen.blit(score_text, (10, 35))
 
    # 5. 游戏结束提示
    if not game_running:
        draw_game_over_screen()
 
    # 6. 把绘制结果显示到屏幕上
    pygame.display.flip()
 
    # ----- 5.5 控制帧率 -----
    clock.tick(FPS)
