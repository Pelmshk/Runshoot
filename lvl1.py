import os
import sys

import pygame
import random

pygame.font.init()


def load_image(name):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    return image


def load_level(filename):
    filename = "data/" + filename
    # читаем уровень, убирая символы перевода строки
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]

    # и подсчитываем максимальную длину
    max_width = max(map(len, level_map))

    # дополняем каждую строку пустыми клетками ('.')
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


FPS = 90
# счетчик очков за уровень
points_cnt = 0
POINTS_COLOR = (216, 169, 3)
# основной персонаж
player = None
player_x, player_y = 2, 503

enemy_cnt = 3
death = 0

# загрузка уровня
levelnum = random.randint(0, 1)
if levelnum:
    level = load_level('map1lvl.txt')
else:
    level = load_level('map2lvl.txt')
points_font = pygame.font.Font(None, 40)

RIGHT = 'to the right'
LEFT = 'to the left'
UP = 'to the top'
DOWN = 'to the bottom'

# группы спрайтов
all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
walls_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
player_bullets_group = pygame.sprite.Group()
coin_group = pygame.sprite.Group()
info_group = pygame.sprite.Group()

tile_images = {
    'wall': load_image('wall.png'),
    'empty': load_image('floor.png')
}
player_image = load_image('mar.png')
enemy_image = load_image('enemy.png')
bullet_image = load_image('bullet.png')
coin_image = load_image('coin.png')
info_image = load_image('info.png')

tile_width = tile_height = 50


def terminate():
    pygame.quit()
    sys.exit()


# создание уровня
def generate_level(level):
    new_player, x, y = None, None, None

    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Tile('empty', x, y)
            elif level[y][x] == '/':
                wall = Wall('wall', x, y)
            Tile('empty', player_x, player_y)

    if levelnum:
        coin1 = Coin(load_image('coin.png'), 6, 6, 110, 60)
        сoin2 = Coin(load_image('coin.png'), 6, 6, 360, 360)
        coin3 = Coin(load_image('coin.png'), 6, 6, 13 * 50 + 10, 9 * 50 + 10)

        enemy1 = EnemyHorizontal(2, 52, 8)
        enemy2 = EnemyVertical(2, 152, 3)
        enemy3 = EnemyVertical(603, 203, 5)

    else:
        coin1 = Coin(load_image('coin.png'), 6, 6, 7 * 50 + 10, 50 + 10)
        сoin2 = Coin(load_image('coin.png'), 6, 6, 50 + 10, 5 * 50 + 10)
        coin3 = Coin(load_image('coin.png'), 6, 6, 9 * 50 + 10, 6 * 50 + 10)

        enemy1 = EnemyHorizontal(6 * 50 + 2, 52, 7)
        enemy2 = EnemyVertical(2, 2, 5)
        enemy3 = EnemyHorizontal(3 * 50 + 2, 8 * 50 + 2, 10)

    # вернем игрока, а также размер поля в клетках
    return x, y


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)


# класс препятсвий
class Wall(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)
        walls_group.add(self)


# класс пуль
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.direction = direction
        if direction == UP:
            self.image = bullet_image
            self.rect = self.image.get_rect()
            self.rect.bottom = y
            self.rect.centerx = x
            self.speedy = -10
        elif direction == LEFT:
            self.image = pygame.transform.rotate(bullet_image, 90)
            self.rect = self.image.get_rect()
            self.rect.bottom = y + 40
            self.rect.centerx = x - 20
            self.speedy = -10
        elif direction == DOWN:
            self.image = pygame.transform.rotate(bullet_image, 180)
            self.rect = self.image.get_rect()
            self.rect.bottom = y + 70
            self.rect.centerx = x
            self.speedy = 10
        elif direction == RIGHT:
            self.image = pygame.transform.rotate(bullet_image, 270)
            self.rect = self.image.get_rect()
            self.rect.bottom = y + 40
            self.rect.centerx = x + 20
            self.speedy = 10

    def update(self):
        global enemy_cnt, points_cnt
        if self.direction in [UP, DOWN]:
            self.rect.y += self.speedy
        elif self.direction in [LEFT, RIGHT]:
            self.rect.x += self.speedy

        if self.rect.bottom < 0 or pygame.sprite.groupcollide(player_bullets_group, walls_group, True, False):
            self.kill()
        elif pygame.sprite.groupcollide(player_bullets_group, enemy_group, True, True):
            enemy_cnt -= 1
            points_cnt += 500
            self.kill()
            print(enemy_cnt)


