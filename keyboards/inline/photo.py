from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from loguru import logger

@logger.catch
def photo() -> InlineKeyboardMarkup:
    """
    функция для опроса нужны ли фотографии
    :return: InlineKeyboardMarkup
    """
    keyboard_photo = InlineKeyboardMarkup()
    key_yes = InlineKeyboardButton(text='Да', callback_data='yes')
    key_no = InlineKeyboardButton(text='Нет', callback_data='no')
    keyboard_photo.add(key_no, key_yes)
    return keyboard_photo
