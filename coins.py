import requests
import os
import pickle
from yahoo_fin import stock_info as si
from secrets import CURRENCY_API_KEY


coins = {}
emojis = {
    'up': u'\U00002B06',
    'down': u'\U00002B07',
    'green': u' \U0001F7E9',
    'red': u'\U0001F7E5'
}


def save():
    global coins
    with open('coins.bin', 'wb') as datafile:
        pickle.dump(coins, datafile)


def get_change(current, previous):
    if current == previous:
        return 0
    try:
        return ((current - previous) / previous) * 100.0
    except ZeroDivisionError:
        return 0


def get_diff_msg(ticker, rate):
    old_rate = coins[ticker]
    diff = round(rate - old_rate, 6)
    diff_per = round(get_change(rate, old_rate), 8)
    if diff >= 0.0:
        t1 = emojis["up"] * (int(abs(diff_per) // 5))
        t2 = f'\n {t1}\n{emojis["green"]} +'
    else:
        t1 = emojis["down"] * (int(abs(diff_per) // 5))
        t2 = f'\n {t1}\n{emojis["red"]} '
    return t2 + f'{str(diff_per) + "%"}'


def get_rate(c_from, c_to):
    global emojis, coins
    try:
        c_from = c_from.lower()
        c_to = c_to.lower()
        base_url = 'https://www.alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE'
        full_url = base_url + f'&from_currency={c_from}&to_currency={c_to}&apikey={CURRENCY_API_KEY}'
        response = requests.get(full_url)
        data = response.json()['Realtime Currency Exchange Rate']
        rate = float(data["5. Exchange Rate"])
        msg = f'1 {data["1. From_Currency Code"]} = {rate} {data["3. To_Currency Code"]}'
        if c_from + c_to in coins.keys():
            old_rate = coins[c_from + c_to]
            diff = round(rate - old_rate, 6)
            diff_per = round(get_change(rate, old_rate), 8)
            if diff >= 0.0:
                t1 = emojis["up"] * (int(abs(diff_per) // 5))
                t2 = f'\n {t1}\n{emojis["green"]} +'
            else:
                t1 = emojis["down"] * (int(abs(diff_per) // 5))
                t2 = f'\n {t1}\n{emojis["red"]} '
            msg += t2 + f'{str(diff_per) + "%"}'
        coins[c_from + c_to] = rate
        save()
    except Exception:
        msg = 'Проблемы с АПИ либо неверно указан тикеры валют :('
    return msg


def get_stock_rate(ticker):
    try:
        ticker = ticker.lower()
        stock = si.get_quote_table(ticker)
        rate = stock['Quote Price']
        msg = f'{ticker.upper()} сейчас торгуется по {round(rate, 4)}'
        if ticker in coins.keys():
            msg += get_diff_msg(ticker, rate)
        coins[ticker] = rate
        save()
    except Exception:
        msg = 'Проблемы с АПИ либо неверно указан тикер акции :(\n(пока что я работаю только с NASDAQ)'
    return msg


if not os.path.exists('coins.bin'):
    save()
else:
    with open('coins.bin', 'rb') as f:
        coins = pickle.load(f)
