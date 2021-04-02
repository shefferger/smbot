from telebot import types


def get_keyboard():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
    item_btn1 = types.KeyboardButton(u'\U0001F60E' + 'Мы покурили' + u'\U0001F60E')
    item_btn2 = types.KeyboardButton(u'\U000023F3' + 'Через 2 мин пойдем' + u'\U000023F3')
    item_btn3 = types.KeyboardButton(u'\U0001F550' + 'Сколько до кура?' + u'\U0001F550')
    item_btn4 = types.KeyboardButton(u'\U0001F324' + 'Погода' + u'\U00002601')
    markup.add(item_btn1, item_btn2, item_btn4, item_btn3)
    return markup
