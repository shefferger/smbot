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
    '2': 'Двойка',
    '3': 'Тройка',
    '4': 'Четверка',
    '5': 'Пятерка',
    '6': 'Шестерка',
    '7': 'Семерка',
    '8': 'Восьмерка',
    '9': 'Девятка',
    '10': 'Червонец',
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
    card = translator[card]
    return f'[{card} {suits[suit_id]}]'


def get_hand_translation(hand: list):
    return ', '.join([get_card_translation(i) for i in hand])


def get_new_deck():
    deck = []
    for i in range(2, 15):
        for j in range(0, 4):
            deck.append(f'{str(i)}-{str(j)}')
    return deck


def get_hand_sum(hand) -> int:
    summ = 0
    for i in hand:
        card, suit = i.split('-')
        val = int(card)
        if val > 10:
            val = 10
        elif val == 14:
            val = 11
            if summ + val > 21:
                val = 1
        summ += val
    return summ


def build_message(chat_id, dealer_reveal=False):
    games[chat_id]['msg'] = '[BJ] '
    if dealer_reveal:
        games[chat_id]['msg'] += f'\nВаша рука: {get_hand_translation(games[chat_id]["player_hand"])}' \
                                 f'\nРука дилера: {get_hand_translation(games[chat_id]["dealer_hand"])}'
    else:
        hand_len = len(games[chat_id]["dealer_hand"])
        dealer_hand = ''
        for card, i in zip(games[chat_id]["dealer_hand"], range(0, hand_len)):
            if i == 0:
                dealer_hand += get_card_translation(card)
            else:
                dealer_hand += ', [X]'
        games[chat_id]['msg'] += f'\nВаша рука: {get_hand_translation(games[chat_id]["player_hand"])}' \
                                 f'\nРука дилера: {dealer_hand}'


def start_game(chat_id):
    if chat_id not in games.keys():
        games[chat_id] = {
            'is_in_game': True,
            'deck': get_new_deck(),
            'dealer_hand': [],
            'player_hand': [],
            'msg': ''
        }
        return player_add(chat_id, True)
    elif not games[chat_id]['is_in_game']:
        games[chat_id]['is_in_game'] = True
        games[chat_id]['deck'] = get_new_deck()
        games[chat_id]['dealer_hand'] = []
        games[chat_id]['player_hand'] = []
        games[chat_id]['msg'] = ''
        return player_add(chat_id, True)
    else:
        return 'Сначала доиграйте текущую партию!'


def check_win(chat_id, dealer_hand: list, player_hand: list):
    dealer_sum = get_hand_sum(dealer_hand)
    player_sum = get_hand_sum(player_hand)
    if (dealer_sum > 21 and player_sum > 21) or (dealer_sum == player_sum):
        games[chat_id]['is_in_game'] = False
        build_message(chat_id, True)
        games[chat_id]['msg'] += '\n\n<b>Ничья!</b>'
    else:
        if (dealer_sum > 21 or (dealer_sum < 21 and player_sum
                                == 21) or (21 >= player_sum > dealer_sum)) and player_sum <= 21:
            games[chat_id]['is_in_game'] = False
            build_message(chat_id, True)
            games[chat_id]['msg'] += '\n\n<b>Поздравляю, вы победили!</b>'
        else:
            games[chat_id]['is_in_game'] = False
            build_message(chat_id, True)
            games[chat_id]['msg'] += '\n\n<b>Вы проиграли</b>'


def dealer_add(chat_id, fill=False):
    summ = get_hand_sum(games[chat_id]['dealer_hand'])
    if summ <= 17:
        deck_size = len(games[chat_id]['deck'])
        games[chat_id]['dealer_hand'].append(games[chat_id]['deck'].pop(random.randint(0, deck_size - 1)))
        if fill:
            dealer_add(chat_id, True)
    elif summ >= 21:
        check_win(chat_id, games[chat_id]['dealer_hand'], games[chat_id]['player_hand'])


def player_add(chat_id, on_start=False):
    if not games[chat_id]['is_in_game']:
        return 'Сначала начните игру\n/bj'
    player_summ = get_hand_sum(games[chat_id]['player_hand'])
    deck_size = len(games[chat_id]['deck'])
    games[chat_id]['player_hand'].append(games[chat_id]['deck'].pop(random.randint(0, deck_size - 1)))
    if player_summ >= 21:
        dealer_add(chat_id, True)
        check_win(chat_id, games[chat_id]['dealer_hand'], games[chat_id]['player_hand'])
    else:
        dealer_add(chat_id, False)
        if get_hand_sum(games[chat_id]['dealer_hand']) >= 21:
            check_win(chat_id, games[chat_id]['dealer_hand'], games[chat_id]['player_hand'])
    if on_start:
        player_add(chat_id, False)
    else:
        build_message(chat_id)
    player_summ = get_hand_sum(games[chat_id]['player_hand'])
    dealer_summ = get_hand_sum(games[chat_id]['dealer_hand'])
    print(f'\ndealer: {dealer_summ}\nplayer: {player_summ}')
    return games[chat_id]['msg']


def player_stay(chat_id):
    if not games[chat_id]['is_in_game']:
        return 'Сначала начните игру\n<b>/bj</b>'
    games[chat_id]['msg'] = '[BJ] '
    dealer_add(chat_id, True)
    build_message(chat_id)
    check_win(chat_id, games[chat_id]['dealer_hand'], games[chat_id]['player_hand'])
    return games[chat_id]['msg']
