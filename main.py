import random
import pygame

pygame.init()

# Настройки окна и объектов
WIDTH, HEIGHT = 800, 600
PLAYER_SIZE = (220, 220)
ITEM_SIZE = (78, 78)
PLAYER_SPEED = 6
BOTTOM_MARGIN = 44
PLAYER_HITBOX_SIZE = (92, 110)
ITEM_HITBOX_SIZE = (54, 54)

# Небольшая корректировка размеров отдельных картинок
GOOD_ITEM_SCALES = [1.0, 1.18, 1.0, 1.0]
BAD_ITEM_SCALES = [1.0, 1.0, 1.0]

# Цвета интерфейса
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
MENU_TEXT = (76, 52, 109)
MENU_HINT = (108, 93, 145)
PLAYER1_TEXT = (214, 96, 156)
PLAYER2_TEXT = (236, 184, 52)

# Окно и шрифты
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Робот-сборщик")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)
big_font = pygame.font.SysFont(None, 64)
small_font = pygame.font.SysFont(None, 28)


# Работа с картинками
def trim_transparent_area(image):
    # Удаляет лишние прозрачные края у картинки.
    bounds = image.get_bounding_rect()
    if bounds.width == 0 or bounds.height == 0:
        return image
    return image.subsurface(bounds).copy()


def load_scaled_image(path, size, alpha=True):
    # Загружает картинку и приводит её к нужному размеру.
    image = pygame.image.load(path)
    image = image.convert_alpha() if alpha else image.convert()
    if alpha:
        image = trim_transparent_area(image)
    return pygame.transform.scale(image, size)


def scale_to_canvas(image, canvas_size, scale_multiplier=1.0):
    # Меняет размер картинки и ставит её по центру.
    new_size = (
        int(canvas_size[0] * scale_multiplier),
        int(canvas_size[1] * scale_multiplier),
    )
    scaled = pygame.transform.smoothscale(image, new_size)
    canvas = pygame.Surface(canvas_size, pygame.SRCALPHA)
    position = (
        (canvas_size[0] - new_size[0]) // 2,
        (canvas_size[1] - new_size[1]) // 2,
    )
    canvas.blit(scaled, position)
    return canvas


def make_panel(size, fill_color, border_color, radius, border_width):
    # Создаёт закруглённую панель интерфейса.
    width, height = size
    panel = pygame.Surface(size, pygame.SRCALPHA).convert_alpha()
    pygame.draw.rect(panel, fill_color, (0, 0, width, height), border_radius=radius)
    pygame.draw.rect(panel, border_color, (0, 0, width, height), width=border_width, border_radius=radius)
    return panel


# Загрузка графики
player1_img = load_scaled_image("assets/robot1.png", PLAYER_SIZE)
player2_img = load_scaled_image("assets/robot2.png", PLAYER_SIZE)
bg_img = load_scaled_image("assets/bg.png", (WIDTH, HEIGHT), alpha=False)

good_images = [
    scale_to_canvas(load_scaled_image("assets/good1.png", ITEM_SIZE), ITEM_SIZE, GOOD_ITEM_SCALES[0]),
    scale_to_canvas(load_scaled_image("assets/good2.png", ITEM_SIZE), ITEM_SIZE, GOOD_ITEM_SCALES[1]),
    scale_to_canvas(load_scaled_image("assets/good3.png", ITEM_SIZE), ITEM_SIZE, GOOD_ITEM_SCALES[2]),
    scale_to_canvas(load_scaled_image("assets/good4.png", ITEM_SIZE), ITEM_SIZE, GOOD_ITEM_SCALES[3]),
]

bad_images = [
    scale_to_canvas(load_scaled_image("assets/bad1.png", ITEM_SIZE), ITEM_SIZE, BAD_ITEM_SCALES[0]),
    scale_to_canvas(load_scaled_image("assets/bad2.png", ITEM_SIZE), ITEM_SIZE, BAD_ITEM_SCALES[1]),
    scale_to_canvas(load_scaled_image("assets/bad3.png", ITEM_SIZE), ITEM_SIZE, BAD_ITEM_SCALES[2]),
]


