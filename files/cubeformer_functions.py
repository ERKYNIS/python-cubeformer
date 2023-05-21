import sqlite3
import configparser

database = sqlite3.connect('files/cubeformer.db')  # Подключение базы данных
db = database.cursor()


def save_info(column=None, value=None, table=None, where=False, where_column=None,
              where_value='game_id'):
    config = configparser.ConfigParser()  # Конфиг
    config.read('files/settings.ini')  # Прочитаем файл настроек
    if where_value == 'game_id':
        where_value = config['Game']['last_game_id']
    if where:
        db.execute(f"UPDATE `{table}` SET {column}=? WHERE {where_column}=?",
                   (value, where_value,))
    else:
        db.execute(f"UPDATE `{table}` SET {column}=?", (value,))
    database.commit()