import requests
from secrets import WEATHER_TOKEN


def get_current_weather():
    try:
        res = requests.get("http://api.openweathermap.org/data/2.5/weather",
                           params={'id': '524901', 'units': 'metric', 'lang': 'ru', 'APPID': WEATHER_TOKEN, 'country': 'ru'})
        data = res.json()
        forecast = 'Погода сейчас в Москве: ' + data['weather'][0]['description'] + ', температура от ' +\
                   str(round(data['main']['temp_min'], 1)) + '° до ' + str(round(data['main']['temp_max'], 1)) +\
                   '°. Ощущается как ' + str(round(data['main']['feels_like'], 1)) + '°. Влажность ' \
                   + str(data['main']['humidity']) + '%, ветер ' + str(data['wind']['speed']) + ' м/с.'
        return forecast
    except Exception as e:
        print("Exception (weather):", e)
        return None
