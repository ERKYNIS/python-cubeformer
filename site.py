"""
Пояснения функций библиотеки pywebio:

    with use_scope('название области') - создать область.
    set_scope('название области', position=позиция) - вывести область.
    clear('название области') - очистить область.
    remove('название области') - удалить область.


    input_group - группа полей для ввода:
        validate - проверки.
        cancelable (True/False) - возможность отмены.

    input - поле для ввода:
        name - имя поля (для проверки и вывода ошибки).
        type - тип поля (например "Text" - текст).
        required (True/False) - обязательное поле или нет.

    radio - поле для выбора:
        options - варианты для выбора.

    toast - уведомление.

    put_text - вывести на экран текст.
    put_markdown - вывести на экран заголовок.
    put_loading - вывести на экран загрузку.

    .style() - установка стиля для текста или заголовка (например, установка цвета).

    put_buttons - вывести на экран кнопки:
        label - текст на кнопке.
        value - похожее на "name" в поле ввода.
        color - цвет кнопки.
        onclick - действие после нажатия.

    with popup('название окна') - создать окно (открывается сверху экрана).
    close_popup() - закрыть окно.


    run_async(фукнция) - запустить фукнцию, чтобы сайт ждал её выполнения (например,
    ввода пользователя).
"""
import datetime
import os
import sqlite3
import time
from random import sample

from pymorphy2 import MorphAnalyzer

morph = MorphAnalyzer()

import pywebio
from pywebio import start_server
from pywebio.input import *
from pywebio.output import *
from pywebio.session import run_async

# Установка названия сайта для вкладки браузера и установка тёмной темы.
pywebio.config(title="Cubeформер", theme='dark')

database = sqlite3.connect('files/cubeformer.db')  # Загрузка базы данных
db = database.cursor()


