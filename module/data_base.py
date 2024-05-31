from aiogram.types import Message

import sqlite3
from config_data.config import Config, load_config
import logging


config: Config = load_config()
db = sqlite3.connect('database.db', check_same_thread=False, isolation_level='EXCLUSIVE')


# СОЗДАНИЕ ТАБЛИЦ - users
def create_table_users() -> None:
    """
    Создание таблицы верифицированных пользователей
    :return: None
    """
    logging.info("table_users")
    with db:
        sql = db.cursor()
        sql.execute("""CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY,
            telegram_id INTEGER,
            username TEXT,
            is_admin INTEGER,
            list_category TEXT,
            rating INTEGER
        )""")
        db.commit()


# MAIN - добавление супер-админа в таблицу users
def add_admin(id_admin: int, user_name: str) -> None:
    """
    Добавление супер-админа в таблицу пользователей
    :param id_admin: id_telegram супер-админа
    :param user_name: имя супер-админа в телеграм
    :return:
    """
    logging.info(f'add_super_admin')
    with db:
        sql = db.cursor()
        sql.execute('SELECT telegram_id FROM users')
        list_user = [row[0] for row in sql.fetchall()]

        if int(id_admin) not in list_user:
            sql.execute(f'INSERT INTO users (telegram_id, username, is_admin, list_category, rating) '
                        f'VALUES ({id_admin}, "{user_name}", 1, "0", 0)')
            db.commit()


# MAIN - добавление супер-админа в таблицу users
def add_user(id_user: int, user_name: str) -> None:
    """
    Добавление супер-админа в таблицу пользователей
    :param id_user: id_telegram пользователя
    :param user_name: имя пользователя в телеграм
    :return:
    """
    logging.info(f'add_super_admin')
    with db:
        sql = db.cursor()
        sql.execute('SELECT telegram_id FROM users')
        list_user = [row[0] for row in sql.fetchall()]

        if int(id_user) not in list_user:
            sql.execute(f'INSERT INTO users (telegram_id, username, is_admin, list_category, rating) '
                        f'VALUES ({id_user}, "{user_name}", 0, "0", 0)')
            db.commit()


# ПАРТНЕР - Получить список пользователей не являющихся администратором
def get_list_notadmins() -> list:
    """
    Получить список верифицированных пользователей не являющихся администратором
    :return:
    """
    logging.info(f'get_list_notadmins')
    with db:
        sql = db.cursor()
        sql.execute('SELECT telegram_id, username FROM users WHERE is_admin = ?', (0,))
        list_notadmins = [row for row in sql.fetchall()]
        return list_notadmins


# АДМИНИСТРАТОРЫ - Назначить пользователя администратором
def set_admins(telegram_id: int):
    """
    Назначение пользователя с id_telegram администратором
    :param telegram_id:
    :return:
    """
    logging.info(f'set_admins')
    with db:
        sql = db.cursor()
        sql.execute('UPDATE users SET is_admin = ? WHERE telegram_id = ?', (1, telegram_id))
        db.commit()


# АДМИНИСТРАТОРЫ - Разжаловать пользователя из администраторов
def set_notadmins(telegram_id):
    """
    Разжаловать пользователя с id_telegram из администраторов
    :param telegram_id:
    :return:
    """
    logging.info(f'set_notadmins')
    with db:
        sql = db.cursor()
        sql.execute('UPDATE users SET is_admin = ? WHERE telegram_id = ?', (0, telegram_id))
        db.commit()


# ПАРТНЕР - Получить список пользователей не являющихся администратором
def get_list_notadmins_mailer() -> list:
    """
    Получить список верифицированных пользователей не являющихся администратором
    :return:
    """
    logging.info(f'get_list_notadmins')
    with db:
        sql = db.cursor()
        sql.execute('SELECT * FROM users WHERE is_admin = ?', (0,))
        list_notadmins = [row for row in sql.fetchall()]
        return list_notadmins


# ПАРТНЕР - получение списка администраторов
def get_list_admins() -> list:
    """
    Получение списка администраторов
    :return:
    """
    logging.info(f'get_list_admins')
    with db:
        sql = db.cursor()
        sql.execute('SELECT telegram_id, username FROM users WHERE is_admin = ?', (1,))
        list_admins = [row for row in sql.fetchall()]
        return list_admins


# # ПОЛЬЗОВАТЕЛЬ - имя пользователя по его id
def get_user(telegram_id: int):
    """
    ПОЛЬЗОВАТЕЛЬ - имя пользователя по его id
    :param telegram_id:
    :return:
    """
    logging.info(f'get_user')
    with db:
        sql = db.cursor()
        return sql.execute('SELECT username FROM users WHERE telegram_id = ?', (telegram_id,)).fetchone()


