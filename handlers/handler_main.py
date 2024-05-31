from aiogram import Router
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
                              f"Вы супер-администратор проекта, вы можете добавить/удалить партнеров, "
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



