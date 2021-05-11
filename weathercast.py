import requests
import datetime
from secrets import WEATHER_TOKEN


def get_current_weather():
    try:
        res = requests.get("http://api.openweathermap.org/data/2.5/weather",
                           params={'id': '524901', 'units': 'metric', 'lang': 'ru', 'APPID': WEATHER_TOKEN,
                                   'country': 'ru'})
        data = res.json()
        res_f = requests.get("http://api.openweathermap.org/data/2.5/forecast",
                             params={'id': '524901', 'units': 'metric', 'lang': 'ru', 'APPID': WEATHER_TOKEN,
                                     'country': 'ru'})
        data_f = res_f.json()
        now_tm = int(datetime.datetime.now().timestamp())
        forecast = f'Погода <b>сейчас в Москве</b>\n<b>{data["weather"][0]["description"].capitalize()}</b>\n' \
                   f'От {str(round(data["main"]["temp_min"], 1))}° до {str(round(data["main"]["temp_max"], 1))}°.\n' + \
                   f'Ощущается как <b>{str(round(data["main"]["feels_like"], 1))}°</b>.\n' \
                   f'Влажность {str(data["main"]["humidity"])}%, ветер {str(data["wind"]["speed"])} м/с.\n'
        for i in data_f['list']:
            if now_tm + 3600 < i['dt'] < now_tm + (3600 * 9):
                w = i['main']
                forecast += f'\nПрогноз на <b>{datetime.datetime.fromtimestamp(i["dt"]).strftime("%H:%M")}</b>\n' \
                            f'<b>{i["weather"][0]["description"].capitalize()}</b>.\n' \
                            f'От {str(round(w["temp_min"], 1))}° до {str(round(w["temp_max"], 1))}°.\n' + \
                            f'Будет ощущаться как <b>{round(w["feels_like"], 1)}°</b>.\n'
        return forecast
    except Exception as e:
        print("Exception (weather):", e)
        return None
