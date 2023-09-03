from telebot.types import Message
from loader import bot
from keyboards.reply import all_key
from states.mystates import MyStates
from os import getenv
from database_bot.database import execute_query, execute_read_query
from loguru import logger


@logger.catch
@bot.message_handler(commands=['start'])
def bot_start(message: Message) -> None:
    bot.set_state(message.from_user.id, MyStates.start, message.chat.id)
    with bot.retrieve_data(message.from_user.id) as data:
        data['tg_user_id'] = message.from_user.id
        data['bd_param'] = {'host': 'localhost', 'user': getenv('SQL_USER'), 'passwd': getenv('MYSQL_ROOT_PASSWORD'),
                            'database': 'travel_bot_data_base'}
        query_ins = f"""SELECT tg_user_id from user WHERE tg_user_id = {message.from_user.id}"""

        exist_user = execute_read_query(data['bd_param'], query_ins)
        if not exist_user:
            ins_query = '''INSERT INTO user (tg_user_id, name, surname)
                           VALUES
                               ( %s, %s, %s)'''
            query_d = [(message.from_user.id, message.from_user.first_name, message.from_user.last_name)]
            execute_query(data['bd_param'], ins_query, query_d)
            logger.info('Записан новый пользователь')

    bot.send_message(message.from_user.id,
                     f'Привет {message.from_user.first_name},\nВыберите режим поиска',
                     reply_markup=all_key.start_searching()
                     )
