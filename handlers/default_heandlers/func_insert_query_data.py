from database_bot.database import execute_query
from loguru import logger


@logger.catch
def insert_query_data(data) -> None:
    query_ins = """INSERT INTO query_data (user_id, data_time, command, city_destination, check_in, check_out)
                             VALUES (%s, %s, %s, %s, %s, %s)"""
    values = [(data['user_id'], data['start_command'], data['command'], f'{data["city"]}',
               data["arrival_date"], data["departure_date"])]
    execute_query(data['bd_param'], query_ins, values)

