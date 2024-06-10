from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.types import FSInputFile
from module.data_base import get_list_users, delete_user
import logging
from config_data.config import Config, load_config
router = Router()
config: Config = load_config()

@router.callback_query()
async def all_calback(callback: CallbackQuery) -> None:
    logging.info(f'all_calback: {callback.message.chat.id}')
    # print(callback.data)


@router.message()
async def all_message(message: Message) -> None:
    logging.info(f'all_message')
    if message.photo:
        logging.info(f'all_message message.photo')
        # print(message.photo[-1].file_id)

    if message.sticker:
        logging.info(f'all_message message.sticker')
        # Получим ID Стикера
        # print(message.sticker.file_id)
    list_super_admin = list(map(int,config.tg_bot.admin_ids.split(',')))
    # производим рассылку информационного сообщения
    if message.chat.id in list_super_admin:
        if message.text == '/get_logfile':
            file_path = "py_log.log"
            await message.answer_document(FSInputFile(file_path))
        if message.text == '/get_dbfile':
            file_path = "database.db"
            await message.answer_document(FSInputFile(file_path))
        if message.text == '/get_listusers':
            list_user = get_list_users()
            text = 'Список пользователей:\n'
            for i, user in enumerate(list_user):
                text += f'{i+1}. {user[1]} - {user[2]} - {user[-1]}\n'
                if i % 20 == 0 and i > 0:
                    await message.answer(text=text)
                    text = ''
            await message.answer(text=text)
        if '/del_user' in message.text:
            try:
                telegram_id = int(message.text.split()[1])
                delete_user(telegram_id=telegram_id)
                await message.answer(text='Пользователь удален')
            except:
                await message.answer(text='Пользователь не найден')
