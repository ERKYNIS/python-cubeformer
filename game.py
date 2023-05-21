import time

import pygame  # Основная библиотека pygame
from files.cubeformer_functions import save_info

# Инициализация игры
pygame.mixer.init()
pygame.init()
pygame.font.init()

# Переменные:
# =================
# Переменные для установки ширины и высоты окна
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
size = [SCREEN_WIDTH, SCREEN_HEIGHT]

# Переменные звуков:
click_sound = pygame.mixer.Sound("files/click_sound.wav")
portal_on_sound = pygame.mixer.Sound("files/portal_on.wav")
portal_off_sound = pygame.mixer.Sound("files/portal_off.wav")
next_level_sound = pygame.mixer.Sound("files/next_level.wav")
jump_sound = pygame.mixer.Sound("files/jump.wav")
victory_sound = pygame.mixer.Sound("files/victory.wav")

# Другие переменные:
id_game = 0
victory = False


# ===================


def load():
    global screen
    screen = pygame.display.set_mode(size)

    pygame.display.set_caption("Cubeформер | IT Cube")  # Название игры

    icon = pygame.image.load("files/red_player.png")  # Загрузка иконки игры
    pygame.display.set_icon(icon)  # Иконка игры

    # Подключение фото для заднего фона
    global bg
    bg = pygame.image.load('files/bg.png')


# Класс, для игроков
class Player(pygame.sprite.Sprite):
    def __init__(self, color, name):
        super().__init__()  # Для работы библиотеки tkinter

        self.color = color

        self.level = None

        self.name = name

        self.right = False  # Изначально игрок смотрит вправо, поэтому эта переменная True

        # Создаем изображение для игрока
        if color == 'red':
            self.image = pygame.image.load('files/red_player.png')
        else:
            self.image = pygame.image.load('files/green_player.png')

        self.rect = self.image.get_rect()

        # Задаем вектор скорости игрока
        self.change_x = 0
        self.change_y = 0

    def update(self):  # Передвижение + обновление игрока
        self.calc_grav()  # Гравитация

        # Передвижение игрока. change_x будет меняться при нажатии на стрелочки клавиатуры
        self.rect.x += self.change_x

        # Следим ударяем ли мы какой-то другой объект платформы
        block_hit_list = pygame.sprite.spritecollide(self, self.level.platform_list, False)

        # Перебираем все возможные объекты, с которыми могли бы столкнуться (влево/вправо)
        for block in block_hit_list:
            # Если мы идем направо,
            # устанавливает нашу правую сторону на левой стороне предмета, которого мы ударили
            if self.change_x > 0:
                self.rect.right = block.rect.left
            elif self.change_x < 0:
                # В противном случае, если мы движемся влево, то делаем наоборот
                self.rect.left = block.rect.right

        self.rect.y += self.change_y  # Передвижение вверх/вниз

        # Перебираем все возможные объекты, с которыми могли бы столкнуться (вверх/вниз)
        block_hit_list = pygame.sprite.spritecollide(self, self.level.platform_list, False)
        for block in block_hit_list:
            # Устанавливаем нашу позицию на основе верхней/нижней части объекта, на который мы попали
            if self.change_y > 0:
                self.rect.bottom = block.rect.top
            elif self.change_y < 0:
                self.rect.top = block.rect.bottom

            # Останавливаем вертикальное движение
            self.change_y = 0

    def calc_grav(self):  # Гравитация
        if self.change_y == 0:
            self.change_y = 1
        else:
            self.change_y += .95

        # Если уже на земле, то ставим позицию Y = 0
        if self.rect.y >= SCREEN_HEIGHT - self.rect.height and self.change_y >= 0:
            self.change_y = 0
            self.rect.y = SCREEN_HEIGHT - self.rect.height

    def jump(self):  # Прыжок
        # Опускаемся на 10 пикселей по Y, чтобы проверить соприкосновение и далее поднимаемся обратно
        self.rect.y += 10
        platform_hit_list = pygame.sprite.spritecollide(self, self.level.platform_list, False)
        self.rect.y -= 10

        # Если всё в порядке, передвигаем игрока вверх (прыжок).
        if len(platform_hit_list) > 0 or self.rect.bottom >= SCREEN_HEIGHT:
            self.change_y = -16
            jump_sound.play()

    def go_left(self):  # Передвижение игрока влево
        self.change_x = -9  # Двигаем игрока по Х
        if self.right:  # Если игрок смотрит вправо, то переворачиваем его
            self.flip()
            self.right = False

    def go_right(self):  # Передвижение игрока вправо (похожее на go_left)
        self.change_x = 9
        if not self.right:
            self.flip()
            self.right = True

    def stop(self):  # Оставить игрока
        self.change_x = 0

    def flip(self):  # Переворот игрока (зеркальное отражение)
        self.image = pygame.transform.flip(self.image, True, False)

    def restart(self):  # Перезапуск персонажа
        self.right = False
        self.change_x = 0
        self.change_y = 0

        self.rect.x = 340
        self.rect.y = SCREEN_HEIGHT - self.rect.height