class Profile:  # Класс профиля
    def __init__(self):
        self.id = None
        self.name = None
        self.surname = None
        self.email = None
        self.gender = None
        self.role = None
        self.nick = None
        self.password = None
        self.auth_key = None

    async def register(self):  # Функция регистрации
        clear('login')
        clear('register')
        clear('main')
        set_scope('register', position=-1)
        with use_scope('register'):
            await input_group("➕ Регистрация", [
                input('Ваш никнейм:', type=TEXT, name="nickname", validate=check_nickname,
                      required=True),
                input('Ваше имя:', type=TEXT, name="name", required=True),
                input('Ваша фамилия:', type=TEXT, name="surname", required=True),
                radio("Ваш пол:", options=['Мужской', 'Женский'], name="gender", required=True),
                input('Ваша почта:', type=TEXT, name="email", validate=check_email),
                input('Пароль:', type=PASSWORD, name="password", required=True),
                input('Повторите пароль:', type=PASSWORD, name="test_password", required=True),
            ], validate=lambda regdata: self.check_reg_passwords(regdata['password'],
                                                                 regdata['test_password'],
                                                                 regdata['nickname'],
                                                                 regdata['name'],
                                                                 regdata['surname'],
                                                                 regdata['gender'],
                                                                 regdata['email'],
                                                                 regdata['password']))

    # Проверка совпадения паролей на этапе регистрации
    def check_reg_passwords(self, one, two, nickname, name, surname, gender, email, password):
        if one != two:
            return 'test_password', 'Пароли не совпадают!'
        else:
            run_async(self.register_success(nickname, name, surname, gender, email, password))

    # Успешная регистрация:
    async def register_success(self, nickname, name, surname, gender, email, password):
        clear('register_success')
        set_scope('register_success', position=-1)
        db.execute("INSERT INTO `accounts` (`nickname`, `name`, `surname`, `gender`, `email`, "
                   "`password`, `role`) VALUES (?, ?, ?, ?, ?, ?, 'default')",
                   (nickname, name, surname, gender, email, password))
        database.commit()
        with use_scope('register_success'):
            toast(f'Вы успешно зарегистрировались!', color='success')
            print(f'[SiteLog {datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")}] '
                  f'Произведена регистрация аккаунта {nickname}.')
            put_markdown('## Успешная регистрация!').style('color:green')
            put_markdown('Поздравляем! Вы успешно зарегистрировались!').style('bold:true')
            put_text(' ')
            put_text('Теперь войдите в аккаунт:')
        run_async(self.login())

    async def login(self):  # Авторизация
        remove('login')
        await input_group("👤 Авторизация", [
            input('Логин (email или никнейм):', type=TEXT, name='test_email', required=True),
            input('Пароль:', type=PASSWORD, name='test_password', required=True),
        ], validate=lambda m2: self.check_login(m2['test_email'], m2['test_password']))

    # Проверка логина и пароля на этапе авторизации:
    def check_login(self, test_email_or_nick, test_password):
        db.execute('SELECT nickname FROM accounts WHERE email=?', (test_email_or_nick,))
        if not db.fetchone():
            db.execute('SELECT nickname FROM accounts WHERE nickname=?', (test_email_or_nick,))
            if not db.fetchone():
                return 'test_email', "⚠ Неверный логин!"
            else:
                db.execute('SELECT password FROM accounts WHERE nickname=?', (test_email_or_nick,))
                if test_password != db.fetchall()[0][0]:
                    return 'test_password', "⚠ Неверный пароль!"
                else:
                    toast(f'Добро пожаловать, {test_email_or_nick}! 👋', color='success')
                    run_async(self.get_information(test_email_or_nick, 'никнейма'))
        else:
            db.execute('SELECT password FROM accounts WHERE email=?', (test_email_or_nick,))
            if test_password != db.fetchall()[0][0]:
                return 'test_password', "⚠ Неверный пароль!"
            else:
                db.execute('SELECT nickname FROM accounts WHERE email=?', (test_email_or_nick,))
                username = db.fetchall()[0][0]
                toast(f'Добро пожаловать, {username}! 👋', color='success')
                run_async(self.get_information(username, 'почты'))

    async def get_information(self, nick, method=None):  # Функция получения информации об аккаунте
        clear('main')
        clear('login')
        clear('register')
        clear('register_success')
        clear('login_success')
        clear('login_history')
        with use_scope('login_success'):
            put_markdown('## Успешная авторизация! 🎉').style('color:green')
            put_markdown('Вы успешно авторизовались! ✅').style('bold:true')
            put_text('Загрузка вашего аккаунта...')
            put_loading(color="success")
        self.nick = nick
        db.execute('SELECT * FROM accounts WHERE nickname=?', (self.nick,))
        data = db.fetchall()[0]
        self.id = data[0]
        self.name = data[2]
        self.surname = data[3]
        self.email = data[4]
        self.password = data[6]
        self.role = data[7]
        if data[5] == 'Мужской':
            self.gender = 'Мужской 👨'
        else:
            self.gender = 'Женский 👩'
        print(f'[SiteLog | {datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")}] '
              f'Произведена авторизация в аккаунт {nick} с помощью {method}.')
        db.execute("INSERT INTO `login_history` ('time', `nickname`, 'method') "
                   "VALUES (?, ?, ?)", (datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S"),
                                        nick, method))
        database.commit()
        time.sleep(3)
        clear('login_success')
        run_async(self.account_info())

    async def quit(self, notification=1):  # Функция выхода из аккаунта
        remove('info')
        remove('button_panel')
        remove('login_history')
        remove('user_reports')
        remove('crashes_list')
        self.id = None
        self.name = None
        self.surname = None
        self.email = None
        self.gender = None
        self.role = None
        self.password = None
        if notification:
            toast('Вы вышли из своего аккаунта! ✅', color='error')
            print(f'[SiteLog | {datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")}] '
                  f'Произведён выход из аккаунта {self.nick}.')
        self.nick = None
        run_async(main())

    def button_panel(self, page=0):  # Функция панели с кнопками (сверху)
        remove('info')
        remove('games')
        remove('login_history')
        remove('user_reports')
        remove('crashes_list')
        remove('change_pass')
        remove('button_panel')
        with use_scope('button_panel'):
            lc = 'info'
            login_history_but = 'info'
            user_reports_but = 'info'
            crashes_list_but = 'info'
            games_list = 'info'

            if not page:
                lc = 'success'
            if page == 1:
                login_history_but = 'success'
            if page == 2:
                user_reports_but = 'success'
            if page == 3:
                crashes_list_but = 'success'
            if page == 4:
                games_list = 'success'

            if self.role == 'admin':
                put_buttons([dict(label='👤 Личный кабинет', value='lc', color=lc),
                             dict(label='🔓 История входов', value='login_history',
                                  color=login_history_but),
                             dict(label='🎮 История игр', value='games', color=games_list),
                             dict(label='⚠ Список крашей', value='crashes_list',
                                  color=crashes_list_but),
                             dict(label='🛎 Обращения пользователей', value='user_reports',
                                  color=user_reports_but),
                             dict(label='❌ Выйти из аккаунта', value='quit',
                                  color='danger')],
                            onclick=[lambda: run_async(self.account_info()),
                                     lambda: run_async(self.login_history()),
                                     lambda: run_async(self.games()),
                                     lambda: run_async(self.crashes_list()),
                                     lambda: run_async(self.user_reports()),
                                     lambda: run_async(self.quit())], position=0)
            else:
                put_buttons([dict(label='👤 Личный кабинет', value='lc', color=lc),
                             dict(label='🔓 История входов', value='login_history',
                                  color=login_history_but),
                             dict(label='🎮 История игр', value='games', color=games_list),
                             dict(label='⚠ Список крашей', value='crashes_list',
                                  color=crashes_list_but),
                             dict(label='❌ Выйти из аккаунта', value='quit',
                                  color='danger')],
                            onclick=[lambda: run_async(self.account_info()),
                                     lambda: run_async(self.login_history()),
                                     lambda: run_async(self.games()),
                                     lambda: run_async(self.crashes_list()),
                                     lambda: run_async(self.quit())], position=0)

    async def account_info(self):  # Функция страницы личного кабинета
        self.button_panel()
        with use_scope('info'):
            put_markdown(f'## 👤 Личный кабинет | {self.nick} ({self.name} {self.surname}).')
            if self.role == 'default':
                user_role = put_text('Пользователь 😎').style('color:green')
            elif self.role == 'admin':
                user_role = put_text('Администратор 👮‍♂').style('color:#B22222')
            put_text('')
            put_table([
                ['🆔:', f'№{self.id}'],
                ['🎫 Никнейм:', self.nick],
                ['👔 Должность:', user_role],
                ['📋 Имя:', self.name],
                ['📋 Фамилия:', self.surname],
                ['🚻 Пол:', self.gender]
            ], header=['📘 Информация об аккаунте:'])
            put_table([
                ['✉ Почта:', self.email],
                ['🔐 Пароль:', put_buttons(
                    [dict(label='🔏 Изменить', value='edit', color='warning'), ],
                    onclick=[lambda: run_async(self.change_pass())])],
                ['🔑 Ключ доступа:', put_buttons(
                    [dict(label='🙏 Получить', value='get', color='success'), ],
                    onclick=[lambda: run_async(self.get_auth_key())])]
            ],
                header=['📙 Безопасность:'])
            put_buttons([
                dict(label='❌ Выйти из аккаунта', value='quit', color='danger'),
            ], onclick=[lambda: run_async(self.quit())])
            await pywebio.session.hold()
        put_text('')

    async def get_auth_key(self, ans=0):  # Функция получения ключа доступа
        if not ans:
            close_popup()
            with popup('🔑 Ключ доступа'):
                put_text('Ваш ключ доступа:')
                put_loading(color="info")
                await getting_auth_key()
        if ans:
            time.sleep(1)
            close_popup()
            with popup('🔑 Ключ доступа'):
                put_text('Ваш ключ доступа:')
                put_markdown(f'## {self.auth_key}').style('color:orange')
                put_text('Данный ключ действует 1 минуту.').style('color:red')
            for i in range(60):
                db.execute('SELECT authkey FROM accounts WHERE nickname=? AND authkey=?',
                           (self.nick, self.auth_key))
                if not db.fetchall():
                    break
                time.sleep(1)
            print(1)
            db.execute("UPDATE `accounts` SET authkey=NULL WHERE nickname=?", (self.nick,))
            database.commit()
            close_popup()
            with popup('🔑 Ключ доступа'):
                put_text('Ваш ключ доступа истёк или использован!').style('color:red')
                put_button('🙏 Получить новый', color='warning',
                           onclick=lambda: self.get_auth_key(ans=0))

    async def change_pass(self):  # Функция изменения пароля
        with use_scope('change_pass'):
            await input_group("🔏 Изменение пароля", [
                input('Старый пароль:', type=TEXT, name="old_pass",
                      required=True),
                input('Новый пароль:', type=TEXT, name="pass", required=True),
                input('Повтор нового пароля', type=TEXT, name="pass2", required=True),
            ], validate=lambda dt: self.pass_validate(dt['old_pass'], dt['pass'], dt['pass2']),
                              cancelable=True)

    # Проверка правильности пароля на этапе смены пароля:
    def pass_validate(self, old_pass, new_pass, new_pass2):
        if self.password != old_pass:
            return 'old_pass', "Неверный пароль!"
        elif new_pass != new_pass2:
            return 'pass2', "Пароли не совпадают!"
        else:
            db.execute("UPDATE `accounts` SET password=? WHERE nickname=?", (new_pass, self.nick,))
            database.commit()
            self.password = new_pass
            toast('Вы успешно изменили пароль!', color='success')
            remove('change_pass')
            toast('Войдите в аккаунт заново, используя новый пароль.', color='orange')
            run_async(self.quit(0))
            print(f'[SiteLog | {datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")}] '
                  f'Произведено изменение пароля аккаунта {self.nick}.')

    async def login_history(self):  # Функция страницы с историей входов
        self.button_panel(1)
        with use_scope('login_history'):
            db.execute('SELECT * FROM login_history WHERE nickname=? ORDER by time DESC',
                       (self.nick,))
            data = db.fetchall()
            for i in range(len(data)):
                if i == 0:
                    put_table([
                        ['С помощью', f'{data[i][2]}'],
                    ], header=[f'{data[i][0]} (текущий)'])
                else:
                    put_table([
                        ['С помощью', f'{data[i][2]}'],
                    ], header=[data[i][0]])
        await pywebio.session.hold()

    async def games(self):  # Функция страницы с обращениями пользователей
        self.button_panel(4)
        with use_scope('games'):
            db.execute('SELECT * FROM games WHERE acc_nick=? ORDER by id', (self.nick,))
            data = db.fetchall()
            put_text()
            put_text(f'🎮 Всего {len(data)} '
                     f'{morph.parse("игра")[0].make_agree_with_number(len(data))[0]}:')
            if len(data) < 1:
                put_text('')
                put_text(f'Игр не найдено! ❌').style('color:red')
            else:
                for i in range(len(data)):
                    put_text()
                    if data[i][6] == 'Краш':
                        result = put_text("КРАШ ⚠").style("color:red")
                    elif data[i][6] == 'Выход':
                        result = put_text("ВЫХОД ❌").style("color:red")
                    elif data[i][6] == 'В процессе':
                        result = put_text("В процессе 🕹").style("color:green")
                    elif data[i][6] == 'Победа':
                        result = put_text("Победа 🥇").style("color:yellow")
                    put_table([
                        ['🆔 в системе:', f'№{data[i][0]}'],
                        ['⌚ Дата/время:', f'{data[i][7]}'],
                        [put_text('👤 Игрок №1:').style("color:red"), f'{data[i][2]}'],
                        [put_text('👤 Игрок №2:').style("color:green"), f'{data[i][3]}'],
                        ['🏆 Результат:', result]
                    ], header=[f'№{i + 1}'])
        await pywebio.session.hold()

    async def user_reports(self):  # Функция страницы с обращениями пользователей
        self.button_panel(2)
        with use_scope('user_reports'):
            db.execute('SELECT * FROM reports ORDER by id')
            data = db.fetchall()
            put_text(f'🛎 Всего {len(data)} '
                     f'{morph.parse("обращение")[0].make_agree_with_number(len(data))[0]}:')
            if len(data) < 1:
                put_text('')
                put_text(f'Обращений не найдено! ❌').style('color:success')
            else:
                for i in range(len(data)):
                    put_table([
                        ['⌚ Дата/время:', f'{data[i][1]}'],
                        ['👤 Пользователь:', f'{data[i][2]}'],
                        ['✉ Почта:', put_link(data[i][3], f"mailto:{data[i][3]}", new_window=True)],
                        ['📖 Обращение:', f'{data[i][4]}']
                    ], header=[f'№{data[i][0]}'])
                    put_buttons([
                        dict(label="Удалить", value='del', color='danger')
                    ], onclick=[lambda x=data[i][0]: run_async(self.del_report(data[i][0]))])
        await pywebio.session.hold()

    async def del_report(self, repid, ans=0):  # Функция удаления обращения
        if not ans:
            with popup('❌ Удаление обращения'):
                put_markdown('## ⚠ Внимание! Это действие нельзя будет отменить!').style('color:red')
                put_text(f'Вы точно хотите удалить обращение №{repid}?').style('color:yellow')
                put_buttons([
                    dict(label='Да', value='yes', color='danger'),
                    dict(label='Нет', value='no', color='success')
                ], onclick=[lambda: run_async(self.del_report(repid, ans=1)),
                            lambda: close_popup()])
        if ans:
            db.execute("DELETE FROM reports WHERE id=?", (repid,))
            database.commit()
            close_popup()
            toast(f'Вы успешно удалили обращение №{repid}! ✅', color='warning')
            run_async(self.user_reports())

    async def crashes_list(self):  # Функция страницы с логами крашей
        remove('check_crash')
        self.button_panel(3)
        with use_scope('crashes_list'):
            put_text('')
            if not os.path.exists('crashes'):
                put_text(f'⚠ Всего 0 логов крашей:')
                put_text(f'Логов крашей не найдено! ❌').style('color:success')
            else:
                put_text(f'⚠ Всего {len(os.listdir("crashes"))} '
                         f'{morph.parse("лог")[0].make_agree_with_number(len(os.listdir("crashes")))[0]}'
                         f' крашей:')
                file_num = 0
                if len(os.listdir("crashes")) < 0:
                    put_text(f'Логов крашей не найдено! ❌').style('color:success')
                else:
                    for file in os.listdir("crashes"):
                        content = open(f'./crashes/{file}', 'rb').read()
                        put_table([
                            [put_file(f'{file}', content), put_buttons([
                                dict(label="Посмотреть 📃", value='view', color='info')
                            ], onclick=[lambda x=file: run_async(self.check_crash(x))])]
                        ], header=[f'№{file_num + 1}'])
                        file_num += 1
        await pywebio.session.hold()

    async def check_crash(self, name, act=0):  # Функция просмотра лога краша
        remove('crashes_list')
        remove('button_panel')
        if not act:
            with use_scope('check_crash'):
                put_buttons([
                    dict(label='↩ Назад', value='back', color='warning'),
                ], onclick=[lambda: run_async(self.crashes_list())])
                with open(f'crashes/{name}', 'r') as crash_file:
                    put_text(f'crashes/{name}:')
                    put_code(crash_file.read())
                put_buttons([
                    dict(label='Удалить ❌', value='del', color='danger'),
                ], onclick=[lambda: run_async(self.check_crash(name, 1))])
        if act == 1:
            with popup('❌ Удаление лога краша'):
                put_markdown('## ⚠ Внимание! Это действие нельзя будет отменить!').style('color:red')
                put_text(f'Вы точно хотите удалить лог краша crashes/{name}?').style('color:yellow')
                put_buttons([
                    dict(label='Да', value='yes', color='danger'),
                    dict(label='Нет', value='no', color='success')
                ], onclick=[lambda: run_async(self.check_crash(name, 2)),
                            lambda: close_popup()])
        if act == 2:
            os.remove(f'crashes/{name}')
            if len(os.listdir("crashes")) < 1:
                os.rmdir('crashes')
            toast(f'Лог краша crashes/{name} удалён! ✅', color='orange')
            close_popup()
            run_async(self.crashes_list())
        await pywebio.session.hold()


