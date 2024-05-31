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
    button_1 = InlineKeyboardButton(text='Согласовано время', callback_data=f'changestatus_time_{id_order}')
    button_2 = InlineKeyboardButton(text='На объекте', callback_data=f'changestatus_object_{id_order}')
    button_3 = InlineKeyboardButton(text='Отчет', callback_data=f'changestatus_report_{id_order}')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1], [button_2], [button_3]],)
    return keyboard


def keyboard_payment(payment_id: int) -> None:
    logging.info("keyboard_select_period_sales")
    button_1 = InlineKeyboardButton(text='Оплатить', callback_data=f'payment_{payment_id}')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1]],)
    return keyboard

def keyboard_select_period_sales_new() -> None:
    logging.info("keyboard_select_period_sales")
    button_1 = InlineKeyboardButton(text='Сегодня', callback_data='salesperiod_1')
    button_2 = InlineKeyboardButton(text='Календарь', callback_data='salesperiod_calendar')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1], [button_2]],)
    return keyboard

def keyboard_select_scale_sales() -> None:
    logging.info("keyboard_select_scale_sales")
    button_1 = InlineKeyboardButton(text='Менеджер', callback_data='salesmanager')
    button_2 = InlineKeyboardButton(text='Компания', callback_data='salescompany')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1], [button_2]],)
    return keyboard


def keyboards_list_product_sales(list_manager: list):
    logging.info("keyboards_list_product_sales")
    kb_builder = InlineKeyboardBuilder()
    buttons = []
    for i, manager in enumerate(list_manager):
        callback = f'salesmanager#{manager[1]}'
        buttons.append(InlineKeyboardButton(
            text=manager[1],
            callback_data=callback))
    kb_builder.row(*buttons, width=1)
    return kb_builder.as_markup()

def keyboard_get_exel() -> None:
    logging.info("keyboard_select_scale_sales")
    button_1 = InlineKeyboardButton(text='Выгрузить отчет Excel', callback_data='exel')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1],], )
    return keyboard