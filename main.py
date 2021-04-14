#!venv/bin/python3
from threading import Timer

import coins
from keyboard import get_keyboard
from weathercast import get_current_weather
from secrets import TG_TOKEN
import datetime
import random
import smok_ph
import telebot
import os
import pickle
import statsm

data = {'default': {
    'interval': 50.0,
    'interval_from_start': 1.0,
    'timer_start': datetime.datetime.now()
}
}

timers = {'default': []}

bot = telebot.TeleBot(TG_TOKEN, parse_mode=None)
admins = (384100208, 249717672, 1385540951)
emoji = {
    'smoke': u'\U0001F6AC',
    'cool': u'\U0001F60E',
    'poke': u'\U0001F610',
    'eyes': u'\U0001F440'
}

constructor = [
    ['Господа, ', 'Товарищи, ', 'Друзья, ', 'Дорогие Украинцы, ', 'Печенеги, ', 'Коллеги, ', 'Кол, так сказать, леги, ',
     'Куряги, ', 'Хлопцы, ', 'Работяги, '],
    ['пришло время ', 'настало время ', 'наступило время ', 'пора бы уже ', 'давно пора ', 'самое время ',
     'сейчас самый подходящий момент ', 'настал тот час, чтобы ', 'я, конечно, все понимаю, но, кажется, пора '],
    ['пойти и ', 'попиздовать ', 'отправиться ', 'двинуть ', 'отчалить ', 'вытащить жопу и ', 'выйти, ',
     'встать, размять шею, спину, и пойти уже наконец и '],
    ['покурить.', 'курнуть.', 'поцыбарить.', 'посмолить.', 'подымить.', 'попыхтеть.', 'подышать свежим воздухом.',
     'подышать.']]


def get_timeleft(time_started, time_interval):
    days = 0
    while time_interval > 1440:
        days += 1
        time_interval -= 1440
    if time_started + datetime.timedelta(minutes=time_interval) > datetime.datetime.now():
        mins, secs = divmod((time_started - datetime.datetime.now() +
                             datetime.timedelta(minutes=time_interval)).seconds, 60)
    else:
        mins, secs = 0, 1
    return mins + (days * 1440), secs


def on_startup():
    for chat in data.keys():
        if chat != 'default':
            if 'is_active' not in data[chat].keys():
                data[chat]['is_active'] = True
            elif data[chat]['is_active']:
                timers[chat] = []
                print(f'[STARTUP] {data[chat]}')
                mins, secs = get_timeleft(data[chat]['timer_start'], data[chat]['interval_from_start'])
                start_timer(mins + secs / 60, chat)


def save():
    with open('data.bin', 'wb') as datafile:
        pickle.dump(data, datafile)


if not os.path.exists('data.bin'):
    save()
else:
    with open('data.bin', 'rb') as f:
        data = pickle.load(f)


def notifier(chat_id: str):
    global data
    if not chat_active(chat_id):
        data[chat_id]['is_active'] = True
    msg = ''
    for i in constructor:
        msg += i[random.randint(0, len(i) - 1)]
    timers[chat_id] = []
    save()
    bot.send_message(chat_id=chat_id, reply_markup=get_keyboard(), text=msg)
    print(f'[END TIMER] Timer stopped at {datetime.datetime.now()} for chat {chat_id}')


def start_timer(tm, cid, update_st_timer=True):
    global data
    data[cid]['interval_from_start'] = tm
    if update_st_timer:
        data[cid]['timer_start'] = datetime.datetime.now()
    timers[cid] = [Timer(tm * 60, notifier, args=(cid,))]
    print(f'[START TIMER] Timer started for chat {str(cid)} with {str(tm)} minutes.\n'
          f'[START TIMER] Should be ended at {data[cid]["timer_start"] + datetime.timedelta(minutes=tm)}')
    timers[cid][-1].start()
    save()


def chat_active(chat_id: str) -> 'Chat ID':
    global data
    return data[chat_id]['is_active']


@bot.message_handler(
    func=lambda message: message.text is not None and '/coin ' in message.text and message.content_type == 'text')
def crypto_hanler(message):
    vals = message.text.replace('/coin ', '').split(' ')
    if len(vals) != 2:
        bot.send_message(message.chat.id, 'Неверно указаны тикеры валют')
        return
    statsm.register(message.chat.id, f'coin-{vals[0]}-{vals[1]}')
    bot.send_message(message.chat.id, coins.get_rate(vals[0], vals[1]), parse_mode='HTML')


@bot.message_handler(commands=['stop'])
def stop_handler(message):
    global data
    if message.from_user.id in admins:
        if message.chat.id in data.keys() and chat_active(message.chat.id):
            if timers[message.chat.id]:
                for i in timers[message.chat.id]:
                    i.cancel()
            data[message.chat.id]['is_active'] = False
            bot.send_message(message.chat.id, 'Чат успешно отключен от бота')
            save()


