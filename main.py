import pygame
import os
import sys
import random

FPS = 60
WIDTH, HEIGHT = 800, 600
tile_width = tile_height = 50

def load_image(name):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    return image


def terminate():
    pygame.quit()
    sys.exit()


def start_screen():
    intro_text = ["ПОБЕГ КОТА", "",
                  "Правила игры:",
                  "Стрелками управляйте котом,",
                  "Не дайте себя поймать",
                  "Режимы:",
                  "9 жизней",
                  "Без права на ошибку (клавиша 1)"]

    fon = pygame.transform.scale(load_image('start.jpg'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('white'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)
        pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return 1 if event.type == pygame.KEYDOWN and event.key == pygame.K_1 else 9
        clock.tick(FPS)


def end_screen():
    img = load_image('good_end.jpg' if lives else 'bad_end.jpg')
    font = pygame.font.Font(None, 80)
    string_rendered = font.render('Победа' if lives else 'Вы проиграли', 1, pygame.Color('white'))
    outro_rect = string_rendered.get_rect()
    outro_rect.x = (WIDTH - outro_rect.width) // 2
    outro_rect.y = (HEIGHT - outro_rect.height) // 2
    img = pygame.transform.scale(img, (WIDTH, HEIGHT))
    screen.blit(img, (0, 0))
    screen.blit(string_rendered, outro_rect)
    if lives:
        result_string = font.render('Съедено рыбок: ' + str(got_bonuses), 1, pygame.Color('white'))
        rect = result_string.get_rect()
        rect.y = outro_rect.bottom + 10
        rect.x = (WIDTH - rect.width) // 2
        screen.blit(result_string, rect)
    pygame.display.flip()
    while True:
        for event in pygame.event.get():
            if event.type in (pygame.QUIT, pygame.MOUSEBUTTONDOWN, pygame.KEYDOWN):
                terminate()


def load_level(filename):
    filename = "data/" + filename
    # читаем уровень, убирая символы перевода строки
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]
    # и подсчитываем максимальную длину
    max_width = max(map(len, level_map))
    # дополняем каждую строку пустыми клетками ('.')
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        if tile_type == 'wall':
            walls_group.add(self)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)


class Bonus(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(bonus_group, all_sprites)
        self.image = bonus_image
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)

class Door(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(doors_group, all_sprites)
        self.image = door_image
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y + 5)

