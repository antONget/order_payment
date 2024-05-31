import asyncio

from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from aiogram.fsm.state import State, StatesGroup, default_state

from filter.admin_filter import check_admin
from config_data.config import Config, load_config
from keyboards.keyboards_create_order import keyboards_set_category, keyboard_mailer_order, keyboard_get_order
from module.data_base import get_list_order, get_list_notadmins_mailer, get_list_category, get_title_category,\
    create_table_order, add_order, create_table_category, set_mailer_order, set_status_order, set_user_order, get_order_id

import logging
import requests
from datetime import datetime

router = Router()
config: Config = load_config()


class Order(StatesGroup):
    description = State()
    contact = State()


user_dict = {}


def get_telegram_user(user_id, bot_token):
    url = f'https://api.telegram.org/bot{bot_token}/getChat'
    data = {'chat_id': user_id}
    response = requests.post(url, data=data)
    return response.json()


@router.message(F.text == 'Создать заявку', lambda message: check_admin(message.chat.id))
async def process_create_order(message: Message, state: FSMContext) -> None:
    """
    Создание заявки
    :param message:
    :param state:
    :return:
    """
    logging.info(f'process_create_order: {message.chat.id}')
    create_table_order()
    create_table_category()
    await message.answer(text="Введите описание заявки")
    await state.set_state(Order.description)


@router.message(F.text, StateFilter(Order.description))
async def get_description_order(message: Message, state: FSMContext) -> None:
    """
    Получение описание заявки
    :param message: message.text содержит описание заявки
    :param state:
    :return:
    """
    logging.info(f'get_description_order: {message.chat.id}')
    await state.update_data(description_order=message.text)
    await message.answer(text="Введите информацию, которую исполнитель получит после того как откликнется на заявку")
    await state.set_state(Order.contact)


@router.message(F.text, StateFilter(Order.contact))
async def get_contact_order(message: Message, state: FSMContext) -> None:
    """
    Получение контактных данных заявки
    :param message: message.text контакты заявки
    :param state:
    :return:
    """
    logging.info(f'get_contact_order: {message.chat.id}')
    await state.update_data(contact_order=message.text)
    list_category = get_list_category()
    print(list_category)
    keyboard = keyboards_set_category(list_category=list_category,
                                      back=0,
                                      forward=2,
                                      count=6)
    await message.answer(text='Выберите категорию заявки',
                         reply_markup=keyboard)


# >>>>
@router.callback_query(F.data.startswith('setforward'))
async def process_setforward(callback: CallbackQuery) -> None:
    logging.info(f'process_setforward: {callback.message.chat.id}')
    list_category = get_list_category()
    forward = int(callback.data.split('_')[1]) + 1
    back = forward - 2
    keyboard = keyboards_set_category(list_category=list_category,
                                      back=back,
                                      forward=forward,
                                      count=6)
    try:
        await callback.message.edit_text(text='Выбeрите категорию заявки',
                                         reply_markup=keyboard)
    except:
        await callback.message.edit_text(text='Выберите категорию заявки',
                                         reply_markup=keyboard)

# <<<<
@router.callback_query(F.data.startswith('setback'))
async def process_setback(callback: CallbackQuery) -> None:
    logging.info(f'process_setback: {callback.message.chat.id}')
    list_category = get_list_category()
    back = int(callback.data.split('_')[1]) - 1
    forward = back + 2
    keyboard = keyboards_set_category(list_category=list_category,
                                      back=back,
                                      forward=forward,
                                      count=6)
    try:
        await callback.message.edit_text(text='Выберите категорию заявки',
                                         reply_markup=keyboard)
    except:
        await callback.message.edit_text(text='Выбeрите категорию заявки',
                                         reply_markup=keyboard)


@router.callback_query(F.data.startswith('setcategory'))
async def process_setcategory(callback: CallbackQuery, state: FSMContext) -> None:
    logging.info(f'process_setcategory: {callback.message.chat.id}')
    user_dict[callback.message.chat.id] = await state.get_data()
    description_order = user_dict[callback.message.chat.id]['description_order']
    contact_order = user_dict[callback.message.chat.id]['contact_order']
    title_category = get_title_category(id_category=int(callback.data.split('_')[1]))
    await state.update_data(title_category=int(callback.data.split('_')[1]))
    await state.set_state(default_state)
    list_order = get_list_order()
    if len(list_order) == 0:
        number_order = 0
    else:
        number_order = list_order[0][0]
    await callback.message.edit_text(text=f'Заявка № {number_order}.\n'
                                          f'Категория: {title_category}\n'
                                          f'Описание: {description_order}\n'
                                          f'Контакты: {contact_order}',
                                     reply_markup=keyboard_mailer_order(),
                                     parse_mode='html')


