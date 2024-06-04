from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
import logging


def keyboard_order() -> InlineKeyboardMarkup:
    logging.info("keyboard_order")
    button_1 = InlineKeyboardButton(text='Выполненные', callback_data='completed_tasks')
    button_2 = InlineKeyboardButton(text='В работе', callback_data='tasks_in_progress')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1], [button_2]],)
    return keyboard


def keyboard_order_in_process(filter_order_status: list) -> InlineKeyboardMarkup:
    logging.info("keyboard_order_in_process")
    inline_keyboard = []
    for order in filter_order_status:
        text = f'Заявка № {order[0]}'
        callback = f'processorder_{order[0]}'
        button = [InlineKeyboardButton(text=text, callback_data=callback)]
        inline_keyboard.append(button)
    keyboard = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
    return keyboard


def keyboard_change_status_order(id_order: int) -> None:
    logging.info("keyboard_change_status_order")
    button_1 = InlineKeyboardButton(text='В работе', callback_data=f'changestatus_inprogress_{id_order}')
    button_2 = InlineKeyboardButton(text='Комментарий', callback_data=f'changestatus_comment_{id_order}')
    button_3 = InlineKeyboardButton(text='Отчет', callback_data=f'changestatus_report_{id_order}')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1], [button_2], [button_3]],)
    return keyboard


def keyboard_payment(payment_url: str, payment_id: int) -> None:
    logging.info("keyboard_select_period_sales")
    button_1 = InlineKeyboardButton(text='Проверить', callback_data=f'payment_{payment_id}')
    button_2 = InlineKeyboardButton(text='Оплатить', url=f'{payment_url}')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_2], [button_1]],)
    return keyboard


def keyboard_comment() -> None:
    logging.info("keyboard_select_period_sales")
    button_1 = InlineKeyboardButton(text='Добавить', callback_data=f'comment_add')
    button_2 = InlineKeyboardButton(text='Отменить', url=f'comment_cancel')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_2], [button_1]],)
    return keyboard