from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
import logging


# ГЛАВНОЕ МЕНЮ СУПЕР-АДМИНИСТРАТОРА
def keyboards_super_admin() -> ReplyKeyboardMarkup:
    logging.info("keyboards_super_admin")
    button_1 = KeyboardButton(text='Заявки')
    button_2 = KeyboardButton(text='Партнер')
    button_3 = KeyboardButton(text='Категории')
    button_4 = KeyboardButton(text='Создать заявку')
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[button_1], [button_2], [button_3], [button_4]],
        resize_keyboard=True
    )
    return keyboard


# ГЛАВНОЕ МЕНЮ ПАРТНЕРА
def keyboards_partner() -> ReplyKeyboardMarkup:
    logging.info("keyboards_partner")
    button_1 = KeyboardButton(text='Заявки')
    button_2 = KeyboardButton(text='Категории')
    button_3 = KeyboardButton(text='Создать заявку')
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[button_1], [button_2], [button_3]],
        resize_keyboard=True
    )
    return keyboard


# ГЛАВНОЕ МЕНЮ ПОЛЬЗОВАТЕЛЯ
def keyboards_user() -> ReplyKeyboardMarkup:
    logging.info("keyboards_user")
    button_1 = KeyboardButton(text='Заявки')
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[button_1]],
        resize_keyboard=True
    )
    return keyboard
