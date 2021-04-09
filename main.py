#!venv/bin/python3
from threading import Timer
from keyboard import get_keyboard
from weathercast import get_current_weather
from secrets import TG_TOKEN
import datetime
import random
import smok_ph
import telebot
import os
import pickle
import stat

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


def time_remain(chat_id):
    mins, secs = divmod((data[chat_id]['timer_start'] +
                         datetime.timedelta(minutes=data[chat_id]['interval_from_start']) -
                         datetime.datetime.now()).seconds, 60)
    return mins, secs


def on_startup():
    for chat in data.keys():
        if chat != 'default':
            timers[chat] = []
            if data[chat]['timer_start'] + datetime.timedelta(minutes=data[chat]['interval']) > datetime.datetime.now():
                mins, secs = time_remain(chat)
            else:
                mins = 0
                secs = 10
            bot.send_message(chat, 'Я только включился. По идее вы пойдете курить через ' +
                             str(mins) + ' мин. и ' + str(secs) + ' сек.')
            start_timer(mins + secs / 60, chat, False)


def save():
    with open('data.bin', 'wb') as datafile:
        pickle.dump(data, datafile)


if not os.path.exists('data.bin'):
    save()
else:
    with open('data.bin', 'rb') as f:
        data = pickle.load(f)


def notifier(chat_id):
    global data
    msg = ''
    for i in constructor:
        msg += i[random.randint(0, len(i) - 1)]
    timers[chat_id] = []
    save()
    bot.send_message(chat_id=chat_id, reply_markup=get_keyboard(), text=msg)


def start_timer(tm, cid, update_st_timer=True):
    global data
    data[cid]['interval_from_start'] = tm
    if update_st_timer:
        data[cid]['timer_start'] = datetime.datetime.now()
    timers[cid] = [Timer(tm * 60, notifier, args=(cid,))]
    print('\nTimer started ' + str(tm))
    timers[cid][-1].start()


@bot.message_handler(commands=['start'])
def start_help_handler(message):
    global emoji, data
    if message.from_user.id in admins:
        if message.chat.id not in data.keys():
            data[message.chat.id] = {'interval': data['default']['interval'],
                                     'interval_from_start': data['default']['interval_from_start'],
                                     'timer_start': data['default']['timer_start'],
                                     'timers': []}
            save()
        if message.chat.id not in timers.keys():
            bot.send_message(message.chat.id, 'Я начал следить за Вашим покуром ' + emoji['eyes'])
            start_timer(data[message.chat.id]['interval_from_start'], message.chat.id)
        else:
            bot.send_message(message.chat.id, 'Не выпендривайся, таймер уже активен')


def end_day(days_wait, chat_id):
    tmrw = datetime.datetime.now() + datetime.timedelta(days=days_wait)
    next_time = datetime.datetime(tmrw.year, tmrw.month, tmrw.day, 10, 0, 0) + \
                datetime.timedelta(minutes=data[chat_id]['interval'])
    mins, secs = time_remain(next_time)
    return mins


@bot.message_handler(
    func=lambda message: message.text is not None and 'Мы покурили' in message.text and message.content_type == 'text')
def smok_handler(message):
    global data
    if message.chat.id not in data.keys():
        return
    if timers[message.chat.id]:
        bot.send_message(message.chat.id, 'Вообще-то еще рано, жди уведомление!')
        return
    bot.send_message(message.chat.id, random.choice(list(emoji.values())) + ' ' + smok_ph.get_phrase())
    delay = data[message.chat.id]['interval']
    if datetime.datetime.now().hour >= 17 or datetime.datetime.now().hour <= 9:
        msg = 'Увидимся завтра!'
        delay = end_day(1, message.chat.id)
        if datetime.datetime.today().weekday() >= 4:
            msg = 'До понедельника) Хороших выходных! ' + emoji['cool']
            delay = end_day(3, message.chat.id)
        bot.send_message(message.chat.id, msg)
    stat.register(message.chat.id, 'smoking')
    start_timer(delay, message.chat.id)
    save()


@bot.message_handler(func=lambda message: message.text is not None and (
        '/time' in message.text or 'Сколько до кура?' in message.text) and message.content_type == 'text')
def time_left_handler(message):
    global data
    if message.chat.id not in data.keys():
        return
    if message.from_user.id not in admins:
        bot.reply_to(message, 'Только админы умеют это, а ты не админ(')
        return
    if timers[message.chat.id] and data[message.chat.id]['timer_start']:
        stat.register(message.chat.id, 'timeleft')
        mins, secs = time_remain(message.chat.id)
        bot.send_message(message.chat.id, smok_ph.get_timeleft_phrase())
        bot.send_message(message.chat.id, 'До покура осталось ' + str(mins) + ' минут и ' + str(secs) + ' секунд.')


@bot.message_handler(
    func=lambda message: message.text is not None and '/interval ' in message.text and message.content_type == 'text')
def interval_handler(message):
    global data
    if message.chat.id not in data.keys():
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
    if message.from_user.id not in admins:
        bot.reply_to(message, 'Только админы умеют это, а ты не админ(')
        return
    stext = message.text.replace('/delphrase ', '')
    ph_id = -1
    try:
        ph_id = int(stext)
    except ValueError:
        bot.send_message(message.chat.id, 'ID неправильный')
    if ph_id != -1:
        smok_ph.del_phrase(ph_id)
        bot.reply_to(message, 'Фраза удалена')


@bot.message_handler(
    func=lambda message: message.text is not None and '/list' in message.text and message.content_type == 'text')
def smok_handler(message):
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
    if message.from_user.id not in admins:
        bot.reply_to(message, 'Только админы умеют это, а ты не админ(')
        return
    stats = stat.get_stats(message.chat.id)
    msg = 'История\n'
    bot.send_message(message.chat.id, msg, parse_mode='HTML')


@bot.message_handler(
    func=lambda message: message.text is not None and 'Погода' in message.text and message.content_type == 'text')
def weather_handler(message):
    forecast = get_current_weather()
    if forecast:
        msg = forecast
    else:
        msg = 'Прогноз погоды недоступен, проблемы с их АПИ'
    stat.register(message.chat.id, 'weather')
    bot.send_message(message.chat.id, msg)


@bot.message_handler(func=lambda
        message: message.text is not None and '/keyboardupdate' in message.text and message.content_type == 'text')
def kbupdate_handler(message):
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
    if message.chat.id not in data.keys():
        return
    stat.register(message.chat.id, '2mins')
    if timers[message.chat.id]:
        mins, secs = time_remain(message.chat.id)
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
