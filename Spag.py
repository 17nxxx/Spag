import pygame
import random
import math
from pygame import mixer

# Инициализация pygame
pygame.init()

# Создание экрана
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Космический стрелок")

# Загрузка изображений
player_img = pygame.image.load('music/boat.png')
enemy_img = pygame.image.load('music/enemy.png')
bullet_img = pygame.image.load('music/bullet (1).png')
boss_img = pygame.image.load('music/boss.png')
background_img = pygame.image.load('music/back.jpg')
background_img = pygame.transform.scale(background_img, (screen_width, screen_height))

# Загрузка звуков
mixer.music.load('music/spaceice.wav')
mixer.music.set_volume(0.3)
laser_sound = mixer.Sound('music/laser.wav')
explosion_sound = mixer.Sound('music/explos.wav')

# Игровые переменные
player_x = 370
player_y = 480
player_speed = 10
player_health = 100
player_lives = 3
score = 0
level = 1
game_over = False
boss_active = False

# Пули игрока
bullets = []
bullet_speed = 30
bullet_cooldown = 10

# Пули босса
boss_bullets = []
boss_bullet_speed = 15

# Враги
enemies = []
enemy_speed = 1
enemy_spawn_timer = 0

# Босс
boss_x = 300
boss_y = 50
boss_speed = 1
boss_health = 200
boss_attack_timer = 0

# Улучшения
powerups = []
powerup_types = ['health', 'speed', 'double_shot']

# Шрифты
font = pygame.font.SysFont('Arial', 32)
big_font = pygame.font.SysFont('Arial', 64)


def show_score():
    score_text = font.render(f"Очки: {score}", True, (255, 255, 255))
    screen.blit(score_text, (10, 10))

    level_text = font.render(f"Уровень: {level}", True, (255, 255, 255))
    screen.blit(level_text, (10, 50))

    health_text = font.render(f"Здоровье: {player_health}", True, (255, 255, 255))
    screen.blit(health_text, (10, 90))

    lives_text = font.render(f"Жизни: {player_lives}", True, (255, 255, 255))
    screen.blit(lives_text, (10, 130))


def player(x, y):
    screen.blit(player_img, (x, y))


def spawn_enemy():
    x = random.randint(0, screen_width - 64)
    y = random.randint(-100, -40)
    enemies.append([x, y])


def spawn_boss():
    global boss_active, boss_health
    boss_active = True
    boss_health = 200 + (level * 50)


def draw_enemies():
    for enemy in enemies:
        screen.blit(enemy_img, (enemy[0], enemy[1]))


def fire_bullet(x, y):
    bullets.append([x + 16, y])
    laser_sound.play()


def draw_bullets():
    for bullet in bullets:
        screen.blit(bullet_img, (bullet[0], bullet[1]))


def draw_boss_bullets():
    for bullet in boss_bullets:
        screen.blit(bullet_img, (bullet[0], bullet[1]))


def check_collision(obj1_x, obj1_y, obj2_x, obj2_y, obj1_size, obj2_size):
    distance = math.sqrt((obj1_x - obj2_x) ** 2 + (obj1_y - obj2_y) ** 2)
    return distance < (obj1_size + obj2_size)


def spawn_powerup(x, y):
    powerup_type = random.choice(powerup_types)
    powerups.append([x, y, powerup_type])


def draw_powerups():
    for powerup in powerups:
        if powerup[2] == 'health':
            pygame.draw.rect(screen, (255, 0, 0), (powerup[0], powerup[1], 20, 20))
        elif powerup[2] == 'speed':
            pygame.draw.rect(screen, (0, 255, 0), (powerup[0], powerup[1], 20, 20))
        else:
            pygame.draw.rect(screen, (0, 0, 255), (powerup[0], powerup[1], 20, 20))


def show_game_over():
    game_over_text = big_font.render("ИГРА ОКОНЧЕНА", True, (255, 255, 255))
    screen.blit(game_over_text, (200, 250))
    final_score_text = font.render(f"Финальный счет: {score}", True, (255, 255, 255))
    screen.blit(final_score_text, (250, 320))


# Основной игровой цикл
running = True
mixer.music.play(-1)

