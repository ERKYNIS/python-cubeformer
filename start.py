import sqlite3  # Библиотека для управления базы данных SQL

import pip  # Встроенная библиотека для установки необходимых библиотек
import os  # Встроенная библиотека для управления файлами
import time  # Встроенная библиотека для управления задержки игры
import datetime  # Встроенная библиотека для управления временем и даты (получение текущей и т.д.)
import traceback  # Встроенная библиотека для получения ошибки выполнения кода
import configparser  # Встроенная библиотека для управления настройками (.ini и .cfg файлами)

import requests

config = configparser.ConfigParser()  # Конфиг
config.read('settings.ini')  # Прочитаем файл настроек

if 'Desktop' == os.getcwd().split('\\')[-1]:  # Проверка нахождения на рабочем столе.
    print('\n[!] Файл start.py находиться на рабочем столе!\n'
          'Советуем создать папку и переложить его туда, чтобы не засорять рабочий стол.\n\n'
          'Нажмите "Enter", если хотите продолжить.\n ')
    input()

print('\n[•] Проверка и запуск необходимых исполняющих файлов...')
# Проверка и загрузка игры, если не найдена.
if not os.path.exists('game.py'):
    print('\n[•] Загрузка файла игры...')
    with open('game.py', 'wb') as handler:
        handler.write(requests.get('https://www.dropbox.com/s/n4ww089la20sxvi/game.py?dl=1').content)
        print(f'[📥] Файл игры (game.py) загружен.')

# Проверка и загрузка сайта, если не найден.
if not os.path.exists('site.py'):
    print('\n[•] Загрузка сайта...')
    with open('site.py', 'wb') as handler:
        handler.write(requests.get('https://www.dropbox.com/s/jcmr77znn2ekln4/site.py?dl=1').content)
        print(f'[📥] Файл сайта (site.py) загружен.')

if not os.path.exists('files'):  # Создание папки files, если не найдена
    os.mkdir("files")

# Проверка и загрузка файла с функциями.
if not os.path.exists('files/cubeformer_functions.py'):
    print('\n[•] Загрузка файла с функциями...')
    with open('files/cubeformer_functions.py', 'wb') as handler:
        handler.write(requests.get('https://www.dropbox.com/s/1s3ifc8xymdnn1m/'
                                   'cubeformer_functions.py?dl=1').content)
        print(f'[📥] Файл с функциями (files/cubeformer_functions.py) загружен.')
        time.sleep(1)

# Проверка и запуск библиотек для игры, если не найдены - загрузка их:
print('\n[•] Проверяю и запускаю необходимые библиотеки...')

installed_libraries = []

try:
    import pygame  # Проверка запуска библиотеки
except ModuleNotFoundError:  # Если произошла ошибка "Модуль не найден":
    print('[📥] Устанавливаю библиотеку "pygame"...')
    pip.main(['install', 'pygame'])  # Установка библиотеки
    installed_libraries.append('pygame')  # Добавление библиотеки в установленные (для вывода)
    import pygame

# Все остальные сделаны так же, как и "pyttsx3"

try:
    import pywebio
except ModuleNotFoundError:
    print('[📥] Устанавливаю библиотеку "pywebio"...')
    pip.main(['install', 'pywebio'])
    installed_libraries.append('pywebio')
    import pywebio

try:
    import pymorphy2
except ModuleNotFoundError:
    print('[📥] Устанавливаю библиотеку "pymorphy2"...')
    pip.main(['install', 'pywebio'])
    installed_libraries.append('pymorphy2')
    import pymorphy2

try:
    import pymorphy2_dicts_ru
except ModuleNotFoundError:
    print('[📥] Устанавливаю русский язык для библиотеки "pymorphy2"...')
    pip.main(['install', 'pymorphy2-dicts-ru'])
    installed_libraries.append('русский язык для pymorphy2')
    import pymorphy2_dicts_ru

print(f'[•] Все библиотеки успешно прошли проверку!')
# Вывод установленных библиотек, если каких-то не было:
if len(installed_libraries) > 0:
    print(f'[📥] Установлены: {", ".join(installed_libraries)}.')


