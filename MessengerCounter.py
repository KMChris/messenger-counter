import collections
import io
import json
import math
import zipfile
from urllib.error import URLError
from urllib.request import urlopen

import pandas as pd
from matplotlib import pyplot as plt


def count_messages():
    namelist = source.namelist()
    total, senders = {}, {x.split('/')[2] for x in namelist
                          if (x.endswith('/') and x.startswith('messages/inbox/') and x != 'messages/inbox/')}
    for sender in senders:
        messages, i = collections.Counter(), 0
        while True:
            try:
                i+=1
                messages += collections.Counter(pd.DataFrame(json.loads(
                    source.open('messages/inbox/' + sender + '/message_' + str(i) + '.json').read())[
                                                                 'messages']).iloc[:, 0])
            except KeyError:
                break
        total[sender] = {k.encode('iso-8859-1').decode('utf-8'): v for k, v in messages.items()}
        total[sender]['total'] = sum(messages.values())
    with open('messages.json', 'w', encoding='utf-8') as output:
        json.dump(total, output, ensure_ascii=False)


def count_characters():
    namelist = source.namelist()
    total, senders = {}, {x.split('/')[2] for x in namelist
                          if (x.endswith('/') and x.startswith('messages/inbox/') and x != 'messages/inbox/')}
    for sender in senders:
        counted_all, i = collections.Counter(), 0
        while True:
            try:
                i+=1
                frame = pd.DataFrame(json.loads(
                    source.open('messages/inbox/' + sender + '/message_' + str(i) + '.json').read())[
                                         'messages'])
                frame['counted'] = frame.apply(
                    lambda row: collections.Counter(str(row['content']).encode('iso-8859-1').decode('utf-8')), axis=1)
                counted_all += sum(frame['counted'], collections.Counter())
            except KeyError:
                break
        total[sender] = dict(counted_all)
    with open('messages_chars.json', 'w', encoding='utf-8') as output:
        json.dump(total, output, ensure_ascii=False)


def statistics(source):
    source = pd.DataFrame(source).fillna(0).astype('int')
    pd.set_option('display.max_rows', None)
    total_values = source.loc['total'].sort_values(ascending=False)
    print(total_values)
    print(total_values.describe())
    total_values = total_values.sort_values()
    plt.rcdefaults()
    plt.barh(total_values.index.astype(str).str[:10][-20:], total_values.iloc[-20:])
    plt.show()


def conversation_statistics(source, conversation):
    source = pd.DataFrame(source)
    source = source.loc[:, conversation]
    source = source[source > 0].sort_values(ascending=False).astype('int')
    pd.set_option('display.max_rows', None)
    print(source)


def user_statistics(source, user_name):
    source = source.loc[user_name]
    source = source[source > 0].sort_values(ascending=False)
    source.index = source.index.map(lambda x: x.split('_')[0][:30])
    pd.set_option('display.max_rows', None)
    print(user_name, 'statistics:')
    print(source)


def hours_conversation(conversation, delta=0.0):
    messages, i = collections.Counter(), 0
    while True:
        try:
            i+=1
            messages += collections.Counter(pd.to_datetime(pd.DataFrame(json.loads(
                source.open('messages/inbox/' + conversation + '/message_' + str(i) + '.json').read())[
                                                                            'messages']).iloc[:, 1],
                                                           unit='ms').dt.tz_localize('UTC').dt.tz_convert(
                'Europe/Warsaw').add(pd.Timedelta(hours=-delta)).dt.hour)  # +delta*3600000)%86400000//3600000)
        except KeyError:
            break
    messages = pd.DataFrame(messages, index=[0])
    print(messages.iloc[0].describe())
    plt.bar(messages.columns, messages.iloc[0])
    plt.xticks(list(range(24)), [f'{x % 24}:{int(abs((delta - int(delta)) * 60)):02}' for x in
                                 range(-(-math.floor(delta) % 24),
                                       math.floor(delta) % 24 if math.floor(delta) % 24 != 0 else 24)], rotation=90)
    plt.xlim(-1, 24)
    plt.savefig('messages.pdf')
    plt.show()


