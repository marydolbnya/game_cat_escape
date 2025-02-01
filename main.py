import pygame
import os
import sys
import random

# число кадров в секунду
FPS = 60
#размеры игрового поля
WIDTH, HEIGHT = 800, 600
# размеры клетки поля
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
    # построчный вывод заставки
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('white'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)
        # картинка не будет меняться, не нужно ее переключать
        pygame.display.flip()

    while True:
        for event in pygame.event.get():
            # закрытие стартового окна должно завершить игру
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return 1 if event.type == pygame.KEYDOWN and event.key == pygame.K_1 else 9
        clock.tick(FPS)


def end_screen(lives, bonuses):
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
        result_string = font.render('Набрано очков: ' + str(bonuses), 1, pygame.Color('white'))
        rect = result_string.get_rect()
        rect.y = outro_rect.bottom + 10
        rect.x = (WIDTH - rect.width) // 2
        screen.blit(result_string, rect)
    # картинка не будет меняться, не нужно ее обновлять
    pygame.display.flip()
    while True:
        for event in pygame.event.get():
            # любое нажатие просто завершает программу
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
            # спрайты стен сохраняются еще и в своей группе
            walls_group.add(self)
        self.image = tile_images[tile_type]
        # размещаем созданный и сгруппированный спрайт на поле
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)


class Bonus(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(bonus_group, all_sprites)
        # для каждого бонуса картинка выбирается случайно
        self.image = random.choice(bonus_images)
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)

class Door(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(doors_group, all_sprites)
        self.image = door_image
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y + 5)

