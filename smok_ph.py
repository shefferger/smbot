import random
import os
import pickle

smoke_phrases = [
    '— В современном Лондоне не покуришь. Плохая новость для мозга.'
    '— Хорошая для лёгких.'
    '— О, лёгкие... дышать скучно!',
]

timeleft_phrases = [
    'Ну, что, ломает тебя?',
    'Сколько еще раз сюда нажмешь?',
    'Недостаточно маны',
    'Сиди и жди',
    'Совсем нетерпится, да?',
    'Еще раз нажмешь - увеличу интервал'
]


def save():
    with open('phrases.bin', 'wb') as ph:
        pickle.dump(smoke_phrases, ph)


def get_allphrases():
    if not smoke_phrases:
        return ['Фраз нет, но вы держитесь']
    return smoke_phrases


def get_timeleft_phrase():
    if not timeleft_phrases:
        return ['Фраз нет, но вы держитесь']
    return timeleft_phrases[random.randint(0, len(timeleft_phrases) - 1)]


def get_phrase():
    return smoke_phrases[random.randint(0, len(smoke_phrases) - 1)]


def add_phrase(text):
    smoke_phrases.append(text)
    save()


def del_phrase(phr_id):
    smoke_phrases.pop(phr_id)
    save()


if not os.path.exists('phrases.bin'):
    save()
else:
    with open('phrases.bin', 'rb') as f:
        tmp = pickle.load(f)
        for i in smoke_phrases:
            if i not in tmp:
                tmp.append(i)
        smoke_phrases = tmp
