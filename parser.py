import requests
import json


def parse(currency):
    data = json.loads(requests.get(url='https://blockchain.info/ru/ticker').text)
    try:
        return f'Стоимость покупки биткойна в {currency}: {data[currency]["buy"]} {data[currency]["symbol"]}'
    except:
        return 'Нет такой валюты!'
