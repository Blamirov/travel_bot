from handlers.default_heandlers.getters import get_value, get_request
from os import getenv
from loguru import logger


@logger.catch
def get_hotel_info(amount_photo, property_id):
    url_get_hotel = "https://hotels4.p.rapidapi.com/properties/v2/detail"

    payload_get_hotel = {
        "currency": "RUB",
        "eapid": 1,
        "locale": "ru_RU",
        "siteId": 300000001,
        "propertyId": property_id
    }
    headers_get_hotel = {
        "content-type": "application/json",
        "X-RapidAPI-Key": getenv('RAPID_API_KEY'),
        "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
    }

    response_info = get_request("POST", url_get_hotel, params=payload_get_hotel, headers=headers_get_hotel)
    if amount_photo == 0:
        photo_dict = None
    else:
        photo_dict = dict()
        for photo in get_value(get_value(response_info, 'propertyGallery'), 'images'):
            photo_dict[get_value(photo, 'description')] = get_value(photo, 'url')
            if len(photo_dict) == amount_photo:
                break

    full_info = {'name': get_value(response_info, 'name'),
                 'address': get_value(response_info, 'addressLine'),
                 'photo': photo_dict}
    return full_info


if __name__ == '__main__':
    print(get_hotel_info(3))
