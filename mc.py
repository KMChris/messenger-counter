from MessengerCounter import MessengerCounter
import pandas as pd
import argparse
import json


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('file',
                        help='Path to .zip file downloaded from Facebook',
                        nargs='?')
    args = parser.parse_args()
    while True:
        if args.file is not None:
            filename = args.file
        else:
            filename = input('Enter filename: ')
        try:
            counter = MessengerCounter(filename)
            break
        except FileNotFoundError:
            print('File not found.')
    while True:
        user_input = input('>').split(' ')
        if user_input[0] == 'exit':
            counter.close()
            break
        if user_input[0] == 'count':
            counter.count_messages()
        if user_input[0] == 'words':
            counter.count_words()
        if user_input[0] == 'chars':
            counter.count_characters()
        if user_input[0] == 'help' or user_input[0] == '?':
            print('Messenger Counter available commands:')
            print('  count - counts all messages and saves to messages.json')
            print('  chars - counts all characters and saves to messages_chars.json')
            print('  words - counts all words and saves to messages_words.json (time consuming)')
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
                            counter.characters_conversation_statistics(data, key)
                            break
                    else:
                        print('Conversation not found.')
                except FileNotFoundError:
                    if input('Characters not counted. Count characters?[y/n] ').lower() == 'y':
                        counter.count_characters()
            if len(user_input) > 3 and user_input[3] == '-w':
                try:
                    data = json.loads(open('messages_words.json', 'r', encoding='utf-8').read())
                    for key in data.keys():
                        if key.startswith(user_input[1]):
                            counter.words_conversation_statistics(data[key], user_input[2])
                            break
                    else:
                        print('Conversation not found.')
                except FileNotFoundError:
                    if input('Words not counted. Count words?[y/n] ').lower() == 'y':
                        counter.count_words()
            elif len(user_input) > 1 and not user_input[1] == '-c':
                try:
                    data = json.loads(open('messages.json', 'r', encoding='utf-8').read())
                    for key in data.keys():
                        if key.startswith(user_input[1]):
                            counter.conversation_statistics(data, key)
                            break
                    else:
                        print('Conversation not found.')
                except FileNotFoundError:
                    if input('Messages not counted. Count messages?[y/n] ').lower() == 'y':
                        counter.count_messages()
            elif len(user_input) > 1 and user_input[1] == '-c':
                try:
                    data = json.loads(open('messages_chars.json', 'r', encoding='utf-8').read())
                    counter.characters_statistics(data)
                except FileNotFoundError:
                    if input('Characters not counted. Count characters?[y/n] ').lower() == 'y':
                        counter.count_characters()
            else:
                try:
                    data = json.loads(open('messages.json', 'r', encoding='utf-8').read())
                    counter.messages_statistics(data)
                except FileNotFoundError:
                    if input('Messages not counted. Count messages?[y/n] ').lower() == 'y':
                        counter.count_messages()
        if user_input[0] == 'user':
            if len(user_input) > 1:
                try:
                    data = json.loads(open('messages.json', 'r', encoding='utf-8').read())
                    data = pd.DataFrame(data).fillna(0).astype('int')
                    for key in data.index:
                        if key.startswith(' '.join(user_input[1:])):
                            counter.user_statistics(data, key)
                            break
                    else:
                        print('Conversation not found.')
                except FileNotFoundError:
                    if input('Messages not counted. Count messages?[y/n] ').lower() == 'y':
                        counter.count_messages()
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
                                    counter.daily_conversation(key)
                                else:
                                    counter.daily_conversation(key, float(user_input[2]))
                                break
                        else:
                            print('Conversation not found.')
                    else:
                        print('Please specify conversation.')
                except FileNotFoundError:
                    if input('Messages not counted. Count messages?[y/n] ').lower() == 'y':
                        counter.count_messages()
            elif len(user_input) > 1 and user_input[1] == '-h':
                counter.daily_chats(float(user_input[2]))
            else:
                counter.daily_chats()
        if user_input[0] == 'monthly':
            if len(user_input) > 1:
                try:
                    data = json.loads(open('messages.json', 'r', encoding='utf-8').read())
                    if len(user_input) > 1:
                        for key in data.keys():
                            if key.startswith(user_input[1]):
                                counter.monthly_conversation(key)
                        else:
                            print('Conversation not found.')
                    else:
                        print('Please specify conversation.')
                except FileNotFoundError:
                    if input('Messages not counted. Count messages?[y/n] ').lower() == 'y':
                        counter.count_messages()
            else:
                counter.monthly_chats()
        if user_input[0] == 'yearly':
            if len(user_input) > 1:
                try:
                    data = json.loads(open('messages.json', 'r', encoding='utf-8').read())
                    if len(user_input) > 1:
                        for key in data.keys():
                            if key.startswith(user_input[1]):
                                counter.yearly_conversation(key)
                                break
                        else:
                            print('Conversation not found.')
                    else:
                        print('Please specify conversation.')
                except FileNotFoundError:
                    if input('Messages not counted. Count messages?[y/n] ').lower() == 'y':
                        counter.count_messages()
            else:
                counter.yearly_chats()
        if user_input[0] == 'hours':
            if len(user_input) > 1 and not user_input[1] == '-h':
                try:
                    data = json.loads(open('messages.json', 'r', encoding='utf-8').read())
                    if len(user_input) > 1:
                        for key in data.keys():
                            if key.startswith(user_input[1]):
                                if len(user_input) < 3:
                                    counter.hours_conversation(key)
                                else:
                                    counter.hours_conversation(key, float(user_input[2]))
                                break
                        else:
                            print('Conversation not found.')
                    else:
                        print('Please specify conversation.')
                except FileNotFoundError:
                    if input('Messages not counted. Count messages?[y/n] ').lower() == 'y':
                        counter.count_messages()
            elif len(user_input) > 1 and user_input[1] == '-h':
                counter.hours_chats(float(user_input[2]))
            else:
                counter.hours_chats()
