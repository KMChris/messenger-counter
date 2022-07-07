import collections
import io
import json
import math
import zipfile
import logging
from urllib.error import URLError
from urllib.request import urlopen
import pandas as pd
from matplotlib import pyplot as plt


# Getting data

def set_source(filename):
    """
    Sets source global variable to the path of .zip file.

    :param filename: path to the downloaded .zip file
    :return: None

    You can provide relative path to file
    >>> set_source('facebook-YourName.zip')

    Absolute path (works only on Windows)
    >>> set_source('C:/Users/Admin/Downloads/facebook-YourName.zip')
    """
    filename = f'file:///{filename}' if filename[1] == ':' \
        else (f'file:./{filename}' if filename.endswith('.zip') else f'file:./{filename}.zip')
    try:
        global source
        source = zipfile.ZipFile(io.BytesIO(urlopen(filename).read()))
    except URLError:
        logging.error('File not found, try again.')

def get_data(conversation=None, chars=False, user=False):
    """
    Reads data from messages.json or messages_chars.json
    and finds key based on the beginning of the string.

    :param conversation: beginning of the conversation id
                         or None for overall statistics (default None)
    :param chars: True for counting chars in messages_chars.json,
                  False for counting messages in messages.json (default False)
    :param user: True for user name instead of conversation id,
                 False otherwise (default False)
    :return: dictionary containing the data and if applicable
             a key pointing to a specific conversation, otherwise None
    """
    try:
        data = json.loads(open('messages_chars.json' if chars else 'messages.json', 'r', encoding='utf-8').read())
        if user:
            data = pd.DataFrame(data).fillna(0).astype('int')
            for key in data.index:
                if key.lower().startswith(conversation.lower()):
                    return data, key
            else:
                logging.error('Conversation not found.')
                return None, None
        if conversation is not None:
            for key in data.keys():
                if key.lower().startswith(conversation.lower()):
                    return data, key
            else:
                logging.error('Conversation not found.')
                return None, None
        else:
            return data, None
    except FileNotFoundError:
        logging.error('Characters not counted.' if chars else 'Messages not counted.')


# Counting messages and characters

def count_messages():
    """
    Counts messages and saves output to messages.json.

    :return: None
    """
    namelist = source.namelist()
    total, senders = {}, {x.split('/')[2] for x in namelist
                          if ((x.endswith('/') and x.startswith('messages/inbox/') and x != 'messages/inbox/') or (x.endswith('/') and x.startswith('messages/archived_threads/') and x != 'messages/archived_threads/'))}
    for sender in senders:
        messages, i = collections.Counter(), 0
        while True:
            try:
                i += 1
                messages += collections.Counter(pd.DataFrame(json.loads(
                    source.open('messages/inbox/' + sender + '/message_' + str(i) + '.json').read())[
                                                                 'messages'])['sender_name'])
            except KeyError:
                try:
                    messages += collections.Counter(pd.DataFrame(json.loads(
                    source.open('messages/archived_threads/' + sender + '/message_' + str(i) + '.json').read())[
                                                                 'messages'])['sender_name'])
                except KeyError:
                    break
        total[sender] = {k.encode('iso-8859-1').decode('utf-8'): v for k, v in messages.items()}
        total[sender]['total'] = sum(messages.values())
    with open('messages.json', 'w', encoding='utf-8') as output:
        json.dump(total, output, ensure_ascii=False)

def count_characters():
    """
    Counts characters from messages and saves output to messages_chars.json.

    :return: None
    """
    namelist = source.namelist()
    total, senders = {}, {x.split('/')[2] for x in namelist
                          if ((x.endswith('/') and x.startswith('messages/inbox/') and x != 'messages/inbox/') or (x.endswith('/') and x.startswith('messages/archived_threads/') and x != 'messages/archived_threads/'))}
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
                try:
                    frame = pd.DataFrame(json.loads(
                        source.open('messages/archived_threads/' + sender + '/message_' + str(i) + '.json').read())['messages'])
                    frame['counted'] = frame.apply(
                        lambda row: collections.Counter(str(row['content']).encode('iso-8859-1').decode('utf-8')), axis=1)
                    counted_all += sum(frame['counted'], collections.Counter())
                except KeyError:
                    break
        total[sender] = dict(counted_all)
    with open('messages_chars.json', 'w', encoding='utf-8') as output:
        json.dump(total, output, ensure_ascii=False)