def report_to_admin(crash_time):  # Функция для отправки обращения
    pygame.mixer.init()  # Инициализация mixer`а
    pygame.mixer.Sound("files/error.wav").play()  # Воспроизведение звука ошибки
    print('[!] Произошла ошибка при запуске или во время игры.\n'
          'Пожалуйста, попробуйте переустановить её.\n\n'
          'Нажмите "Enter", чтобы оставить обращение.\n'
          'Введите "crash", чтобы посмотреть лог краша.')
    if input() == 'crash':
        with open(f'crashes/{crash_time}.log', 'r') as file:  # Открытие файла с крашем
            print(f'[crashes/{crash_time}.log]:\n{file.read()}')
            file.close()
            print('\nВведите "remove", чтобы удалить лог краша и закрыть программу.\n'
                  'Нажмите "Enter", чтобы закрыть программу без удаления лога краша.')
            if input() == "remove":
                os.remove(f'crashes/{crash_time}.log')  # Удаление файла с крашем
                # Удаление папки с крашами, если в ней больше нет файлов:
                if len(os.listdir("crashes")) < 1:
                    os.rmdir('crashes')
                print(f'[CrashLog] Лог краша crashes/{crash_time}.log удалён.')
    else:
        problem_text = ''
        username = input('[?] Введите своё имя: ')
        while not username:
            username = input('[?] Введите корректное имя: ')
        user_mail = input(f'[?] Приятно познакомиться, {username}! Введите свою почту для связи: ')
        while not user_mail or "@" not in user_mail or (user_mail[0] == "@" or user_mail[-1] == "@"):
            user_mail = input(f'[?] {username}, введите корректную почту: ')
        while not problem_text:
            problem_text = input(f'[?] {username}, пожалуйста, введите подробное описание проблемы '
                                 '(также, укажите в какой момент произошла ошибка): ')
        print('[?] Ваше обращение:\n'
              f'{username} ({user_mail}):\n'
              f'{problem_text}\n\n'
              f'Если всё верно, нажмите "Enter".')
        input()
        print('[?] Спасибо! Ваше обращение получено и мы ответим Вам в ближайшее время!')
        db.execute("INSERT INTO `reports` ('time', `name`, 'email', 'text') VALUES (?, ?, ?, ?)",
                   (datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S"),
                    username, user_mail, problem_text))  # Запрос на отправку запросов
        database.commit()  # Сохранение изменений
    input()
    print('\n[?] Нажмите "Enter", чтобы выйти из программы.')


def save_crash(text):  # Функция для сохранения 
    if not os.path.exists('crashes'):  # Создание папки, если её нет
        os.mkdir('crashes')
    crash_file_name = datetime.datetime.now().strftime("%d.%m.%Y_%H-%M")  # Название файла с крашем
    with open(f'crashes/{crash_file_name}.log', 'w') as file:
        print(f'[CrashLog] Лог краша сохранён - crashes/{crash_file_name}.log.')
        # Запись текста краша в файл:
        file.write(f'Краш {datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")}:\n\n{text}')
        file.close()  # Сохранение и закрытие файла с крашем
    from files.cubeformer_functions import save_info
    save_info(table='games', column='result', value='Краш', where=True,
              where_column='id')
    game.pygame.quit()  # Выход из игры
    time.sleep(2)  # Задержка 2 секунды
    report_to_admin(crash_file_name)  # Запуск функции для отправки обращения


def start_game(player_name1, player_name2):  # Функция запуска игры
    # Пробный запуск игры и выдача ошибки, если игра закрылась с ошибкой
    try:
        print(f'\nИгра | {datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")}\n'
              f'[Игрок №1 (красный)]: {player_name1}\n[Игрок №2 (зелёный)]: {player_name2}\n\n'
              f'[•] Запускаю игру...\n')
        if profile.nick != 'Гость':
            date_now = datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")
            db.execute("INSERT INTO `games` ('acc_nick', `player1_name`, 'player2_name', 'date') "
                       "VALUES (?, ?, ?, ?)", (profile.nick, player_name1, player_name2, date_now,))
            database.commit()
            db.execute('SELECT id FROM games WHERE date=?', (date_now,))
            save_settings('Game', 'last_game_id', str(db.fetchall()[0][0]))
        game.load()
        game.main(player_name1, player_name2)
    except Exception:
        save_crash(traceback.format_exc())