def hours_chats(delta=0.0):
    messages = collections.Counter()
    for sender in {x.split('/')[2] for x in source.namelist() if
                   (x.endswith('/') and x.startswith('messages/inbox/') and x != 'messages/inbox/')}:
        i = 0
        while True:
            try:
                i+=1
                messages += collections.Counter(pd.to_datetime(pd.DataFrame(json.loads(
                    source.open('messages/inbox/' + sender + '/message_' + str(i) + '.json').read())[
                                                                                'messages']).iloc[:, 1],
                                                               unit='ms').dt.tz_localize('UTC').dt.tz_convert(
                    'Europe/Warsaw').add(pd.Timedelta(hours=-delta)).dt.hour)
            except KeyError:
                break
    messages = pd.DataFrame(messages, index=[0])
    print(messages.iloc[0].describe())
    plt.bar(messages.columns, messages.iloc[0])
    plt.xticks(list(range(24)), [f'{x % 24}:{int(abs((delta - int(delta)) * 60)):02}' for x in
                                 range(-(-math.floor(delta) % 24),
                                       math.floor(delta) % 24 if math.floor(delta) % 24 != 0 else 24)], rotation=90)
    plt.xlim(-1, 24)
    plt.savefig('messages.pdf')
    plt.show()


def daily_conversation(conversation, delta=0.0):
    messages, i = collections.Counter(), 0
    while True:
        try:
            i+=1
            messages += collections.Counter(pd.to_datetime(pd.DataFrame(json.loads(
                source.open('messages/inbox/' + conversation + '/message_' + str(i) + '.json').read())[
                                                                            'messages']).iloc[:, 1],
                                                           unit='ms').dt.tz_localize('UTC').dt.tz_convert(
                'Europe/Warsaw').add(pd.Timedelta(hours=-delta)).dt.date)
        except KeyError:
            break
    messages = pd.DataFrame(messages, index=[0])
    print(messages.iloc[0].describe())
    plt.bar(messages.columns, messages.iloc[0])
    plt.savefig('messages.pdf')
    plt.show()


def daily_chats(delta=0.0):
    messages = collections.Counter()
    for sender in {x.split('/')[2] for x in source.namelist() if
                   (x.endswith('/') and x.startswith('messages/inbox/') and x != 'messages/inbox/')}:
        i = 0
        while True:
            try:
                i+=1
                messages += collections.Counter(pd.to_datetime(pd.DataFrame(json.loads(
                    source.open('messages/inbox/' + sender + '/message_' + str(i) + '.json').read())[
                                                                                'messages']).iloc[:, 1],
                                                               unit='ms').dt.tz_localize('UTC').dt.tz_convert(
                    'Europe/Warsaw').add(pd.Timedelta(hours=-delta)).dt.date)
            except KeyError:
                break
    messages = pd.Series(messages).sort_index()
    print(messages.describe())
    plt.bar(messages.index, messages)
    plt.savefig('messages.pdf')
    plt.show()


def monthly_conversation(conversation, delta=0.0):
    messages, i = collections.Counter(), 0
    while True:
        try:
            i+=1
            messages += collections.Counter(pd.to_datetime(pd.DataFrame(json.loads(
                source.open('messages/inbox/' + conversation + '/message_' + str(i) + '.json').read())[
                                                                            'messages']).iloc[:, 1], unit='ms').add(
                pd.Timedelta(days=-delta)).dt.to_period("M").astype(
                'datetime64[ns]'))  # TODO not working charts for monthly
        except KeyError:
            break
    messages = pd.Series(messages).sort_index()
    print(messages.describe())
    plt.bar(messages.index.astype(str), messages)
    plt.xticks(rotation=90)
    plt.subplots_adjust(bottom=0.2)
    plt.savefig('messages.pdf')
    plt.show()


def monthly_chats(delta=0.0):
    messages = collections.Counter()
    for sender in {x.split('/')[2] for x in source.namelist() if
                   (x.endswith('/') and x.startswith('messages/inbox/') and x != 'messages/inbox/')}:
        i = 0
        while True:
            try:
                i+=1
                messages += collections.Counter(pd.to_datetime(pd.DataFrame(json.loads(
                    source.open('messages/inbox/' + sender + '/message_' + str(i) + '.json').read())[
                                                                                'messages']).iloc[:, 1], unit='ms').add(
                    pd.Timedelta(days=-delta)).dt.to_period("M"))
            except KeyError:
                break
    messages = pd.DataFrame(messages, index=[0])
    print(messages.iloc[0].describe())
    plt.bar(messages.columns, messages.iloc[0])
    plt.savefig('messages.pdf')
    plt.show()


def yearly_conversation(conversation, delta=0.0):
    messages, i = collections.Counter(), 0
    while True:
        try:
            i+=1
            messages += collections.Counter(pd.to_datetime(pd.DataFrame(json.loads(
                source.open('messages/inbox/' + conversation + '/message_' + str(i) + '.json').read())[
                                                                            'messages']).iloc[:, 1],
                                                           unit='ms').dt.tz_localize('UTC').dt.tz_convert(
                'Europe/Warsaw').add(pd.Timedelta(weeks=-delta * 4)).dt.year)
        except KeyError:
            break
    messages = pd.DataFrame(messages, index=[0])
    print(messages.iloc[0].describe())
    plt.bar(messages.columns, messages.iloc[0])
    plt.savefig('messages.pdf')
    plt.show()


