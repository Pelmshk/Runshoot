import os
import sys

import pygame




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
# основной персонаж
player = None
player_x, player_y = 15, 505
level = load_level('map1lvl.txt')

RIGHT = 'to the right'
LEFT = 'to the left'
UP = 'to the top'
DOWN = 'to the bottom'
STOP = 'stop'
motion = STOP

# группы спрайтов
all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
walls_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
player_bullets_group = pygame.sprite.Group()

tile_images = {
    'wall': load_image('box.png'),
    'empty': load_image('grass.png')
}
player_image = load_image('mar.png')
bullet_image = load_image('bullet.png')

tile_width = tile_height = 50


def terminate():
    pygame.quit()
    sys.exit()


def generate_level(level):
    new_player, x, y = None, None, None

    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Tile('empty', x, y)
            elif level[y][x] == '/':
                Wall('wall', x, y)
            Tile('empty', player_x, player_y)
            new_player = Player(player_x, player_y)
    # вернем игрока, а также размер поля в клетках
    return new_player, x, y


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)


class Wall(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)






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
            if pos_y != 0:
                if level[pos_y - 1][pos_x] != '/':
                    player_y -= 50

        elif event.key == pygame.K_DOWN:
            if pos_y != 10:
                if level[pos_y + 1][pos_x] != '/':
                    player_y += 50

        elif event.key == pygame.K_LEFT:
            if pos_x != 0:
                if level[pos_y][pos_x - 1] != '/':
                    player_x -= 50

        elif event.key == pygame.K_RIGHT:
            if pos_x != 13:
                if level[pos_y][pos_x + 1] != '/':
                    player_x += 50

        self.rect = self.image.get_rect().move(
            player_x, player_y)


def start_screen():
    global player, motion
    fon = pygame.transform.scale(load_image('fon.jpg'), (width, height))
    screen.blit(fon, (0, 0))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    player, level_x, level_y = generate_level(level)
                    all_sprites.draw(screen)
                    all_sprites.update()
                else:
                    Player.move(player, event)

                player, level_x, level_y = generate_level(level)
                all_sprites.draw(screen)
                all_sprites.update()

        pygame.display.flip()
        clock.tick(FPS)
        pygame.event.pump()


if __name__ == '__main__':
    pygame.init()
    pygame.display.set_caption('RunShoot')
    size = width, height = 700, 550
    screen = pygame.display.set_mode(size)
    screen.fill((0, 0, 255))
    clock = pygame.time.Clock()

    start_screen()
