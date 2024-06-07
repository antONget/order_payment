from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup, default_state
from aiogram.filters import StateFilter
from aiogram.filters.callback_data import CallbackData
import aiogram_calendar

from module.data_base import get_info_user, get_list_order_id, set_status_order, set_report_order, set_amount_order,\
    get_order_id, get_list_order, set_comment_order, get_list_order_id_complete, set_rating
from keyboards.keyboard_order import keyboard_order_in_process, keyboard_order, keyboard_change_status_order, \
    keyboard_payment, keyboard_comment
from services.stat_exel import list_sales_to_exel
from services.payments import create_payment, check_payment

from config_data.config import Config, load_config

from datetime import datetime
from datetime import date
import requests
import logging

router = Router()
config: Config = load_config()


class Tasks(StatesGroup):
    period_start = State()
    period_finish = State()
    comment = State()
    report = State()
    amount = State()


user_dict = {}


def get_telegram_user(user_id, bot_token):
    """
    Проверка возможности отправки сообщения, на случай если пользователь заблокировал бота
    :param user_id:
    :param bot_token:
    :return:
    """
    url = f'https://api.telegram.org/bot{bot_token}/getChat'
    data = {'chat_id': user_id}
    response = requests.post(url, data=data)
    return response.json()


# <editor-fold desc = "СЕКЦИЯ (main keyboard -> [Отчет]">
# main keyboard -> [Отчет]
@router.message(F.text == 'Заявки')
async def process_order(message: Message) -> None:
    """
    Нажата кнопка "Заявки" -> [Выполненные], [В работе]
    :param message:
    :return:
    """
    logging.info(f'process_order: {message.chat.id}')
    await message.answer(text=f'Выберите заявку',
                         reply_markup=keyboard_order())


# календарь
@router.callback_query(F.data == 'completed_tasks')
async def process_buttons_press_start(callback: CallbackQuery, state: FSMContext):
    logging.info(f'process_buttons_press_start: {callback.message.chat.id}')
    calendar = aiogram_calendar.SimpleCalendar(show_alerts=True)
    calendar.set_dates_range(datetime(2024, 1, 1), datetime(2030, 12, 31))
    # получаем текущую дату
    current_date = datetime.now()
    # преобразуем ее в строку
    date1 = current_date.strftime('%m/%d/%y')
    # преобразуем дату в список
    list_date1 = date1.split('/')
    await callback.message.answer(
        "Выберите начало периода, для получения отчета:",
        reply_markup=await calendar.start_calendar(year=int('20'+list_date1[2]), month=int(list_date1[0]))
    )
    await state.set_state(Tasks.period_start)


async def process_buttons_press_finish(callback: CallbackQuery, state: FSMContext):
    logging.info(f'process_buttons_press_finish: {callback.message.chat.id}')
    calendar = aiogram_calendar.SimpleCalendar(show_alerts=True)
    calendar.set_dates_range(datetime(2024, 1, 1), datetime(2028, 12, 31))
    # получаем текущую дату
    current_date = datetime.now()
    # преобразуем ее в строку
    date1 = current_date.strftime('%m/%d/%y')
    # преобразуем дату в список
    list_date1 = date1.split('/')
    await callback.message.answer(
        "Выберите конец периода, для получения отчета:",
        reply_markup=await calendar.start_calendar(year=int('20'+list_date1[2]), month=int(list_date1[0]))
    )
    await state.set_state(Tasks.period_finish)


@router.callback_query(aiogram_calendar.SimpleCalendarCallback.filter(), StateFilter(Tasks.period_start))
async def process_simple_calendar_start(callback_query: CallbackQuery, callback_data: CallbackData, state: FSMContext):
    logging.info(f'process_simple_calendar_start: {callback_query.message.chat.id}')
    calendar = aiogram_calendar.SimpleCalendar(show_alerts=True)
    calendar.set_dates_range(datetime(2022, 1, 1), datetime(2025, 12, 31))
    selected, date = await calendar.process_selection(callback_query, callback_data)
    if selected:
        await callback_query.message.edit_text(
            f'Начало периода {date.strftime("%d/%m/%y")}')
        await state.update_data(period_start=date.strftime("%d/%m/%Y"))
        await process_buttons_press_finish(callback_query, state=state)