class Enemy(pygame.sprite.Sprite):
    def __init__(self, columns, rows, pos_x, pos_y):
        # соответствие номеров спрайтов в спрайтшите ходу и тику
        self.moves = (((1, 0), (12, 13, 14, 15)),
                      ((-1, 0), (8, 9, 10, 11)),
                      ((0, 1), (0, 1, 2, 3)),
                      ((0, -1), (4, 5, 6)))
        self.speed = 1
        # счетчик тиков для переключения спрайтов в спрайтшите
        self.counter = 0
        # сколько кадров держится один спрайт из спрайтшита
        self.move_period = 10
        super().__init__(enemies_group, all_sprites)
        # спрайты из спрайтшита
        self.frames = []
        self.cut_sheet(enemy_image, columns, rows)
        # выбор изначального направления движения
        self.move = random.choice(self.moves)
        self.cur_frame = self.move[1][0]
        self.image = self.frames[self.cur_frame]
        self.rect = self.image.get_rect()
        # размещение на поле
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
        # если движение в выбранном направлении привело к столкновению
        if pygame.sprite.spritecollideany(self, walls_group):
            #отменяем сделанный ход
            self.rect = self.rect.move(*map(lambda x: -x * self.speed, self.move[0]))
            # меняем направление движения
            self.move = random.choice(self.moves)
        # выбираем спрайт из спрайтшита в зависимости от тика и направления движения
        self.cur_frame = self.move[1][(self.counter // self.move_period) % len(self.move[1])]
        self.image = self.frames[self.cur_frame]


def create_sparks(pos):
    # число искр
    particle_count = 20
    # возможные значения для составляющих вектора скорости
    numbers = range(-5, 6)
    for _ in range(particle_count):
        Spark(pos, random.choice(numbers), random.choice(numbers), (0, 0, WIDTH, HEIGHT))


class Player(pygame.sprite.Sprite):
    # игроков может быть несколько, поэтому накопленные бонусы, жизни и управления у каждого свои
    def __init__(self, pos_x, pos_y, lives=9, bonuses=0,
                 control=(pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT)):
        # для проверки столкновения группами у каждого игрока своя группа
        self.group = pygame.sprite.Group()
        super().__init__(player_group, all_sprites, self.group)
        # номера спрайтов в спрайтшите в зависимости от тика и направления движения
        self.moves = (((1, 0), (4, 5, 6, 7)),
                      ((1, 1), (4, 5, 6, 7)),
                      ((1, -1), (4, 5, 6, 7)),
                      ((-1, 0), (12, 13, 14, 15)),
                      ((-1, 1), (12, 13, 14, 15)),
                      ((-1, -1), (12, 13, 14, 15)),
                      ((0, 1), (0, 1, 2, 3)),
                      ((0, -1), (16, 17, 18)))
        self.lives = lives
        self.bonuses = bonuses
        self.control = control
        # количество тиков, в течении которых игрок неуязвим (после потери одной жизни, например)
        self.invulnerable_times = 0
        self.speed = 2
        # число тиков для изменения спрайта для одного направления движения
        self.move_period = 10
        self.frames = []
        self.counter = 0
        self.cut_sheet(player_image, 4, 5)
        self.move = random.choice(self.moves)
        self.cur_frame = self.move[1][0]
        self.image = self.frames[self.cur_frame]
        self.rect = self.image.get_rect()
        self.rect.x = tile_width * pos_x + (tile_width - self.image.get_rect().width) // 2
        self.rect.y = tile_height * pos_y + (tile_height - self.image.get_rect().height) // 2

    def cut_sheet(self, sheet, columns, rows):
        # нарезка спрайтов из спрайтшита и сборка их в список
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self, *args):
        self.counter += 1
        # проверяем нажатость клавиш, управляющих данным игроком
        pressed = pygame.key.get_pressed()
        move = [0, 0]
        if pressed[self.control[3]]:
            move[0] = 1
        if pressed[self.control[2]]:
            move[0] = -1
        if pressed[self.control[0]]:
            move[1] = -1
        if pressed[self.control[1]]:
            move[1] = 1

        if move[0] or move[1]:
            for step in self.moves:
                if step[0] == (move[0], move[1]):
                    self.move = step
            self.rect = self.rect.move(*map(lambda x: x * self.speed, move))
            # если ход в выбранном направлении привед к столкновению со стеной
            if pygame.sprite.spritecollideany(self, walls_group):
                # просто отменяем ход
                self.rect = self.rect.move(*map(lambda x: -x * self.speed, move))
            # если игрок столкнулся с одним из бонусов, спрайт бонуса удаляется
            if pygame.sprite.groupcollide(self.group, bonus_group, False, True):
                self.bonuses += 1
                # из игрока сыплются искры
                create_sparks((self.rect.x, self.rect.y))
        else:
            # если игрок не движется, не нужно менять спрайт в спрайтшите для заданного направления движения
            self.counter = 0
        # меняем спрайт в зависимости от тика и направления движения
        self.cur_frame = self.move[1][(self.counter // self.move_period) % len(self.move[1])]
        self.image = self.frames[self.cur_frame]

        # если игрок уязвим и столкнулся с одним из врагов, удаляем его, если жизнь последняя
        if not self.invulnerable_times and pygame.sprite.groupcollide(self.group, enemies_group,
                                                                      self.lives <= 1, False):
            self.lives -= 1
            # включаем неуязвимость на 3 секунды, чтобы игрок успел отбежать о тврага
            self.invulnerable_times = 3 * FPS

        if self.invulnerable_times:
            # если игрок неуязвим, это должно быть видно, он уменьшается в два раза
            self.image = pygame.transform.scale(self.image, (self.image.get_rect().width // 2,
                                                             self.image.get_rect().height // 2))
            # счетчик тиков неуязвимости уменьшается
            self.invulnerable_times -= 1


class Spark(pygame.sprite.Sprite):
    # генерация картинок искр разных размеров
    fire = [load_image(('star.png'))]
    for scale in (5, 10, 20):
        fire.append(pygame.transform.scale(fire[0], (scale, scale)))

    def __init__(self, pos, dx, dy, field_rect):
        super().__init__(all_sprites)
        self.field_rect = field_rect
        self.image = random.choice(self.fire)
        self.rect = self.image.get_rect()
        # вектор начальной скорости движения искры
        self.velocity = [dx, dy]
        self.rect.x, self.rect.y = pos
        # ускорение свободного падения искр
        self.gravity = 1

    def update(self):
        # к вектору скорости применяется ускорение
        self.velocity[1] += self.gravity
        # координаты искры меняются с заданной скоростью
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]
        # за пределами игрового поля искра гаснет
        if not self.rect.colliderect(self.field_rect):
            self.kill()

# statuses - текущее состояние игроков (жизней, бонусов, (вверх, вниз, вправо, влево))
def generate_level(level, statuses):
    # сначала создается подложка
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '#':
                Tile('wall', x, y)
            else:
                Tile('empty', x, y)
    # поверх подложки создаются бонусы и дверь
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == 'b':
                Bonus(x, y)
            elif level[y][x] == 'd':
                Door(x, y)
    # поверх подложки с бонусами создаются игроки
    player_idx = 0
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '@':
                if statuses and player_idx < len(statuses):
                    # создаем игрока, указывая, сколько у него осталось жизней, сколько имбыло накоплено бонусов
                    # и какими клавишами им можно управлять
                    Player(x, y, statuses[player_idx][0], statuses[player_idx][1], statuses[player_idx][2])
                    player_idx += 1
    # поверх всего оздаются враги - хозяева кота
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '*':
                Enemy(4, 4, x, y)


if __name__ == '__main__':
    # инициализация pygame и создание главного окна игры
    pygame.init()
    pygame.display.set_caption('Побег кота')
    size = WIDTH, HEIGHT
    screen = pygame.display.set_mode(size)

    # однократная загрузка всех картинок из файлов
    tile_images = {
        'wall': load_image('box.jpg'),
        'empty': load_image('floor.png')
    }

    player_image = load_image('catt.png')
    enemy_image = load_image('chel.png')
    bonus_images = (load_image('milk.png'), load_image('sousage.png'), load_image('fish.png'))
    lives_image = load_image('heart.png')
    door_image = load_image('door.png')

    # часы для получения счетчика тиков и синхронизации с FPS
    clock = pygame.time.Clock()

    # шрифт для вывода текстовой информации на игровом поле
    font = pygame.font.Font(None, 50)

    # стартовый экран, функция возвращает начальное количество жизни у каждого игрока
    lives = start_screen()

    # начальные состояния игроков, при смене уровня список создается по результатом оконченного
    players_state = [(lives, 0, (pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT)),
                     (lives, 0, (pygame.K_w, pygame.K_s, pygame.K_a, pygame.K_d))]
    # цикл по уровням
    for level_idx, level_file in enumerate(('map.txt', 'map2.txt', 'map3.txt')):
        # создание/пересоздания пустых групп спрайтов
        # при повторном создании ранее созданные удаляются вместе со всеми размещенными на них объектами
        # это делает сборщик мусора в Python
        all_sprites = pygame.sprite.Group()
        tiles_group = pygame.sprite.Group()
        walls_group = pygame.sprite.Group()
        enemies_group = pygame.sprite.Group()
        bonus_group = pygame.sprite.Group()
        doors_group = pygame.sprite.Group()
        player_group = pygame.sprite.Group()

        # загрузка уровня с созданием всех элементов
        generate_level(load_level(level_file), players_state)
        running = True

        # пока уровень не завершен и не закончились игроки
        while running and player_group.sprites():
            screen.fill(pygame.Color(0, 0, 0))
            # проверяем, не решил ли игрок завершить игру
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    terminate()

            # если один из игроков дошел до двери, ведущей на следующий уровень
            if pygame.sprite.groupcollide(player_group, doors_group, False, True):
                running = False
            # обновляем состояния всех - игрока, врагов, бонусов и т.д.
            all_sprites.update()
            all_sprites.draw(screen)

            # отрисовываем в верхнем левом углу количество жизней всех игроков
            for i in range(sum([x.lives for x in player_group.sprites()])):
                screen.blit(lives_image, (tile_width * i, 0))

            # отрисовываем картинку бонуса и делаем надпись с количеством бонусов, собранных всеми игроками
            screen.blit(bonus_images[0], (0, tile_height))
            # сумма бонусов, имеющихся у всех игроков
            got_bonuses = sum([x.bonuses for x in player_group.sprites()])
            string_rendered = font.render('x ' + str(got_bonuses), 1, pygame.Color('white'))
            string_rect = string_rendered.get_rect()
            string_rect.x = tile_width + 10
            string_rect.y = tile_height + 5
            screen.blit(string_rendered, string_rect)

            # пишем в верхнем правом углу номер уровня
            string_rendered = font.render('Уровень ' + str(level_idx + 1), 1, pygame.Color('white'))
            string_rect = string_rendered.get_rect()
            string_rect.x = WIDTH - string_rect.width - 5
            string_rect.y = 5
            screen.blit(string_rendered, string_rect)

            # переключаем буферы, показывая отрисованный кадр
            pygame.display.flip()
            # ждем синхронизации следующего кадра и FPS
            clock.tick(FPS)
        # если уровень завершен и игроков не осталось
        if not player_group.sprites():
            break
        else:
            # игроки остались, сохраняем их состояние для следующего уровня
            players_state = [(x.lives, x.bonuses, x.control) for x in player_group.sprites()]

    # цикл по уровням завершен, пора показывать итоги
    end_screen(sum([x.lives for x in player_group.sprites()]), sum([x.bonuses for x in player_group.sprites()]))
    terminate()