# # ПОЛЬЗОВАТЕЛЬ - данные пользователя по его id телеграмм
def get_info_user(telegram_id: int):
    """
    ПОЛЬЗОВАТЕЛЬ - имя пользователя по его id
    :param telegram_id:
    :return:
    """
    logging.info(f'get_user')
    with db:
        sql = db.cursor()
        return sql.execute('SELECT * FROM users WHERE telegram_id = ?', (telegram_id,)).fetchone()


# ПОЛЬЗОВАТЕЛЬ - получить список категорий
def get_select(telegram_id: int):
    """
    Получаем флаг пользователя в команде
    :param telegram_id:
    :return:
    """
    logging.info(f'set_select')
    with db:
        sql = db.cursor()
        in_command = sql.execute('SELECT list_category FROM users WHERE telegram_id = ?', (telegram_id,)).fetchone()
        return in_command[0]


# ПОЛЬЗОВАТЕЛЬ - обновляем список категорий
def set_select(list_category: str, telegram_id: int):
    """
    Обновление списка категорий
    :param list_category: список категорий
    :param telegram_id:
    :return:
    """
    logging.info(f'set_select')
    with db:
        sql = db.cursor()
        sql.execute('UPDATE users SET list_category = ? WHERE telegram_id = ?', (list_category, telegram_id))
        db.commit()


# СОЗДАНИЕ ТАБЛИЦ - order
def create_table_order() -> None:
    """
    Создание таблицы проведенных игр
    :return: None
    """
    logging.info("create_table_order")
    with db:
        sql = db.cursor()
        sql.execute("""CREATE TABLE IF NOT EXISTS orders(
            id INTEGER PRIMARY KEY,
            time_order TEXT,
            description_order TEXT,
            contact_order TEXT,
            category INTEGER,
            mailer_order TEXT,
            status TEXT,
            id_user INTEGER, 
            amount INTEGER,
            report TEXT
        )""")
        db.commit()


# ЗАЯВКА - добавление заявки
def add_order(time_order: str, description_order: str, contact_order: str, category: str, mailer_order: str, status: str, id_user: int, amount: int, report: str) -> None:
    """
    Добавление заявки в базу
    :param time_order:
    :param description_order:
    :param contact_order:
    :param category:
    :param mailer_order:
    :param status:
    :param id_user:
    :param amount:
    :return:
    """
    logging.info(f'add_category')
    with db:
        sql = db.cursor()
        sql.execute(f'INSERT INTO orders (time_order, description_order, contact_order, category, mailer_order, status, id_user, amount, report)'
                    f' VALUES ("{time_order}", "{description_order}", "{contact_order}", {category}, "{mailer_order}", "{status}", {id_user}, {amount}, "{report}")')
        db.commit()


# ЗАЯВКА - получение списка заявок
def get_list_order() -> list:
    """
    ЗАЯВКА - получение списка заявок
    :return: list(order:str)
    """
    logging.info(f'get_list_order')
    with db:
        sql = db.cursor()
        sql.execute('SELECT * FROM orders ORDER BY id')
        list_category = [row for row in sql.fetchall()]
        return list_category


# ЗАЯВКА - получение списка заявок исполнителя
def get_list_order_id(id_user: int) -> list:
    """
    ЗАЯВКА - получение списка заявок исполнителя
    :return: list(order:str)
    """
    logging.info(f'get_list_order')
    with db:
        sql = db.cursor()
        sql.execute('SELECT * FROM orders WHERE id_user = ? ORDER BY id', (id_user,))
        list_category = [row for row in sql.fetchall()]
        return list_category


# ЗАЯВКА - получение заявки по id
def get_order_id(id_order: int):
    """
    ЗАЯВКА - получение заявки по id
    :param id_order:
    :return:
    """
    logging.info(f'get_order_id')
    with db:
        sql = db.cursor()
        sql.execute('SELECT * FROM orders WHERE id =?', (id_order,))
        return sql.fetchone()


# ЗАЯВКА - обновляем список рассылки
def set_mailer_order(id_order: int, mailer_order: str):
    """
    Обновляем список рассылки для заказа
    :param id_order:
    :param mailer_order:
    :return:
    """
    logging.info(f'set_select')
    with db:
        sql = db.cursor()
        sql.execute('UPDATE orders SET mailer_order = ? WHERE id = ?', (mailer_order, id_order,))
        db.commit()


# ЗАЯВКА - обновляем статус заявки
def set_status_order(id_order: int, status: str):
    """
    Обновляем список рассылки для заказа
    :param id_order:
    :param status:
    :return:
    """
    logging.info(f'set_select')
    with db:
        sql = db.cursor()
        sql.execute('UPDATE orders SET status = ? WHERE id = ?', (status, id_order,))
        db.commit()