# Проверка файлов для игры, если не найдены - загрузка их:
file_url = [
    'https://i.imgur.com/ULiRd6e.png',  # фон
    'https://i.imgur.com/zJjN0ZH.png',  # 1 игрок
    'https://i.imgur.com/ce8W1v5.png',  # 2 игрок
    'https://i.imgur.com/pQ4fHOW.png',  # кнопка для 1 игрока
    'https://i.imgur.com/aWTpdgG.png',  # кнопка для 2 игрока
    'https://i.imgur.com/L7YdVKH.png',  # платформа
    'https://i.imgur.com/4HAwLrh.png',  # выключенный портал
    'https://i.imgur.com/aEgqDf4.png',  # включенный портал
    'https://i.imgur.com/TnL36tf.png',  # победа
    'https://www.dropbox.com/s/ioje3tw63pqykdf/click_sound.wav?dl=1',  # звук нажатия на клавишу
    'https://www.dropbox.com/s/mmbgl4j893jxs9p/error.wav?dl=1',  # звук ошибки
    'https://www.dropbox.com/s/fpipadnf99m62eg/jump.wav?dl=1',  # звук прыжка игрока
    'https://www.dropbox.com/s/36y37j76a1lvtky/portal_on.wav?dl=1',  # звук включения портала
    'https://www.dropbox.com/s/k9q03hahhs34d1d/portal_off.wav?dl=1',  # звук выключения портала
    'https://www.dropbox.com/s/ryiigybro1v60oe/next_level.wav?dl=1',
    # звук телепорта на следующий уровень
    'https://www.dropbox.com/s/fqciqbt6ee1znzy/victory.wav?dl=1',  # звук победы
    'https://www.dropbox.com/s/yyl9spos4lq81h1/cubeformer.db?dl=1',  # база данных (для сайта)
]
file_names = [
    'bg.png',  # фон
    'red_player.png',  # 1 игрок
    'green_player.png',  # 2 игрок
    'red_button.png',  # кнопка для 1 игрока
    'green_button.png',  # кнопка для 1 игрока
    'platform.png',  # платформа
    'portal_unactive.png',  # выключенный портал
    'portal.png',  # включенный портал
    'victory.png',  # победа
    'click_sound.wav',  # звук нажатия на клавишу
    'error.wav',  # звук ошибки
    'jump.wav',  # звук прыжка игрока
    'portal_on.wav',  # звук включения портала
    'portal_off.wav',  # звук выключения портала
    'next_level.wav',  # звук телепорта на следующий уровень
    'victory.wav',  # звук победы
    'cubeformer.db',  # база данных (для сайта)
]

print('\n[•] Проверяю файлы игры...')

for i in range(len(file_url)):
    # Проверка наличия файла и загрузка в случае, если его нет:
    if not os.path.exists(f'files/{file_names[i]}'):
        with open(f'files/{file_names[i]}', 'wb') as handler:
            handler.write(requests.get(file_url[i]).content)
            print(f'[📥] Загружен файл "files/{file_names[i]}".')

print('[•] Все файлы успешно прошли проверку!\n')

database = sqlite3.connect('files/cubeformer.db')  # Подключение базы данных
db = database.cursor()


def load_settings():  # Загрузка настроек (settings.ini)
    global profile

    # Если нет файла настроек - создание его и установка настроек по умолчанию:
    if not os.path.exists(f'files/settings.ini'):
        with open(f'files/settings.ini', 'w') as settings_file:
            config['User'] = {'nick': 'Гость',
                              'password': 'default'}
            config['Game'] = {'player1': 'default',
                              'player2': 'default',
                              'last_game_id': '0'}
            config.write(settings_file)

    config.read('files/settings.ini')  # Чтение файла настроек
    # Создание профиля с ником и паролем из файла с настройками:
    profile = Profile(config['User']['nick'], config['User']['password'])

    # Если файл с настройками есть, то проверка сохранён верный ник и пароль или нет
    if os.path.exists(f'files/settings.ini'):
        # Если пароль или ник неверны, возврат к настройкам профиля по умолчанию
        if not profile.check_login(auth_nick=config['User']['nick'],
                                   auth_pass=config['User']['password']) and \
                config['User']['nick'] != 'Гость':
            save_settings('User', 'password', 'default')
            profile = Profile(config['User']['nick'], config['User']['password'])
            print('[?] Сохранён неверный логин или пароль! Повторите попытку входа!\n')


