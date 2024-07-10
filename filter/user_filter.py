from module.data_base import get_list_users
import re
import logging


def check_user(telegram_id: int) -> bool:
    logging.info(f'check_user: {telegram_id}')
    list_user = get_list_users()
    for info_user in list_user:
        if info_user[0] == telegram_id:
            return True
    return False


def filter_number_phone(phone_number):
    # Паттерн для российских номеров телефона
    # Российские номера могут начинаться с +7, 8, или без кода страны
    pattern = re.compile(r'^(\+7|8|7)?(\d{10})$')

    # Проверка соответствия паттерну
    match = pattern.match(phone_number)

    return bool(match)