from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from keyboards.keyboards_edit_list_partner import keyboard_edit_list_admins, keyboards_add_admin,\
    keyboard_add_list_admins, keyboards_del_admin, keyboard_del_list_admins
from module.data_base import get_list_notadmins, get_user, set_admins, get_list_admins, set_notadmins
from filter.admin_filter import check_super_admin
from config_data.config import Config, load_config

import asyncio
import logging

config: Config = load_config()
router = Router()
user_dict = {}


# АДМИНИСТРАТОРЫ
@router.message(F.text == 'Партнер', lambda message: check_super_admin(message.chat.id))
async def process_change_list_admins(message: Message) -> None:
    logging.info(f'process_change_list_admins: {message.chat.id}')
    await message.answer(text="Добавить или удалить партнера?",
                         reply_markup=keyboard_edit_list_admins())


# добавление администратора
@router.callback_query(F.data == 'add_admin')
async def process_add_admin(callback: CallbackQuery) -> None:
    logging.info(f'process_add_admin: {callback.message.chat.id}')
    list_admin = get_list_notadmins()
    keyboard = keyboards_add_admin(list_admin, 0, 2, 6)
    await callback.message.edit_text(text='Выберите пользователя, которого нужно сделать партнером',
                                     reply_markup=keyboard)


# >>>>
@router.callback_query(F.data.startswith('adminforward'))
async def process_forwardadmin(callback: CallbackQuery) -> None:
    logging.info(f'process_forwardadmin: {callback.message.chat.id}')
    list_admin = get_list_notadmins()
    forward = int(callback.data.split('_')[1]) + 1
    back = forward - 2
    keyboard = keyboards_add_admin(list_admin, back, forward, 6)
    try:
        await callback.message.edit_text(text='Выберите пользователя, которого вы хотите сделать партнером',
                                         reply_markup=keyboard)
    except:
        await callback.message.edit_text(text='Выберите пользователя, которого нужно сделать партнером',
                                         reply_markup=keyboard)


# <<<<
@router.callback_query(F.data.startswith('adminback'))
async def process_backadmin(callback: CallbackQuery) -> None:
    logging.info(f'process_backadmin: {callback.message.chat.id}')
    list_admin = get_list_notadmins()
    back = int(callback.data.split('_')[1]) - 1
    forward = back + 2
    keyboard = keyboards_add_admin(list_admin, back, forward, 6)
    try:
        await callback.message.edit_text(text='Выберите пользователя, которого вы хотите сделать партнером',
                                         reply_markup=keyboard)
    except:
        await callback.message.edit_text(text='Выберите пользователя, которого нужно сделать партнером',
                                         reply_markup=keyboard)


# подтверждение добавления пользователя в список администраторов
@router.callback_query(F.data.startswith('adminadd'))
async def process_adminadd(callback: CallbackQuery, state: FSMContext) -> None:
    logging.info(f'process_adminadd: {callback.message.chat.id}')
    telegram_id = int(callback.data.split('_')[1])
    user_info = get_user(telegram_id)
    await state.update_data(add_admin_telegram_id=telegram_id)
    await callback.message.edit_text(text=f'Сделать пользователя {user_info[0]} партнером',
                                  reply_markup=keyboard_add_list_admins())


# отмена добавления пользователя в список администраторов
@router.callback_query(F.data == 'notadd_admin_list')
async def process_notadd_admin_list(callback: CallbackQuery) -> None:
    logging.info(f'process_notadd_admin_list: {callback.message.chat.id}')
    await process_change_list_admins(callback.message)


