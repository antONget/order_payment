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
            rating INTEGER, 
            phone TEXT
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
    Добавление пользователя в таблицу Users
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
            sql.execute(f'INSERT INTO users (telegram_id, username, is_admin, list_category, rating, phone) '
                        f'VALUES ({id_user}, "{user_name}", 0, "0", 0, "0")')
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


def get_list_users() -> list:
    """
    Получить список пользователей
    :return:
    """
    logging.info(f'get_list_users')
    with db:
        sql = db.cursor()
        sql.execute('SELECT * FROM users')
        list_users = [row for row in sql.fetchall()]
        return list_users


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


def set_rating(telegram_id: int, rating: int):
    """
    Назначение пользователя с id_telegram администратором
    :param telegram_id:
    :param rating:
    :return:
    """
    logging.info(f'set_rating')
    with db:
        sql = db.cursor()
        sql.execute('UPDATE users SET rating = ? WHERE telegram_id = ?', (rating, telegram_id))
        db.commit()


def set_phone(telegram_id: int, phone: str):
    """
    Назначение пользователя с id_telegram администратором
    :param telegram_id:
    :param phone:
    :return:
    """
    logging.info(f'set_rating')
    with db:
        sql = db.cursor()
        sql.execute('UPDATE users SET phone = ? WHERE telegram_id = ?', (phone, telegram_id))
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
    Получаем всю информацию из таблицы Users по пользователя по его id телеграмм
    :param telegram_id: id ntktuhfv gjkmpjdfntkz
    :return:
    """
    logging.info(f'get_info_user')
    with db:
        sql = db.cursor()
        return sql.execute('SELECT * FROM users WHERE telegram_id = ?', (telegram_id,)).fetchone()


# ПОЛЬЗОВАТЕЛЬ - получить список категорий
def get_select(telegram_id: int) -> str:
    """
    Получаем список id категорий пользователя, по которым он желает получать заявки
    :param telegram_id: id телеграм пользователя
    :return: строка включающая в себя id категорий заявок через запятую
    """
    logging.info(f'set_select')
    with db:
        sql = db.cursor()
        in_command = sql.execute('SELECT list_category FROM users WHERE telegram_id = ?', (telegram_id,)).fetchone()
        return in_command[0]


# ПОЛЬЗОВАТЕЛЬ - обновляем список категорий
def set_select(list_category: str, telegram_id: int):
    """
    Обновление списка категорий выбранных пользователем для получения заявок
    :param list_category: список категорий
    :param telegram_id:
    :return:
    """
    logging.info(f'set_select')
    with db:
        sql = db.cursor()
        sql.execute('UPDATE users SET list_category = ? WHERE telegram_id = ?', (list_category, telegram_id))
        db.commit()


def delete_user(telegram_id: int):
    """
    ПОЛЬЗОВАТЕЛЬ - удаление пользователя по его id_telegram
    :param id_telegram:
    :return:
    """
    logging.info(f'delete_user')
    with db:
        sql = db.cursor()
        sql.execute('DELETE FROM users WHERE telegram_id = ?', (telegram_id,))
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
            id_creator INTEGER,
            description_order TEXT,
            contact_order TEXT,
            category INTEGER,
            mailer_order TEXT,
            status TEXT,
            id_user INTEGER, 
            amount INTEGER,
            report TEXT,
            cancel_id TEXT,
            comment TEXT
        )""")
        db.commit()


# ЗАЯВКА - добавление заявки
def add_order(time_order: str, id_creator: int, description_order: str, contact_order: str, category: str, mailer_order: str, status: str, id_user: int, amount: int, report: str, cancel_id: str, comment: str) -> None:
    """
    Добавление заявки в базу
    :param time_order: время создания заявки
    :param id_creator: id telegram создателя заявки
    :param description_order: описание заявки
    :param contact_order: данные о контактах клиента
    :param category: категория заявки
    :param mailer_order: список кому уже был предложена заявка при ее расслке
    :param status: статус заявки
    :param id_user: id_telegram
    :param amount: стоимость выполнения заявки
    :param report: отчет к заказу
    :param cancel_id: список отказавшихся
    :return:
    """
    logging.info(f'add_category')
    with db:
        sql = db.cursor()
        sql.execute(f'INSERT INTO orders (time_order, id_creator, description_order, contact_order, category, mailer_order, status, id_user, amount, report, cancel_id, comment)'
                    f' VALUES ("{time_order}", {id_creator}, "{description_order}", "{contact_order}", {category}, "{mailer_order}", "{status}", {id_user}, {amount}, "{report}", "{cancel_id}", "{comment}")')
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


# ЗАЯВКА - получение списка заявок исполнителя
def get_list_order_id_not_complete(id_user: int) -> list:
    """
    ЗАЯВКА - получение списка заявок исполнителя
    :return: list(order:str)
    """
    logging.info(f'get_list_order')
    with db:
        sql = db.cursor()
        sql.execute('SELECT * FROM orders WHERE id_user = ? AND NOT status = ? ORDER BY id', (id_user, 'complete'))
        list_category = [row for row in sql.fetchall()]
        return list_category


def get_list_order_id_complete(id_user: int) -> list:
    """
    ЗАЯВКА - получение списка заявок исполнителя
    :return: list(order:str)
    """
    logging.info(f'get_list_order')
    with db:
        sql = db.cursor()
        sql.execute('SELECT * FROM orders WHERE id_user = ? AND status = ? ORDER BY id', (id_user, 'complete'))
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


def set_id_cancel_order(id_order: int, cancel_id: str):
    """
    Обновляем список рассылки для заказа
    :param id_order:
    :param cancel_id:
    :return:
    """
    logging.info(f'set_select')
    with db:
        sql = db.cursor()
        sql.execute('UPDATE orders SET cancel_id = ? WHERE id = ?', (cancel_id, id_order,))
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
    logging.info(f'set_report_order')
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


def set_comment_order(id_order: int, comment: str):
    """
    Обновляем исполнителя заказа
    :param id_order:
    :param comment:
    :return:
    """
    logging.info(f'set_comment_order')
    with db:
        sql = db.cursor()
        sql.execute('UPDATE orders SET comment = ? WHERE id = ?', (comment, id_order,))
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
    Получение списка категорий
    :return: list(id: int, name_category:str)
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
    Получение название категории по id категории
    :return: str
    """
    logging.info(f'get_list_category: {id_category}')
    with db:
        sql = db.cursor()
        sql.execute('SELECT * FROM category WHERE id = ?', (id_category,))
        return sql.fetchone()[1]
