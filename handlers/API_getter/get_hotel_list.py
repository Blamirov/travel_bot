import re
from json import dumps
from handlers.default_heandlers.getters import get_value, get_request
from handlers.API_getter.get_hotel_info import get_hotel_info
from database_bot.database import execute_query
from os import getenv
from loguru import logger


@logger.catch
def get_hotel_list(data):
    """
    Функция принимает  data из обработчика сообщений телеграмм бота запрашивает всю информацию по отелям,
    вносит данные в базу данных в таблицу hotel_info и возвращает
    :param data:
    :return:
    """

    url = "https://hotels4.p.rapidapi.com/properties/v2/list"
    check_in = data['arrival_date']
    check_out = data['departure_date']

    payload = {
        "currency": "USD",
        "eapid": 1,
        "locale": "en_US",
        "siteId": 300000001,
        "destination": {"regionId": data['destination']},
        "checkInDate": {
            "day": check_in.day,
            "month": check_in.month,
            "year": check_in.year
        },
        "checkOutDate": {
            "day": check_out.day,
            "month": check_out.month,
            "year": check_out.year
        },
        "rooms": [
            {
                "adults": 2,
            }
        ],
        "resultsStartingIndex": 0,
        "resultsSize": 50,
        "sort": data['sort'],
        "filters": {"price": {
            "max": 1500,
            "min": 1
        },
            "availableFilter": "SHOW_AVAILABLE_ONLY"}
    }
    headers = {
        "content-type": "application/json",
        "X-RapidAPI-Key": getenv('RAPID_API_KEY'),
        "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
    }

    response_hotels = get_request("POST", url, params=payload, headers=headers)

    try:
        hotels_info = dict()
        for hotel in get_value(response_hotels, 'properties'):
            price = re.search(fr'\$\d+ total', str(hotel)).group()
            price_per_night = int(re.search(fr'\d+', price).group())
            total_price = price_per_night * int((check_out - check_in).days)
            distance = get_value(hotel, 'distanceFromMessaging')
            hotel_id = get_value(hotel, 'id')
            full_information = get_hotel_info(data['amount_photo'], hotel_id)
            url = f'https://www.hoteles.com/ho187112/?chkin={str(check_in)}&expediaPropertyId={hotel_id}'
            hotels_info[hotel_id] = {'name': full_information['name'],
                                     'address': full_information['address'],
                                     'photo': full_information['photo'],
                                     'total_price': f'${total_price}',
                                     'price_per_night': f'${price_per_night}',
                                     'distance': distance, 'url': url}

            query = '''INSERT INTO hotel_info(query_id, name, address, distance, price_per_night, 
                       price_total, web_site, hotel_photo)
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                       '''
            values = [(data['query_id'], full_information['name'], full_information['address'], distance,
                       price_per_night,
                       total_price, url, dumps(full_information['photo']))]
            execute_query(data['bd_param'], query, values)

            if len(hotels_info) == data['amount_hotels']:
                break

        return hotels_info
    except TypeError as e:
        logger.error(e, response_hotels)


if __name__ == '__main__':
    pass
