import os
from dotenv import load_dotenv, find_dotenv
from mysql.connector import connect, Error
from loguru import logger


@logger.catch()
def creation_db() -> None:
    """Функция для создания базы данных если ее еще нет на компьютере."""
    if not find_dotenv():
        exit('Переменные окружения не загружены т.к отсутствует файл .env')
    else:
        load_dotenv()
    try:
        with connect(host='0.0.0.0',
                     user=os.getenv('SQL_USER'),
                     passwd=os.getenv('MYSQL_ROOT_PASSWORD'),
                     database='travel_bot_data_base',
                     port=3306) as connection_check:
            logger.info('База данных обнаружена')

    except Error as e1:

        if '1049 (42000)' in str(e1):
            try:
                with connect(host='0.0.0.0',
                             user=os.getenv('SQL_USER'),
                             passwd=os.getenv('MYSQL_ROOT_PASSWORD'),
                             port=3306
                             ) as connection:

                    create_db_query = 'CREATE DATABASE travel_bot_data_base'
                    with connection.cursor() as cursor:
                        cursor.execute(create_db_query)
                        connection.commit()
            except Error as e2:
                logger.error(f'При создании базы данных обнаружена ошибка: {e2}')

            try:
                with connect(host="0.0.0.0",
                             user=os.getenv('SQL_USER'),
                             passwd=os.getenv('MYSQL_ROOT_PASSWORD'),
                             database='travel_bot_data_base',
                             port=3306) as connection:
                    with connection.cursor() as cursor_db:

                        create_table_user = '''CREATE TABLE `user` (
                                              `id` int NOT NULL AUTO_INCREMENT,
                                              `tg_user_id` int NOT NULL,
                                              `name` varchar(20) NOT NULL,
                                              `surname` varchar(20) DEFAULT NULL,
                                              PRIMARY KEY (`id`)
                                            )
                                            '''
                        cursor_db.execute(create_table_user)
                        create_table_query_date = '''CREATE TABLE `query_data` (
                                                      `id` int NOT NULL AUTO_INCREMENT,
                                                      `user_id` int NOT NULL,
                                                      `data_time` datetime NOT NULL,
                                                      `command` varchar(45) NOT NULL,
                                                      `city_destination` varchar(45) NOT NULL,
                                                      `check_in` date NOT NULL,
                                                      `check_out` date NOT NULL,
                                                      PRIMARY KEY (`id`),
                                                      KEY `index2` (`user_id`),
                                                      CONSTRAINT `id` FOREIGN KEY (`user_id`) REFERENCES `user` (
                                                      `id`))
                                                  '''
                        cursor_db.execute(create_table_query_date)
                        create_table_hotel_info = '''CREATE TABLE `travel_bot_data_base`.`hotel_info` (
                                                  `id` INT NOT NULL AUTO_INCREMENT,
                                                  `query_id` INT NOT NULL,
                                                  `name` VARCHAR(200) NULL,
                                                  `address` VARCHAR(255) NULL,
                                                  `distance` VARCHAR(200) NULL,
                                                  `price_per_night` INT NOT NULL,
                                                  `price_total` INT NOT NULL,
                                                  `web_site` VARCHAR(255) NOT NULL,
                                                  `hotel_photo` JSON NOT NULL,
                                                  PRIMARY KEY (`id`),
                                                  INDEX `query_id` (`query_id` ASC) VISIBLE,
                                                  CONSTRAINT `query_id`
                                                    FOREIGN KEY (`query_id`)
                                                    REFERENCES `travel_bot_data_base`.`query_data` (`id`)
                                                    ON DELETE NO ACTION
                                                    ON UPDATE NO ACTION);'''
                        cursor_db.execute(create_table_hotel_info)
                        connection.commit()
                        logger.info('База данных создана')
            except Error as e3:
                logger.error(f'При создании таблиц обнаружена ошибка: {e3}')

        else:
            logger.error(f'При подключении к MySQL обнаружена ошибка: {e1}')


if __name__ == '__main__':
    pass