while running:
    # Фон
    screen.blit(background_img, (0, 0))

    # Обработка событий
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not game_over:
                fire_bullet(player_x, player_y)
            if event.key == pygame.K_r and game_over:
                # Перезапуск игры
                player_x = 370
                player_y = 480
                player_health = 100
                player_lives = 3
                score = 0
                level = 1
                game_over = False
                boss_active = False
                enemies.clear()
                bullets.clear()
                boss_bullets.clear()
                powerups.clear()

    if not game_over:
        # Управление игроком
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and player_x > 0:
            player_x -= player_speed
        if keys[pygame.K_d] and player_x < screen_width - 64:
            player_x += player_speed
        if keys[pygame.K_w] and player_y > 0:
            player_y -= player_speed
        if keys[pygame.K_s] and player_y < screen_height - 64:
            player_y += player_speed

        # Охлаждение пуль
        if bullet_cooldown > 0:
            bullet_cooldown -= 1

        # Спавн врагов
        enemy_spawn_timer += 1
        if enemy_spawn_timer >= 60 - (level * 5) and len(enemies) < 5 + level:
            spawn_enemy()
            enemy_spawn_timer = 0

        # Движение врагов
        for enemy in enemies[:]:
            enemy[1] += enemy_speed + (level * 0.2)

            # Проверка выхода за экран
            if enemy[1] > screen_height:
                enemies.remove(enemy)
                player_health -= 10
                if player_health <= 0:
                    player_lives -= 1
                    player_health = 100
                    if player_lives <= 0:
                        game_over = True

            # Проверка столкновения с игроком
            if check_collision(player_x, player_y, enemy[0], enemy[1], 15, 45):
                explosion_sound.play()
                enemies.remove(enemy)
                player_health -= 20
                if player_health <= 0:
                    player_lives -= 1
                    player_health = 100
                    if player_lives <= 0:
                        game_over = True

        # Движение пуль игрока
        for bullet in bullets[:]:
            bullet[1] -= bullet_speed
            if bullet[1] < -32:
                bullets.remove(bullet)
                continue

            # Проверка попадания во врага
            for enemy in enemies[:]:
                if check_collision(bullet[0], bullet[1], enemy[0], enemy[1], 15, 45):
                    explosion_sound.play()
                    bullets.remove(bullet)
                    enemies.remove(enemy)
                    score += 10

                    # Шанс выпадения улучшения
                    if random.random() < 0.1:
                        spawn_powerup(enemy[0], enemy[1])
                    break

        # Босс
        if score >= level * 500 and not boss_active:
            spawn_boss()

        if boss_active:
            # Движение босса
            boss_x += boss_speed
            if boss_x <= 0 or boss_x >= screen_width - 128:
                boss_speed *= -1

            # Отрисовка босса
            screen.blit(boss_img, (boss_x, boss_y))

            # Здоровье босса
            pygame.draw.rect(screen, (255, 0, 0), (boss_x, boss_y - 20, 128, 10))
            pygame.draw.rect(screen, (0, 255, 0), (boss_x, boss_y - 20, 128 * (boss_health / (200 + level * 50)), 10))

            # Атака босса
            boss_attack_timer += 1
            if boss_attack_timer >= 60:  # Атака каждую секунду
                # Босс стреляет вниз (в сторону игрока)
                boss_bullets.append([boss_x + 64, boss_y + 128])
                boss_attack_timer = 0

            # Движение пуль босса
            for bullet in boss_bullets[:]:
                bullet[1] += boss_bullet_speed  # Пули летят вниз
                if bullet[1] > screen_height:
                    boss_bullets.remove(bullet)
                    continue

                # Проверка попадания в игрока
                if check_collision(bullet[0], bullet[1], player_x, player_y, 15, 45):
                    explosion_sound.play()
                    boss_bullets.remove(bullet)
                    player_health -= 15
                    if player_health <= 0:
                        player_lives -= 1
                        player_health = 100
                        if player_lives <= 0:
                            game_over = True

            # Проверка попадания пуль игрока в босса
            for bullet in bullets[:]:
                if check_collision(bullet[0], bullet[1], boss_x + 64, boss_y + 64, 32, 128):
                    explosion_sound.play()
                    bullets.remove(bullet)
                    boss_health -= 5
                    if boss_health <= 0:
                        explosion_sound.play()
                        boss_active = False
                        score += 200
                        level += 1
                        spawn_powerup(boss_x + 64, boss_y + 64)

        # Улучшения
        for powerup in powerups[:]:
            powerup[1] += 2
            if check_collision(player_x, player_y, powerup[0], powerup[1], 64, 30):
                if powerup[2] == 'health':
                    player_health = min(100, player_health + 30)
                elif powerup[2] == 'speed':
                    player_speed = min(10, player_speed + 1)
                else:
                    bullet_cooldown = 600  # 10 секунд двойного выстрела
                powerups.remove(powerup)
            elif powerup[1] > screen_height:
                powerups.remove(powerup)

        # Двойной выстрел
        if bullet_cooldown > 0 and pygame.key.get_pressed()[pygame.K_SPACE] and len(bullets) < 2:
            fire_bullet(player_x - 20, player_y)
            fire_bullet(player_x + 20, player_y)

    # Отрисовка игровых объектов
    draw_enemies()
    draw_bullets()
    draw_boss_bullets()
    draw_powerups()
    player(player_x, player_y)
    show_score()

    if game_over:
        show_game_over()

    pygame.display.update()
    pygame.time.delay(30)

pygame.quit()