def count(chars=False):
    """
    Counts messages or characters from messages
    and saves output to the file.

    :param chars: True for counting characters,
                  False for counting messages (default False)
    :return: None
    """
    if chars:
        count_characters()
    else:
        count_messages()


# Statistics

def statistics(data_source, conversation=None, chars=False):
    """
    Prints statistics of given data source.

    :param data_source: dictionary containing prepared data generated
                        by the get_data() function
    :param conversation: conversation id or None for overall statistics
                         (default None)
    :param chars: True for character statistics instead of messages,
                  False otherwise (default False)
    :return: None
    """
    if conversation is None:
        if chars:
            characters_statistics(data_source)
        else:
            messages_statistics(data_source)
    else:
        if chars:
            characters_conversation_statistics(data_source, conversation)
        else:
            print(conversation)
            conversation_statistics(data_source, conversation)

def messages_statistics(data_source):
    """
    Prints messages overall statistics of given data source.

    :param data_source: dictionary containing prepared data generated
                        by the get_data() function
    :return: None
    """
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
    """
    Prints messages statistics for specific conversation of given data source.

    :param data_source: dictionary containing prepared data generated
                        by the get_data() function
    :param conversation: conversation id, or key from get_data() function
    :return: None
    """
    data_source = pd.DataFrame(data_source)
    data_source = data_source.loc[:, conversation]
    data_source = data_source[data_source > 0].sort_values(ascending=False).astype('int')
    pd.set_option('display.max_rows', None)
    print(data_source)

def characters_statistics(data_source):
    """
    Prints characters statistics of given data source.

    :param data_source: dictionary containing prepared data generated
                        by the get_data() function
    :return: None
    """
    data_source = pd.DataFrame(data_source)
    data_source['total'] = data_source.sum(axis=1)
    data_source = data_source.iloc[:, -1]
    data_source = data_source.sort_values(ascending=False).astype('int')
    pd.set_option('display.max_rows', None)
    print(data_source)
    print(f'Total characters: {data_source.sum()}')

# TODO characters conversation statistics
def characters_conversation_statistics(data_source, conversation):
    """
    Prints characters statistics for specific conversation of given data source.

    :param data_source: dictionary containing prepared data generated
                        by the get_data() function
    :param conversation: conversation id, or key from get_data() function
    :return: None
    """
    data_source = pd.DataFrame(data_source)
    data_source = data_source[conversation].dropna()
    data_source = data_source.sort_values(ascending=False).astype('int')
    pd.set_option('display.max_rows', None)
    print(data_source)
    print(f'Total characters: {data_source.sum()}')

# User statistics

def user_statistics(data_source, user_name):
    """
    Prints detailed statistics for specific person of given data source.

    :param data_source: dictionary containing prepared data generated
                        by the get_data() function
    :param user_name: person name, or key from get_data() function
    :return: None
    """
    data_source = data_source.loc[user_name]
    data_source = data_source[data_source > 0].sort_values(ascending=False)
    data_source.index = data_source.index.map(lambda x: x.split('_')[0][:30])
    pd.set_option('display.max_rows', None)
    print(user_name, 'statistics:')
    print(data_source)


# Intervals

