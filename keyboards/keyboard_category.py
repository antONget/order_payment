from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
import logging


def keyboard_edit_list_category() -> None:
    """
    КАТЕГОРИЯ - [Добавить][Удалить]
    :return:
    """
    logging.info("keyboard_edit_list_category")
    button_1 = InlineKeyboardButton(text='Добавить',
                                    callback_data='add_category')
    button_2 = InlineKeyboardButton(text='Удалить',
                                    callback_data='delete_category')
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[button_1, button_2]],
    )
    return keyboard


def keyboards_del_category(list_category: list, back: int, forward: int, count: int):
    """
    КАТЕГОРИЯ -> Удалить категорию
    :param list_users: список категорий
    :param back:
    :param forward:
    :param count:
    :return:
    """
    logging.info("keyboards_del_category")
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

    for row in list_category[back*count:(forward-1)*count]:
        print(row)
        text = row[1]
        button = f'deletecategory_{row[0]}'
        buttons.append(InlineKeyboardButton(
            text=text,
            callback_data=button))
    button_back = InlineKeyboardButton(text='<<',
                                       callback_data=f'back_{str(back)}')
    button_count = InlineKeyboardButton(text=f'{back+1}',
                                        callback_data='none')
    button_next = InlineKeyboardButton(text='>>',
                                       callback_data=f'forward_{str(forward)}')
    kb_builder.row(*buttons, width=1)
    kb_builder.row(button_back, button_count, button_next)
    return kb_builder.as_markup()


def keyboard_delete_category() -> None:
    """
    КАТЕГОРИЯ -> Удалить -> подтверждение удаления категории из базы
    :return:
    """
    logging.info("keyboard_delete_category")
    button_1 = InlineKeyboardButton(text='Удалить',
                                    callback_data='del_category')
    button_2 = InlineKeyboardButton(text='Отмена',
                                    callback_data='notdel_category')
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[button_1, button_2]],
    )
    return keyboard