@router.callback_query(aiogram_calendar.SimpleCalendarCallback.filter(), StateFilter(Tasks.period_finish))
async def process_simple_calendar_finish(callback: CallbackQuery, callback_data: CallbackData, state: FSMContext):
    logging.info(f'process_simple_calendar_finish: {callback.message.chat.id}')
    calendar = aiogram_calendar.SimpleCalendar(show_alerts=True)
    calendar.set_dates_range(datetime(2022, 1, 1), datetime(2025, 12, 31))
    selected, data = await calendar.process_selection(callback, callback_data)
    if selected:
        await callback.message.edit_text(
            f'Конец периода {data.strftime("%d/%m/%y")}')
        await state.update_data(period_finish=data.strftime("%d/%m/%Y"))
        await state.set_state(default_state)
        # информация о пользователе
        info_user = get_info_user(telegram_id=callback.message.chat.id)
        admin_list = list(map(int, config.tg_bot.admin_ids.split(',')))
        # если запрос делает админ
        if callback.message.chat.id in admin_list:
            list_order_id = get_list_order()
        else:
            # данные о заказах пользователя
            list_order_id = get_list_order_id(id_user=callback.message.chat.id)
        # список для отфильтрованных заказов по дате
        filter_order_data = []
        user_dict[callback.message.chat.id] = await state.get_data()
        period_start_str = user_dict[callback.message.chat.id]['period_start']
        period_finish_str = user_dict[callback.message.chat.id]['period_finish']
        period_start_list = period_start_str.split('/')
        period_finish_list = period_finish_str.split('/')
        # print(period_start_list, period_finish_list)
        # test = date(2024, 5, 7)
        # print(test)
        data_start = date(int(period_start_list[2]), int(period_start_list[1]), int(period_start_list[0]))
        data_finish = date(int(period_finish_list[2]), int(period_finish_list[1]), int(period_finish_list[0]))
        for order in list_order_id:
            order_date = order[1].split('/')
            check_date = date(int(order_date[2]), int(order_date[1]), int(order_date[0]))
            print(data_start, check_date, data_finish)
            if data_start <= check_date <= data_finish and order[7] == 'complete':
                filter_order_data.append(order)
        if len(filter_order_data):
            list_sales_to_exel(list_orders=filter_order_data)
            file_path = "order.xlsx"  # или "folder/filename.ext"
            await callback.message.answer_document(FSInputFile(file_path))
        else:
            await callback.message.answer(text=f'В период {period_start_str}-{period_finish_str} выполненных'
                                               f' заказов не найдено. Попробуйте изменить период')


@router.callback_query(F.data == 'tasks_in_progress')
async def process_buttons_press_start(callback: CallbackQuery):
    """
    Получение списка не завершенных исполнителем заявок
    :param callback:
    :return:
    """
    logging.info(f'process_buttons_press_start: {callback.message.chat.id}')
    list_super_admin = config.tg_bot.admin_ids.split(',')
    if callback.message.chat.id in map(int, list_super_admin):
        list_order = get_list_order()
        # фильтруем полученный список заявок
        filter_order_status_admin = []
        for order in list_order:
            if not order[7] == 'complete':
                filter_order_status_admin.append(order)
        if len(filter_order_status_admin):
            list_sales_to_exel(list_orders=filter_order_status_admin)
            file_path = "order.xlsx"  # или "folder/filename.ext"
            await callback.message.answer_document(FSInputFile(file_path))
        else:
            await callback.message.answer(text=f'Заказы не найдены')
        return
    # получение списка заявок пользователя
    list_order_id = get_list_order_id(id_user=callback.message.chat.id)
    # фильтруем полученный список заявок
    filter_order_status = []
    for order in list_order_id:
        if not order[7] == 'complete':
            filter_order_status.append(order)
    # если есть завершенные заявки
    if len(filter_order_status):
        text = f'Для изменения статуса заявки выберите нужную заявку!\n' \
               f'У вас в работе:\n'
        for order in filter_order_status:
            text += f'<b>Заявка № {order[0]}.</b>\n' \
                    f'Описание: {order[3]}\n' \
                    f'Контакты: {order[4]}\n'
        await callback.message.answer(text=f'{text}',
                                      reply_markup=keyboard_order_in_process(filter_order_status=filter_order_status),
                                      parse_mode='html')
    else:
        await callback.message.answer(text='Завершенных заявок не найдено')