def save_settings(section, column, value):  # Функция сохранения настроек
    with open(f'files/settings.ini', 'w') as settings_file:
        config.read('files/settings.ini')
        config.set(section, column, value)
        config.write(settings_file)


class Profile:  # Класс профиля
    def __init__(self, nick, password):
        self.nick = nick
        self.password = password

    # Функция для проверки верности пароля и ника (или почты):
    def check_login(self, auth_key=None, auth_nick=None, auth_pass=None, method=0):
        if not method:
            db.execute('SELECT password FROM accounts WHERE nickname=?', (auth_nick,))
            db_result = db.fetchall()
            if db_result:
                if auth_pass == db_result[0][0]:
                    self.nick = auth_nick
                    self.password = auth_pass
                    return True
            return False
        else:
            db.execute('SELECT nickname, password FROM accounts WHERE authkey=?', (auth_key,))
            db_result = db.fetchall()
            if db_result:
                profile.nick = db_result[0][0]
                profile.password = db_result[0][1]


profile = Profile('Гость', 'default')  # Создание профиля по умолчанию

print('[?] Запустите файл site.py вручную, чтобы запустить сайт.\n')

try:
    import game  # Подключение игры
except Exception:
    print('[!] Произошла ошибка при загрузке файла игры! Попробуйте переустановить его!')

load_settings()
if config['User']['nick'] == 'Гость':
    ans1 = input('[•] Вы хотите войти в свой аккаунт для сохранения статистики (да/нет)? ')
    if ans1.lower() == 'да' or ans1.lower() == 'lf':
        print('\n[?] Введите "cancel", если передумали входить в аккаунт.\n')
        print('[Site] Выберите способ:')
        print('1. Авторизация с помощь ключа доступа.')
        print('2. Авторизация с помощью логина и пароль.')
        ans2 = input('Введите номер способа (1/2): ')
        while ans2 != '1' and ans2 != '2' and ans2 != 'cancel':
            ans2 = input('Введите номер способа (1/2): ')
        if ans2 == '1':
            print('\n[?] Инструкция\n1. Зайдите на сайт и войдите в свой аккаунт или зарегистрируйте'
                  ' новый.\n2. В разделе "Безопасность", напротив "Ключ доступа" нажмите кнопку '
                  '"Получить".\n3. Введите в поле ниже данный ключ.\n'
                  '\n[?] Введите "cancel", если передумали входить в аккаунт.\n')
            db_result = None
            test_key = None
            while not db_result and test_key != 'cancel':
                test_key = input('[Site] Введите ключ доступ, полученный на сайте: ')
                if test_key == 'cancel':
                    print('\n[Site] Вход отменён!')
                else:
                    db.execute('SELECT nickname, password FROM accounts WHERE authkey=?',
                               (test_key,))
                    db_result = db.fetchall()
                    if db_result:
                        profile.nick = db_result[0][0]
                        profile.password = db_result[0][1]
                        db.execute("INSERT INTO `login_history` ('time', `nickname`, 'method') "
                                   "VALUES (?, ?, ?)", (datetime.datetime.now().
                                                        strftime("%d.%m.%Y %H:%M:%S"),
                                                        profile.nick, 'ключа доступа (в игру)'))
                        db.execute("UPDATE `accounts` SET authkey=NULL WHERE nickname=?",
                                   (profile.nick,))
                        database.commit()
                        save_settings('User', 'nick', profile.nick)
                        save_settings('User', 'password', profile.password)
        elif ans2 == '2':
            print('\n[?] Инструкция\n1. Если у Вас ещё нет аккаунта, зайдите на сайт '
                  'и зарегистрируйтесь. '
                  '\n2. Введите в поле ниже сначала логин своего аккаунта, затем пароль.\n'
                  '\n[?] Введите "cancel", если передумали входить в аккаунт.\n')
            test_name = input('[Site] Введите логин (никнейм): ')
            if test_name == 'cancel':
                print('[Site] Вход отменён!')
            else:
                test_password = input('[Site] Введите пароль: ')
                while not profile.check_login(auth_nick=test_name, auth_pass=test_password):
                    print('\n[Site] Неверный логин или пароль!')
                    test_name = input('[Site] Введите логин (никнейм): ')
                    if test_name == 'cancel':
                        print('\n[Site] Вход отменён!')
                    else:
                        test_password = input('[Site] Введите пароль: ')
                    if test_name != 'cancel':
                        db.execute("INSERT INTO `login_history` ('time', `nickname`, 'method') "
                                   "VALUES (?, ?, ?)", (datetime.datetime.now().
                                                        strftime("%d.%m.%Y %H:%M:%S"), test_name,
                                                        'никнейма (в игру)'))
                        database.commit()
                        save_settings('User', 'nick', profile.nick)
                        save_settings('User', 'password', profile.password)
    print()