# ЗАЯВКА - обновляем исполнителя заявки
def set_user_order(id_order: int, id_user: int):
    """
    Обновляем исполнителя заказа
    :param id_order:
    :param id_user:
    :return:
    """
    logging.info(f'set_select')
    with db:
        sql = db.cursor()
        sql.execute('UPDATE orders SET id_user = ? WHERE id = ?', (id_user, id_order,))
        db.commit()


# ЗАЯВКА - обновляем статус заявки
def set_report_order(id_order: int, report: str):
    """
    Обновляем исполнителя заказа
    :param id_order:
    :param report:
    :return:
    """
    logging.info(f'set_select')
    with db:
        sql = db.cursor()
        sql.execute('UPDATE orders SET report = ? WHERE id = ?', (report, id_order,))
        db.commit()


# ЗАЯВКА - обновляем сумму заявки
def set_amount_order(id_order: int, amount: int):
    """
    Обновляем исполнителя заказа
    :param id_order:
    :param amount:
    :return:
    """
    logging.info(f'set_select')
    with db:
        sql = db.cursor()
        sql.execute('UPDATE orders SET amount = ? WHERE id = ?', (amount, id_order,))
        db.commit()


# СОЗДАНИЕ ТАБЛИЦ - category
def create_table_category() -> None:
    """
    Создание таблицы проведенных игр
    :return: None
    """
    logging.info("create_table_category")
    with db:
        sql = db.cursor()
        sql.execute("""CREATE TABLE IF NOT EXISTS category(
            id INTEGER PRIMARY KEY,
            name_category TEXT
        )""")
        db.commit()


# КАТЕГОРИЯ - добавление категории в базу
def add_category(category: str) -> None:
    """
    Добавление токена в таблицу пользователей с указанием кто его добавил
    :param category:
    :return:
    """
    logging.info(f'add_category')
    with db:
        sql = db.cursor()
        sql.execute(f'INSERT INTO category (name_category) VALUES ("{category}")')
        db.commit()


# КАТЕГОРИЯ - получение списка категорий
def get_list_category() -> list:
    """
    КАТЕГОРИЯ - получение списка категорий
    :return: list(category:str)
    """
    logging.info(f'get_list_category')
    with db:
        sql = db.cursor()
        sql.execute('SELECT * FROM category ORDER BY id')
        list_category = [row for row in sql.fetchall()]
        return list_category


# КАТЕГОРИЯ - удаление категории по его id
def delete_category(category_id: int):
    """
    КАТЕГОРИЯ - удаление категории по его id
    :param category_id:
    :return:
    """
    logging.info(f'delete_category')
    with db:
        sql = db.cursor()
        sql.execute('DELETE FROM category WHERE id = ?', (category_id,))
        db.commit()


# КАТЕГОРИЯ - получение названия категории ее id
def get_title_category(id_category: int) -> list:
    """
    КАТЕГОРИЯ - получение списка категорий
    :return: list(category:str)
    """
    logging.info(f'get_list_category: {id_category}')
    with db:
        sql = db.cursor()
        sql.execute('SELECT * FROM category WHERE id = ?', (id_category,))
        return sql.fetchone()[1]

#
#
#
#
#
#
#
#
#

#
#
#
#
#
# # ПОЛЬЗОВАТЕЛЬ - список пользователей верифицированных в боте
# def get_list_users_filter() -> list:
#     """
#     ПОЛЬЗОВАТЕЛЬ - список пользователей верифицированных в боте
#     :return: list(telegram_id:int, username:str)
#     """
#     logging.info(f'get_list_users_filter')
#     with db:
#         sql = db.cursor()
#         sql.execute('SELECT telegram_id, username, in_command FROM users WHERE NOT username = ?'
#                     ' ORDER BY id', ('username',))
#         list_username = [row for row in sql.fetchall()]
#         return list_username
#
#
# # ПОЛЬЗОВАТЕЛЬ - информация о трененре
# def get_info_coach(id_coach: int) -> tuple:
#     """
#     ПОЛЬЗОВАТЕЛЬ - список пользователей верифицированных в боте
#     :return: list(telegram_id:int, username:str)
#     """
#     logging.info(f'get_list_users_filter')
#     with db:
#         sql = db.cursor()
#         info_coach = sql.execute('SELECT telegram_id, username, in_command, in_game FROM users WHERE telegram_id = ?', (id_coach,)).fetchone()
#
#         return info_coach
#
#
#
#
#
# # ПОЛЬЗОВАТЕЛЬ - получение списка команды (заявка на игру)
# def get_list_command(id_coach: int = None) -> list:
#     """
#     ИГРА - список команды
#     :param id_coach: id_telegram тренера (админа)
#     :return: list(telegram_id:int, username:str)
#     """
#     logging.info(f'get_list_users')
#     with db:
#         sql = db.cursor()
#         sql.execute('SELECT telegram_id, username, in_game FROM users WHERE NOT username = ? AND coach = ?'
#                     ' AND in_command = ? ORDER BY id', ('username', id_coach, 1))
#         list_command = [row for row in sql.fetchall()]
#         return list_command
#
#
#
#
#

