from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.filters import CommandStart, or_f

from config_data.config import Config, load_config
from module.data_base import create_table_users, create_table_category, add_user, get_list_category, get_select, \
    set_select, get_title_category, set_phone, get_info_user
from keyboards.keyboard_user import keyboards_user, keyboards_create_list_category, keyboard_confirm_list_category, \
    keyboards_get_contact, keyboard_confirm_phone, keyboard_confirm_phone_1

from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from aiogram.fsm.state import State, StatesGroup, default_state

import logging
import re

router = Router()
user_dict = {}
config: Config = load_config()


class User(StatesGroup):
    phone = State()

def validate_russian_phone_number(phone_number):
    # Паттерн для российских номеров телефона
    # Российские номера могут начинаться с +7, 8, или без кода страны
    pattern = re.compile(r'^(\+7|8|7)?(\d{10})$')

    # Проверка соответствия паттерну
    match = pattern.match(phone_number)

    return bool(match)


@router.message(CommandStart())
async def process_start_command_user(message: Message) -> None:
    logging.info("process_start_command_user")
    """
    Запуск бота исполнителем и выбор категорий для получения заявок
    :param message: 
    :return: 
    """
    create_table_users()
    create_table_category()
    add_user(id_user=message.chat.id, user_name=message.from_user.username)
    await message.answer(text=f"Привет, {message.from_user.first_name} 👋\n"
                              f"Здесь можно получить  и создать заявку",
                         reply_markup=keyboards_user())

    list_select_category = get_select(telegram_id=message.chat.id)

    if list_select_category == "-" or len(list_select_category) == 0:
        list_user = []
    else:
        if ',' in list_select_category:
            list_user = [int(item) for item in list_select_category.split(',')]
        else:
            list_user = [int(list_select_category)]
    list_category = []
    for item in get_list_category():
        if item[0] in list_user:
            list_category.append([item[0], item[1], 1])
        else:
            list_category.append([item[0], item[1], 0])

    keyboard = keyboards_create_list_category(list_category=list_category,
                                              back=0,
                                              forward=2,
                                              count=6)
    await message.answer(text="Отметьте категории ✅ ,нажав на кнопку с ее названием по которым бы хотели получать"
                              " заявки. Можно выбрать несколько категорий.",
                         reply_markup=keyboard)


# >>>>
@router.callback_query(F.data.startswith('categoryforward'))
async def process_forward(callback: CallbackQuery) -> None:
    """
    Действие на пагинацию, если в блоке недостаточно места для всех категорий
    :param callback: callback.data.split('_')[1] номер блока для вывода списка категорий
    :return:
    """
    logging.info(f'process_forward: {callback.message.chat.id}')
    forward = int(callback.data.split('_')[1]) + 1
    back = forward - 2
    list_select_category = get_select(telegram_id=callback.message.chat.id)
    if list_select_category == "-" or len(list_select_category) == 0:
        list_user = []
    else:
        if ',' in list_select_category:
            list_user = [int(item) for item in list_select_category.split(',')]
        else:
            list_user = [int(list_select_category)]
    list_category = []
    for item in get_list_category():
        if item[0] in list_user:
            list_category.append([item[0], item[1], 1])
        else:
            list_category.append([item[0], item[1], 0])
    keyboard = keyboards_create_list_category(list_category=list_category,
                                              back=back,
                                              forward=forward,
                                              count=6)
    try:
        await callback.message.edit_text(text="Отметьте категории ✅ ,нажав на кнопку с ее названием по которым бы"
                                              " хотeли получать заявки. Можно выбрать несколько категорий.",
                                         reply_markup=keyboard)
    except:
        await callback.message.edit_text(text="Отметьте категории ✅ ,нажав на кнопку с ее названием по которым бы"
                                              " хотели получать заявки. Можно выбрать несколько категорий.",
                                         reply_markup=keyboard)


