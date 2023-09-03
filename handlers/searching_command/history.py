from loader import bot
from database_bot.database import execute_read_query
from loguru import logger
from states.mystates import MyStates
import json


@logger.catch
def history(message):
    with bot.retrieve_data(message.from_user.id) as data:
        query_select = f"""select q_d.id, q_d.data_time, q_d.command, q_d.city_destination
                        from query_data q_d
                        join user u on q_d.user_id = u.id
                        where u.tg_user_id = {data['tg_user_id']}"""

    query_id = execute_read_query(data['bd_param'], query_select)
    if query_id:
        for query in query_id:
            mes = f'Номер запроса: {query[0]}, Время: {query[1]}, режим поиска: {query[2]}, город - {query[3]}'
            bot.send_message(message.chat.id, mes)
        bot.set_state(message.from_user.id, MyStates.history)
        bot.send_message(message.chat.id, 'Для просмотра найденных отелей, введите номер интересующего запроса ')

    else:
        bot.send_message(message.chat.id, 'Запросов еще не было')


@bot.message_handler(state=MyStates.history)
@logger.catch
def hotel_info(message):
    if message.text.isdigit():
        with bot.retrieve_data(message.from_user.id) as data:
            query_hotels = f"""select * from hotel_info
                               where query_id = {message.text}"""
            query_id = execute_read_query(data['bd_param'], query_hotels)
            if query_id is not None:
                for hotel in query_id:
                    description = f"Отель: {hotel[2]}\n" \
                                  f"расположен по адресу: {hotel[3]}\n" \
                                  f"цена за ночь: {hotel[5]}$\n" \
                                  f"полная стоимость проживания: {hotel[6]}$\n" \
                                  f"расположение - {hotel[4]}\n" \
                                  f"web-site - {hotel[7]}"
                    bot.send_message(message.chat.id, description)
                    if hotel[8] is not None:
                        for photo in json.loads(hotel[8]).values():
                            bot.send_photo(message.chat.id, photo)
            else:
                bot.send_message(message.chat.id, 'Отели по этому запросу не обнаружены')

    else:
        bot.send_message(message.chat.id,
                         'Для нового поиска нажмите /start, для просмотра результатов введите номер запроса')