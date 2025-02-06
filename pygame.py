import pygame
import random
import os

# Инициализация Pygame
pygame.init()

# Константы
WIDTH = 480
HEIGHT = 800
FPS = 60
GRAVITY = 0.8
JUMP_POWER = -20
PLATFORM_WIDTH = 70
PLATFORM_HEIGHT = 20
PLAYER_SIZE = 40

# Цвета
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
BACKGROUND_COLOR = (135, 206, 235)

# Пути к изображениям
current_dir = os.path.dirname(__file__)
image_dir = os.path.join(current_dir, 'images')


# Загрузка изображений
def load_image(name, size=None):
    path = os.path.join(image_dir, name)
    image = pygame.image.load(path).convert_alpha()
    if size:
        image = pygame.transform.scale(image, size)
    return image


# Класс игрока
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = load_image('player.png', (PLAYER_SIZE, PLAYER_SIZE))
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH // 2, HEIGHT - 100)
        self.velocity_y = 0
        self.velocity_x = 0
        self.jump_power = JUMP_POWER
        self.bonus_jump = False
        self.bonus_timer = 0

    def update(self):
        self.velocity_y += GRAVITY
        self.rect.y += self.velocity_y
        self.rect.x += self.velocity_x

        # Обновление бонусов
        if self.bonus_jump:
            self.bonus_timer += 1
            if self.bonus_timer >= 300:  # 5 секунд при FPS=60
                self.jump_power = JUMP_POWER
                self.bonus_jump = False
                self.bonus_timer = 0

        # Границы экрана
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH


# Класс платформ
class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, type='normal'):
        super().__init__()
        self.type = type
        self.load_images()
        self.image = self.images[self.type]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.move_speed = 3 if type == 'moving' else 0
        self.direction = 1
        self.disappear = False
        self.disappear_timer = 0

    def load_images(self):
        self.images = {
            'normal': load_image('platform.png', (PLATFORM_WIDTH, PLATFORM_HEIGHT)),
            'moving': load_image('moving_platform.png', (PLATFORM_WIDTH, PLATFORM_HEIGHT)),
            'disappearing': load_image('disappearing_platform.png', (PLATFORM_WIDTH, PLATFORM_HEIGHT)),
            'bonus': load_image('bonus_platform.png', (PLATFORM_WIDTH, PLATFORM_HEIGHT))
        }

    def update(self):
        if self.type == 'moving':
            self.rect.x += self.move_speed * self.direction
            if self.rect.right >= WIDTH or self.rect.left <= 0:
                self.direction *= -1
        elif self.type == 'disappearing' and self.disappear:
            self.disappear_timer += 1
            if self.disappear_timer >= 30:
                self.kill()


# Класс врагов
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = load_image('enemy.png', (40, 40))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = 1

    def update(self):
        self.rect.x += self.speed
        if self.rect.right >= WIDTH or self.rect.left <= 0:
            self.speed *= -1


