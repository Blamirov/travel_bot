import datetime
from telebot.types import Message, CallbackQuery, ReplyKeyboardRemove
from loader import bot
from telegram_bot_calendar import DetailedTelegramCalendar
from datetime import date, timedelta
from keyboards.inline import photo, destination_line
from states.mystates import MyStates
from handlers.API_getter import get_destination as g, get_hotel_list as hl
from handlers.default_heandlers.func_insert_query_data import insert_query_data
from database_bot.database import execute_query, execute_read_query
from loguru import logger
from handlers.searching_command.history import history
from keyboards.reply import all_key



@bot.message_handler(state=MyStates.start)
@logger.catch
def start_ex(message: Message) -> None:
    """
    Начало поиска, запрашивается название города
    Передается информация о пользователе в базу данных
    """
    with bot.retrieve_data(message.from_user.id) as data:
        if message.text == 'По возрастанию цены':
            data['sort'] = 'PRICE_LOW_TO_HIGH'
        elif message.text == 'По убыванию цены':
            data['sort'] = 'PRICE_HIGH_TO_LOW'
        elif message.text == 'Лучшее предложение':
            data['sort'] = 'DISTANCE'
        elif message.text == 'История поиска':
            history(message)
            return
        else:
            bot.send_message(message.from_user.id,
                             f'Для начала выбери режим поиска',
                             reply_markup=all_key.start_searching()
                             )
            return
        data['command'] = message.text
        query_user = f'''SELECT id FROM user WHERE tg_user_id = {message.from_user.id}'''
        data['user_id'] = execute_read_query(data['bd_param'], query_user)[0][0]
    bot.set_state(message.from_user.id, MyStates.city, message.chat.id)
    bot.send_message(message.chat.id, 'Введите название города, в котором будем искать отели',
                     reply_markup=ReplyKeyboardRemove())


@bot.message_handler(state=MyStates.city)
@logger.catch
def get_city_data(message: Message) -> None:
    """
    Функция для обратки отправленного пользователем названия города,
    :param message: Message, сообщение от пользователя
    :return: None
    """
    with bot.retrieve_data(message.from_user.id) as data:
        data['city'] = message.text
        data['start_command'] = datetime.datetime.now()

    all_destination = g.get_destination_id(message.text)
    if len(all_destination) > 1:
        bot.send_message(message.chat.id,
                         'Выберете район',
                         reply_markup=destination_line.destination_ask(all_destination)
                         )
        bot.set_state(message.from_user.id, MyStates.destination)

    elif len(all_destination) == 1:
        with bot.retrieve_data(message.chat.id) as data:
            for key, value in all_destination.items():
                data['destination'] = key
        bot.set_state(message.chat.id, MyStates.arrival_date)

        calendar_1, step = DetailedTelegramCalendar(min_date=date.today(),
                                                    max_date=date.today() + datetime.timedelta(days=480),
                                                    calendar_id=1).build()
        bot.send_message(message.chat.id,
                         'Дата приезда',
                         reply_markup=calendar_1)

    else:
        bot.send_message(message.chat.id, 'Нет информации по данному городу, попробуйте другое написание или другой '
                                          'город')


@bot.callback_query_handler(state=MyStates.destination, func=lambda call: True)
@logger.catch
def destination(call: CallbackQuery) -> None:
    """Функция для обработки ответа на вопрос в каком райне искать"""
    with bot.retrieve_data(call.from_user.id) as data:
        data['destination'] = call.data
    bot.edit_message_reply_markup(chat_id=call.from_user.id, message_id=call.message.id, reply_markup=None)
    bot.set_state(call.from_user.id, MyStates.arrival_date)

    calendar_1, step = DetailedTelegramCalendar(min_date=date.today(),
                                                max_date=date.today() + datetime.timedelta(days=480),
                                                calendar_id=1).build()
    bot.send_message(call.from_user.id,
                     'Дата приезда',
                     reply_markup=calendar_1)


@bot.callback_query_handler(state=MyStates.arrival_date, func=DetailedTelegramCalendar.func(calendar_id=1))
@logger.catch
def cal1(call: CallbackQuery) -> None:
    """
    Функция принимает ответ из инлайн клавиатуры календаря, и меняет ее на месяцы, а потом на дни
    после того как arrival_date принимает значение, отправляет новый календарь для даты отъезда
    :param call:
    :return: None
    """
    arrival_date, key, step = DetailedTelegramCalendar(min_date=date.today(),
                                                       max_date=date.today() + datetime.timedelta(days=480),
                                                       calendar_id=1).process(call.data)
    if not arrival_date and key:
        bot.edit_message_text('Дата приезда',
                              call.message.chat.id,
                              call.message.message_id,
                              reply_markup=key)
    elif arrival_date:
        bot.edit_message_text(f"Дата приезда {arrival_date}",
                              call.message.chat.id,
                              call.message.message_id)
        with bot.retrieve_data(call.from_user.id) as data:
            data['arrival_date'] = arrival_date

            bot.set_state(call.from_user.id, MyStates.departure_date)

            calendar_2, step = DetailedTelegramCalendar(min_date=data['arrival_date'] + timedelta(days=1),
                                                        calendar_id=2).build()
            bot.send_message(call.message.chat.id,
                             "Дата отъезда",
                             reply_markup=calendar_2)


