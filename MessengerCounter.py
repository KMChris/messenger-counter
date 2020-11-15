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
                i += 1
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
                i += 1
                frame = pd.DataFrame(json.loads(
                    source.open('messages/inbox/' + sender + '/message_' + str(i) + '.json').read())['messages'])
                frame['counted'] = frame.apply(
                    lambda row: collections.Counter(str(row['content']).encode('iso-8859-1').decode('utf-8')), axis=1)
                counted_all += sum(frame['counted'], collections.Counter())
            except KeyError:
                break
        total[sender] = dict(counted_all)
    with open('messages_chars.json', 'w', encoding='utf-8') as output:
        json.dump(total, output, ensure_ascii=False)


def statistics(data_source):
    data_source = pd.DataFrame(data_source).fillna(0).astype('int')
    pd.set_option('display.max_rows', None)
    total_values = data_source.loc['total'].sort_values(ascending=False)
    print(total_values)
    print(total_values.describe())
    total_values = total_values.sort_values()
    plt.rcdefaults()
    plt.barh(total_values.index.astype(str).str[:10][-20:], total_values.iloc[-20:])
    plt.show()


def conversation_statistics(data_source, conversation):
    data_source = pd.DataFrame(data_source)
    data_source = data_source.loc[:, conversation]
    data_source = data_source[data_source > 0].sort_values(ascending=False).astype('int')
    pd.set_option('display.max_rows', None)
    print(data_source)


def user_statistics(data_source, user_name):
    data_source = data_source.loc[user_name]
    data_source = data_source[data_source > 0].sort_values(ascending=False)
    data_source.index = data_source.index.map(lambda x: x.split('_')[0][:30])
    pd.set_option('display.max_rows', None)
    print(user_name, 'statistics:')
    print(data_source)


def interval_count(inbox_name, function, delta=0.0):
    messages, i = collections.Counter(), 0
    while True:
        try:
            i += 1
            messages += collections.Counter(function(pd.to_datetime(pd.DataFrame(json.loads(
                source.open('messages/inbox/' + inbox_name + '/message_' + str(i) + '.json').read())[
                                                                                     'messages']).iloc[:, 1],
                                                                    unit='ms').dt.tz_localize('UTC').dt.tz_convert(
                'Europe/Warsaw').add(pd.Timedelta(hours=-delta))))
        except KeyError:
            break
    return messages


def interval_plot(messages):
    messages = pd.Series(messages).sort_index()
    print(messages.describe())
    plt.bar(messages.index, messages)
    plt.savefig('messages.pdf')
    plt.show()


def hours_plot(messages, delta):
    messages = pd.DataFrame(messages, index=[0])
    print(messages.iloc[0].describe())
    plt.bar(messages.columns, messages.iloc[0])
    plt.xticks(list(range(24)), [f'{x % 24}:{int(abs((delta - int(delta)) * 60)):02}'
                                 for x in range(-(-math.floor(delta) % 24),
                                                math.floor(delta) % 24 if math.floor(delta) % 24 != 0 else 24)],
               rotation=90)
    plt.xlim(-1, 24)
    plt.savefig('messages.pdf')
    plt.show()


def hours_conversation(conversation, delta=0.0):
    hours_plot(interval_count(conversation, lambda x: x.dt.hour, delta), delta)


def hours_chats(delta=0.0):
    messages = collections.Counter()
    for sender in {x.split('/')[2] for x in source.namelist()
                   if (x.endswith('/') and x.startswith('messages/inbox/') and x != 'messages/inbox/')}:
        messages += interval_count(sender, lambda x: x.dt.hour, delta)
    hours_plot(messages, delta)


def daily_conversation(conversation, delta=0.0):
    interval_plot(interval_count(conversation, lambda x: x.dt.date, delta))


def daily_chats(delta=0.0):
    messages = collections.Counter()
    for sender in {x.split('/')[2] for x in source.namelist() if
                   (x.endswith('/') and x.startswith('messages/inbox/') and x != 'messages/inbox/')}:
        messages += interval_count(sender, lambda x: x.dt.date, delta)
    interval_plot(messages)


def monthly_conversation(conversation):  # TODO not working charts for monthly
    interval_plot(interval_count(conversation, lambda x: x.dt.to_period("M").astype('datetime64[ns]')))


def monthly_chats():
    messages = collections.Counter()
    for sender in {x.split('/')[2] for x in source.namelist() if
                   (x.endswith('/') and x.startswith('messages/inbox/') and x != 'messages/inbox/')}:
        messages += interval_count(sender, lambda x: x.dt.to_period("M").astype('datetime64[ns]'))
    interval_plot(messages)


def yearly_conversation(conversation):
    interval_plot(interval_count(conversation, lambda x: x.dt.year))


def yearly_chats():
    messages = collections.Counter()
    for sender in {x.split('/')[2] for x in source.namelist()
                   if (x.endswith('/') and x.startswith('messages/inbox/') and x != 'messages/inbox/')}:
        messages += interval_count(sender, lambda x: x.dt.year)
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
    print(f'Total characters: {data_source.sum()}')


def characters_conversation_statistics(data_source, conversation):  # TODO characters conversation statistics
    print()


while True:
    filename = input('Enter filename: ')
    filename = f'file:///{filename}' if filename[1] == ':'\
         else (f'file:./{filename}' if filename.endswith('.zip') else f'file:./{filename}.zip')
    try:
        source = zipfile.ZipFile(io.BytesIO(urlopen(filename).read()))
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
        print('  yearly [name] - yearly messages')
        print('         [specific user]')
        # print('  monthly [name, -d] - monthly messages (available soon)')
        # print('          [specific user, day difference]')
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
        if len(user_input) > 1:
            try:
                data = json.loads(open('messages.json', 'r', encoding='utf-8').read())
                if len(user_input) > 1:
                    for key in data.keys():
                        if key.startswith(user_input[1]):
                            monthly_conversation(key)
                    else:
                        print('Conversation not found.')
                else:
                    print('Please specify conversation.')
            except FileNotFoundError:
                if input('Messages not counted. Count messages?[y/n] ').lower() == 'y':
                    count_messages()
        else:
            monthly_chats()
    if user_input[0] == 'yearly':
        if len(user_input) > 1:
            try:
                data = json.loads(open('messages.json', 'r', encoding='utf-8').read())
                if len(user_input) > 1:
                    for key in data.keys():
                        if key.startswith(user_input[1]):
                            yearly_conversation(key)
                            break
                    else:
                        print('Conversation not found.')
                else:
                    print('Please specify conversation.')
            except FileNotFoundError:
                if input('Messages not counted. Count messages?[y/n] ').lower() == 'y':
                    count_messages()
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