print(f'[Site] Добро пожаловать, {profile.nick}!\n')

flag1 = False
flag2 = False
# Если в настройках указан ник не по умолчанию, предложение изменить никнеймы или оставить текущие:
if config['Game']['player1'] != 'default' and config['Game']['player2'] != 'default':
    print(f'\n[?] Сохранённые никнеймы:\n[Игрок №1 (красный)] {config["Game"]["player1"]}\n[Игрок '
          f'№2 (зелёный)] {config["Game"]["player2"]}\n')
    player1 = config['Game']['player1']
    player2 = config['Game']['player2']

# Установка никнеймов если в настройках они стоят по умолчанию или если игроки хотят изменить их:
if config['Game']['player1'] == 'default' and config['Game']['player2'] == 'default' \
        or input('[?] Желаете изменить никнеймы (да/нет)? ').lower() in ['да', 'lf']:
    if profile.nick != 'Гость':
        print('[?] Выберите нужный вариант:\n1. Введите "1" в поле ниже, '
              'если хотите использовать никнейм привязанного аккаунта.\n2. '
              'Введите желаемый никнейм в поле ниже.\n')
    while not flag1:
        player1 = input('Игрок №1, введите никнейм: ')
        if not player1:
            player1 = config['Game']['player1']
            flag1 = True
        else:
            if player1 == '1':
                if profile.nick != 'Гость':
                    player1 = profile.nick
                    flag1 = True
                else:
                    print('\n[!] Вы не привязали аккаунт!\n')
            else:
                if len(player1) < 5 or len(player1) > 35:
                    print('\n[Игрок №1] Длина никнейма должна быть больше 5 и меньше 35.\n')
                else:
                    flag1 = True
            if flag1:
                print(f'\n[Игрок №1] Приятной познакомиться, {player1}!\n')
    while not flag2:
        player2 = input('Игрок №2, введите никнейм: ')
        if not player2:
            player2 = config['Game']['player2']
            flag2 = True
        else:
            if player2 == '1':
                if player1 == profile.nick:
                    print('\n[Игрок №2] Игрок №1 уже взял себе никнейм привязанного аккаунта!\n')
                else:
                    if config['User']['nick'] != 'Гость':
                        player2 = profile.nick
                        flag2 = True
                    else:
                        print('\n[!] Вы не привязали аккаунт!\n')
            else:
                if len(player2) < 5 or len(player2) > 35:
                    print('\n[Игрок №2] Длина никнейма должна быть больше 5 и меньше 35.\n')
                else:
                    flag2 = True
            if flag2:
                print(f'\n[Игрок №2] Приятной познакомиться, {player2}!\n')
    if input('Хотите сохранить свои никнеймы (да/нет)? ').lower() in ['да', 'lf']:
        print('[?] Ваши никнеймы сохранены!')
        save_settings('Game', 'player1', player1)  # Сохранение ника игрока №1
        save_settings('Game', 'player2', player2)  # Сохранение ника игрока №2
start_game(player1, player2)  # Запуск игры
