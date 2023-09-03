from loader import bot
import handlers
from telebot.custom_filters import StateFilter, IsDigitFilter
from utils.set_bot_commands import set_default_commands
from database_bot import creation_data_base as create
from loguru import logger


if __name__ == '__main__':
    logger.add('logger.log', format='{time:YYYY-MM-DD HH:mm:ss} {level} {message}')
    logger.info('Начался новый сеанс')
    create.creation_db()
    bot.add_custom_filter(StateFilter(bot))
    bot.add_custom_filter(IsDigitFilter())
    set_default_commands(bot)
    bot.infinity_polling()