class Enemy(pygame.sprite.Sprite):
    def __init__(self, columns, rows, pos_x, pos_y):
        self.moves = (((1, 0), (12, 13, 14, 15)),
                      ((-1, 0), (8, 9, 10, 11)),
                      ((0, 1), (0, 1, 2, 3)),
                      ((0, -1), (4, 5, 6)))
        self.speed = 1
        self.counter = 0
        self.move_period = 10
        super().__init__(enemies_group, all_sprites)
        self.frames = []
        self.cut_sheet(enemy_image, columns, rows)
        self.move = random.choice(self.moves)
        self.cur_frame = self.move[1][0]
        self.image = self.frames[self.cur_frame]
        self.rect.x = tile_width * pos_x + (tile_width - self.image.get_rect().width) // 2
        self.rect.y = tile_height * pos_y + (tile_height - self.image.get_rect().height) // 2

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self):
        self.counter += 1
        self.rect = self.rect.move(*map(lambda x: x * self.speed, self.move[0]))
        if pygame.sprite.spritecollideany(self, walls_group):
            self.rect = self.rect.move(*map(lambda x: -x * self.speed, self.move[0]))
            self.move = random.choice(self.moves)
        self.cur_frame = self.move[1][(self.counter // self.move_period) % len(self.move[1])]
        self.image = self.frames[self.cur_frame]


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.moves = (((1, 0), (4, 5, 6, 7)),
                      ((1, 1), (4, 5, 6, 7)),
                      ((-1, 0), (12, 13, 14, 15)),
                      ((-1, 1), (12, 13, 14, 15)),
                      ((0, 1), (0, 1, 2, 3)),
                      ((0, -1), (16, 17, 18)))
        self.speed = 2
        self.move_period = 10
        self.frames = []
        self.counter = 0
        self.cut_sheet(player_image, 4, 5)
        self.move = random.choice(self.moves)
        self.cur_frame = self.move[1][0]
        self.image = self.frames[self.cur_frame]
        self.rect.x = tile_width * pos_x + (tile_width - self.image.get_rect().width) // 2
        self.rect.y = tile_height * pos_y + (tile_height - self.image.get_rect().height) // 2

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self, *args):
        self.counter += 1
        pressed = pygame.key.get_pressed()
        move = [0, 0]
        if pressed[pygame.K_RIGHT]:
            move[0] = 1
        if pressed[pygame.K_LEFT]:
            move[0] = -1
        if pressed[pygame.K_UP]:
            move[1] = -1
        if pressed[pygame.K_DOWN]:
            move[1] = 1

        if move[0] or move[1]:
            for step in self.moves:
                if step[0] == (move[0], move[1]):
                    self.move = step
            self.rect = self.rect.move(*map(lambda x: x * self.speed, move))
            if pygame.sprite.spritecollideany(self, walls_group):
                self.rect = self.rect.move(*map(lambda x: -x * self.speed, move))
        else:
            self.counter = 0
        self.cur_frame = self.move[1][(self.counter // self.move_period) % len(self.move[1])]
        self.image = self.frames[self.cur_frame]


def generate_level(level):
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '#':
                Tile('wall', x, y)
            else:
                Tile('empty', x, y)
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == 'b':
                Bonus(x, y)
            elif level[y][x] == 'd':
                Door(x, y)
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '@':
                Player(x, y)
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '*':
                Enemy(4, 4, x, y)


if __name__ == '__main__':
    pygame.init()
    pygame.display.set_caption('Побег кота')
    size = WIDTH, HEIGHT
    screen = pygame.display.set_mode(size)

    tile_images = {
        'wall': load_image('box.jpg'),
        'empty': load_image('floor.png')
    }

    player_image = load_image('catt.png')
    enemy_image = load_image('chel.png')
    bonus_image = load_image('bonus.png')
    lives_image = load_image('heart.png')
    door_image = load_image('door.png')

    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 50)
    lives = start_screen()
    got_bonuses = 0
    invulnerable_times = 0
    for level_idx, level_file in enumerate(('map.txt', 'map2.txt', 'map3.txt')):
        all_sprites = pygame.sprite.Group()
        tiles_group = pygame.sprite.Group()
        walls_group = pygame.sprite.Group()
        enemies_group = pygame.sprite.Group()
        bonus_group = pygame.sprite.Group()
        doors_group = pygame.sprite.Group()
        player_group = pygame.sprite.Group()
        generate_level(load_level(level_file))
        running = True
        while running:
            if invulnerable_times:
                invulnerable_times -= 1
            screen.fill(pygame.Color(0, 0, 0))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    terminate()

            if not invulnerable_times and pygame.sprite.groupcollide(player_group, enemies_group, False, False):
                lives -= 1
                if not lives:
                    running = False
                else:
                    invulnerable_times = 3 * FPS
            if pygame.sprite.groupcollide(player_group, bonus_group, False, True):
                got_bonuses += 1
            if pygame.sprite.groupcollide(player_group, doors_group, False, True):
                running = False
            enemies_group.update()
            player_group.update()
            all_sprites.draw(screen)

            for i in range(lives):
                screen.blit(lives_image, (tile_width * i, 0))

            screen.blit(bonus_image, (0, tile_height))
            string_rendered = font.render('x ' + str(got_bonuses), 1, pygame.Color('white'))
            string_rect = string_rendered.get_rect()
            string_rect.x = tile_width + 10
            string_rect.y = tile_height + 5
            screen.blit(string_rendered, string_rect)

            string_rendered = font.render('Уровень ' + str(level_idx + 1), 1, pygame.Color('white'))
            string_rect = string_rendered.get_rect()
            string_rect.x = WIDTH - string_rect.width - 5
            string_rect.y = 5
            screen.blit(string_rendered, string_rect)

            pygame.display.flip()
            clock.tick(FPS)
        if not lives:
            break
    end_screen()
    pygame.quit()