import os
import random
import pickle

suits = {
    '0': u'\U00002660',  # SPADE
    '1': u'\U00002663',  # CLUB
    '2': u'\U00002665',  # HEART
    '3': u'\U00002666'  # DIAMOND
}

translator = {
    '11': 'Валет',
    '12': 'Дама',
    '13': 'Король',
    '14': 'Туз'
}

games = {
    1251: {
        'is_in_game': False,
        'deck': [],
        'dealer_hand': [],
        'player_hand': [],
        'msg': ''
    }
}


def get_card_translation(card_str: str):
    card, suit_id = card_str.split('-')
    if int(card) >= 10:
        card = translator[card]
    return f'{card} {suits[suit_id]}'


def get_hand_translation(hand: list):
    return ', '.join([get_card_translation(i) for i in hand])


def get_new_deck():
    deck = []
    for i in range(2, 15):
        for j in range(0, 4):
            deck.append(f'{str(i)}-{str(j)}')
    return deck


def get_hand_sum(hand):
    summ = 0
    for i in hand:
        card, suit = i.split('-')
        summ += int(card)
    return summ


def dealer_add(chat_id, fill=False):
    summ = get_hand_sum(games[chat_id]['dealer_hand'])
    if summ <= 17:
        deck_size = len(games[chat_id]['deck'])
        games[chat_id]['dealer_hand'].append(games[chat_id]['deck'].pop(random.randint(0, deck_size)))
        if fill:
            dealer_add(chat_id, True)


def start_game(chat_id):
    if chat_id not in games.keys():
        games[chat_id] = {
            'is_in_game': True,
            'deck': get_new_deck(),
            'dealer_hand': [],
            'player_hand': [],
            'msg': ''
        }
        player_add(chat_id)
    elif not games[chat_id]['is_in_game']:
        games[chat_id]['is_in_game'] = True
        games[chat_id]['deck'] = get_new_deck()
        games[chat_id]['dealer_hand'] = []
        games[chat_id]['player_hand'] = []
        player_add(chat_id)
    else:
        return 'Сначала доиграйте текущую партию!'


def player_add(chat_id):
    summ = get_hand_sum(games[chat_id]['player_hand'])
    if summ == 21:
        dealer_add(chat_id, True)
        return  # BJ
    elif summ > 21:
        dealer_add(chat_id, True)
        return  # LOSE
    else:
        dealer_add(chat_id, False)
        deck_size = len(games[chat_id]['deck'])
        games[chat_id]['player_hand'].append(games[chat_id]['deck'].pop(random.randint(0, deck_size)))
    games[chat_id]['msg'] += f'\nВаша рука: {get_hand_translation(games[chat_id]["player_hand"])}'


def player_stay(chat_id):
    dealer_add(chat_id, True)