@bot.message_handler(commands=['start'])
def start_handler(message):
    global emoji, data
    if message.from_user.id in admins:
        if message.chat.id not in data.keys():
            data[message.chat.id] = {'interval': data['default']['interval'],
                                     'interval_from_start': data['default']['interval_from_start'],
                                     'timer_start': data['default']['timer_start'],
                                     'is_active': True}
        elif not chat_active(message.chat.id):
            data[message.chat.id]['is_active'] = True
        save()
        if message.chat.id not in timers.keys():
            bot.send_message(message.chat.id, 'Я начал следить за Вашим покуром ' + emoji['eyes'])
            start_timer(data[message.chat.id]['interval_from_start'], message.chat.id)
        else:
            bot.send_message(message.chat.id, 'Не выпендривайся, таймер уже активен')


@bot.message_handler(commands=['blackjack'])
def start_handler(message):
    return


def end_day(days_wait, chat_id):
    tmrw = datetime.datetime.now() + datetime.timedelta(days=days_wait)
    next_time = datetime.datetime(tmrw.year, tmrw.month, tmrw.day, 10, 0, 0) + \
                datetime.timedelta(minutes=data[chat_id]['interval'])
    mins = (next_time - datetime.datetime.now()).total_seconds() / 60
    return mins


@bot.message_handler(
    func=lambda message: message.text is not None and 'Мы покурили' in message.text and message.content_type == 'text')
def smok_handler(message):
    global data
    if message.chat.id not in data.keys() or not chat_active(message.chat.id):
        return
    if timers[message.chat.id]:
        bot.send_message(message.chat.id, 'Вообще-то еще рано, жди уведомление!')
        return
    bot.send_message(message.chat.id, random.choice(list(emoji.values())) + ' ' + smok_ph.get_phrase())
    delay = data[message.chat.id]['interval']
    dtn = datetime.datetime.now()
    if dtn.hour >= 17 or (dtn.hour == 16 and dtn.minute >= 35):
        msg = 'Увидимся завтра!'
        delay = end_day(1, message.chat.id)
        print(f'Day ended for chat {message.chat.id}, delay setted to {delay} mins')
        if datetime.datetime.today().weekday() >= 4:
            msg = 'До понедельника) Хороших выходных! ' + emoji['cool']
            delay = end_day(3, message.chat.id)
            print(f'Week ended for chat {message.chat.id}, delay setted to {delay} mins')
        bot.send_message(message.chat.id, msg)
    print(f'Saving delay {delay} to chat {message.chat.id}')
    save()
    statsm.register(message.chat.id, 'smoking')
    start_timer(delay, message.chat.id)


@bot.message_handler(func=lambda message: message.text is not None and (
        '/time' in message.text or 'Сколько до кура?' in message.text) and message.content_type == 'text')
def time_left_handler(message):
    global data
    if message.chat.id not in data.keys() or not chat_active(message.chat.id):
        return
    if message.from_user.id not in admins:
        bot.reply_to(message, 'Только админы умеют это, а ты не админ(')
        return
    if timers[message.chat.id] and data[message.chat.id]['timer_start']:
        statsm.register(message.chat.id, 'timeleft')
        mins, secs = get_timeleft(data[message.chat.id]['timer_start'], data[message.chat.id]['interval_from_start'])
        bot.send_message(message.chat.id, smok_ph.get_timeleft_phrase())
        hours = 0
        msg = f'<b>{mins} мин</b> и {secs} сек.'
        if mins >= 60:
            hours, mins = divmod(mins, 60)
            msg = f'<b>{hours} часов</b> и {mins} мин.'
        elif mins == 0:
            msg = f'<b>{secs} сек</b>.'
        if hours >= 24:
            days, hours = divmod(hours, 24)
            msg = f'<b>{days} дней</b>, {hours} часов и {mins} мин.'
        bot.send_message(message.chat.id, 'До покура осталось ' + msg, parse_mode='HTML')
    else:
        msg = f'Уже пора давно пойти курить.\n\nЕсли что, стандартный интервал был установлен на ' \
              f'{data[message.chat.id]["interval"]} минут, а последний раз использовался интервал в ' \
              f'{data[message.chat.id]["interval_from_start"]} мин.'
        bot.send_message(message.chat.id, msg, parse_mode='HTML')


@bot.message_handler(
    func=lambda message: message.text is not None and '/interval ' in message.text and message.content_type == 'text')
def interval_handler(message):
    global data
    if message.chat.id not in data.keys() or not chat_active(message.chat.id):
        return
    if message.from_user.id not in admins:
        bot.reply_to(message, 'Только админы умеют это, а ты не админ(')
        return
    stext = message.text.replace('/interval ', '')
    if stext == '':
        bot.reply_to(message, 'Ну написал бы хоть что нибудь')
        return
    try:
        val = int(stext)
        if not (1 <= val <= 90):
            raise ValueError
        interval = val
        for i in timers[message.chat.id]:
            i.cancel()
        start_timer(interval, message.chat.id)
        data[message.chat.id]['interval'] = interval
        bot.send_message(message.chat.id, 'Интервал успешно обновлен, таймер сброшен. Пойдете курить через '
                         + str(val) + ' мин.')
        save()
    except ValueError:
        bot.send_message(message.chat.id, 'Неправильный интервал (указывается в минутах)')
        return


