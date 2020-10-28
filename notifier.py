from copy import deepcopy
from time import sleep
import requests
import inquirer
import json
import re


with open('config.json') as f:
    config = json.loads(f.read())


def fetch_store_information(series: str) -> list:
    res = requests.get(
        f'https://reserve-prime.apple.com/{config.get("country","CN")}/{config.get("language","zh_CN")}/reserve/{series}/stores.json')
    if res.status_code != 200:
        return []
    stores = res.json().get('stores')
    filterCities = config.get('filterCities')
    filterStores = config.get('filterStores')
    if filterCities and len(filterCities):
        stores = list(filter(lambda store: store.get(
            'city') in filterCities, stores))
    if filterStores and len(filterStores):
        stores = list(filter(lambda store: store.get(
            'storeName') in filterStores or store.get('storeNumber') in filterStores, stores))
    return stores


def fetch_stock_information(series: str, stores: dict, products: list) -> list:
    res = requests.get(
        f'https://reserve-prime.apple.com/{config.get("country","CN")}/{config.get("language","zh_CN")}/reserve/{series}/availability.json')
    if res.status_code != 200:
        return []
    infos = res.json().get('stores', {})
    stock_result = []
    for store in stores.values():
        for product in products:
            if infos.get(store['storeNumber'], {}).get(product['partNumber'], {}).get('availability', {}).get('unlocked'):
                stock_result.append({'store': store, 'product': product})
    return stock_result


def normalize_str(noticeContent: str, info: dict) -> str:
    noticeContent = re.sub(
        r'\{\{\s*reserveUrl\s*\}\}', f'https://reserve-prime.apple.com/{config.get("country","CN")}/{config.get("language","zh_CN")}/reserve/{series}/availability?'+r'store={{ storeNumber }}&iUP=N&appleCare=N&rv=0&partNumber={{ productSeries }}', noticeContent)
    noticeContent = re.sub(
        r'\{\{\s*productName\s*\}\}', info['product']['description'], noticeContent)
    noticeContent = re.sub(
        r'\{\{\s*productSeries\s*\}\}', info['product']['partNumber'], noticeContent)
    noticeContent = re.sub(
        r'\{\{\s*productColor\s*\}\}', info['product']['color'], noticeContent)
    noticeContent = re.sub(
        r'\{\{\s*productCapacity\s*\}\}', info['product']['capacity'], noticeContent)
    noticeContent = re.sub(
        r'\{\{\s*productPrice\s*\}\}', info['product']['price'], noticeContent)
    noticeContent = re.sub(
        r'\{\{\s*city\s*\}\}', info['store']['city'], noticeContent)
    noticeContent = re.sub(
        r'\{\{\s*storeNumber\s*\}\}', info['store']['storeNumber'], noticeContent)
    noticeContent = re.sub(
        r'\{\{\s*storeName\s*\}\}', info['store']['storeName'], noticeContent)
    return noticeContent


def normalize_dict(d: dict, info: dict) -> dict:
    d = deepcopy(d)
    for key in d.keys():
        d[key] = normalize_anything(d[key], info)
    return d


def normalize_list(l: list, info: dict) -> list:
    l = deepcopy(l)
    for i in range(len(l)):
        l[i] = normalize_anything(l[i], info)
    return l


def normalize_anything(o, info: dict):
    if type(o) is str:
        return normalize_str(o, info)
    if type(o) is dict:
        return normalize_dict(o, info)
    if type(o) is list:
        return normalize_list(o, info)
    return o


products = sorted(list(
    set(map(lambda product: product['description'], config['products']))))
question = [
    inquirer.Checkbox(
        'products',
        message='What type of products are you interested in?',
        choices=products)
]
answer = inquirer.prompt(question)
selected_products = list(filter(
    lambda product: product['description'] in answer['products'], config['products']))
selected_series = list(
    set(map(lambda product: product['_series'], selected_products)))
print(
    f'You selected {",".join(answer["products"])}, will listen on reserve series(es): {",".join(selected_series)}')
store_information = {}
for series in selected_series:
    information = {}
    stores = fetch_store_information(series)
    for store in stores:
        information[store['storeNumber']] = store
    store_information[series] = information
while True:
    try:
        try:
            loop_stock_result = []
            for series in selected_series:
                loop_stock_result += fetch_stock_information(
                    series, store_information[series], selected_products)
            for info in loop_stock_result:
                notifyMethod = config.get('webHookUrl')
                if notifyMethod == 'CLI' or notifyMethod == 'cli' or not notifyMethod:
                    noticeContent = config.get('webHookFormat', '')
                    noticeContent = normalize_anything(noticeContent, info)
                    print(noticeContent)
                else:
                    noticeContent = normalize_anything(
                        config.get('webHookFormat'), info)
                    if type(noticeContent) is not str:
                        noticeContent = json.dumps(noticeContent)
                    requests.post(notifyMethod, noticeContent, headers={
                        'Content-Type': config.get('contentType', 'application/json')})
        except KeyboardInterrupt:
            exit(0)
    except Exception:
        pass
    sleep(config.get('queryInterval', 10))