def yearly_chats(delta=0.0):

    messages = collections.Counter()
    for sender in {x.split('/')[2] for x in source.namelist() if
                   (x.endswith('/') and x.startswith('messages/inbox/') and x != 'messages/inbox/')}:
        i = 0
        while True:
            try:
                i+=1
                messages += collections.Counter(pd.to_datetime(pd.DataFrame(json.loads(
                    source.open('messages/inbox/' + sender + '/message_' + str(i) + '.json').read())[
                                                                                'messages']).iloc[:, 1],
                                                               unit='ms').dt.tz_localize('UTC').dt.tz_convert(
                    'Europe/Warsaw').add(pd.Timedelta(weeks=-delta * 4)).dt.year)
            except KeyError:
                break
    messages = pd.DataFrame(messages, index=[0])
    print(messages.iloc[0].describe())
    plt.bar(messages.columns, messages.iloc[0])
    plt.savefig('messages.pdf')
    plt.show()


def characters_statistics(data_source):
    data_source = pd.DataFrame(data_source)
    data_source['total'] = data_source.sum(axis=1)
    data_source = data_source.iloc[:, -1]
    data_source = data_source.sort_values(ascending=False).astype('int')
    pd.set_option('display.max_rows', None)
    print(data_source)
    print(data_source[data_source.index.isin(['0', '1', '2', '3', '4', '5', '6', '7,' '8', '9'])])
    print(data_source[data_source.index.isin(
        ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v',
         'w', 'x', 'y', 'z', 'ę', 'ó', 'ą', 'ś', 'ł', 'ż', 'ź', 'ć', 'ń'])])
    print(f'Total characters: {data_source.sum()}')


def characters_conversation_statistics(data_source, conversation): # TODO characters conversation statistics
    print()


while True:
    filename = input('Enter filename: ')
    try:
        source = zipfile.ZipFile(io.BytesIO(urlopen(f'file:./{filename}' if filename.endswith('.zip') else f'file:./{filename}.zip').read()))
        break
    except URLError:
        print('File not found, try again.')
