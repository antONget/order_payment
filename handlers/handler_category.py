from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from aiogram.fsm.state import State, StatesGroup, default_state
import logging
import requests
from module.data_base import create_table_category, add_category, get_list_category, delete_category, get_list_users
from keyboards.keyboard_category import keyboards_del_category, keyboard_delete_category, keyboard_edit_list_category
from filter.admin_filter import check_super_admin
from config_data.config import Config, load_config

router = Router()
user_dict = {}
config: Config = load_config()


class Category(StatesGroup):
    title_category = State()


def get_telegram_user(user_id, bot_token):
    url = f'https://api.telegram.org/bot{bot_token}/getChat'
    data = {'chat_id': user_id}
    response = requests.post(url, data=data)
    return response.json()


# КАТЕГОРИЯ
@router.message(F.text == 'Категории', lambda message: check_super_admin(message.chat.id))
async def process_category(message: Message) -> None:
    logging.info(f'process_category: {message.chat.id}')
    create_table_category()
    await message.answer(text="Добавить или удалить категорию",
                         reply_markup=keyboard_edit_list_category())


# добавить категорию
@router.callback_query(F.data == 'add_category')
async def process_add_category(callback: CallbackQuery, state: FSMContext) -> None:
    logging.info(f'process_add_category: {callback.message.chat.id}')
    await callback.message.edit_text(text=f'Для добавления категории пришлите ее название')
    await state.set_state(Category.title_category)


@router.message(F.text, StateFilter(Category.title_category))
async def process_get_title_category(message: Message, state: FSMContext, bot: Bot) -> None:
    logging.info(f'process_get_title_category: {message.chat.id}')
    add_category(category=message.text)
    await message.answer(text="Новая категория добавлена в базу")
    # получаем список пользователей для рассылки
    #             id INTEGER PRIMARY KEY,
    #             telegram_id INTEGER,
    #             username TEXT,
    #             is_admin INTEGER,
    #             list_category TEXT,
    #             rating INTEGER
    list_mailer_category = get_list_users()
    list_super_admin = config.tg_bot.admin_ids.split(',')
    for user in list_mailer_category:
        if user[1] not in map(int, list_super_admin):
            result = get_telegram_user(user_id=user[1], bot_token=config.tg_bot.token)
            if 'result' in result:
                try:
                    await bot.send_message(chat_id=user[1],
                                           text=f'Создана новая категория {message.text}\n'
                                                f'Если желаете добавить ее в список категорий для получения заявок по ней,'
                                                f' то нажмите /start или введите ее в поле ввода')
                except:
                    pass
    await state.set_state(default_state)


# удалить пользователя
@router.callback_query(F.data == 'delete_category')
async def process_delete_category(callback: CallbackQuery) -> None:
    logging.info(f'process_delete_category: {callback.message.chat.id}')
    list_category = get_list_category()
    print(list_category)
    keyboard = keyboards_del_category(list_category=list_category,
                                      back=0,
                                      forward=2,
                                      count=6)
    await callback.message.edit_text(text='Выберите категорию, которого вы хотите удалить',
                                     reply_markup=keyboard)


# >>>>
@router.callback_query(F.data.startswith('forward'))
async def process_forward(callback: CallbackQuery) -> None:
    logging.info(f'process_forward: {callback.message.chat.id}')
    list_category = get_list_category()
    forward = int(callback.data.split('_')[1]) + 1
    back = forward - 2
    keyboard = keyboards_del_category(list_category=list_category,
                                      back=back,
                                      forward=forward,
                                      count=6)
    try:
        await callback.message.edit_text(text='Выбeрите категорию, которого вы хотите удалить',
                                         reply_markup=keyboard)
    except:
        await callback.message.edit_text(text='Выберите категорию, которого вы хотите удалить',
                                         reply_markup=keyboard)


# <<<<
@router.callback_query(F.data.startswith('back'))
async def process_back(callback: CallbackQuery) -> None:
    logging.info(f'process_back: {callback.message.chat.id}')
    list_category = get_list_category()
    back = int(callback.data.split('_')[1]) - 1
    forward = back + 2
    keyboard = keyboards_del_category(list_category=list_category,
                                      back=back,
                                      forward=forward,
                                      count=6)
    try:
        await callback.message.edit_text(text='Выберите категорию, которого вы хотите удалить',
                                         reply_markup=keyboard)
    except:
        await callback.message.edit_text(text='Выбeрите категорию, которого вы хотите удалить',
                                         reply_markup=keyboard)


# подтверждение удаления категории из базы
@router.callback_query(F.data.startswith('deletecategory'))
async def process_deletecategory(callback: CallbackQuery, state: FSMContext) -> None:
    logging.info(f'process_deletecategory: {callback.message.chat.id}')
    telegram_id = int(callback.data.split('_')[1])
    await state.update_data(del_category_id=telegram_id)
    await callback.message.edit_text(text=f'Удалить категорию',
                                     reply_markup=keyboard_delete_category())


# отмена удаления пользователя
@router.callback_query(F.data == 'notdel_category')
async def process_notdel_category(callback: CallbackQuery, bot: Bot) -> None:
    logging.info(f'process_notdel_category: {callback.message.chat.id}')
    try:
        await bot.delete_message(chat_id=callback.message.chat.id,
                                 message_id=callback.message.message_id)
    except:
        pass
    await process_category(callback.message)


# удаление после подтверждения
@router.callback_query(F.data == 'del_category')
async def process_del_category(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    logging.info(f'process_del_category: {callback.message.chat.id}')
    user_dict[callback.message.chat.id] = await state.get_data()
    delete_category(category_id=(user_dict[callback.message.chat.id]["del_category_id"]))
    try:
        await bot.delete_message(chat_id=callback.message.chat.id,
                                 message_id=callback.message.message_id)
    except:
        pass
    await callback.message.answer(text=f'Категория успешно удалена')

