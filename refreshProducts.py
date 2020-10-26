import requests
import demjson
import json
import re


with open('config.json', 'r') as f:
    config = json.loads(f.read())


def fetch_information(series: str) -> list:
    res = requests.get(
        f'https://reserve-prime.apple.com/{config.get("country","CN")}/{config.get("language","zh_CN")}/reserve/{series}/availability', allow_redirects=False)
    if res.status_code != 200:
        return []
    html = res.text
    json_like_information = re.compile(
        r'''<script type=["']text/javascript["']>\s*data\.products\s*=\s*(.*?)</script>''', re.MULTILINE | re.UNICODE | re.DOTALL).search(html)
    if not json_like_information:
        return []
    json_like_information = json_like_information.group(1).strip()
    if json_like_information[-1] == ';':
        json_like_information = json_like_information[:-1]
    products = demjson.decode(json_like_information)
    if not products:
        return []
    products = products.get('products')
    if not products:
        return []
    for product in products:
        product['_series'] = series
    return products


information_result = []
for index in range(26):
    current_series = chr(ord('A')+index)
    information_result += fetch_information(current_series)
config['products'] = information_result

with open('config.json', 'w') as f:
    f.write(json.dumps(config))
