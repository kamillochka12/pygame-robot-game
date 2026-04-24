import random
import pygame

pygame.init()

WIDTH, HEIGHT = 800, 600
PLAYER_SIZE = (205, 205)
ITEM_SIZE = (95, 95)
PLAYER_SPEED = 6

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (130, 130, 130)
YELLOW = (255, 220, 80)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Робот-сборщик")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)
big_font = pygame.font.SysFont(None, 64)


def load_scaled_image(path, size, alpha=True):
    image = pygame.image.load(path)
    image = image.convert_alpha() if alpha else image.convert()
    return pygame.transform.scale(image, size)


player1_img = load_scaled_image("assets/robot1.png", PLAYER_SIZE)
player2_img = load_scaled_image("assets/robot2.png", PLAYER_SIZE)
bg_img = load_scaled_image("assets/bg.png", (WIDTH, HEIGHT), alpha=False)

good_images = [
    load_scaled_image(f"assets/good{i}.png", ITEM_SIZE)
    for i in range(1, 5)
]
bad_images = [
    load_scaled_image(f"assets/bad{i}.png", ITEM_SIZE)
    for i in range(1, 4)
]

difficulties = ["Легкий", "Средний", "Сложный"]
difficulty_settings = {
    "Легкий": {"good_speed": 2, "bad_speed": 3, "lives": 4},
    "Средний": {"good_speed": 3, "bad_speed": 4, "lives": 3},
    "Сложный": {"good_speed": 5, "bad_speed": 6, "lives": 2},
}

game_state = "menu"
difficulty = "Средний"
two_players = True
menu_index = 0

score1 = score2 = 0
lives = 3
good_speed = 3
bad_speed = 4

player1_x, player1_y = WIDTH // 2 - 190, HEIGHT - 155
player2_x, player2_y = WIDTH // 2 + 70, HEIGHT - 155

good_x, good_y = 0, -150
bad_x, bad_y = 0, -220
current_good = None
current_bad = None


def random_x():
    return random.randint(20, WIDTH - ITEM_SIZE[0] - 20)


def reset_item(kind):
    global good_x, good_y, bad_x, bad_y, current_good, current_bad

    if kind == "good":
        good_x, good_y = random_x(), -150
        current_good = random.choice(good_images)
    else:
        bad_x, bad_y = random_x(), -220
        current_bad = random.choice(bad_images)


def start_new_game():
    global player1_x, player2_x, score1, score2, lives, good_speed, bad_speed

    player1_x = WIDTH // 2 - 190
    player2_x = WIDTH // 2 + 70
    score1 = score2 = 0

    settings = difficulty_settings[difficulty]
    good_speed = settings["good_speed"]
    bad_speed = settings["bad_speed"]
    lives = settings["lives"]

    reset_item("good")
    reset_item("bad")


def change_difficulty(direction):
    global difficulty
    difficulty = difficulties[(difficulties.index(difficulty) + direction) % len(difficulties)]


def draw_text(text, x, y, color=WHITE, current_font=font):
    screen.blit(current_font.render(text, True, color), (x, y))


