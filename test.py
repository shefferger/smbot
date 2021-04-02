#!venv/bin/python3
import requests
from secrets import WEATHER_TOKEN


def get_current_weather():
    try:
        res = requests.get("http://api.openweathermap.org/data/2.5/weather",
                           params={'id': '524901', 'units': 'metric', 'lang': 'ru', 'APPID': WEATHER_TOKEN, 'country': 'ru'})
        data = res.json()
        for i in data.keys():
            print(str(i) + ' >> ' + str(data[i]))
        forecast = 'Погода сейчас в Москве: ' + data['weather'][0]['description'] + ', температура от ' +\
                   str(data['main']['temp_min']) + '° до ' + str(data['main']['temp_max']) +\
                   '° градусов. Ощущается как ' + str(data['main']['feels_like']) + '°.'
        return ''
    except Exception as e:
        print("Exception (weather):", e)
        return None


print(get_current_weather())
