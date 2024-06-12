from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message

from filter.admin_filter import check_super_admin, check_admin
from module.data_base import create_table_users, add_admin, add_user
from keyboards.keyboard_main import keyboards_super_admin, keyboards_partner, keyboards_user

import logging

router = Router()
# create_table_users()


@router.message(CommandStart(), lambda message: check_super_admin(message.chat.id))
async def s(message: Message) -> None:
    logging.info("process_start_command")
    """
    Запуск бота супер-администратором
    :param message: 
    :return: 
    """
    create_table_users()
    add_admin(id_admin=message.chat.id, user_name=message.from_user.username)
    await message.answer(text=f"Привет, {message.from_user.first_name} 👋\n"
                              f"Вы супер-администратор проекта, вы можете добавить/удалить Категории, "
                              f"смотреть отчеты и создавать заявки.",
                         reply_markup=keyboards_super_admin())


@router.message(CommandStart(), lambda message: check_admin(message.chat.id))
async def process_start_command_admin(message: Message) -> None:
    logging.info("process_start_command")
    """
    Запуск бота администратором
    :param message: 
    :return: 
    """
    create_table_users()
    add_admin(id_admin=message.chat.id, user_name=message.from_user.username)
    await message.answer(text=f"Привет, {message.from_user.first_name} 👋\n"
                              f"Вы партнер проекта, вы можете смотреть отчеты и создавать заявки.",
                         reply_markup=keyboards_partner())


@router.message(F.text == 'Поддержка')
async def process_support(message: Message) -> None:
    logging.info("process_support")
    await message.answer(text=f'Если у вас возникли вопросы или предложения по работе бота,'
                              f' то можете их задать <a href="https://t.me/Roman_holod24">менеджеру проекта</a>, '
                              f'а также воспользоваться поддержкой комьюнити в'
                              f' <a href="https://t.me/+VPOiR01TArg0Mjgy">общем чате</a>',
                         disable_web_page_preview=True,
                         parse_mode='html')