def interval_count(inbox_name, function, delta=0.0):
    """
    Counts number of messages based on given timeframe function

    :param inbox_name: directory name that contains requested messages
                       (usually conversation id)
    :param function: pandas function that returns requested time part
    :param delta: number of hours to time shift by
                  and count messages differently (default 0.0)
    :return: dictionary of number of messages grouped by timeframe
    """
    messages, i = collections.Counter(), 0
    while True:
        try:
            i += 1
            # iterates over all .json files in requested directory
            messages += collections.Counter(function(pd.to_datetime(pd.DataFrame(json.loads(
                source.open('messages/inbox/' + inbox_name + '/message_' + str(i) + '.json').read())[
                            'messages']).iloc[:, 1], unit='ms').dt.tz_localize('UTC').dt.tz_convert(
                            'Europe/Warsaw').add(pd.Timedelta(hours=-delta))))
        except KeyError:
            try:
                # iterates over all .json files in requested directory
                messages += collections.Counter(function(pd.to_datetime(pd.DataFrame(json.loads(
                    source.open('messages/archived_threads/' + inbox_name + '/message_' + str(i) + '.json').read())[
                                'messages']).iloc[:, 1], unit='ms').dt.tz_localize('UTC').dt.tz_convert(
                                'Europe/Warsaw').add(pd.Timedelta(hours=-delta))))
            except KeyError:
                break
    return messages

def interval_plot(messages):
    """
    Shows chart based on previously defined timeframe

    :param messages: dictionary of number of messages
                     grouped by timeframe
    :return: None
    """
    messages = pd.Series(messages).sort_index()
    print(messages.describe())
    plt.bar(messages.index, messages)
    plt.savefig('messages.pdf')
    plt.show()


# Hours

def hours(difference, conversation=None):
    """
    Shows chart of average number of messages
    send by hour throughout the day.

    :param difference: number of hours to time shift by
                       and show statistics differently
    :param conversation: conversation id or None for statistics
                         from all conversations (default None)
    :return: None
    """
    if conversation is None:
        hours_chats(difference)
    else:
        data = json.loads(open('messages.json', 'r', encoding='utf-8').read())
        for key in data.keys():
            if key.lower().startswith(conversation.lower()):
                hours_conversation(key, difference)
                break
        else:
            print('Conversation not found.')

def hours_conversation(conversation, delta=0.0):
    """
    Shows chart of average number of messages send
    in specific conversation by hour throughout the day.

    :param conversation: conversation id, or key from get_data() function
    :param delta: number of hours to time shift by
                  and show statistics differently (default 0.0)
    :return: None
    """
    hours_plot(interval_count(conversation, lambda x: x.dt.hour, delta), delta)

def hours_chats(delta=0.0):
    """
    Shows chart of average number of messages send
    across all conversations by hour throughout the day.

    :param delta: number of hours to time shift by
                  and show statistics differently (default 0.0)
    :return: None
    """
    messages = collections.Counter()
    for sender in {x.split('/')[2] for x in source.namelist()
                   if ((x.endswith('/') and x.startswith('messages/inbox/') and x != 'messages/inbox/') or (x.endswith('/') and x.startswith('messages/archived_threads/') and x != 'messages/archived_threads/'))}:
        messages += interval_count(sender, lambda x: x.dt.hour, delta)
    hours_plot(messages, delta)

def hours_plot(messages, delta):
    """
    Shows chart of average number of messages
    grouped by hour throughout the day.

    :param messages: dictionary of number of messages
                     grouped by timeframe
    :param delta: number of hours to time shift by
                  and show statistics differently
    :return: None
    """
    messages = pd.DataFrame(messages, index=[0])
    print(messages.iloc[0].describe())
    plt.bar(messages.columns, messages.iloc[0])
    plt.xticks(list(range(24)), [f'{x % 24}:{int(abs((delta - int(delta)) * 60)):02}'
                                 for x in range(-(-math.floor(delta) % 24),
                                 math.floor(delta) % 24 if math.floor(delta) % 24 != 0 else 24)], rotation=90)
    plt.xlim(-1, 24)
    plt.savefig('messages.pdf')
    plt.show()


# Daily