# Класс бонусов
class Bonus(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.type = random.choice(['jump', 'points'])
        self.image = load_image(f'bonus_{self.type}.png', (30, 30))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def apply(self, player):
        if self.type == 'jump':
            player.jump_power = JUMP_POWER * 1.5
            player.bonus_jump = True
        elif self.type == 'points':
            global score
            score += 500


# Инициализация окна
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Doodle Jump2")
clock = pygame.time.Clock()
background = load_image('background.png', (WIDTH, HEIGHT))

# Группы спрайтов
all_sprites = pygame.sprite.Group()
platforms = pygame.sprite.Group()
enemies = pygame.sprite.Group()
bonuses = pygame.sprite.Group()


# Система рекордов
def load_highscore():
    try:
        with open('highscore.txt', 'r') as f:
            return int(f.read())
    except:
        return 0


def save_highscore(value):
    with open('highscore.txt', 'w') as f:
        f.write(str(int(value)))


# Игровые переменные
high_score = load_highscore()
score = 0
game_over = False
game_state = 'menu'  # 'menu', 'playing', 'game_over'


# Создание объектов
def create_objects():
    global player
    # Игрок
    player = Player()
    all_sprites.add(player)

    # Начальная платформа
    Platform(WIDTH // 2 - PLATFORM_WIDTH // 2, HEIGHT - 50, 'normal').add(all_sprites, platforms)

    # Генерация платформ с ограничением по вертикали
    last_y = HEIGHT - 50  # Y позиция стартовой платформы
    min_distance = 50  # Минимальное расстояние между платформами
    max_distance = 150  # Максимальное расстояние между платформами

    # Генерация платформ
    for _ in range(14):
        x = random.randint(0, WIDTH - PLATFORM_WIDTH)
        # Новая Y координата с учетом ограничений
        last_y -= random.randint(min_distance, max_distance)
        type = random.choices(
            ['normal', 'moving', 'disappearing', 'bonus'],
            weights=[60, 20, 10, 10]
        )[0]
        Platform(x, last_y, type).add(all_sprites, platforms)

    # Генерация врагов и бонусов
    for _ in range(1):
        Enemy(random.randint(0, WIDTH), random.randint(100, HEIGHT - 200)).add(all_sprites, enemies)
    for _ in range(2):
        Bonus(random.randint(0, WIDTH), random.randint(100, HEIGHT - 200)).add(all_sprites, bonuses)


# Основной цикл игры
running = True
while running:
    clock.tick(FPS)

    # Обработка событий
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if game_state == 'menu' and event.key == pygame.K_SPACE:
                game_state = 'playing'
                all_sprites.empty()
                platforms.empty()
                enemies.empty()
                bonuses.empty()
                create_objects()
                score = 0
            elif game_state == 'game_over' and event.key == pygame.K_SPACE:
                game_state = 'playing'
                all_sprites.empty()
                platforms.empty()
                enemies.empty()
                bonuses.empty()
                create_objects()
                score = 0

    # Игровая логика
    if game_state == 'playing':
        # Управление
        keys = pygame.key.get_pressed()
        player.velocity_x = 0
        if keys[pygame.K_LEFT]:
            player.velocity_x = -8
        if keys[pygame.K_RIGHT]:
            player.velocity_x = 8

        # Движение камеры
        if player.rect.y <= HEIGHT // 3:
            scroll = abs(player.velocity_y)
            player.rect.y += scroll
            score += int(scroll)

            for sprite in all_sprites:
                if sprite != player:
                    sprite.rect.y += scroll

                    if sprite.rect.y > HEIGHT:
                        if isinstance(sprite, Platform):
                            sprite.kill()
                            # Генерация новых платформ
                            new_x = random.randint(0, WIDTH - PLATFORM_WIDTH)
                            if platforms:
                                highest = min([plat.rect.y for plat in platforms])
                                new_y = highest - random.randint(100, 200)
                            else:
                                new_y = -20
                            new_type = random.choices(
                                ['normal', 'moving', 'disappearing', 'bonus'],
                                weights=[60, 20, 10, 10]
                            )[0]
                            Platform(new_x, new_y, new_type).add(all_sprites, platforms)
                        else:
                            sprite.kill()

        # Проверка столкновений
        # С платформами
        platform_hits = pygame.sprite.spritecollide(player, platforms, False)
        for plat in platform_hits:
            if player.velocity_y > 0 and abs(player.rect.bottom - plat.rect.top) < 20:
                player.velocity_y = player.jump_power
                if plat.type == 'disappearing':
                    plat.disappear = True
                elif plat.type == 'bonus':
                    plat.kill()
                    Bonus(plat.rect.centerx, plat.rect.top - 20).add(all_sprites, bonuses)

        # С врагами
        if pygame.sprite.spritecollide(player, enemies, False):
            game_state = 'game_over'
            if score > high_score:
                high_score = score
                save_highscore(high_score)

        # С бонусами
        bonus_hits = pygame.sprite.spritecollide(player, bonuses, True)
        for bonus in bonus_hits:
            bonus.apply(player)

        # Проверка смерти
        if player.rect.y > HEIGHT:
            game_state = 'game_over'
            if score > high_score:
                high_score = score
                save_highscore(high_score)

    # Отрисовка
    screen.blit(background, (0, 0))
    all_sprites.draw(screen)

    # Интерфейс
    font = pygame.font.Font(None, 36)

    if game_state == 'menu':
        text = font.render("Doodle Jump2", True, WHITE)
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 3))
        text = font.render("Нажмите ПРОБЕЛ для начала игры", True, WHITE)
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2))
        text = font.render(f"Лучший рекорд: {high_score}", True, WHITE)
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 + 50))

    elif game_state == 'playing':
        text = font.render(f"рекорд: {score}", True, WHITE)
        screen.blit(text, (10, 10))
        text = font.render(f"Лучший рекорд: {high_score}", True, WHITE)
        screen.blit(text, (10, 50))

    elif game_state == 'game_over':
        text = font.render("Конец игры!", True, RED)
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 3))
        text = font.render(f"Рекорд: {score}", True, WHITE)
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2))
        text = font.render(f"Лучший рекорд: {high_score}", True, WHITE)
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 + 50))
        text = font.render("Для перезапуска нажмите ПРОБЕЛ!", True, WHITE)
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT - 100))

    pygame.display.flip()
    all_sprites.update()

pygame.quit()
