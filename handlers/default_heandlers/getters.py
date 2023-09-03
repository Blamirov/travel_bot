from requests import request, codes
import json
from loguru import logger


@logger.catch
def get_value(some_dict: dict, looking: str):
    """

    :param some_dict:
    :param looking:
    :return:
    """
    if looking in some_dict:
        return some_dict[looking]
    if isinstance(some_dict, dict):
        for key, value in some_dict.items():
            if isinstance(value, dict):
                result = get_value(value, looking)
                if result:
                    return result
            elif isinstance(value, list):
                for elem in value:
                    result = get_value(elem, looking)
                    if result:
                        return result


@logger.catch
def get_request(method, url, params, headers):
    try:
        if method == "POST":
            response = request(method, url, json=params, headers=headers)
        else:
            response = request(method, url, params=params, headers=headers)

        if response.status_code == codes.ok:
            return json.loads(response.text)
    except Exception as e:
        logger.error(e)

