import requests
from secrets import CURRENCY_API_KEY


def get_rate(c_from, c_to):
    try:
        base_url = 'https://www.alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE'
        full_url = base_url + f'&from_currency={c_from}&to_currency={c_to}&apikey={CURRENCY_API_KEY}'
        response = requests.get(full_url)
        data = response.json()['Realtime Currency Exchange Rate']
        msg = f'1 {data["1. From_Currency Code"]} = {float(data["5. Exchange Rate"])} {data["3. To_Currency Code"]}'
    except Exception:
        msg = 'Проблемы с АПИ либо неверно указан тикер'
    return msg
