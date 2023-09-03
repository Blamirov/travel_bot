from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from loguru import logger


@logger.catch
def destination_ask(destinationid: dict) -> InlineKeyboardMarkup:
    '''
    Функция преобразует словарь с destination_id в  inline клавиатуру,  для выбора необходимого района в городе
    :param destinationid:
    :return:
    '''
    all_destination = [InlineKeyboardButton(text=key, callback_data=values)
                       for key, values in destinationid.items()]
    keyboard_dest = InlineKeyboardMarkup(row_width=1)
    keyboard_dest.add(*all_destination)
    return keyboard_dest