profile = Profile()


async def main():  # Функция главной страницы
    close_popup()
    clear('login')
    image_url = "https://i.imgur.com/zJjN0ZH.png"
    pywebio.session.run_js("""
        $('#favicon32,#favicon16').remove(); 
        $('head').append('<link rel="icon" type="image/png" href="%s">')
        """ % image_url)
    clear('main')
    set_scope('main', position=0)
    with use_scope('main'):
        put_markdown('## Cubeформер | Главная страница.')
        put_text('Выберите действие:')
        put_buttons(['➕ Регистрация', '👤 Авторизация'],
                    onclick=[lambda: run_async(profile.register()),
                             lambda: run_async(profile.login())])
    put_text('')
    await pywebio.session.hold()


def check_nickname(nickname):  # Функция проверки никнейма
    if ' ' in nickname or '-' in nickname or '!' in nickname or \
            '"' in nickname or "'" in nickname or '%' in nickname or ';' in nickname or \
            ':' in nickname or '*' in nickname or '&' in nickname or '{' in nickname or \
            '}' in nickname or '[' in nickname or ']' in nickname or ',' in nickname or \
            '/' in nickname or '<' in nickname or '>' in nickname or '|' in nickname or \
            '/' in nickname or '\n' in nickname or '+' in nickname or '=' in nickname or \
            '"' in nickname:
        return '⚠ Ник может состоять только из цифр, ' \
               'букв и некоторых символов, таких как _ @ $ ( ) .'
    if len(nickname) > 30:
        return '⚠ Ник может состоять максимум из 30 символов!'
    if len(nickname) < 4:
        return '⚠ Ник должен состоять минимум из 4 символов!'
    db.execute("SELECT nickname FROM accounts WHERE nickname=?", (nickname,))
    result = db.fetchone()
    if result:
        return '⚠ Данный никнейм уже используется!'


