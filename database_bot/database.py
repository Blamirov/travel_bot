from mysql.connector import connect, Error
import os
from loguru import logger


@logger.catch
def execute_query(connect_param: dict, insert_query: str, query_data: list) -> None:
    '''
    Функция принимает
    :param connect_param:
    :param insert_query:
    :param query_data:
    :return:
    '''
    try:
        with connect(
                host=connect_param.get('host'),
                user=connect_param.get('user'),
                passwd=connect_param.get('passwd'),
                database=connect_param.get('database')) as connection:

            with connection.cursor() as cursor:
                cursor.executemany(insert_query,
                                   query_data)
                connection.commit()
    except Error as e1:
        logger.error(e1)


@logger.catch
def execute_read_query(connect_param: dict, query: str) -> (None, str):
    try:
        with connect(
                host=connect_param.get('host'),
                user=connect_param.get('user'),
                passwd=connect_param.get('passwd'),
                database=connect_param.get('database')) as connection_rq:

            with connection_rq.cursor() as cursor_rq:
                cursor_rq.execute(query)
                result = cursor_rq.fetchall()
                return result
    except Error as e2:
        logger.error(e2)


if __name__ == '__main__':
    pass