while True:
    user_input = input('>').split(' ')
    if user_input[0] == 'exit':
        break
    if user_input[0] == '' or user_input[0] == 'count':
        count_messages()
    if user_input[0] == 'chars':
        count_characters()
    if user_input[0] == 'help' or user_input[0] == '?':
        print('Messenger Counter available commands:')
        print('  count - counts all messages and saves to messages.json')
        print('  chars - counts all characters and saves to messages_chars.json')
        print('  stats [conversation, -c] - displays statistics for counted messages')
        print('        [detailed statistics for specific conversation, character statistics]')
        print('  user [name] - detailed statistics for specific user')
        print('  yearly [name, -m] - daily messages')
        print('         [specific user, month difference]')
        print('  monthly [name, -d] - daily messages')
        print('          [specific user, day difference]')
        print('  daily [name, -h] - daily messages')
        print('        [specific user, hours difference]')
        print('  hours [name, -h] - hour distribution of messages')
        print('        [specific user, hours difference]')
        print('  help - displays this help prompt')
        print('  exit - exits the program')
    if user_input[0] == 'stats':
        if len(user_input) > 2 and user_input[2] == '-c':
            try:
                data = json.loads(open('messages_chars.json', 'r', encoding='utf-8').read())
                for key in data.keys():
                    if key.startswith(user_input[1]):
                        characters_conversation_statistics(data, key)
                        break
                else:
                    print('Conversation not found.')
            except FileNotFoundError:
                if input('Characters not counted. Count characters?[y/n] ').lower() == 'y':
                    count_characters()
        elif len(user_input) > 1 and not user_input[1] == '-c':
            try:
                data = json.loads(open('messages.json', 'r', encoding='utf-8').read())
                for key in data.keys():
                    if key.startswith(user_input[1]):
                        conversation_statistics(data, key)
                        break
                else:
                    print('Conversation not found.')
            except FileNotFoundError:
                if input('Messages not counted. Count messages?[y/n] ').lower() == 'y':
                    count_messages()
        elif len(user_input) > 1 and user_input[1] == '-c':
            try:
                data = json.loads(open('messages_chars.json', 'r', encoding='utf-8').read())
                characters_statistics(data)
            except FileNotFoundError:
                if input('Characters not counted. Count characters?[y/n] ').lower() == 'y':
                    count_characters()
        else:
            try:
                data = json.loads(open('messages.json', 'r', encoding='utf-8').read())
                statistics(data)
            except FileNotFoundError:
                if input('Messages not counted. Count messages?[y/n] ').lower() == 'y':
                    count_messages()
    if user_input[0] == 'user':
        if len(user_input) > 1:
            try:
                data = json.loads(open('messages.json', 'r', encoding='utf-8').read())
                data = pd.DataFrame(data).fillna(0).astype('int')
                for key in data.index:
                    if key.startswith(' '.join(user_input[1:])):
                        user_statistics(data, key)
                        break
                else:
                    print('Conversation not found.')
            except FileNotFoundError:
                if input('Messages not counted. Count messages?[y/n] ').lower() == 'y':
                    count_messages()
        else:
            print('Please specify user name.')
    if user_input[0] == 'daily':
        if len(user_input) > 1 and not user_input[1] == '-h':
            try:
                data = json.loads(open('messages.json', 'r', encoding='utf-8').read())
                if len(user_input) > 1:
                    for key in data.keys():
                        if key.startswith(user_input[1]):
                            if len(user_input) < 3:
                                daily_conversation(key)
                            else:
                                daily_conversation(key, float(user_input[2]))
                            break
                    else:
                        print('Conversation not found.')
                else:
                    print('Please specify conversation.')
            except FileNotFoundError:
                if input('Messages not counted. Count messages?[y/n] ').lower() == 'y':
                    count_messages()
        elif len(user_input) > 1 and user_input[1] == '-h':
            daily_chats(float(user_input[2]))
        else:
            daily_chats()
    if user_input[0] == 'monthly':
        if len(user_input) > 1 and not user_input[1] == '-d':
            try:
                data = json.loads(open('messages.json', 'r', encoding='utf-8').read())
                if len(user_input) > 1:
                    for key in data.keys():
                        if key.startswith(user_input[1]):
                            if len(user_input) < 3:
                                monthly_conversation(key)
                            else:
                                monthly_conversation(key, float(user_input[2]))
                            break
                    else:
                        print('Conversation not found.')
                else:
                    print('Please specify conversation.')
            except FileNotFoundError:
                if input('Messages not counted. Count messages?[y/n] ').lower() == 'y':
                    count_messages()
        elif len(user_input) > 1 and user_input[1] == '-d':
            monthly_chats(float(user_input[2]))
        else:
            monthly_chats()
    if user_input[0] == 'yearly':
        if len(user_input) > 1 and not user_input[1] == '-m':
            try:
                data = json.loads(open('messages.json', 'r', encoding='utf-8').read())
                if len(user_input) > 1:
                    for key in data.keys():
                        if key.startswith(user_input[1]):
                            if len(user_input) < 3:
                                yearly_conversation(key)
                            else:
                                yearly_conversation(key, float(user_input[2]))
                            break
                    else:
                        print('Conversation not found.')
                else:
                    print('Please specify conversation.')
            except FileNotFoundError:
                if input('Messages not counted. Count messages?[y/n] ').lower() == 'y':
                    count_messages()
        elif len(user_input) > 1 and user_input[1] == '-m':
            yearly_chats(float(user_input[2]))
        else:
            yearly_chats()
    if user_input[0] == 'hours':
        if len(user_input) > 1 and not user_input[1] == '-h':
            try:
                data = json.loads(open('messages.json', 'r', encoding='utf-8').read())
                if len(user_input) > 1:
                    for key in data.keys():
                        if key.startswith(user_input[1]):
                            if len(user_input) < 3:
                                hours_conversation(key)
                            else:
                                hours_conversation(key, float(user_input[2]))
                            break
                    else:
                        print('Conversation not found.')
                else:
                    print('Please specify conversation.')
            except FileNotFoundError:
                if input('Messages not counted. Count messages?[y/n] ').lower() == 'y':
                    count_messages()
        elif len(user_input) > 1 and user_input[1] == '-h':
            hours_chats(float(user_input[2]))
        else:
            hours_chats()

# def print_statistics():
#     print('Total conversations:', len(senders))
#     # for loop
#     print('–' * 50)
#     print('Conversation with', sender.split('_')[0])
#     print('Messages in total:', sum(messages.values()))
#     print()
#     maximum = max(len(item) for item in messages.keys())
#     for key, value in messages.items():
#         print(f"{key.encode('iso-8859-1').decode('utf-8'):<{maximum}}{value:>10}")