@router.callback_query(F.data.startswith('processorder'))
async def process_order_change_status(callback: CallbackQuery, state: FSMContext):
    logging.info(f'process_buttons_press_start: {callback.message.chat.id}')
    id_order = int(callback.data.split('_')[1])
    await callback.message.answer(text=f'Выберите статус заказа',
                                  reply_markup=keyboard_change_status_order(id_order=id_order))


@router.callback_query(F.data.startswith('changestatus'))
async def process_order_change_status(callback: CallbackQuery, bot: Bot, state: FSMContext):
    logging.info(f'process_buttons_press_start: {callback.message.chat.id}')
    id_order = int(callback.data.split('_')[2])
    change_status = callback.data.split('_')[1]
    await state.update_data(report_id_order=id_order)
    if change_status == 'inprogress':
        set_status_order(id_order=id_order, status=change_status)
        await callback.answer(text=f'Статус заказа № {id_order} обновлен', show_alert=True)
        # производим рассылку супер админам
        list_super_admin = config.tg_bot.admin_ids.split(',')
        for id_superadmin in list_super_admin:
            result = get_telegram_user(user_id=int(id_superadmin),
                                       bot_token=config.tg_bot.token)
            if 'result' in result:
                await bot.send_message(chat_id=int(id_superadmin),
                                       text=f'Пользователь {callback.from_user.username} изменил статус'
                                            f' заявки № {id_order} на "Согласовано время"')
        info_order = get_order_id(id_order=id_order)
        result = get_telegram_user(user_id=info_order[2],
                                   bot_token=config.tg_bot.token)
        if 'result' in result and info_order[2] not in map(int, list_super_admin):
            await bot.send_message(chat_id=info_order[2],
                                   text=f'Пользователь {callback.from_user.username} изменил статус'
                                        f' заявки № {id_order} на "Согласовано время"')
        await bot.delete_message(chat_id=callback.message.chat.id,
                                 message_id=callback.message.message_id)
    elif change_status == 'comment':
        # set_status_order(id_order=id_order, status=change_status)
        await callback.message.answer(text=f'Пришлите комментарий для заказа № {id_order}')
        await state.set_state(Tasks.comment)
        # # производим рассылку супер админам
        # list_super_admin = config.tg_bot.admin_ids.split(',')
        # for id_superadmin in list_super_admin:
        #     result = get_telegram_user(user_id=int(id_superadmin),
        #                                bot_token=config.tg_bot.token)
        #     if 'result' in result:
        #         await bot.send_message(chat_id=int(id_superadmin),
        #                                text=f'Пользователь {callback.from_user.username} изменил статус'
        #                                     f' заявки № {id_order} на "На объекте"')
        # info_order = get_order_id(id_order=id_order)
        # result = get_telegram_user(user_id=info_order[2],
        #                            bot_token=config.tg_bot.token)
        # if 'result' in result and info_order[2] not in map(int, list_super_admin):
        #     await bot.send_message(chat_id=info_order[2],
        #                            text=f'Пользователь {callback.from_user.username} изменил статус'
        #                                 f' заявки № {id_order} на "На объекте"')
    elif change_status == 'report':
        set_status_order(id_order=id_order, status='preview_report')
        await callback.message.answer(text=f'Пришлите краткий отчет о выполнении заказа № {id_order}')
        # производим рассылку супер админам
        list_super_admin = config.tg_bot.admin_ids.split(',')
        for id_superadmin in list_super_admin:
            result = get_telegram_user(user_id=int(id_superadmin),
                                       bot_token=config.tg_bot.token)
            if 'result' in result:
                await bot.send_message(chat_id=int(id_superadmin),
                                       text=f'Пользователь {callback.from_user.username} выполнил'
                                            f' заявку № {id_order} и готов представить отчет')
        info_order = get_order_id(id_order=id_order)
        result = get_telegram_user(user_id=info_order[2],
                                   bot_token=config.tg_bot.token)
        if 'result' in result and info_order[2] not in map(int, list_super_admin):
            await bot.send_message(chat_id=info_order[2],
                                   text=f'Пользователь {callback.from_user.username} выполнил'
                                        f' заявку № {id_order} и готов представить отчет')
        await state.set_state(Tasks.report)