# монетки
class Coin(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, x, y):
        super().__init__(all_sprites)
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(x, y)

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self):
        global points_cnt
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]
        if self.rect.colliderect(player.rect):
            points_cnt += 1000
            self.kill()


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.image = player_image
        self.rect = self.image.get_rect().move(
            pos_x, pos_y)

    def move(self, event):
        global player_x, player_y
        pos_x, pos_y = player_x // 50, player_y // 50
        if event.key == pygame.K_UP:
            if pos_y != 0 and level[pos_y - 1][pos_x] != '/':
                player_y -= 50

        elif event.key == pygame.K_DOWN:
            if pos_y != 10 and level[pos_y + 1][pos_x] != '/':
                player_y += 50

        elif event.key == pygame.K_LEFT:
            if pos_x != 0 and level[pos_y][pos_x - 1] != '/':
                player_x -= 50

        elif event.key == pygame.K_RIGHT:
            if pos_x != 13 and level[pos_y][pos_x + 1] != '/':
                player_x += 50

        self.rect = self.image.get_rect().move(
            player_x, player_y)

    # функция стрельбы, создающая объект класса Bullet
    def shoot(self, direction):
        bullet = Bullet(self.rect.centerx, self.rect.top, direction)
        all_sprites.add(bullet)
        player_bullets_group.add(bullet)


class EnemyHorizontal(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, way):
        super().__init__(enemy_group, all_sprites)
        self.image = enemy_image
        self.rect = self.image.get_rect().move(
            pos_x, pos_y)
        self.cnt, self.goright = 0, True
        self.pos_x, self.pos_y, self.way = pos_x, pos_y, way

    def update(self):
        global death
        if pygame.sprite.groupcollide(player_group, enemy_group, True, False):
            self.kill()
            death = 1
        if self.goright:
            self.cnt += 1
            self.pos_x += 2
            self.rect = self.image.get_rect().move(
                self.pos_x, self.pos_y)
            if self.cnt >= self.way * 25:
                self.goright = False
        else:
            self.cnt -= 1
            self.pos_x -= 2
            self.rect = self.image.get_rect().move(
                self.pos_x, self.pos_y)
            if self.cnt <= 0:
                self.goright = True


class EnemyVertical(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, way):
        super().__init__(enemy_group, all_sprites)
        self.image = enemy_image
        self.rect = self.image.get_rect().move(
            pos_x, pos_y)
        self.cnt, self.goright = 0, True
        self.pos_x, self.pos_y, self.way = pos_x, pos_y, way

    def update(self):
        global death
        if pygame.sprite.groupcollide(player_group, enemy_group, True, False):
            self.kill()
            death = 1
        if self.goright:
            self.cnt += 1
            self.pos_y += 2
            self.rect = self.image.get_rect().move(
                self.pos_x, self.pos_y)
            if self.cnt >= self.way * 25:
                self.goright = False
        else:
            self.cnt -= 1
            self.pos_y -= 2
            self.rect = self.image.get_rect().move(
                self.pos_x, self.pos_y)
            if self.cnt <= 0:
                self.goright = True


class Info(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(info_group, all_sprites)
        self.image = info_image
        self.rect = self.image.get_rect().move(
            pos_x, pos_y)


def start_screen():
    global player, motion
    fon = pygame.transform.scale(load_image('fon.png'), (width, height))
    screen.blit(fon, (0, 0))

    gogo = True
    started = False
    info_opened = False

    while True:
        if enemy_cnt == 0 or death == 1:
            gogo = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not started:
                    level_x, level_y = generate_level(level)
                    player = Player(player_x, player_y)
                    all_sprites.draw(screen)
                    all_sprites.update()
                    started = True
                elif event.key == pygame.K_F1:
                    if not info_opened:
                        info = Info(0, 0)
                        info_group.draw(screen)
                        info_opened = True
                    else:
                        info.kill()
                        info_opened = False
                elif event.key in [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT]:
                    Player.move(player, event)
                elif event.key == 119:
                    player.shoot(UP)
                elif event.key == 100:
                    player.shoot(RIGHT)
                elif event.key == 115:
                    player.shoot(DOWN)
                elif event.key == 97:
                    player.shoot(LEFT)

        if gogo:
            all_sprites.draw(screen)
            all_sprites.update()

            points_text = points_font.render(f'points: {points_cnt}', True, POINTS_COLOR)
            screen.blit(points_text, (10, 10))
            pygame.display.update()

            pygame.display.flip()
            clock.tick(FPS)
            pygame.event.pump()
        else:
            if enemy_cnt == 0:
                fon = pygame.transform.scale(load_image('win.png'), (width, height))
                screen.blit(fon, (0, 0))
                points_text = points_font.render(f'Your score: {points_cnt}', True, POINTS_COLOR)
                screen.blit(points_text, (260, 420))
            else:
                fon = pygame.transform.scale(load_image('gameover.png'), (width, height))
                screen.blit(fon, (0, 0))

            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    terminate()
                elif event.type == pygame.KEYDOWN:
                    terminate()



if __name__ == '__main__':
    pygame.init()
    pygame.display.set_caption('RunShoot')
    size = width, height = 700, 550
    screen = pygame.display.set_mode(size)
    screen.fill((0, 0, 255))
    clock = pygame.time.Clock()

    start_screen()