# удаление после подтверждения
@router.callback_query(F.data == 'add_admin_list')
async def process_add_admin_list(callback: CallbackQuery, state: FSMContext) -> None:
    logging.info(f'process_add_admin_list: {callback.message.chat.id}')
    user_dict[callback.message.chat.id] = await state.get_data()
    # user_info = get_user(user_dict[callback.message.chat.id]["add_admin_telegram_id"])
    # print('add_admin_list', user_info, user_dict[callback.message.chat.id]["add_admin_telegram_id"])
    set_admins(int(user_dict[callback.message.chat.id]["add_admin_telegram_id"]))
    await callback.answer(text=f'Пользователь успешно назначен партнером', show_alert=True)
    await asyncio.sleep(1)
    await process_change_list_admins(callback.message)


# разжалование администратора
@router.callback_query(F.data == 'delete_admin')
async def process_del_admin(callback: CallbackQuery) -> None:
    logging.info(f'process_del_admin: {callback.message.chat.id}')
    list_admin = get_list_admins()
    keyboard = keyboards_del_admin(list_admin, 0, 2, 6)
    await callback.message.answer(text='Выберите пользователя, которого нужно удалить из партнеров',
                                  reply_markup=keyboard)


# >>>>
@router.callback_query(F.data.startswith('admindelforward'))
async def process_forwarddeladmin(callback: CallbackQuery) -> None:
    logging.info(f'process_forwarddeladmin: {callback.message.chat.id}')
    list_admin = get_list_admins()
    forward = int(callback.data.split('_')[1]) + 1
    back = forward - 2
    keyboard = keyboards_del_admin(list_admin, back, forward, 2)
    try:
        await callback.message.edit_text(text='Выберите пользователя, которого вы хотите удалить из партнеров',
                                         reply_markup=keyboard)
    except:
        await callback.message.edit_text(text='Выберитe пользоватeля, которого вы хотите удалить из партнеров',
                                         reply_markup=keyboard)


# <<<<
@router.callback_query(F.data.startswith('admindelback'))
async def process_backdeladmin(callback: CallbackQuery) -> None:
    logging.info(f'process_backdeladmin: {callback.message.chat.id}')
    list_admin = get_list_admins()
    back = int(callback.data.split('_')[1]) - 1
    forward = back + 2
    keyboard = keyboards_del_admin(list_admin, back, forward, 2)
    try:
        await callback.message.edit_text(text='Выберите пользователя, которого вы хотите удалить из партнеров',
                                         reply_markup=keyboard)
    except:
        await callback.message.edit_text(text='Выберитe пользоватeля, которого вы хотите удалить из партнеров',
                                         reply_markup=keyboard)


# подтверждение добавления админа в список
@router.callback_query(F.data.startswith('admindel'))
async def process_deleteuser(callback: CallbackQuery, state: FSMContext) -> None:
    logging.info(f'process_deleteuser: {callback.message.chat.id}')
    telegram_id = int(callback.data.split('_')[1])
    user_info = get_user(telegram_id)
    await state.update_data(del_admin_telegram_id=telegram_id)
    await callback.message.answer(text=f'Удалить пользователя {user_info[0]} из партнеров',
                                  reply_markup=keyboard_del_list_admins())


# отмена добавления пользователя в список администраторов
@router.callback_query(F.data == 'notdel_admin_list')
async def process_notdel_admin_list(callback: CallbackQuery) -> None:
    logging.info(f'process_deleteuser: {callback.message.chat.id}')
    await process_change_list_admins(callback.message)


# удаление после подтверждения
@router.callback_query(F.data == 'del_admin_list')
async def process_del_admin_list(callback: CallbackQuery, state: FSMContext) -> None:
    logging.info(f'process_description: {callback.message.chat.id}')
    user_dict[callback.message.chat.id] = await state.get_data()
    # user_info = get_user(user_dict[callback.message.chat.id]["del_admin_telegram_id"])
    # print('process_description', user_info, user_dict[callback.message.chat.id]["del_admin_telegram_id"])
    set_notadmins(int(user_dict[callback.message.chat.id]["del_admin_telegram_id"]))
    await callback.answer(text=f'Пользователь успешно удален из партнеров', show_alert=True)
    await asyncio.sleep(1)
    await process_change_list_admins(callback.message)