@router.callback_query(F.data == 'order_cancel')
async def process_order_cancel(callback: CallbackQuery, bot: Bot):
    """
    Отмена рассылки созданной заявки
    :param callback:
    :param bot:
    :return:
    """
    logging.info(f'process_order_cancel: {callback.message.chat.id}')
    await bot.delete_message(chat_id=callback.message.chat.id,
                             message_id=callback.message.message_id)
    await callback.answer(text='Рассылка заявки отменена')


@router.callback_query(F.data == 'order_mailer')
async def order_mailer(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    """
    Запуск рассылки заявки по списку исполнителей согласно рейтингу
    :param callback:
    :param state:
    :return:
    """
    logging.info(f'process_forward: {callback.message.chat.id}')
    await bot.delete_message(chat_id=callback.message.chat.id,
                             message_id=callback.message.message_id)
    current_date = datetime.now()
    time_game = current_date.strftime('%d/%m/%Y')
    user_dict[callback.message.chat.id] = await state.update_data()
    description_order = user_dict[callback.message.chat.id]['description_order']
    contact_order = user_dict[callback.message.chat.id]['contact_order']
    title_category = user_dict[callback.message.chat.id]['title_category']
    add_order(time_order=time_game,
              description_order=description_order,
              contact_order=contact_order,
              category=title_category,
              mailer_order='none',
              status='minute',
              id_user=0,
              amount=0,
              report='none')
    await process_mailer(bot=bot)


async def process_mailer(bot: Bot):
    # id INTEGER, telegram_id INTEGER, username TEXT, is_admin INTEGER, list_category TEXT, rating INTEGER
    # получаем список пользователей для рассылки
    list_mailer = get_list_notadmins_mailer()
    # сортируем его по рейтингу
    list_sorted_user = sorted(list_mailer, key=lambda mailer: mailer[5], reverse=True)
    print(list_sorted_user)
    # id INTEGER, time_order TEXT, description_order TEXT, contact_order TEXT, category INTEGER, mailer_order TEXT, status TEXT, id_user, INTEGER, amount INTEGER
    # получаем список заявок
    list_order = get_list_order()
    # 1 - проходим по списку заявок
    for order in list_order:
        # если заявка находится на стадии досыльных сообщений пользователю то не запускаем рассылку
        if order[6] == 'one_minute':
            continue
        # если исполнителен не определен, то продолжаем рассылку
        info_order = get_order_id(id_order=order[0])
        if info_order[7] == 0:
            # получаем список пользователей кому уже была произведена рассылка
            mailer_order = order[5]
            if mailer_order == 'none':
                mailer_list = []
            else:
                if ',' in mailer_order:
                    mailer_list = map(int, mailer_order.split(','))
                else:
                    mailer_list = [int(mailer_order)]
            # проходим по отсортированному по рейтингу в порядке его убывания списку пользователей
            for user in list_sorted_user:
                # получаем допустимые категории для пользователя
                categorys = user[4]
                if categorys == '0':
                    category_list = []
                else:
                    if ',' in categorys:
                        category_list = map(int, categorys.split(','))
                    else:
                        category_list = [int(categorys)]
                # если пользователю еще не рассылали заявку и список его категорий допустим
                if user[0] not in mailer_list and order[4] in category_list:
                    result = get_telegram_user(user_id=user[1], bot_token=config.tg_bot.token)
                    msg1, msg2, msg3 = 0, 0, 0
                    # ПЕРВОЕ СООБЩЕНИЕ
                    # если пользователь не заблокировал бота
                    if 'result' in result:
                        set_status_order(id_order=order[0], status='one_minute')
                        # отправляем ему сообщение
                        msg1 = await bot.send_message(chat_id=user[1],
                                                      text=f'Поступила заявка\n'
                                                           f'Заявка № {order[0]}.\n'
                                                           f'Категория: {order[4]}\n'
                                                           f'Описание: {order[2]}\n',
                                                      reply_markup=keyboard_get_order(id_order=order[0]))
                        # обновляем список рассылки заявки
                        mailer_list.append(user[0])
                        if len(mailer_list) == 1:
                            set_mailer_order(id_order=order[0],
                                             mailer_order=str(mailer_list[0]))
                        else:
                            mailer_order = ','.join(map(str, mailer_list))
                            set_mailer_order(id_order=order[0],
                                             mailer_order=mailer_order)

                    await asyncio.sleep(1*60)
                    info_order = get_order_id(id_order=order[0])
                    print(info_order)
                    if info_order[7] == 0 and not info_order[6] == 'three_minute':
                        if 'result' in result:
                            await bot.delete_message(chat_id=user[1],
                                                     message_id=msg1.message_id)
                            # отправляем ему сообщение
                            msg2 = await bot.send_message(chat_id=user[1],
                                                          text=f'У вас еще есть шанс взять заявку\n'
                                                               f'Заявка № {order[0]}.\n'
                                                               f'Категория: {order[4]}\n'
                                                               f'Описание: {order[2]}\n',
                                                          reply_markup=keyboard_get_order(id_order=order[0]))
                    else:
                        return

                    await asyncio.sleep(1 * 60)
                    info_order = get_order_id(id_order=order[0])
                    if info_order[7] == 0 and not info_order[6] == 'three_minute':
                        if 'result' in result:
                            await bot.delete_message(chat_id=user[1],
                                                     message_id=msg2.message_id)
                            # отправляем ему сообщение
                            msg3 = await bot.send_message(chat_id=user[1],
                                                          text=f'Последняя попытка взять заказ\n'
                                                               f'Заявка № {order[0]}.\n'
                                                               f'Категория: {order[4]}\n'
                                                               f'Описание: {order[2]}\n',
                                                          reply_markup=keyboard_get_order(id_order=order[0]))
                    else:
                        return
                    await asyncio.sleep(1 * 60)
                    info_order = get_order_id(id_order=order[0])
                    if info_order[7] == 0 and not info_order[6] == 'three_minute':
                        if 'result' in result:
                            await bot.delete_message(chat_id=user[1],
                                                     message_id=msg3.message_id)
                            set_status_order(id_order=order[0], status='three_minute')
                    else:
                        return


@router.callback_query(F.data.startswith('getorder_cancel_'))
async def getorder_cancel(callback: CallbackQuery, bot: Bot) -> None:
    logging.info(f'process_forward: {callback.message.chat.id}')
    # удаляем сообщение у пользователя
    await bot.delete_message(chat_id=callback.message.chat.id,
                             message_id=callback.message.message_id)
    # получаем номер заказа из callback_data
    id_order = int(callback.data.split('_')[2])
    # обновляем статус заявки, для запуска рассылки другим пользователям
    set_status_order(id_order=id_order, status='three_minute')
    # получаем список супер-админов для информирования
    list_super_admin = config.tg_bot.admin_ids.split(',')
    # производим рассылку информационного сообщения
    for id_superadmin in list_super_admin:
        result = get_telegram_user(user_id=int(id_superadmin),
                                   bot_token=config.tg_bot.token)
        if 'result' in result:
            await bot.send_message(chat_id=int(id_superadmin),
                                   text=f'Пользователь {callback.from_user.username} отказался от'
                                        f' выполнения заявки № {id_order}')
    await process_mailer(bot=bot)


@router.callback_query(F.data.startswith('getorder_confirm_'))
async def getorder_confirm(callback: CallbackQuery, bot: Bot) -> None:
    logging.info(f'getorder_confirm: {callback.message.chat.id}')
    # удаляем сообщение у пользователя
    await bot.delete_message(chat_id=callback.message.chat.id,
                             message_id=callback.message.message_id)
    # id заявки в базе данных
    id_order = int(callback.data.split('_')[2])
    # изменяем статус заявки
    set_status_order(id_order=id_order,
                     status='в работе')
    # устанавливаем исполнителя
    set_user_order(id_order=id_order,
                   id_user=callback.message.chat.id)
    # производим рассылку супер админам
    list_super_admin = config.tg_bot.admin_ids.split(',')
    for id_superadmin in list_super_admin:
        result = get_telegram_user(user_id=int(id_superadmin),
                                   bot_token=config.tg_bot.token)
        if 'result' in result:
            await bot.send_message(chat_id=int(id_superadmin),
                                   text=f'Пользователь {callback.from_user.username} взял'
                                        f' заявку № {id_order}')
    # получаем информацию о заказе
    info_order = get_order_id(id_order=id_order)
    await callback.message.answer(text=f'Вы взяли в работу заявку № {id_order}.\n'
                                       f'Описание: {info_order[2]}\n'
                                       f'Контакты: {info_order[3]}')