#
#
#
#
#
# # ПОЛЬЗОВАТЕЛЬ - Устанавливаем флаг добавления пользователя в розыгрыш
# def set_game(in_game: int, telegram_id: int):
#     """
#     Устанавливаем флаг добавления пользователя в розыгрыш
#     :param in_game: флаг розыгрыша
#     :param telegram_id:
#     :return:
#     """
#     logging.info(f'set_select')
#     with db:
#         sql = db.cursor()
#         sql.execute('UPDATE users SET in_game = ? WHERE telegram_id = ?', (in_game, telegram_id))
#         db.commit()
#
#
# # ПОЛЬЗОВАТЕЛЬ - Получаем флаг состояния игрока в розыгрыше
# def get_game(telegram_id: int):
#     """
#     Получаем флаг пользователя в розыгрыше
#     :param telegram_id:
#     :return:
#     """
#     logging.info(f'set_select')
#     with db:
#         sql = db.cursor()
#         in_command = sql.execute('SELECT in_game FROM users WHERE telegram_id = ?', (telegram_id,)).fetchone()
#         return in_command[0]
#
#
#
#
#
#
#
#
# # ИГРА - Добавление игры в базу данных
# def add_game(name_game: str, time_game: str, place_game: str, goal: int, goal_break: int, nogoal: int, turnover: int,
#              stat_command: str, id_coach: int) -> None:
#     """
#     ИГРА - Добавление игры в базу данных
#     :param name_game: название команд
#     :param time_game: дата проведения игры
#     :param place_game: место проведения игры
#     :param goal: количество голов забитых из положения АТАКА
#     :param goal_break: количество голов забитых из положение ЗАЩИТА
#     :param nogoal: количество пропущенных голов
#     :param turnover: количество совершенных turnover
#     :param stat_command: словарь со статистикой игроков
#     :param id_coach: id_telegram трененра
#     :return:
#     """
#     logging.info(f'add_game')
#     with db:
#         sql = db.cursor()
#         print(type(stat_command))
#         sql.execute(f'INSERT INTO games (name_game, time_game, place_game, goal, goal_break, nogoal, turnover,'
#                     f' stat_command, coach)'
#                     f'VALUES ("{name_game}", "{time_game}", "{place_game}", {goal}, {goal_break}, {nogoal}, {turnover},'
#                     f' "{stat_command}", {id_coach})')
#         db.commit()
#
#
# # СТАТИСТИКА - получить id_telegram тренера, который добавил игрока
# def get_id_coach(id_player: int) -> int:
#     """
#     СТАТИСТИКА - получить id тренера
#     :param id_player: id_telegram игрока
#     :return: telegram_id:int
#     """
#     logging.info(f'get_list_users_filter')
#     with db:
#         sql = db.cursor()
#         coach = sql.execute('SELECT coach FROM users WHERE telegram_id = ?', (id_player,)).fetchone()
#
#         return coach[0]
#
#
# # СТАТИСТИКА - Получение списка проведенных игр тренера с id_telegram id_coach
# def get_list_game(id_coach: int) -> list:
#     """
#     СТАТИСТИКА - список всех игр заведенных тренеров с id_telegram id_coach
#     :param id_coach: id_telegram тренера
#     :return: list(telegram_id:int, username:str)
#     """
#     logging.info(f'get_list_users_filter')
#     with db:
#         sql = db.cursor()
#         sql.execute('SELECT * FROM games WHERE coach = ?'
#                     ' ORDER BY id', (id_coach,))
#         list_username = [row for row in sql.fetchall()]
#         return list_username
#
#
# # АДМИНИСТРАТОРЫ - Получить список верифицированных пользователей не являющихся администратором
# def get_list_notadmins() -> list:
#     """
#     Получить список верифицированных пользователей не являющихся администратором
#     :return:
#     """
#     logging.info(f'get_list_notadmins')
#     with db:
#         sql = db.cursor()
#         sql.execute('SELECT telegram_id, username FROM users WHERE is_admin = ? AND NOT username = ?', (0, 'username'))
#         list_notadmins = [row for row in sql.fetchall()]
#         return list_notadmins
#
#

#
#

