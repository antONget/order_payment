from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
import logging


# ГЛАВНОЕ МЕНЮ ПОЛЬЗОВАТЕЛЯ
def keyboards_user() -> ReplyKeyboardMarkup:
    logging.info("keyboards_user")
    button_1 = KeyboardButton(text='Заявки')
    button_2 = KeyboardButton(text='Создать заявку')
    button_3 = KeyboardButton(text='Поддержка')
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[button_1], [button_2], [button_3]],
        resize_keyboard=True
    )
    return keyboard




def keyboards_create_list_category(list_category: list, back: int, forward: int, count: int):
    logging.info("keyboards_create_list_category")
    # считаем сколько всего блоков по заданному количество элементов в блоке
    count_users = len(list_category)
    whole = count_users // count
    remains = count_users % count
    max_forward = whole + 1
    if count_users <= count:
        back = 0
        forward = 2
    else:
        # проверка чтобы не ушли в минус
        if back < 0:
            back = 0
            forward = 2

        # если есть остаток, то увеличиваем количество блоков на один, чтобы показать остаток
        if remains:
            max_forward = whole + 2
        if forward > max_forward:
            forward = max_forward
            back = forward - 2
    kb_builder = InlineKeyboardBuilder()
    buttons = []
    # print(list_users, count_users, back, forward, max_forward)
    for row in list_category[back*count:(forward-1)*count]:
        # row - [telegram_id, username, select]
        if row[2] == 0:
            select = ' ❌'
        else:
            select = ' ✅'
        text = row[1] + select
        button = f'selectcategory_{row[0]}'
        buttons.append(InlineKeyboardButton(
            text=text,
            callback_data=button))
    button_back = InlineKeyboardButton(text='<<',
                                       callback_data=f'categoryback_{str(back)}')
    button_count = InlineKeyboardButton(text=f'Подтвердить',
                                        callback_data='create_list_user_category')
    button_next = InlineKeyboardButton(text='>>',
                                       callback_data=f'categoryforward_{str(forward)}')
    kb_builder.row(*buttons, width=1)
    kb_builder.row(button_back, button_count, button_next)
    return kb_builder.as_markup()


def keyboard_confirm_list_category() -> None:
    """
    ПОЛЬЗОВАТЕЛЬ -> подтверждение списка категорий
    :return:
    """
    logging.info("keyboard_confirm_list_category")
    button_1 = InlineKeyboardButton(text='Подтвердить',
                                    callback_data='confirm_user_category')
    button_2 = InlineKeyboardButton(text='Изменить',
                                    callback_data='change_user_category')
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[button_1], [button_2]],
    )
    return keyboard

def keyboards_get_contact() -> ReplyKeyboardMarkup:
    logging.info("keyboards_get_contact")
    button_1 = KeyboardButton(text='Отправить свой контакт ☎️', request_contact=True)
    button_2 = KeyboardButton(text='Отмена')
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[button_1]],
        resize_keyboard=True
    )
    return keyboard

def keyboard_confirm_phone() -> None:
    logging.info("keyboard_confirm_phone")
    button_1 = InlineKeyboardButton(text='Верно',
                                    callback_data='confirm_phone')
    button_2 = InlineKeyboardButton(text='Назад',
                                    callback_data='getphone_back')
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[button_1], [button_2]],
    )
    return keyboard

def keyboard_confirm_phone_1() -> None:
    logging.info("keyboard_confirm_phone")
    button_1 = InlineKeyboardButton(text='Верно',
                                    callback_data='confirm_phone_1')
    button_2 = InlineKeyboardButton(text='Изменить',
                                    callback_data='getphone_back')
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[button_1], [button_2]],
    )
    return keyboard