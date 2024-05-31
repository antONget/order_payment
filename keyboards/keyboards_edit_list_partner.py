from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
import logging


# АДМИНИСТРАТОРЫ
def keyboard_edit_list_admins() -> None:
    """
    Клавиатура для редактирования списка администраторов
    :return:
    """
    button_1 = InlineKeyboardButton(text='Назначить',
                                    callback_data='add_admin')
    button_2 = InlineKeyboardButton(text='Разжаловать',
                                    callback_data='delete_admin')
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[button_1, button_2]],
    )
    return keyboard


# АДМИНИСТРАТОРЫ -> Назначить
def keyboards_add_admin(list_admin, back, forward, count):
    logging.info(f'keyboards_add_admin')
    # проверка чтобы не ушли в минус
    if back < 0:
        back = 0
        forward = 2
    # считаем сколько всего блоков по заданному количество элементов в блоке
    count_users = len(list_admin)
    whole = count_users // count
    remains = count_users % count
    max_forward = whole + 1
    # если есть остаток то, увеличиваем количество блоков на один, чтобы показать остаток
    if remains:
        max_forward = whole + 2
    if forward > max_forward:
        forward = max_forward
        back = forward - 2
    kb_builder = InlineKeyboardBuilder()
    buttons = []
    print(list_admin, count_users, back, forward, max_forward)
    for row in list_admin[back*count:(forward-1)*count]:
        print(row)
        text = row[1]
        button = f'adminadd_{row[0]}'
        buttons.append(InlineKeyboardButton(
            text=text,
            callback_data=button))
    button_back = InlineKeyboardButton(text='<<<<',
                                       callback_data=f'adminback_{str(back)}')
    button_count = InlineKeyboardButton(text=f'{back+1}',
                                        callback_data='none')
    button_next = InlineKeyboardButton(text='>>>>',
                                       callback_data=f'adminforward_{str(forward)}')

    kb_builder.row(*buttons, width=1)
    kb_builder.row(button_back, button_count, button_next)

    return kb_builder.as_markup()


# АДМИНИСТРАТОРЫ -> Назначить -> подтверждение добавления админа в список админов
def keyboard_add_list_admins() -> None:
    """
    Клавиатура для подтверждения добавления пользователя в список администраторов
    :return:
    """
    button_1 = InlineKeyboardButton(text='Назначить',
                                    callback_data='add_admin_list')
    button_2 = InlineKeyboardButton(text='Отменить',
                                    callback_data='notadd_admin_list')
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[button_1, button_2]],
    )
    return keyboard


# АДМИНИСТРАТОРЫ -> Разжаловать
def keyboards_del_admin(list_admin, back, forward, count):
    logging.info(f'keyboards_del_admin')
    # проверка чтобы не ушли в минус
    if back < 0:
        back = 0
        forward = 2
    # считаем сколько всего блоков по заданному количество элементов в блоке
    count_users = len(list_admin)
    whole = count_users // count
    remains = count_users % count
    max_forward = whole + 1
    # если есть остаток то увеличиваем количество блоков на один, чтобы показать остаток
    if remains:
        max_forward = whole + 2
    if forward > max_forward:
        forward = max_forward
        back = forward - 2
    kb_builder = InlineKeyboardBuilder()
    buttons = []
    print(list_admin, count_users, back, forward, max_forward)
    for row in list_admin[back*count:(forward-1)*count]:
        print(row)
        text = row[1]
        button = f'admindel_{row[0]}'
        buttons.append(InlineKeyboardButton(
            text=text,
            callback_data=button))
    button_back = InlineKeyboardButton(text='<<<<',
                                       callback_data=f'admindelback_{str(back)}')
    button_count = InlineKeyboardButton(text=f'{back+1}',
                                        callback_data='none')
    button_next = InlineKeyboardButton(text='>>>>',
                                       callback_data=f'admindelforward_{str(forward)}')

    kb_builder.row(*buttons, width=1)
    kb_builder.row(button_back, button_count, button_next)

    return kb_builder.as_markup()


# АДМИНИСТРАТОРЫ -> Разжаловать -> подтверждение добавления админа в список админов
def keyboard_del_list_admins() -> None:
    """
    Клавиатура для разжалования пользователя в список администраторов
    :return:
    """
    button_1 = InlineKeyboardButton(text='Разжаловать',
                                    callback_data='del_admin_list')
    button_2 = InlineKeyboardButton(text='Отменить',
                                    callback_data='notdel_admin_list')
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[button_1, button_2]],
    )
    return keyboard