@router.message(F.text, StateFilter(Tasks.comment))
async def process_get_comment_order(message: Message, state: FSMContext):
    logging.info(f'process_get_comment_order: {message.chat.id}')
    comment = message.text
    await state.update_data(comment=comment)
    user_dict[message.chat.id] = await state.get_data()
    id_order = user_dict[message.chat.id]['report_id_order']
    await message.answer(text=f'Добавить комментарий:\n{comment}\nк заказу № {id_order}',
                         reply_markup=keyboard_comment())


@router.callback_query(F.data == 'comment_add')
async def process_order_comment_add(callback: CallbackQuery, bot: Bot, state: FSMContext):
    logging.info(f'process_order_comment_add: {callback.message.chat.id}')
    user_dict[callback.message.chat.id] = await state.get_data()
    id_order = user_dict[callback.message.chat.id]['report_id_order']
    comment = user_dict[callback.message.chat.id]['comment']
    await bot.delete_message(chat_id=callback.message.chat.id,
                             message_id=callback.message.message_id)
    await callback.answer(text=f'Комментарий к заказу № {id_order} добавлен', show_alert=True)
    list_super_admin = config.tg_bot.admin_ids.split(',')
    for id_superadmin in list_super_admin:
        result = get_telegram_user(user_id=int(id_superadmin),
                                   bot_token=config.tg_bot.token)
        if 'result' in result:
            await bot.send_message(chat_id=int(id_superadmin),
                                   text=f'К заказу № {id_order} добавлен комментарий\n'
                                        f'{comment}')
    info_order = get_order_id(id_order=id_order)
    result = get_telegram_user(user_id=info_order[2],
                               bot_token=config.tg_bot.token)
    if 'result' in result and info_order[2] not in map(int, list_super_admin):
        await bot.send_message(chat_id=info_order[2],
                               text=f'К заказу № {id_order} добавлен комментарий\n'
                                    f'{comment}')
    set_comment_order(id_order=id_order, comment=comment)
    await state.set_state(default_state)


@router.callback_query(F.data == 'comment_cancel')
async def process_order_comment_cancel(callback: CallbackQuery, state: FSMContext, bot: Bot):
    logging.info(f'process_order_comment_cancel: {callback.message.chat.id}')
    await bot.delete_message(chat_id=callback.message.chat.id,
                             message_id=callback.message.message_id)
    user_dict[callback.message.chat.id] = await state.get_data()
    id_order = user_dict[callback.message.chat.id]['report_id_order']
    await callback.answer(text=f'Добавление комментария к заказу № {id_order} отменено', show_alert=True)
    await state.set_state(default_state)


@router.message(F.text, StateFilter(Tasks.report))
async def process_get_report_order(message: Message, bot: Bot, state: FSMContext):
    """
    Ожидание ввода отчета от пользователя
    :param message:
    :param bot:
    :param state:
    :return:
    """
    logging.info(f'process_get_report_order: {message.chat.id}')
    report = message.text
    user_dict[message.chat.id] = await state.get_data()
    id_order = user_dict[message.chat.id]['report_id_order']
    set_report_order(id_order=id_order, report=report)
    # производим рассылку супер админам
    list_super_admin = config.tg_bot.admin_ids.split(',')
    for id_superadmin in list_super_admin:
        result = get_telegram_user(user_id=int(id_superadmin),
                                   bot_token=config.tg_bot.token)
        if 'result' in result:
            await bot.send_message(chat_id=int(id_superadmin),
                                   text=f'Пользователь {message.from_user.username} отправил отчет о выполнении'
                                        f' заявки № {id_order}:\n'
                                        f'{report}')
    info_order = get_order_id(id_order=id_order)
    result = get_telegram_user(user_id=info_order[2],
                               bot_token=config.tg_bot.token)
    if 'result' in result and info_order[2] not in map(int, list_super_admin):
        await bot.send_message(chat_id=info_order[2],
                               text=f'Пользователь {message.from_user.username} отправил отчет о выполнении'
                                    f' заявки № {id_order}:\n'
                                    f'{report}')
    await message.answer(text='Пришлите стоимость выполненной заявки')
    await state.set_state(Tasks.amount)