# Готовые панели
GAME_OVERLAY = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA).convert_alpha()
GAME_OVERLAY.fill((0, 0, 0, 60))

MENU_TINT = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA).convert_alpha()
MENU_TINT.fill((255, 235, 248, 170))

GAME_OVER_TINT = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA).convert_alpha()
GAME_OVER_TINT.fill((245, 232, 255, 180))

MENU_PANEL = make_panel((470, 360), (255, 248, 255, 225), (255, 196, 225, 255), 28, 4)
GAME_OVER_PANEL = make_panel((500, 290), (255, 248, 255, 230), (255, 196, 225, 255), 28, 4)
HUD_PANEL = make_panel((270, 120), (255, 248, 255, 220), (255, 196, 225, 255), 20, 3)
MENU_ITEM_PANEL = make_panel((320, 46), (255, 240, 248, 210), (255, 240, 248, 210), 18, 0)
MENU_ACTIVE_PANEL = make_panel((320, 46), (255, 223, 150, 230), (255, 191, 87, 255), 18, 3)
MENU_HINT_PANEL = make_panel((360, 86), (255, 248, 255, 215), (212, 190, 236, 255), 18, 2)
GAME_OVER_HINT_PANEL = make_panel((320, 58), (255, 248, 255, 220), (212, 190, 236, 255), 18, 2)


# Настройки сложности
difficulties = ["Легкий", "Средний", "Сложный"]
difficulty_settings = {
    "Легкий": {"good_speed": 2, "bad_speed": 3, "lives": 4},
    "Средний": {"good_speed": 3, "bad_speed": 4, "lives": 3},
    "Сложный": {"good_speed": 5, "bad_speed": 6, "lives": 2},
}


# Состояние игры
game_state = "menu"
difficulty = "Средний"
two_players = True
menu_index = 0

score1 = 0
score2 = 0
lives = 3
good_speed = 3
bad_speed = 4

PLAYER_Y = HEIGHT - PLAYER_SIZE[1] - BOTTOM_MARGIN