@bot.message_handler(
    func=lambda message: message.text is not None and '/addphrase ' in message.text and message.content_type == 'text')
def phraseadd_handler(message):
    if not chat_active(message.chat.id):
        return
    if message.from_user.id not in admins:
        bot.reply_to(message, 'Только админы умеют это, а ты не админ(')
        return
    stext = message.text.replace('/addphrase ', '')
    if stext == '':
        bot.reply_to(message, 'Ну написал бы хоть что нибудь')
        return
    smok_ph.add_phrase(stext)
    bot.reply_to(message, 'Фраза добавлена')


@bot.message_handler(
    func=lambda message: message.text is not None and '/delphrase ' in message.text and message.content_type == 'text')
def phrasedel_handler(message):
    if not chat_active(message.chat.id):
        return
    if message.from_user.id not in admins:
        bot.reply_to(message, 'Только админы умеют это, а ты не админ(')
        return
    stext = message.text.replace('/delphrase ', '')
    ph_id = -1
    try:
        ph_id = int(stext)
    except ValueError:
        bot.send_message(message.chat.id, 'ID неправильный')
    except IndexError:
        bot.send_message(message.chat.id, 'ID неправильный')
    if ph_id != -1:
        smok_ph.del_phrase(ph_id)
        bot.reply_to(message, 'Фраза удалена')


@bot.message_handler(
    func=lambda message: message.text is not None and '/list' in message.text and message.content_type == 'text')
def smok_handler(message):
    if not chat_active(message.chat.id):
        return
    if message.from_user.id not in admins:
        bot.reply_to(message, 'Только админы умеют это, а ты не админ(')
        return
    k = 0
    msg = ''
    for i in smok_ph.get_allphrases():
        msg += '(' + str(k) + ') ' + i + '\n'
        k += 1
    bot.send_message(message.chat.id, msg, parse_mode='HTML')


@bot.message_handler(
    func=lambda message: message.text is not None and '/stats' in message.text and message.content_type == 'text')
def stats_handler(message):
    if not chat_active(message.chat.id):
        return
    if message.from_user.id not in admins:
        bot.reply_to(message, 'Только админы умеют это, а ты не админ(')
        return
    stats = statsm.get_stats(message.chat.id)
    msg = 'История\n\n'
    action_dict = {
        'smoking': 'Покур',
        'timeleft': 'Запрос времени до покура',
        '2mins': 'Перенос на 2 минуты',
        'weather': 'Запрос погоды'
    }
    for action in stats.keys():
        if action in action_dict.keys():
            action_translated = action_dict[action]
        else:
            action_translated = action
        msg += f'<b>{action_translated}</b>\n'
        for date in stats[action].keys():
            msg += 'Дата: ' + date.strftime("%d-%m-%Y") + '\n'
            for k in stats[action][date]:
                msg += k.strftime("%H:%M:%S") + '\n'
        msg += '\n'
    print(msg)
    bot.send_message(message.chat.id, msg, parse_mode='HTML')


@bot.message_handler(
    func=lambda message: message.text is not None and 'Погода' in message.text and message.content_type == 'text')
def weather_handler(message):
    forecast = get_current_weather()
    if forecast:
        msg = forecast
    else:
        msg = 'Прогноз погоды недоступен, проблемы с их АПИ'
    statsm.register(message.chat.id, 'weather')
    bot.send_message(message.chat.id, msg)


@bot.message_handler(func=lambda
        message: message.text is not None and '/keyboardupdate' in message.text and message.content_type == 'text')
def kbupdate_handler(message):
    if not chat_active(message.chat.id):
        return
    bot.send_message(message.chat.id, emoji['smoke'], reply_markup=get_keyboard())


@bot.message_handler(func=lambda
        message: message.text is not None and '/info' in message.text and message.content_type == 'text')
def info_handler(message):
    msg = ''
    for i in data[message.chat.id].keys():
        msg += str(i) + ' >> ' + str(data[message.chat.id][i]) + '\n'
    bot.send_message(message.chat.id, 'Информация о чате\n' + msg, parse_mode='HTML')


@bot.message_handler(func=lambda
        message: message.text is not None and 'Через 2 мин пойдем' in message.text and message.content_type == 'text')
def smok_handler(message):
    global data
    if message.chat.id not in data.keys() or not chat_active(message.chat.id):
        return
    statsm.register(message.chat.id, '2mins')
    if timers[message.chat.id]:
        mins, secs = get_timeleft(data[message.chat.id]['timer_start'], data[message.chat.id]['interval_from_start'])
        timers[message.chat.id][-1].cancel()
        mult = 2
        if mins <= 2:
            bot.send_message(message.chat.id, 'Окей, продлю на 2 минуты')
            mult += mins + (secs / 60)
        else:
            bot.send_message(message.chat.id, 'Не вопрос, пойдете через 2 минуты')
        start_timer(mult, message.chat.id)
    else:
        start_timer(2, message.chat.id)
        bot.send_message(message.chat.id, 'Хорошо, позову через 2 минуты')


on_startup()
bot.polling()