@router.message(F.text, StateFilter(Tasks.amount), lambda message: message.text.isdigit())
async def process_get_amount_order(message: Message, bot: Bot, state: FSMContext):
    logging.info(f'process_get_amount_order: {message.chat.id}')
    amount = int(message.text)
    user_dict[message.chat.id] = await state.get_data()
    id_order = user_dict[message.chat.id]['report_id_order']
    set_amount_order(id_order=id_order, amount=amount)
    # производим рассылку супер админам
    list_super_admin = config.tg_bot.admin_ids.split(',')
    for id_superadmin in list_super_admin:
        result = get_telegram_user(user_id=int(id_superadmin),
                                   bot_token=config.tg_bot.token)
        if 'result' in result:
            await bot.send_message(chat_id=int(id_superadmin),
                                   text=f'Пользователь {message.from_user.username} выполнил'
                                        f' заявку № {id_order} на сумму {amount}')
    info_order = get_order_id(id_order=id_order)
    result = get_telegram_user(user_id=info_order[2],
                               bot_token=config.tg_bot.token)
    if 'result' in result and info_order[2] not in map(int, list_super_admin):
        await bot.send_message(chat_id=info_order[2],
                               text=f'Пользователь {message.from_user.username} выполнил'
                                    f' заявку № {id_order} на сумму {amount}')
    price_amount = int(amount/2)
    PRICE = f'{price_amount}.00'
    payment_url, payment_id = create_payment(amount=PRICE, chat_id=message.chat.id)
    await message.answer(text=f'Произведите оплату за полученную заявку в размере {price_amount}',
                         reply_markup=keyboard_payment(payment_url=payment_url,
                                                       payment_id=payment_id))
    await state.set_state(default_state)

@router.callback_query(F.data.startswith('payment'))
async def check_handler(callback: CallbackQuery, bot: Bot, state: FSMContext):
    logging.info(f'check_handler: {callback.message.chat.id}-{callback.data.split("_")[1]}')
    payment_id = callback.data.split('_')[1]
    result = check_payment(payment_id)
    if result == 'succeeded':

        user_dict[callback.message.chat.id] = await state.get_data()
        id_order = user_dict[callback.message.chat.id]['report_id_order']
        set_status_order(id_order=id_order, status='complete')
        await callback.message.answer(text=f'Платеж проведен успешно!')
        list_super_admin = config.tg_bot.admin_ids.split(',')
        for id_superadmin in list_super_admin:
            result = get_telegram_user(user_id=int(id_superadmin),
                                       bot_token=config.tg_bot.token)
            if 'result' in result:
                await bot.send_message(chat_id=int(id_superadmin),
                                       text=f'Платеж за заказ № {id_order} проведен успешно!')
        info_order = get_order_id(id_order=id_order)
        result = get_telegram_user(user_id=info_order[2],
                                   bot_token=config.tg_bot.token)
        if 'result' in result and info_order[2] not in map(int, list_super_admin):
            await bot.send_message(chat_id=info_order[2],
                                   text=f'Платеж за заказ № {id_order} проведен успешно!')
        info_user = get_info_user(telegram_id=callback.message.chat.id)
        #     id INTEGER PRIMARY KEY,
        #     time_order TEXT,
        #     id_creator INTEGER,
        #     description_order TEXT,
        #     contact_order TEXT,
        #     category INTEGER,
        #     mailer_order TEXT,
        #     status TEXT,
        #     id_user INTEGER,
        #     amount INTEGER,
        #     report TEXT,
        #     cancel_id TEXT,
        #     comment TEXT
        list_order_id_complete = get_list_order_id_complete(id_user=callback.message.chat.id)
        total_amount = 0
        for order in list_order_id_complete:
            total_amount += order[9]
        rating = total_amount // len(list_order_id_complete)
        set_rating(telegram_id=callback.message.chat.id, rating=rating)
        await callback.answer(text='Ваш рейтинг обновлен', show_alert=True)




@router.message(StateFilter(Tasks.amount))
async def error_amount_order(message: Message):
    logging.info(f'error_amount_order: {message.chat.id}')
    await message.answer(text='Некорректно указана сумма заказа, повторите ввод!')