player1_x = float(WIDTH // 2 - 190)
player1_y = PLAYER_Y
player2_x = float(WIDTH // 2 + 70)
player2_y = PLAYER_Y

good_x = 0.0
good_y = -150.0
bad_x = 0.0
bad_y = -220.0
current_good = None
current_bad = None


# Игровая логика
def random_x():
    # Возвращает случайную координату по X в пределах экрана.
    return random.randint(20, WIDTH - ITEM_SIZE[0] - 20)


def reset_good_item():
    # Создаёт новый полезный предмет сверху экрана.
    global good_x, good_y, current_good
    good_x = float(random_x())
    good_y = -150.0
    current_good = random.choice(good_images)


def reset_bad_item():
    # Создаёт новый вредный предмет сверху экрана.
    global bad_x, bad_y, current_bad
    bad_x = float(random_x())
    bad_y = -220.0
    current_bad = random.choice(bad_images)


def start_new_game():
    # Сбрасывает позиции, очки, жизни и скорости перед новой игрой.
    global player1_x, player2_x, score1, score2, lives, good_speed, bad_speed

    player1_x = float(WIDTH // 2 - 190)
    player2_x = float(WIDTH // 2 + 70)
    score1 = 0
    score2 = 0

    settings = difficulty_settings[difficulty]
    good_speed = settings["good_speed"]
    bad_speed = settings["bad_speed"]
    lives = settings["lives"]

    reset_good_item()
    reset_bad_item()


def change_difficulty(direction):
    # Переключает сложность вперёд или назад по кругу.
    global difficulty
    index = (difficulties.index(difficulty) + direction) % len(difficulties)
    difficulty = difficulties[index]


def move_players():
    # Двигает игроков по клавишам.
    global player1_x, player2_x

    keys = pygame.key.get_pressed()

    if keys[pygame.K_LEFT]:
        player1_x -= PLAYER_SPEED
    if keys[pygame.K_RIGHT]:
        player1_x += PLAYER_SPEED

    if two_players:
        if keys[pygame.K_a]:
            player2_x -= PLAYER_SPEED
        if keys[pygame.K_d]:
            player2_x += PLAYER_SPEED

    player1_x = max(0, min(player1_x, WIDTH - PLAYER_SIZE[0]))
    player2_x = max(0, min(player2_x, WIDTH - PLAYER_SIZE[0]))


def make_player_hitbox(player_x, player_y):
    # Создаёт уменьшенную зону столкновения для робота.
    return pygame.Rect(
        round(player_x) + (PLAYER_SIZE[0] - PLAYER_HITBOX_SIZE[0]) // 2,
        player_y + PLAYER_SIZE[1] - PLAYER_HITBOX_SIZE[1] - 18,
        *PLAYER_HITBOX_SIZE,
    )


def make_item_hitbox(item_x, item_y):
    # Создаёт уменьшенную зону столкновения для предмета.
    return pygame.Rect(
        round(item_x) + (ITEM_SIZE[0] - ITEM_HITBOX_SIZE[0]) // 2,
        round(item_y) + (ITEM_SIZE[1] - ITEM_HITBOX_SIZE[1]) // 2,
        *ITEM_HITBOX_SIZE,
    )


def update_game():
    # Обновляет движение, столкновения, очки и жизни.
    global good_y, bad_y, score1, score2, lives, game_state

    move_players()
    good_y += good_speed
    bad_y += bad_speed

    if good_y > HEIGHT:
        reset_good_item()
    if bad_y > HEIGHT:
        reset_bad_item()

    player1_rect = make_player_hitbox(player1_x, player1_y)
    player2_rect = make_player_hitbox(player2_x, player2_y)
    good_rect = make_item_hitbox(good_x, good_y)
    bad_rect = make_item_hitbox(bad_x, bad_y)

    if player1_rect.colliderect(good_rect):
        score1 += 1
        reset_good_item()
    elif two_players and player2_rect.colliderect(good_rect):
        score2 += 1
        reset_good_item()

    if player1_rect.colliderect(bad_rect):
        lives -= 1
        reset_bad_item()
    elif two_players and player2_rect.colliderect(bad_rect):
        lives -= 1
        reset_bad_item()

    if lives <= 0:
        game_state = "game_over"


# Отрисовка
def draw_text(text, x, y, color=WHITE, current_font=font):
    # Рисует текст в указанной точке экрана.
    screen.blit(current_font.render(text, True, color), (x, y))


def draw_centered(text, y, color=WHITE, current_font=font):
    # Рисует текст по центру экрана.
    surface = current_font.render(text, True, color)
    rect = surface.get_rect(center=(WIDTH // 2, y))
    screen.blit(surface, rect)


def draw_menu():
    # Рисует главное меню.
    screen.blit(bg_img, (0, 0))
    screen.blit(MENU_TINT, (0, 0))
    screen.blit(MENU_PANEL, (WIDTH // 2 - 235, 95))

    draw_centered("Робот-сборщик", 145, MENU_TEXT, big_font)

    menu_items = [
        f"Режим: {'2 игрока' if two_players else '1 игрок'}",
        f"Сложность: {difficulty}",
        "Начать игру",
        "Выход",
    ]

    for i, item in enumerate(menu_items):
        y = 225 + i * 58
        panel = MENU_ACTIVE_PANEL if i == menu_index else MENU_ITEM_PANEL
        screen.blit(panel, (WIDTH // 2 - 160, y - 4))
        draw_text(item, WIDTH // 2 - 120, y + 4, MENU_TEXT)

    hint_x = WIDTH - 380
    hint_y = HEIGHT - 105
    screen.blit(MENU_HINT_PANEL, (hint_x, hint_y))
    draw_text("Вверх/вниз - выбор", hint_x + 18, hint_y + 14, MENU_TEXT, small_font)
    draw_text("Влево/вправо - изменить", hint_x + 18, hint_y + 38, MENU_TEXT, small_font)
    draw_text("Enter - старт, Esc - выход", hint_x + 18, hint_y + 62, MENU_TEXT, small_font)


def draw_hud():
    # Рисует панель с очками и жизнями.
    screen.blit(HUD_PANEL, (10, 10))

    if two_players:
        lines = [
            (f"Игрок 1: {score1}", PLAYER1_TEXT),
            (f"Игрок 2: {score2}", PLAYER2_TEXT),
            (f"Общие жизни: {lives}", MENU_TEXT),
        ]
    else:
        lines = [
            (f"Ваш счёт: {score1}", MENU_TEXT),
            (f"Осталось жизней: {lives}", MENU_TEXT),
        ]

    for i, (text, color) in enumerate(lines):
        draw_text(text, 28, 25 + i * 35, color)


def draw_game():
    # Рисует игровой экран.
    screen.blit(bg_img, (0, 0))
    screen.blit(GAME_OVERLAY, (0, 0))
    screen.blit(current_good, (round(good_x), round(good_y)))
    screen.blit(current_bad, (round(bad_x), round(bad_y)))
    screen.blit(player1_img, (round(player1_x), player1_y))

    if two_players:
        screen.blit(player2_img, (round(player2_x), player2_y))

    draw_hud()


def draw_game_over():
    # Рисует экран завершения игры.
    screen.blit(bg_img, (0, 0))
    screen.blit(GAME_OVER_TINT, (0, 0))
    screen.blit(GAME_OVER_PANEL, (WIDTH // 2 - 250, HEIGHT // 2 - 150))

    draw_centered("ИГРА ОКОНЧЕНА", HEIGHT // 2 - 85, MENU_TEXT, big_font)

    if two_players:
        if score1 > score2:
            result = "Победа игрока 1"
        elif score2 > score1:
            result = "Победа игрока 2"
        else:
            result = "Дружеская ничья"

        draw_centered(result, HEIGHT // 2 - 5, MENU_TEXT)
        draw_centered(f"Игрок 1: {score1}", HEIGHT // 2 + 24, PLAYER1_TEXT)
        draw_centered(f"Игрок 2: {score2}", HEIGHT // 2 + 54, PLAYER2_TEXT)
    else:
        draw_centered(f"Ваш итоговый счёт: {score1}", HEIGHT // 2 + 12, MENU_TEXT)

    hint_x = WIDTH // 2 - 160
    hint_y = HEIGHT // 2 + 80
    screen.blit(GAME_OVER_HINT_PANEL, (hint_x, hint_y))
    draw_text("Enter - меню, Esc - выход", hint_x + 22, hint_y + 17, MENU_TEXT, small_font)


# Обработка клавиш
def handle_menu_key(event_key):
    # Обрабатывает клавиши в меню.
    global running, menu_index, two_players, game_state

    if event_key == pygame.K_ESCAPE:
        running = False
    elif event_key == pygame.K_UP:
        menu_index = (menu_index - 1) % 4
    elif event_key == pygame.K_DOWN:
        menu_index = (menu_index + 1) % 4
    elif event_key in (pygame.K_LEFT, pygame.K_RIGHT):
        if menu_index == 0:
            two_players = not two_players
        elif menu_index == 1:
            change_difficulty(1 if event_key == pygame.K_RIGHT else -1)
    elif event_key == pygame.K_RETURN:
        if menu_index == 2:
            start_new_game()
            game_state = "game"
        elif menu_index == 3:
            running = False


def handle_game_over_key(event_key):
    # Обрабатывает клавиши на экране завершения.
    global running, game_state

    if event_key == pygame.K_RETURN:
        game_state = "menu"
    elif event_key == pygame.K_ESCAPE:
        running = False


# Главный цикл
running = True

while running:
    clock.tick_busy_loop(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if game_state == "menu":
                handle_menu_key(event.key)
            elif game_state == "game_over":
                handle_game_over_key(event.key)

    if game_state == "game":
        update_game()

    if game_state == "menu":
        draw_menu()
    elif game_state == "game":
        draw_game()
    else:
        draw_game_over()

    pygame.display.flip()

pygame.quit()
