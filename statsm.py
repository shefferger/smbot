import datetime
import os
import pickle

chats = {}


# chats = { 0:
#              {'smoking':
#                   {'2011-03-04' :
#                           ['18:55', '19:55']
#                   },
#               'weather':
#                   {'2012-04-05' :
#                           ['15:23']
#                   }
#              }
#         }


def save():
    with open('stats.bin', 'wb') as datafile:
        pickle.dump(chats, datafile)


# actions: smoking, weather, 2mins, timeleft
def register(chat_id, action='smoking'):
    global chats
    date = datetime.date.today()
    time = datetime.datetime.today().time()
    if chat_id not in chats.keys():
        chats[chat_id] = {action: {date: [time]}}
    else:
        if action not in chats[chat_id].keys():
            chats[chat_id][action] = {date: [time]}
        else:
            if date not in chats[chat_id][action].keys():
                chats[chat_id][action][date] = [time]
            else:
                chats[chat_id][action][date].append(time)
    save()


def get_stats(chat_id):
    return chats[chat_id]


if not os.path.exists('stats.bin'):
    save()
else:
    with open('stats.bin', 'rb') as f:
        chats = pickle.load(f)