def draw_centered(text, y, offset_x=0, color=WHITE, current_font=font):
    surface = current_font.render(text, True, color)
    rect = surface.get_rect(center=(WIDTH // 2 + offset_x, y))
    screen.blit(surface, rect)


def draw_menu():
    screen.fill((20, 20, 20))
    draw_centered("Робот-сборщик", 130, current_font=big_font)

    menu_items = [
        f"Режим: {'2 игрока' if two_players else '1 игрок'}",
        f"Сложность: {difficulty}",
        "Начать игру",
        "Выход",
    ]

    for i, item in enumerate(menu_items):
        y = 230 + i * 60
        color = YELLOW if i == menu_index else WHITE
        draw_text(item, WIDTH // 2 - 130, y, color)
        if i == menu_index:
            draw_text(">", WIDTH // 2 - 170, y, YELLOW)

    hints = [
        ("Вверх/вниз - выбор", WIDTH // 2 - 150, 500),
        ("Влево/вправо - изменить", WIDTH // 2 - 170, 530),
        ("Enter - начать | Esc - выйти", WIDTH // 2 - 180, 560),
    ]
    for text, x, y in hints:
        draw_text(text, x, y, GRAY)


def move_players():
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


def update_game():
    global good_y, bad_y, score1, score2, lives, game_state, good_speed, bad_speed

    move_players()
    good_y += good_speed
    bad_y += bad_speed

    if good_y > HEIGHT:
        reset_item("good")
    if bad_y > HEIGHT:
        reset_item("bad")

    player_rects = [
        pygame.Rect(player1_x, player1_y, *PLAYER_SIZE),
        pygame.Rect(player2_x, player2_y, *PLAYER_SIZE),
    ]
    good_rect = pygame.Rect(good_x, good_y, *ITEM_SIZE)
    bad_rect = pygame.Rect(bad_x, bad_y, *ITEM_SIZE)

    if player_rects[0].colliderect(good_rect):
        score1 += 1
        reset_item("good")
    elif two_players and player_rects[1].colliderect(good_rect):
        score2 += 1
        reset_item("good")

    if player_rects[0].colliderect(bad_rect):
        lives -= 1
        reset_item("bad")
    elif two_players and player_rects[1].colliderect(bad_rect):
        lives -= 1
        reset_item("bad")

    total_score = score1 + score2
    if total_score > 0 and total_score % 5 == 0:
        good_speed += 0.01
        bad_speed += 0.01

    if lives <= 0:
        game_state = "game_over"


def draw_hud():
    pygame.draw.rect(screen, BLACK, (10, 10, 260, 120), border_radius=15)
    lines = [f"Игрок 1: {score1}"]

    if two_players:
        lines.append(f"Игрок 2: {score2}")
    lines.append(f"Жизни: {lives}")

    for i, text in enumerate(lines):
        draw_text(text, 25, 25 + i * 35)


def draw_game():
    screen.blit(bg_img, (0, 0))

    dark = pygame.Surface((WIDTH, HEIGHT))
    dark.set_alpha(60)
    dark.fill(BLACK)
    screen.blit(dark, (0, 0))

    for image, pos in [
        (current_good, (good_x, good_y)),
        (current_bad, (bad_x, bad_y)),
        (player1_img, (player1_x, player1_y)),
    ]:
        screen.blit(image, pos)

    if two_players:
        screen.blit(player2_img, (player2_x, player2_y))

    draw_hud()


def draw_game_over():
    screen.fill((20, 20, 20))
    draw_centered("ИГРА ОКОНЧЕНА", HEIGHT // 2 - 100, current_font=big_font)

    if two_players:
        if score1 > score2:
            result = "Победил игрок 1"
        elif score2 > score1:
            result = "Победил игрок 2"
        else:
            result = "Ничья"

        draw_centered(result, HEIGHT // 2 - 20)
        draw_centered(f"Игрок 1: {score1}   Игрок 2: {score2}", HEIGHT // 2 + 30)
    else:
        draw_centered(f"Очки: {score1}", HEIGHT // 2)

    draw_centered("Enter - меню | Esc - выйти", HEIGHT // 2 + 100)


def handle_menu_key(event_key):
    global running, menu_index, two_players, game_state

    menu_count = 4

    if event_key == pygame.K_ESCAPE:
        running = False
    elif event_key == pygame.K_UP:
        menu_index = (menu_index - 1) % menu_count
    elif event_key == pygame.K_DOWN:
        menu_index = (menu_index + 1) % menu_count
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
    global running, game_state

    if event_key == pygame.K_RETURN:
        game_state = "menu"
    elif event_key == pygame.K_ESCAPE:
        running = False


running = True

while running:
    clock.tick(60)

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
