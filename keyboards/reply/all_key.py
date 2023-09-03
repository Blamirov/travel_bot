from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from loader import bot



def start_searching() -> ReplyKeyboardMarkup:
    markup_reply = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
    low_price = KeyboardButton(text='По возрастанию цены')
    high_price = KeyboardButton(text='По убыванию цены')
    best_deals = KeyboardButton(text='Лучшее предложение')
    history = KeyboardButton(text='История поиска')

    markup_reply.add(low_price, high_price, best_deals, history)
    return markup_reply