def daily(difference, conversation=None):
    """
    Shows chart of number of messages per day.

    :param difference: number of hours to time shift by
                       and show statistics differently
    :param conversation: conversation id or None for statistics
                         from all conversations (default None)
    :return: None
    """
    if conversation is None:
        daily_chats(difference)
    else:
        data = json.loads(open('messages.json', 'r', encoding='utf-8').read())
        for key in data.keys():
            if key.lower().startswith(conversation.lower()):
                daily_conversation(key, difference)
                break
        else:
            print('Conversation not found.')

def daily_conversation(conversation, delta=0.0):
    """
    Shows chart of number of messages per day
    from the beginning of the conversation.

    :param conversation: conversation id, or key from get_data() function
    :param delta: number of hours to time shift by
                  and show statistics differently (default 0.0)
    :return: None
    """
    interval_plot(interval_count(conversation, lambda x: x.dt.date, delta))

def daily_chats(delta=0.0):
    """
    Shows chart of number of messages per day
    across all conversation.

    :param delta: number of hours to time shift by
                  and show statistics differently (default 0.0)
    :return: None
    """
    messages = collections.Counter()
    for sender in {x.split('/')[2] for x in source.namelist() if
                   ((x.endswith('/') and x.startswith('messages/inbox/') and x != 'messages/inbox/') or (x.endswith('/') and x.startswith('messages/archived_threads/') and x != 'messages/archived_threads/'))}:
        messages += interval_count(sender, lambda x: x.dt.date, delta)
    interval_plot(messages)


# Monthly (not working)

def monthly_conversation(conversation):  # TODO not working charts for monthly
    """
    Shows chart of number of messages per month.

    :param conversation: conversation id or None for statistics
                         from all conversations (default None)
    :return: None
    """
    interval_plot(interval_count(conversation, lambda x: x.dt.to_period("M").astype('datetime64[ns]')))

def monthly_chats():
    """
    Shows chart of number of messages per month
    across all conversation.

    :return: None
    """
    messages = collections.Counter()
    for sender in {x.split('/')[2] for x in source.namelist() if
                   ((x.endswith('/') and x.startswith('messages/inbox/') and x != 'messages/inbox/') or (x.endswith('/') and x.startswith('messages/archived_threads/') and x != 'messages/archived_threads/'))}:
        messages += interval_count(sender, lambda x: x.dt.to_period("M").astype('datetime64[ns]'))
    interval_plot(messages)


# Yearly

def yearly(conversation=None):
    """
    Shows chart of number of messages per year.

    :param conversation: conversation id or None for statistics
                         from all conversations (default None)
    :return: None
    """
    if conversation is None:
        yearly_chats()
    else:
        data = json.loads(open('messages.json', 'r', encoding='utf-8').read())
        for key in data.keys():
            if key.lower().startswith(conversation.lower()):
                yearly_conversation(key)
                break
        else:
            print('Conversation not found.')

def yearly_conversation(conversation):
    """
    Shows chart of number of messages per year
    from the beginning of the conversation.

    :param conversation: conversation id, or key from get_data() function
    :return: None
    """
    interval_plot(interval_count(conversation, lambda x: x.dt.year))

def yearly_chats():
    """
    Shows chart of number of messages per year
    across all conversation.

    :return: None
    """
    messages = collections.Counter()
    for sender in {x.split('/')[2] for x in source.namelist()
                   if ((x.endswith('/') and x.startswith('messages/inbox/') and x != 'messages/inbox/') or (x.endswith('/') and x.startswith('messages/archived_threads/') and x != 'messages/archived_threads/'))}:
        messages += interval_count(sender, lambda x: x.dt.year)
    messages = pd.DataFrame(messages, index=[0])
    print(messages.iloc[0].describe())
    plt.bar(messages.columns, messages.iloc[0])
    plt.savefig('messages.pdf')
    plt.show()


if __name__=='__main__':
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
                    messages_statistics(data)
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