class Portal(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load('files/portal_unactive.png')
        self.rect = self.image.get_rect()
        self.state = False

    def set_active(self, state):
        self.state = state
        if self.state:
            self.image = pygame.image.load('files/portal.png')
        else:
            self.image = pygame.image.load('files/portal_unactive.png')


class Button(pygame.sprite.Sprite):  # Класс кнопки
    def __init__(self, color):
        super().__init__()
        if color == 1:
            self.color = 'red'
        else:
            self.color = 'green'
        self.image = pygame.image.load(f'files/{self.color}_button.png')
        self.rect = self.image.get_rect()
        self.state = False

    def set_tapped(self):
        self.state = not self.state
        if self.state:
            self.image = pygame.transform.scale(pygame.image.load(f'files/{self.color}_button.png'),
                                                (40, 25))
            self.rect.y = self.rect.y + 7
        else:
            self.image = pygame.transform.scale(pygame.image.load(f'files/{self.color}_button.png'),
                                                (40, 32))
            self.rect.y = self.rect.y - 7


class Platform(pygame.sprite.Sprite):  # Класс платформы
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load('files/platform.png')  # Загрузка изображения для платформы
        self.rect = self.image.get_rect()  # Получение размера изображения


class Victory(pygame.sprite.Sprite):  # Класс платформы
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load('files/victory.png')  # Загрузка изображения для платформы
        self.rect = self.image.get_rect()  # Получение размера изображения


def game_victory(screen_arg):
    save_info(table='games', column='result', value='Победа', where=True,
              where_column='id')
    time.sleep(3)
    global victory
    victory = True
    victory_sound.play()


class Level(object):  # Класс для расстановки платформ на сцене
    def __init__(self, player):
        self.platform_list = pygame.sprite.Group()  # Создаем группу спрайтов (для платформ)
        self.buttons_list = pygame.sprite.Group()  # Создаем группу спрайтов (для кнопок)
        self.portals = pygame.sprite.Group()  # Создаем группу спрайтов (для порталов)
        self.objects = pygame.sprite.Group()  # Создаем группу спрайтов (для остальных объектов)
        self.player = player  # Ссылка на игрока

    def update(self):  # Обновление платформ и кнопок на экране
        self.platform_list.update()
        self.buttons_list.update()
        self.portals.update()
        self.objects.update()

    # Метод для создания объектов (платформ, кнопок и фонового изображения) на экране
    def draw(self, screen_arg):
        screen_arg.blit(bg, (0, 0))  # Задний фон игры

        # Загрузка всех платформ и кнопок из групп
        self.platform_list.draw(screen_arg)
        self.buttons_list.draw(screen_arg)
        self.portals.draw(screen_arg)
        if victory:
            self.objects.draw(screen_arg)


class Level_01(Level):  # Расстановка кнопок и платформ по местам

    def __init__(self, player):
        Level.__init__(self, player)

        # Данные для кнопок
        global buttons_level01
        global buttons
        global portals
        global portals_blocks

        portals_blocks = []
        buttons = []

        buttons_level01 = [
            [250, 380, 1],
            [550, 480, 2]
        ]

        # Данные для портала (финиша)
        portals = [
            [
                [735, 210,
                 [0, 1]
                 ]  # x, y, далее идут индексы кнопок, которые должны быть активны
            ]
        ]

        # Данные для платформ
        level01 = [
            [500, 500],
            [200, 400],
            [600, 300]
        ]

        # Перебираем список и добавляем каждую платформу в группу спрайтов - platform_list
        for platform in level01:
            block = Platform()
            block.rect.x = platform[0]
            block.rect.y = platform[1]
            block.player = self.player
            self.platform_list.add(block)

        # Перебираем список и добавляем каждую кнопку в группу спрайтов - buttons_list
        for button in buttons_level01:
            block = Button(button[2])
            block.rect.x = button[0]
            block.rect.y = button[1]
            block.player = self.player
            self.buttons_list.add(block)
            buttons.append(block)

        index = 0
        for portal in portals:
            block = Portal()
            block.rect.x = portal[index][0]
            block.rect.y = portal[index][1]
            block.player = self.player
            self.portals.add(block)
            portals_blocks.append(block)
            index += 1

        block = Victory()
        block.rect.x = 0
        block.rect.y = 0
        block.player = self.player
        self.objects.add(block)


def crash():  # Функция для вызова краша игры (для проверки)
    print('( Вызван принудительный краш игры! )')
    print(Level.buttons_level01[0])


def main(name_player1, name_player2):  # Основная функция игры
    print('\n[•] Приятной игры!\n')
    # Создание игроков
    player = Player('red', name_player1)
    player2 = Player('green', name_player2)

    # Создаем все уровни
    global level_list
    level_list = [Level_01(player)]

    # Устанавливаем текущий уровень
    current_level_no = 0
    current_level = level_list[current_level_no]

    active_sprite_list = pygame.sprite.Group()
    player.level = current_level

    player.rect.x = 340
    player.rect.y = SCREEN_HEIGHT - player.rect.height
    player2.level = current_level

    player2.rect.x = 340
    player2.rect.y = SCREEN_HEIGHT - player2.rect.height
    active_sprite_list.add(player)
    active_sprite_list.add(player2)

    done = False  # Чтобы игра работала, пока пользователь не нажмёт кнопку закрытия

    clock = pygame.time.Clock()  # Используется для управления скоростью обновления экрана

    # Основной цикл игры
    while not done:
        # Получение действий от пользователя
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # Если пользователь закрыл игру, то останавливаем цикл
                done = True

            # Действия по нажатию клавиш на клавиатуре
            if event.type == pygame.KEYDOWN:
                if not victory:
                    if event.key == pygame.K_LEFT:  # [1 игрок] Влево (стрелка влево)
                        player.go_left()
                    if event.key == pygame.K_RIGHT:  # [1 игрок] Вправо (стрелка вправо)
                        player.go_right()
                    if event.key == pygame.K_UP:  # [1 игрок] Вверх (стрелка вверх)
                        player.jump()

                    if event.key == pygame.K_a:  # [2 игрок] Влево (A)
                        player2.go_left()
                    if event.key == pygame.K_d:  # [2 игрок] Вправо (D)
                        player2.go_right()
                    if event.key == pygame.K_w:  # [2 игрок] Вверх (W)
                        player2.jump()

                    # [Оба игрока] Нажатие на кнопку (S или стрелки вниз):
                    if event.key == pygame.K_s or event.key == pygame.K_DOWN:
                        index = 0
                        for button in buttons_level01:
                            if player2.rect.x in range(button[0] - 30, button[0] + 30) \
                                    and player2.rect.y == button[1] - 40 and button[2] == 2 \
                                    and event.key == pygame.K_s:
                                click_sound.play()
                                buttons[index].set_tapped()
                            if player.rect.x in range(button[0] - 30, button[0] + 30) \
                                    and player.rect.y == button[1] - 40 and button[2] == 1 \
                                    and event.key == pygame.K_DOWN:
                                click_sound.play()
                                buttons[index].set_tapped()
                            index += 1

                        index = 0
                        active_buttons = 0
                        for portal in portals:
                            for but in portal[index][2]:
                                if buttons[int(but)].state:
                                    active_buttons += 1
                            if active_buttons == len(portal[index][2]):
                                if not portals_blocks[index].state:
                                    portal_on_sound.play()
                                    portals_blocks[index].set_active(1)
                            else:
                                if portals_blocks[index].state:
                                    portal_off_sound.play()
                                    portals_blocks[index].set_active(0)

                            portal_x = range(portal[index][0] - 30, portal[index][0] + 30)
                            portal_y = portal[index][1] + 30
                            if ((player.rect.x in portal_x and player.rect.y == portal_y)
                                    and (player2.rect.x in portal_x and player2.rect.y == portal_y)):
                                next_level_sound.play()
                                game_victory(screen)

                            index += 1

                if event.key == pygame.K_F5:  # Рестарт игры
                    player.restart()
                    player2.restart()

                if event.key == pygame.K_F3:
                    crash()

                if victory:
                    if event.key == pygame.K_RETURN:
                        done = True

            # Действия по отжатию клавиш на клавиатуре
            if event.type == pygame.KEYUP:
                # Остановить игрока 1 (при# движении влево) :
                if event.key == pygame.K_LEFT and player.change_x < 0:
                    player.stop()
                # Остановить игрока 1 (при движении вправо):
                if event.key == pygame.K_RIGHT and player.change_x > 0:
                    player.stop()
                # Остановить игрока 2 (при движении влево):
                if event.key == pygame.K_a and player2.change_x < 0:
                    player2.stop()
                # Остановить игрока 2 (при движении вправо):
                if event.key == pygame.K_d and player2.change_x > 0:
                    player2.stop()

        # Обновляем игрока
        active_sprite_list.update()

        # Обновляем объекты на экране
        current_level.update()

        # Если игрок приблизится к правой стороне, то дальше его не двигаем
        if player.rect.right > SCREEN_WIDTH:  # 1 игрок
            player.rect.right = SCREEN_WIDTH

        if player2.rect.right > SCREEN_WIDTH:  # 2 игрок
            player2.rect.right = SCREEN_WIDTH

        # Если игрок приблизится к левой стороне, то дальше его не двигаем
        if player.rect.left < 0:  # 1 игрок
            player.rect.left = 0

        if player2.rect.left < 0:  # 2 игрок
            player2.rect.left = 0

        # Создаём объекты на экране
        current_level.draw(screen)
        active_sprite_list.draw(screen)

        # Устанавливаем количество FPS (кадров в секунду)
        clock.tick(60)

        # Обновляем экран после рисования объектов
        pygame.display.flip()

    # Закрытие игры, если пользователь закрыл окно
    if not victory:
        save_info(table='games', column='result', value='Выход', where=True,
                  where_column='id')

    print('[•] Были рады Вас видеть!')

    pygame.quit()