# <<<<
@router.callback_query(F.data.startswith('playerback'))
async def process_back(callback: CallbackQuery) -> None:
    """
    Действие на пагинацию, если в блоке недостаточно места для всех категорий
    :param callback: callback.data.split('_')[1] номер блока для вывода списка категорий
    :return:
    """
    logging.info(f'process_back: {callback.message.chat.id}')
    back = int(callback.data.split('_')[1]) - 1
    forward = back + 2
    list_select_category = get_select(telegram_id=callback.message.chat.id)
    if list_select_category == "0" or len(list_select_category) == 0:
        list_user = []
    else:
        if ',' in list_select_category:
            list_user = [int(item) for item in list_select_category.split(',')]
        else:
            list_user = [int(list_select_category)]
    list_category = []
    for item in get_list_category():
        if item[0] in list_user:
            list_category.append([item[0], item[1], 1])
        else:
            list_category.append([item[0], item[1], 0])
    keyboard = keyboards_create_list_category(list_category=list_category,
                                              back=back,
                                              forward=forward,
                                              count=6)
    try:
        await callback.message.edit_text(text="Отметьте категории ✅ ,нажав на кнопку с ее названием по которым бы"
                                              " хотeли получать заявки. Можно выбрать несколько категорий.",
                                         reply_markup=keyboard)
    except:
        await callback.message.edit_text(text="Отметьте категории ✅ ,нажав на кнопку с ее названием по которым бы"
                                              " хотели получать заявки. Можно выбрать несколько категорий.",
                                         reply_markup=keyboard)


# добавление игрока в команду
@router.callback_query(F.data.startswith('selectcategory_'))
async def process_select_category(callback: CallbackQuery) -> None:
    """
    Перевод категорий в список пользователя,
    на клавиатуре при нажатии появляются эмодзи ❌ и ✅ для добавления и удаления из списка
    :param callback: callback.data.split('_')[1] содержит id категории заявки
    :return:
    """
    logging.info(f'process_select_player: {callback.message.chat.id}')
    category_id = int(callback.data.split('_')[1])

    list_select_category = get_select(telegram_id=callback.message.chat.id)
    if list_select_category == "0" or len(list_select_category) == 0:
        list_user = []
    else:
        if ',' in list_select_category:
            list_user = [int(item) for item in list_select_category.split(',')]
        else:
            list_user = [int(list_select_category)]
    if category_id in list_user:
        list_user.remove(category_id)

        set_select(list_category=','.join(map(str, list_user)), telegram_id=callback.message.chat.id)
    else:
        list_user.append(category_id)
        set_select(list_category=','.join(map(str, list_user)), telegram_id=callback.message.chat.id)
    list_category = []
    for item in get_list_category():
        if item[0] in list_user:
            list_category.append([item[0], item[1], 1])
        else:
            list_category.append([item[0], item[1], 0])

    keyboard = keyboards_create_list_category(list_category=list_category,
                                              back=0,
                                              forward=2,
                                              count=6)
    try:
        await callback.message.edit_text(text="Отметьте категории ✅ ,нажав на кнопку с ее названием по которым бы"
                                              " хотeли получать заявки. Можно выбрать несколько категорий.",
                                         reply_markup=keyboard)
    except:
        await callback.message.edit_text(text="Отметьте категории ✅ ,нажав на кнопку с ее названием по которым бы"
                                              " хотели получать заявки. Можно выбрать несколько категорий.",
                                         reply_markup=keyboard)


@router.callback_query(F.data == 'create_list_user_category')
async def process_create_command(callback: CallbackQuery) -> None:
    """
    Согласование состава команды на игру (заявки на игру)
    :param callback:
    :return:
    """
    logging.info(f'create_list_user_category: {callback.message.chat.id}')
    list_select_category = get_select(telegram_id=callback.message.chat.id)
    if list_select_category == "0" or len(list_select_category) == 0:
        list_user = []
    else:
        if ',' in list_select_category:
            list_user = [int(item) for item in list_select_category.split(',')]
        else:
            print(list_select_category)
            list_user = [int(list_select_category)]
    list_category = get_list_category()

    text = f'<b>Список выбранных категорий:</b>\n'
    for i, id_category in enumerate(list_user):
        print(id_category)
        title_category = get_title_category(id_category=id_category)
        text += f'{i+1}. {title_category}\n'
    await callback.message.edit_text(text=text,
                                     reply_markup=keyboard_confirm_list_category(),
                                     parse_mode='html')


