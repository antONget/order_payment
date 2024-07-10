from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
import logging


def keyboards_set_category(list_category: list, back: int, forward: int, count: int):
    """
    Клавиатура для выбора категории создаваемой заявки
    :param list_category: список категорий
    :param back:
    :param forward:
    :param count:
    :return:
    """
    logging.info("keyboards_set_category")
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
        button = f'setcategory_{row[0]}'
        buttons.append(InlineKeyboardButton(
            text=text,
            callback_data=button))
    button_back = InlineKeyboardButton(text='<<',
                                       callback_data=f'setback_{str(back)}')
    button_count = InlineKeyboardButton(text=f'{back+1}',
                                        callback_data='none')
    button_next = InlineKeyboardButton(text='>>',
                                       callback_data=f'setforward_{str(forward)}')
    kb_builder.row(*buttons, width=1)
    kb_builder.row(button_back, button_count, button_next)
    return kb_builder.as_markup()


def keyboard_mailer_order() -> None:
    logging.info("keyboard_select_place")
    button_1 = InlineKeyboardButton(text='Разослать',
                                    callback_data=f'order_mailer')
    button_2 = InlineKeyboardButton(text='Отмена',
                                    callback_data='order_cancel')
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[button_1, button_2]],
    )
    return keyboard


def keyboard_get_order(id_order: int) -> None:
    logging.info("keyboard_get_order")
    button_1 = InlineKeyboardButton(text='Взять',
                                    callback_data=f'getorder_confirm_{id_order}')
    button_2 = InlineKeyboardButton(text='Отмена',
                                    callback_data=f'getorder_cancel_{id_order}')
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[button_1, button_2]],
    )
    return keyboard


def keyboard_contract(id_order: int) -> None:
    logging.info("keyboard_get_order")
    button_1 = InlineKeyboardButton(text='Договорились',
                                    callback_data=f'contract_confirm_{id_order}')
    button_2 = InlineKeyboardButton(text='НЕ договорились',
                                    callback_data=f'contract_cancel_{id_order}')
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[button_1, button_2]],
    )
    return keyboard


def keyboard_reassert_contract(id_order: int, id_telegram: int, message_id: int) -> None:
    logging.info("keyboard_get_order")
    button_1 = InlineKeyboardButton(text='Подтвердить',
                                    callback_data=f'reassertcancel_{id_order}_{id_telegram}_{message_id}')
    button_2 = InlineKeyboardButton(text='НЕ подтверждать',
                                    callback_data=f'reassert_{id_order}_{id_telegram}_{message_id}')
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[button_1, button_2]],
    )
    return keyboard