@bot.callback_query_handler(state=MyStates.departure_date, func=DetailedTelegramCalendar.func(calendar_id=2))
@logger.catch
def cal2(call: CallbackQuery) -> None:
    """
    Функция делает тоже самое что и функция cal1 но для даты отъезда
    :param call:
    :return:
    """
    with bot.retrieve_data(call.from_user.id) as data:
        departure_date, key, step = DetailedTelegramCalendar(min_date=data['arrival_date'] + timedelta(days=1),
                                                             calendar_id=2).process(call.data)
        if not departure_date and key:
            bot.edit_message_text("Дата отъезда",
                                  call.from_user.id,
                                  call.message.message_id,
                                  reply_markup=key)
        elif departure_date:
            bot.edit_message_text(f"Дата отъезда {departure_date}",
                                  call.from_user.id,
                                  call.message.message_id)
            data['departure_date'] = departure_date
            bot.set_state(call.from_user.id, MyStates.amount_hotels)

            bot.send_message(call.from_user.id, 'Сколько отелей показать? (max 5)')


@bot.message_handler(state=MyStates.amount_hotels)
@logger.catch
def amount_hotels(message: Message) -> None:
    """
    Функция принимает сообщение о количестве выводимых отелей и проверяет на соответствие
    :param message:
    :return:
    """
    try:
        if int(message.text) > 5:
            bot.send_message(message.chat.id, 'Максимально возможное количество 5, выведем 5 отелей')
            amt_hotels = 5
        else:
            amt_hotels = int(message.text)
        with bot.retrieve_data(message.chat.id) as data:
            data['amount_hotels'] = amt_hotels
        bot.set_state(message.chat.id, MyStates.photo)

        bot.send_message(message.chat.id, 'Нужны ли вам фотографии?', reply_markup=photo.photo())
    except ValueError:
        bot.send_message(message.chat.id, 'Введите натуральное число')


@bot.callback_query_handler(state=MyStates.photo, func=lambda call: True)
@logger.catch
def need_photo(call: CallbackQuery) -> None:
    """Функция для обработки ответа на вопрос нужны ли фотографии"""
    bot.edit_message_reply_markup(chat_id=call.from_user.id, message_id=call.message.id, reply_markup=None)
    if call.data == 'yes':
        with bot.retrieve_data(call.from_user.id) as data:
            data['photo'] = True
            bot.set_state(call.from_user.id, MyStates.amount_photo)
            bot.send_message(call.from_user.id, 'Введите необходимое количество фотографий (max 5):')
    else:

        with bot.retrieve_data(call.from_user.id) as data:
            data['photo'] = False
            data['amount_photo'] = 0
            bot.send_message(call.from_user.id, 'Запрос обрабатывается...')
            insert_query_data(data)
            query = f'''SELECT id FROM query_data WHERE user_id = {data['user_id']}'''
            data['query_id'] = int(execute_read_query(data['bd_param'], query)[-1][0])
            request = hl.get_hotel_list(data)
            for values in request.values():
                description = f"Отель {values['name']}\n" \
                              f"расположен по адресу: {values['address']}\n" \
                              f"цена за ночь: {values['price_per_night']}\n" \
                              f"полная стоимость проживания {values['total_price']}\n" \
                              f"расположение - {values['distance']}\n" \
                              f"web-site {values['url']}"
                bot.send_message(call.from_user.id, description)

@bot.message_handler(state=MyStates.amount_photo)
@logger.catch
def amount_photo(message: Message) -> None:
    """
    Обрабатывает сообщение о необходимом количестве фотографий и проверяет на соответствие
    :param message:
    :return:
    """
    try:
        if int(message.text) > 5:
            bot.send_message(message.chat.id, 'Максимально возможное количество 5, выведем 5 фотографий')
            amt_photo = 5
        else:
            amt_photo = int(message.text)
        with bot.retrieve_data(message.chat.id) as data:
            data['amount_photo'] = amt_photo
            insert_query_data(data)
            query = f'''SELECT id FROM query_data WHERE user_id = {data['user_id']}'''
            data['query_id'] = int(execute_read_query(data['bd_param'], query)[-1][0])
            bot.send_message(message.chat.id, 'Запрос в обработке...')
            request = hl.get_hotel_list(data)
            for values in request.values():
                description = f"Отель {values['name']}\n" \
                              f"расположен по адресу: {values['address']}\n" \
                              f"цена за ночь: {values['price_per_night']}\n" \
                              f"полная стоимость проживания {values['total_price']}\n" \
                              f"расположение - {values['distance']}\n" \
                              f"web-site - {values['url']}"
                bot.send_message(message.chat.id, description)
                for caption, url in values['photo'].items():
                    bot.send_photo(chat_id=message.chat.id, photo=url, caption=caption)

    except ValueError as e:
        bot.send_message(message.chat.id, 'Введите натуральное число')


@bot.message_handler(commands=['info'])
def bot_info(message: Message) -> None:
    with bot.retrieve_data(message.chat.id) as data:
        bot.send_message(message.chat.id, f'Ваши внесенные данные:\n город {data["city"]}'
                                          f'\n регион {data["destination"]}\nДата прибытия {data["arrival_date"]}'
                                          f'\nдата отъезда {data["departure_date"]}\nКоличество отелей'
                                          f'{data["amount_hotels"]}\nНужно ли фото{data["photo"]}'
                                          f'\nколичество фото{data["amount_photo"]}'
                         )
