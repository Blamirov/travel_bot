import json
from os import getenv
from handlers.default_heandlers.getters import get_value, get_request
from loguru import logger


@logger.catch
def get_destination_id(city):
    """
    :return:
    """
    try:
        url = "https://hotels4.p.rapidapi.com/locations/v3/search"

        querystring = {"q": city, "locale": "ru_RU", "langid": "1033", "siteid": "300000001"}

        headers = {
            "X-RapidAPI-Key": getenv('RAPID_API_KEY'),
            "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
        }

        response_destination = get_request("GET", url, headers=headers, params=querystring)

        destination_dict = dict()
        for group in get_value(response_destination, 'sr'):
            if group['type'] in ('CITY', 'NEIGHBORHOOD'):
                destination_dict[get_value(group, 'shortName')] = get_value(group, 'gaiaId')

        return destination_dict
    except json.decoder.JSONDecodeError:
        return dict()


if __name__ == '__main__':
    print(get_destination_id('New York'))