@router.callback_query(F.data == 'change_user_category')
async def process_change_command(callback: CallbackQuery, bot: Bot) -> None:
    """
    Изменение состава команды (заявки на игру)
    :param callback:
    :param state:
    :return:
    """
    logging.info(f'process_change_command: {callback.message.chat.id}')
    await bot.delete_message(chat_id=callback.message.chat.id,
                             message_id=callback.message.message_id)
    list_select_category = get_select(telegram_id=callback.message.chat.id)
    if list_select_category == "0" or len(list_select_category) == 0:
        list_user = []
    else:
        if ',' in list_select_category:
            list_user = [int(item) for item in list_select_category.split(',')]
        else:
            list_user = [int(list_select_category)]
    list_category = []
    for item in get_list_category():
        if item[0] in list_user:
            list_category.append([item[0], item[1], 1])
        else:
            list_category.append([item[0], item[1], 0])

    keyboard = keyboards_create_list_category(list_category=list_category,
                                              back=0,
                                              forward=2,
                                              count=6)
    await callback.message.answer(text="Отметьте категории ✅ ,нажав на кнопку с ее названием по которым бы хотели "
                                       "получать заявки. Можно выбрать несколько категорий.",
                                  reply_markup=keyboard)


@router.callback_query(F.data == 'confirm_user_category')
async def process_confirm_command(callback: CallbackQuery, bot: Bot, state: FSMContext) -> None:
    """
    Подтверждение создания состава команды (заявки на игру)
    :param callback:
    :param bot:
    :return:
    """
    logging.info(f'process_confirm_command: {callback.message.chat.id}')
    await bot.delete_message(chat_id=callback.message.chat.id,
                             message_id=callback.message.message_id)
    await callback.answer(text='Список категорий успешно помещен в базу', show_alert=True)
    list_info_user = get_info_user(telegram_id=callback.message.chat.id)
    if list_info_user[-1] == "0":
        await callback.message.answer(
            text='Для получения выплат за размещенные вами заявки укажите номер телефона в поле ввода'
                 ' или воспользуйтесь кнопкой "Отправить свой контакт ☎️"',
            reply_markup=keyboards_get_contact())
        await state.set_state(User.phone)
    else:
        await callback.message.answer(text=f'Твой номер телефона, {list_info_user[-1]}. Верно?',
                                      reply_markup=keyboard_confirm_phone_1())


@router.message(or_f(F.text, F.contact), StateFilter(User.phone))
async def process_validate_russian_phone_number(message: Message, state: FSMContext) -> None:
    logging.info("process_start_command_user")
    if message.contact:
        phone = str(message.contact.phone_number)
    else:
        phone = message.text
        if not validate_russian_phone_number(phone):
            await message.answer(text="Неверный формат номера. Повторите ввод, например 89991112222:")
            return
    await state.update_data(phone=phone)
    await state.set_state(default_state)
    await message.answer(text=f'Записываю, {phone}. Верно?',
                         reply_markup=keyboard_confirm_phone())


@router.callback_query(F.data == 'confirm_phone')
async def process_confirm_phone(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    logging.info(f'process_confirm_phone: {callback.message.chat.id}')
    user_dict[callback.message.chat.id] = await state.get_data()
    phone = user_dict[callback.message.chat.id]['phone']
    set_phone(telegram_id=callback.message.chat.id, phone=phone)
    await bot.delete_message(chat_id=callback.message.chat.id,
                             message_id=callback.message.message_id)
    await callback.message.answer(text='Номер телефона успешно занесен в базу',
                                  reply_markup=ReplyKeyboardRemove())
    await callback.message.answer(text=f"Здесь можно получить и создать заявку",
                                  reply_markup=keyboards_user())


@router.callback_query(F.data == 'confirm_phone_1')
async def process_confirm_phone_1(callback: CallbackQuery, bot: Bot) -> None:
    logging.info(f'process_confirm_phone_1: {callback.message.chat.id}')
    await bot.delete_message(chat_id=callback.message.chat.id,
                             message_id=callback.message.message_id)


@router.callback_query(F.data == 'getphone_back')
async def process_confirm_username(callback: CallbackQuery, bot: Bot, state: FSMContext) -> None:
    logging.info(f'process_confirm_username: {callback.message.chat.id}')
    await bot.delete_message(chat_id=callback.message.chat.id,
                             message_id=callback.message.message_id)
    await callback.message.answer(
        text='Для получения выплат за размещенные вами заявки укажите номер телефона в поле ввода'
             ' или воспользуйтесь кнопкой "Отправить свой контакт ☎️"',
        reply_markup=keyboards_get_contact())
    await state.set_state(User.phone)
