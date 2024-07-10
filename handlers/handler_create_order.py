import asyncio

from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from aiogram.fsm.state import State, StatesGroup, default_state

from filter.admin_filter import check_admin
from config_data.config import Config, load_config
from keyboards.keyboards_create_order import keyboards_set_category, keyboard_mailer_order, keyboard_get_order, keyboard_contract, keyboard_reassert_contract
from module.data_base import get_list_order, get_list_notadmins_mailer, get_list_category, get_title_category,\
    create_table_order, add_order, create_table_category, set_mailer_order, set_status_order, set_user_order,\
    get_order_id, get_list_users, get_list_order_id_not_complete, get_info_user, set_id_cancel_order

import logging
import requests
from datetime import datetime, date

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


@router.message(F.text == 'Создать заявку')
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
    Получение контактных данных заявки и формирование клавиатуры для выбора категории заявки
    :param message: message.text контакты заявки
    :param state:
    :return:
    """
    logging.info(f'get_contact_order: {message.chat.id}')
    await state.update_data(contact_order=message.text)
    list_category = get_list_category()
    keyboard = keyboards_set_category(list_category=list_category,
                                      back=0,
                                      forward=2,
                                      count=6)
    await message.answer(text='Выберите категорию заявки',
                         reply_markup=keyboard)


# >>>>
@router.callback_query(F.data.startswith('setforward'))
async def process_setforward(callback: CallbackQuery) -> None:
    """
    Действие на пагинацию вперед >>, если в блоке недостаточно места для всех категорий
    :param callback:
    :return:
    """
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
    """
    Действие на пагинацию назад <<, если в блоке недостаточно места для всех категорий
    :param callback:
    :return:
    """
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
    """
    Выбор категории для созданной заявки
    :param callback:
    :param state:
    :return:
    """
    logging.info(f'process_setcategory: {callback.message.chat.id}')
    user_dict[callback.message.chat.id] = await state.get_data()
    description_order = user_dict[callback.message.chat.id]['description_order']
    contact_order = user_dict[callback.message.chat.id]['contact_order']
    title_category = get_title_category(id_category=int(callback.data.split('_')[1]))
    await state.update_data(title_category=int(callback.data.split('_')[1]))
    await state.set_state(default_state)
    list_order = get_list_order()
    if len(list_order) == 0:
        number_order = 1
    else:
        number_order = list_order[-1][0] + 1
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
    logging.info(f'order_mailer: {callback.message.chat.id}')
    await bot.delete_message(chat_id=callback.message.chat.id,
                             message_id=callback.message.message_id)
    current_date = datetime.now()
    time_game = current_date.strftime('%d/%m/%Y')
    user_dict[callback.message.chat.id] = await state.update_data()
    description_order = user_dict[callback.message.chat.id]['description_order']
    contact_order = user_dict[callback.message.chat.id]['contact_order']
    title_category = user_dict[callback.message.chat.id]['title_category']
    add_order(time_order=time_game,
              id_creator=callback.message.chat.id,
              description_order=description_order,
              contact_order=contact_order,
              category=title_category,
              mailer_order='none',
              status='minute',
              id_user=0,
              amount=0,
              report='none',
              cancel_id='0,0',
              comment='none')
    await callback.message.answer(text=f'Рассылка заявки запущена. Ожидайте изменения статуса заявки.')
    await process_mailer(bot=bot)


async def process_mailer(bot: Bot):
    """
    Рассылка заявки по списку пользователей
    :param bot:
    :return:
    """
    logging.info('process_mailer')
    # id INTEGER, telegram_id INTEGER, username TEXT, is_admin INTEGER, list_category TEXT, rating INTEGER
    # получаем список пользователей для рассылки
    #             id INTEGER PRIMARY KEY,
    #             telegram_id INTEGER,
    #             username TEXT,
    #             is_admin INTEGER,
    #             list_category TEXT,
    #             rating INTEGER
    list_mailer = get_list_users()
    # сортируем его по рейтингу
    list_sorted_user = sorted(list_mailer, key=lambda mailer: mailer[5], reverse=True)
    # получаем список заявок c конца
    list_order = get_list_order()[::-1]
    # 1 - проходим по списку заявок
    for order in list_order:
        print(232, order)
        # если заявка находится на стадии досыльных сообщений пользователю то не запускаем рассылку
        if order[7] == 'one_minute':
            continue
        # если исполнителен для заявки не определен, то продолжаем рассылку
        # id INTEGER PRIMARY KEY,
        #             time_order TEXT,
        #             id_creator INTEGER,
        #             description_order TEXT,
        #             contact_order TEXT,
        #             category INTEGER,
        #             mailer_order TEXT,
        #             status TEXT,
        #             id_user INTEGER,
        #             amount INTEGER,
        #             report TEXT
        info_order = get_order_id(id_order=order[0])
        current_date = datetime.now().strftime('%d/%m/%Y')
        list_current_date = list(map(int, current_date.split('/')))
        current_date = date(list_current_date[2], list_current_date[1], list_current_date[0])
        list_date_order = list(map(int, info_order[1].split('/')))
        date_order = date(list_date_order[2], list_date_order[1], list_date_order[0])
        # если исполнитель еще не определен и заявке не более суток
        if info_order[8] == 0 and current_date == date_order:
            # получаем список пользователей кому уже была произведена рассылка
            mailer_order = order[6]
            if mailer_order == 'none':
                mailer_list = []
            else:
                if ',' in mailer_order:
                    mailer_list = list(map(int, mailer_order.split(',')))
                else:
                    mailer_list = [int(mailer_order)]
            # проходим по отсортированному по рейтингу в порядке его убывания списку пользователей
            for user in list_sorted_user:
                # проверяем количество заявок в работе и что получатель не супер-админ
                list_order_id_not_complete = get_list_order_id_not_complete(id_user=user[1])
                list_super_admin = config.tg_bot.admin_ids.split(',')
                result = get_telegram_user(user_id=user[1], bot_token=config.tg_bot.token)
                if len(list_order_id_not_complete) >= 5 or\
                        user[1] in map(int, list_super_admin) or\
                        'result' not in result or\
                        user[1] == order[2]:
                    # print(len(list_order_id_not_complete) >= 2, user[1] in map(int, list_super_admin))
                    continue
                # получаем допустимые категории для пользователя
                categorys = user[4]
                if categorys == '0':
                    category_list = []
                else:
                    if ',' in categorys:
                        category_list = list(map(int, categorys.split(',')))
                    else:
                        category_list = [int(categorys)]
                # print(f'user[0]: {user[0]} mailer_list: {mailer_list} order[4]: {order[5]} category_list: {category_list}\n\n')
                # если пользователю еще не рассылали заявку и список его категорий допустим
                if user[0] not in mailer_list and order[5] in category_list:

                    result = get_telegram_user(user_id=user[1], bot_token=config.tg_bot.token)
                    msg1, msg2, msg3 = 0, 0, 0
                    # ПЕРВОЕ СООБЩЕНИЕ
                    # если пользователь не заблокировал бота
                    if 'result' in result:
                        set_status_order(id_order=order[0], status='one_minute')
                        title_category = get_title_category(order[5])
                        # отправляем ему сообщение
                        try:
                            msg1 = await bot.send_message(chat_id=user[1],
                                                          text=f'Поступила заявка\n'
                                                               f'Заявка № {order[0]}.\n'
                                                               f'Категория: {title_category}\n'
                                                               f'Описание: {order[3]}\n',
                                                          reply_markup=keyboard_get_order(id_order=order[0]))
                        except:
                            continue
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
                    list_id_cancel = list(map(int, info_order[11].split(',')))
                    # если исполнитель еще не определен и пользователь не отказался от заказа
                    if info_order[8] == 0 and user[0] not in list_id_cancel:
                        if 'result' in result:
                            title_category = get_title_category(order[5])
                            try:
                                await bot.delete_message(chat_id=user[1],
                                                         message_id=msg1.message_id)
                            except:
                                pass
                            # отправляем ему сообщение
                            try:
                                msg2 = await bot.send_message(chat_id=user[1],
                                                              text=f'У вас еще есть шанс взять заявку\n'
                                                                   f'Заявка № {order[0]}.\n'
                                                                   f'Категория: {title_category}\n'
                                                                   f'Описание: {order[3]}\n',
                                                              reply_markup=keyboard_get_order(id_order=order[0]))
                            except:
                                pass
                    else:
                        return

                    await asyncio.sleep(1 * 60)
                    info_order = get_order_id(id_order=order[0])
                    # если пользователь еще не определен
                    list_id_cancel = list(map(int, info_order[11].split(',')))
                    # если исполнитель еще не определен и пользователь не отказался от заказа
                    if info_order[8] == 0 and user[0] not in list_id_cancel:
                        if 'result' in result:
                            title_category = get_title_category(order[5])
                            try:
                                await bot.delete_message(chat_id=user[1],
                                                         message_id=msg2.message_id)
                            except:
                                pass
                            # отправляем ему сообщение
                            try:
                                msg3 = await bot.send_message(chat_id=user[1],
                                                              text=f'Последняя попытка взять заказ\n'
                                                                   f'Заявка № {order[0]}.\n'
                                                                   f'Категория: {title_category}\n'
                                                                   f'Описание: {order[3]}\n',
                                                              reply_markup=keyboard_get_order(id_order=order[0]))
                            except:
                                pass
                    else:
                        return
                    await asyncio.sleep(1 * 60)
                    info_order = get_order_id(id_order=order[0])
                    list_id_cancel = list(map(int, info_order[11].split(',')))
                    # если исполнитель еще не определен и пользователь не отказался от заказа
                    if info_order[8] == 0 and user[0] not in list_id_cancel:
                        if 'result' in result:
                            try:
                                await bot.delete_message(chat_id=user[1],
                                                         message_id=msg3.message_id)
                            except:
                                pass
                            set_status_order(id_order=order[0], status='three_minute')
                    else:
                        return
                else:
                    # переходим к следующему пользователю если этому уже производилась рассылка
                    continue


@router.callback_query(F.data.startswith('getorder_cancel_'))
async def getorder_cancel(callback: CallbackQuery, bot: Bot) -> None:
    logging.info(f'process_forward: {callback.message.chat.id}')
    # удаляем сообщение у пользователя
    try:
        await bot.delete_message(chat_id=callback.message.chat.id,
                                 message_id=callback.message.message_id)
    except:
        pass
    # получаем номер заказа из callback_data
    id_order = int(callback.data.split('_')[2])
    # обновляем статус заявки, для запуска рассылки другим пользователям
    set_status_order(id_order=id_order, status='three_minute')
    # получаем список супер-админов для информирования
    list_super_admin = config.tg_bot.admin_ids.split(',')
    info_order = get_order_id(id_order=id_order)

    # производим рассылку информационного сообщения
    for id_superadmin in list_super_admin:
        result = get_telegram_user(user_id=int(id_superadmin),
                                   bot_token=config.tg_bot.token)
        if 'result' in result:
            await bot.send_message(chat_id=int(id_superadmin),
                                   text=f'Пользователь {callback.from_user.username} отказался от'
                                        f' выполнения заявки № {id_order}\n\n'
                                        f'Номер телефона мастера {callback.from_user.username}:'
                                        f' {get_info_user(callback.message.chat.id)[-1]}\n'
                                        f'Информация о заявке № {id_order}:\n'
                                        f'Дата заявки: {info_order[1]}\n'
                                        f'Создатель заявки: @{get_info_user(info_order[2])[2]}-{get_info_user(info_order[2])[1]}\n'
                                        f'Описание заявки: {info_order[3]}\n'
                                        f'Контакты клиента: {info_order[4]}\n'
                                        f'Категория заявки: {info_order[5]}\n'
                                        f'Статус заявки: {info_order[7]}\n'
                                        f'Исполнитель заявки: @{get_info_user(info_order[8])[2]}-{get_info_user(info_order[8])[1]}\n'
                                        f'Стоимость заявки: {info_order[9]}')
    #         id INTEGER PRIMARY KEY,
    #         time_order TEXT,
    #         id_creator INTEGER,
    #         description_order TEXT,
    #         contact_order TEXT,
    #         category INTEGER,
    #         mailer_order TEXT,
    #         status TEXT,
    #         id_user INTEGER,
    #         amount INTEGER,
    #         report TEXT

    # id_cancel_str = info_order[11]
    # list_id_cancel = id_cancel_str.split(',')
    # print("list_id_cancel",list_id_cancel)
    list_id_cancel = list(map(int, info_order[11].split(',')))
    info_user = get_info_user(telegram_id=callback.message.chat.id)
    list_id_cancel.append(info_user[0])
    set_id_cancel_order(id_order=id_order, cancel_id=','.join(map(str, list_id_cancel)))
    result = get_telegram_user(user_id=info_order[2],
                               bot_token=config.tg_bot.token)
    if 'result' in result and info_order[2] not in map(int, list_super_admin):
        await bot.send_message(chat_id=info_order[2],
                               text=f'Пользователь {callback.from_user.username} отказался от'
                                    f' выполнения заявки № {id_order}.')
    # print(f'Пользователь {callback.from_user.username} отказался от выполнения заявки № {id_order}')
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
                     status='in_progress')
    # устанавливаем исполнителя
    set_user_order(id_order=id_order,
                   id_user=callback.message.chat.id)
    # производим рассылку супер админам
    list_super_admin = config.tg_bot.admin_ids.split(',')
    info_order = get_order_id(id_order=id_order)

    for id_superadmin in list_super_admin:
        result = get_telegram_user(user_id=int(id_superadmin),
                                   bot_token=config.tg_bot.token)
        if 'result' in result:
            await bot.send_message(chat_id=int(id_superadmin),
                                   text=f'Пользователь {callback.from_user.username} взял'
                                        f' заявку № {id_order}\n\n'
                                        f'Номер телефона мастера {callback.from_user.username}:'
                                        f' {get_info_user(callback.message.chat.id)[-1]}\n'
                                        f'Информация о заявке № {id_order}:\n'
                                        f'Дата заявки: {info_order[1]}\n'
                                        f'Создатель заявки: @{get_info_user(info_order[2])[2]}-{get_info_user(info_order[2])[1]}\n'
                                        f'Описание заявки: {info_order[3]}\n'
                                        f'Контакты клиента: {info_order[4]}\n'
                                        f'Категория заявки: {info_order[5]}\n'
                                        f'Статус заявки: {info_order[7]}\n'
                                        f'Исполнитель заявки: @{get_info_user(info_order[8])[2]}-{get_info_user(info_order[8])[1]}\n'
                                        f'Стоимость заявки: {info_order[9]}')

    result = get_telegram_user(user_id=info_order[2],
                               bot_token=config.tg_bot.token)
    if 'result' in result and info_order[2] not in map(int, list_super_admin):
        await bot.send_message(chat_id=info_order[2],
                               text=f'Пользователь {callback.from_user.username} взял'
                                    f' заявку № {id_order}.')
    # получаем информацию о заказе
    info_order = get_order_id(id_order=id_order)
    title_category = get_title_category(info_order[5])
    msg = await callback.message.answer(text=f'Вы взяли в работу заявку № {id_order}.\n'
                                             f'Категория:{title_category}\n'
                                             f'Описание: {info_order[3]}\n'
                                             f'Контакты: {info_order[4]}\n\n'
                                             f'Если не договорились с клиентом то обязательно нажмите'
                                             f' "НЕ договорились".\n\n'
                                             f'Для внесения информации о ходе выполнения заявки и для ее закрытия'
                                             f' воспользуйтесь кнопкой "Заявки" в главном меню',
                                        reply_markup=keyboard_contract(id_order=id_order))
    # время
    await asyncio.sleep(60 * 10)
    info_order = get_order_id(id_order=id_order)
    status = info_order[7]
    logging.debug(f'{info_order}')
    if status != 'yes_contract':
        try:
            await bot.delete_message(chat_id=callback.message.chat.id,
                                     message_id=msg.message_id)
        except:
            pass
        await callback.message.answer(text=f'Вы не успели подтвердить заказ № {info_order[0]}!')

        # производим рассылку супер админам
        list_super_admin = config.tg_bot.admin_ids.split(',')
        info_order = get_order_id(id_order=id_order)

        for id_superadmin in list_super_admin:
            result = get_telegram_user(user_id=int(id_superadmin),
                                       bot_token=config.tg_bot.token)
            if 'result' in result:
                await bot.send_message(chat_id=int(id_superadmin),
                                       text=f'Пользователь {callback.from_user.username} не успел подтвердить заказ'
                                            f' № {id_order}. Заказ запущен на повторную рассылку.\n\n'
                                            f'Номер телефона мастера {callback.from_user.username}:'
                                            f' {get_info_user(callback.message.chat.id)[-1]}\n'
                                            f'Информация о заявке № {id_order}:\n'
                                            f'Дата заявки: {info_order[1]}\n'
                                            f'Создатель заявки: @{get_info_user(info_order[2])[2]}-{get_info_user(info_order[2])[1]}\n'
                                            f'Описание заявки: {info_order[3]}\n'
                                            f'Контакты клиента: {info_order[4]}\n'
                                            f'Категория заявки: {info_order[5]}\n'
                                            f'Статус заявки: {info_order[7]}\n'
                                            f'Исполнитель заявки: @{get_info_user(info_order[8])[2]}-{get_info_user(info_order[8])[1]}\n'
                                            f'Стоимость заявки: {info_order[9]}')

        result = get_telegram_user(user_id=info_order[2],
                                   bot_token=config.tg_bot.token)
        if 'result' in result and info_order[2] not in map(int, list_super_admin):
            await bot.send_message(chat_id=info_order[2],
                                   text=f'Пользователь {callback.from_user.username} не успел подтвердить заказ'
                                        f' № {id_order}. Заказ запущен на повторную рассылку.')
        # устанавливаем исполнителя
        set_user_order(id_order=id_order,
                       id_user=0)
        await process_mailer(bot=bot)


@router.callback_query(F.data.startswith('contract'))
async def getorder_contract(callback: CallbackQuery, bot: Bot) -> None:
    """
    Подтверждение того что пользователь Договорился или НЕ Договорился
    :param callback:
    :param bot:
    :return:
    """
    logging.info(f'getorder_contract: {callback.message.chat.id}')
    # ответ пользователя
    contract = callback.data.split('_')
    # на какой заказ ответил пользователь
    id_order = int(contract[2])
    # если пользователь не договорился
    if contract[1] == 'cancel':
        # # обновляем статус
        set_status_order(id_order=id_order,
                         status='not_contract')
        # # обнуляем исполнителя
        # set_user_order(id_order=id_order,
        #                id_user=0)

        # производим рассылку супер админам
        list_super_admin = config.tg_bot.admin_ids.split(',')
        info_order = get_order_id(id_order=id_order)
        for id_superadmin in list_super_admin:
            result = get_telegram_user(user_id=int(id_superadmin),
                                       bot_token=config.tg_bot.token)
            if 'result' in result:
                info_user = get_info_user(telegram_id=callback.message.chat.id)
                await bot.send_message(chat_id=int(id_superadmin),
                                       text=f'Пользователь {callback.from_user.username} (тел: {info_user[-1]}) не договорился по'
                                            f' заявке № {id_order}.\n\n'
                                            f'Номер телефона мастера {callback.from_user.username}:'
                                            f' {get_info_user(callback.message.chat.id)[-1]}\n'
                                            f'Информация о заявке № {id_order}:\n'
                                            f'Дата заявки: {info_order[1]}\n'
                                            f'Создатель заявки: @{get_info_user(info_order[2])[2]}-{get_info_user(info_order[2])[1]}\n'
                                            f'Описание заявки: {info_order[3]}\n'
                                            f'Контакты клиента: {info_order[4]}\n'
                                            f'Категория заявки: {info_order[5]}\n'
                                            f'Статус заявки: {info_order[7]}\n'
                                            f'Исполнитель заявки: @{get_info_user(info_order[8])[2]}-{get_info_user(info_order[8])[1]}\n'
                                            f'Стоимость заявки: {info_order[9]}\n\n'
                                            f'Заявка запущена на рассылку')
                                       # reply_markup=keyboard_reassert_contract(id_order=id_order,
                                       #                                         id_telegram=callback.message.chat.id,
                                       #                                         message_id=callback.message.message_id))
        # производим рассылку создателю заявки
        result = get_telegram_user(user_id=info_order[2],
                                   bot_token=config.tg_bot.token)
        if 'result' in result and info_order[2] not in map(int, list_super_admin):
            await bot.send_message(chat_id=info_order[2],
                                   text=f'Пользователь {callback.from_user.username} не договорился по'
                                        f' заявке № {id_order}.')
        await bot.delete_message(chat_id=callback.message.chat.id,
                                 message_id=callback.message.message_id)
        # удаляем исполнителя заказа
        set_user_order(id_order=id_order,
                       id_user=0)
        await process_mailer(bot=bot)
        await callback.message.answer(text=f"Заявка снята с вас и передана другим мастерам")

    elif contract[1] == 'confirm':
        # обновляем статус
        set_status_order(id_order=id_order,
                         status='yes_contract')
        # производим рассылку супер админам
        list_super_admin = config.tg_bot.admin_ids.split(',')
        info_order = get_order_id(id_order=id_order)

        for id_superadmin in list_super_admin:
            result = get_telegram_user(user_id=int(id_superadmin),
                                       bot_token=config.tg_bot.token)
            if 'result' in result:
                await bot.send_message(chat_id=int(id_superadmin),
                                       text=f'Пользователь {callback.from_user.username} договорился по'
                                            f' заявке № {id_order}.\n\n'
                                            f'Номер телефона мастера {callback.from_user.username}:'
                                            f' {get_info_user(callback.message.chat.id)[-1]}\n'
                                            f'Информация о заявке № {id_order}:\n'
                                            f'Дата заявки: {info_order[1]}\n'
                                            f'Создатель заявки: @{get_info_user(info_order[2])[2]}-{get_info_user(info_order[2])[1]}\n'
                                            f'Описание заявки: {info_order[3]}\n'
                                            f'Контакты клиента: {info_order[4]}\n'
                                            f'Категория заявки: {info_order[5]}\n'
                                            f'Статус заявки: {info_order[7]}\n'
                                            f'Исполнитель заявки: @{get_info_user(info_order[8])[2]}-{get_info_user(info_order[8])[1]}\n'
                                            f'Стоимость заявки: {info_order[9]}')

        result = get_telegram_user(user_id=info_order[2],
                                   bot_token=config.tg_bot.token)
        if 'result' in result and info_order[2] not in map(int, list_super_admin):
            try:
                await bot.send_message(chat_id=info_order[2],
                                       text=f'Пользователь {callback.from_user.username} договорился по'
                                            f' заявке № {id_order}.')
            except:
                pass
        await bot.delete_message(chat_id=callback.message.chat.id,
                                 message_id=callback.message.message_id)
        await callback.message.answer(text=f'Для внесения информации о ходе выполнения заявки и для ее закрытия'
                                           f' воспользуйтесь кнопкой "Заявки" в главном меню')


@router.callback_query(F.data.startswith('reassert'))
async def process_reassert(callback: CallbackQuery, bot: Bot) -> None:
    logging.info(f'process_reassert: {callback.message.chat.id}')
    info_callback = callback.data.split('_')
    print(callback.data)
    if "cancel" in info_callback[0]:
        # обновляем статус
        set_status_order(id_order=int(info_callback[1]),
                         status='not_contract')
        # обнуляем исполнителя
        set_user_order(id_order=int(info_callback[1]),
                       id_user=0)
        await bot.delete_message(chat_id=int(info_callback[2]),
                                 message_id=int(info_callback[3]))
        await bot.delete_message(chat_id=callback.message.chat.id,
                                 message_id=callback.message.message_id)
        await bot.send_message(chat_id=int(info_callback[2]),
                               text='Информация подтверждена, заявка с вас снята')
        await callback.answer(text='Информация подтверждена, заявка снята с пользователя')
        await process_mailer(bot=bot)
    else:
        await bot.send_message(chat_id=int(info_callback[2]),
                               text='Информация не подтверждена')
        await bot.delete_message(chat_id=callback.message.chat.id,
                                 message_id=callback.message.message_id)
        await callback.answer(text='Информация не подтверждена, заявка осталась у пользователя')