def check_gender(gender):  # Функция проверки пола
    if not gender:
        return '⚠ Вы не выбрали ни одного варианта!'


def check_email(email):  # Функция проверки почты
    if email and "@" not in email:
        return '⚠ Неверный формат почты (Используйте: почта@pocha.ru | vasya@gmail.com)!'
    else:
        db.execute("SELECT email FROM accounts WHERE email=?", (email,))
        result = db.fetchone()
        if result:
            return '⚠ Данная почта уже используется!'


async def getting_auth_key():  # Функция получения ключа доступа (проверка на уникальность)
    chars = 'abcdefghijklnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    checked_authkey = ''.join(sample(chars, 15))
    db.execute('SELECT authkey FROM accounts WHERE authkey=?', (checked_authkey,))
    while db.fetchall():
        checked_authkey = ''.join(sample(chars, 15))
        db.execute('SELECT authkey FROM accounts WHERE authkey=?', (checked_authkey,))

    small_letter = 0
    big_letter = 0
    num = 0
    while small_letter < 5 or big_letter < 5 or num < 5:
        small_letter = 0
        big_letter = 0
        num = 0
        checked_authkey = ''.join(sample(chars, 15))
        for symbol in checked_authkey:
            if symbol in 'abcdefghijklnopqrstuvwxyz':
                small_letter += 1
            elif symbol in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
                big_letter += 1
            elif symbol in '0123456789':
                num += 1

    db.execute("UPDATE `accounts` SET authkey=? WHERE nickname=?", (checked_authkey, profile.nick,))
    database.commit()
    profile.auth_key = checked_authkey
    run_async(profile.get_auth_key(ans=1))


if __name__ == "__main__":  # Запуск сайта
    try:
        print(f'\n[SiteLog | {datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")}] '
              f'Сайт успешно запущен. '
              f'Используйте http://localhost:8080/, чтобы зайти.\n')
        start_server(main, port=8080, websocket_ping_interval=30, session_expire_seconds=999999,
                     session_cleanup_interval=999999)
        """
        start_server - запустить сайт:
            main - функция, которая запускается по умолчанию.
            port - порт, на котором запускать сайт
            websocket_ping_interval - 'пингует' каждые n секунд все веб сокеты 
            (помогает сохранить соединение через определённые прокси-серверы, 
            которые закрывают незанятые соединения).
            session_expire_seconds - время до остановки сессии пользователя (при длительном 
            отсутствии).
            session_cleanup_interval - время до очистки сеанса пользователя.
        """
    except Exception:
        print()
        print(f'[SiteLog | {datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")}] '
              f'Произошла ошибка при запуске или во время работы сайта.')
        print()
