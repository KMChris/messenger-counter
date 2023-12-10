from src.counter import MessengerCounter
import pandas as pd
import argparse
import logging
import json


class Loader:
    def __init__(self):
        self.data = {
            'messages': {},
            'chars': {},
            'words': {}
        }
        self.filenames = {
            'messages': 'messages.json',
            'chars': 'messages_chars.json',
            'words': 'messages_words.json'
        }
        self.save = False
        self.from_files()

    def from_files(self):
        for data_type in self.data.keys():
            try:
                file = open(self.filenames[data_type], 'r', encoding='utf-8').read()
                self.data[data_type] = json.loads(file)
            except FileNotFoundError:
                pass

    def to_file(self, data_type='messages'):
        if self.data[data_type]:
            with open(self.filenames[data_type], 'w', encoding='utf-8') as file:
                json.dump(self.data[data_type], file, ensure_ascii=False)

    def require(self, data_type='messages'):
        if not self.data[data_type]:
            if input(f'{data_type.capitalize()} not counted.'
                     f'Count {data_type}?[y/n] ').lower() == 'y':
                self.data[data_type] = counter.count(data_type)
            else:
                return False
        return True

    def find(self, name, where):
        # TODO search by actual name
        for key in self.data[where].keys():
            if key.startswith(name):
                return key
        else:
            logging.error('Conversation not found.')

    def __getitem__(self, item):
        return self.data[item]

    def __setitem__(self, item, value):
        self.data[item] = value
        if self.save:
            self.to_file(item)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('file', nargs='?',
                        help='Path to .zip file downloaded from Facebook')
    args = parser.parse_args()
    if args.file is not None:
        counter = MessengerCounter(args.file)
    else:
        while True:
            filename = input('Enter filename: ')
            try:
                counter = MessengerCounter(filename)
                break
            except Exception as e:
                print(e)

    loader = Loader()
    while True:
        user_input = input('>').split(' ')
        if user_input[0] == 'exit':
            counter.close()
            break
        elif user_input[0] == 'count':
            loader.save = len(user_input) > 2 and 's' in user_input[2]
            if len(user_input) > 1:
                if 'm' in user_input[1]:
                    loader['messages'] = counter.count('messages')
                if 'c' in user_input[1]:
                    loader['chars'] = counter.count('chars')
                if 'w' in user_input[1]:
                    loader['words'] = counter.count('words')
            else:
                loader['messages'] = counter.count('messages')
        elif user_input[0] == 'save':
            for data_type in loader.data.keys():
                loader.to_file(data_type)
        elif user_input[0] == 'load':
            loader.from_files()
        elif user_input[0] in ('help', '?'):
            print('Messenger Counter available commands:')
            print('  count [mcw] [s] - counts messages, characters and words, where:')
            print('         m - messages (default)')
            print('         c - characters')
            print('         w - words')
            print('         s - save to .json file')
            print('  save - saves counted messages, characters and words to .json files')
            print('  load - loads counted messages, characters and words from .json files')
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
        elif user_input[0] == 'stats':
            if len(user_input) > 2 and user_input[2] == '-c':
                if loader.require('chars'):
                    key = loader.find(user_input[1], 'chars')
                    if key:
                        counter.statistics(loader['chars'], key, 'chars')
            if len(user_input) > 3 and user_input[3] == '-w':
                if loader.require('words'):
                    key = loader.find(user_input[1], 'words')
                    if key:
                        counter.words_conversation_statistics(key, user_input[2])
            elif len(user_input) > 1 and not user_input[1] == '-c':
                if loader.require('messages'):
                    key = loader.find(user_input[1], 'messages')
                    if key:
                        counter.statistics(loader['messages'], key, 'messages')
            elif len(user_input) > 1 and user_input[1] == '-c':
                if loader.require('chars'):
                    counter.statistics(loader['chars'], data_type='chars')
            else:
                if loader.require('messages'):
                    counter.statistics(loader['messages'], data_type='messages')
        elif user_input[0] == 'user':
            if len(user_input) > 1:
                if loader.require('messages'):
                    data = pd.DataFrame(loader['messages']).fillna(0).astype('int') # TODO examine this
                    for key in data.index:
                        if key.startswith(' '.join(user_input[1:])):
                            counter.user_statistics(data, key)
                            break
                    else:
                        print('Conversation not found.')
            else:
                print('Please specify user name.')
        elif user_input[0] == 'daily':
            if len(user_input) > 1 and not user_input[1] == '-h':
                if loader.require('messages'):
                    key = loader.find(user_input[1], 'messages')
                    if key:
                        if len(user_input) < 3:
                            counter.daily_conversation(key)
                        else:
                            counter.daily_conversation(key, float(user_input[2]))
            elif len(user_input) > 1 and user_input[1] == '-h':
                counter.daily_chats(float(user_input[2]))
            else:
                counter.daily_chats()
        elif user_input[0] == 'monthly':
            if len(user_input) > 1:
                if loader.require('messages'):
                    key = loader.find(user_input[1], 'messages')
                    if key:
                        counter.monthly_conversation(key)
            else:
                counter.monthly_chats()
        elif user_input[0] == 'yearly':
            if len(user_input) > 1:
                if loader.require('messages'):
                    key = loader.find(user_input[1], 'messages')
                    if key:
                        counter.yearly_conversation(key)
            else:
                counter.yearly_chats()
        elif user_input[0] == 'hours':
            if len(user_input) > 1 and not user_input[1] == '-h':
                if loader.require('messages'):
                    key = loader.find(user_input[1], 'messages')
                    if key:
                        if len(user_input) < 3:
                            counter.hours_conversation(key)
                        else:
                            counter.hours_conversation(key, float(user_input[2]))
            elif len(user_input) > 1 and user_input[1] == '-h':
                counter.hours_chats(float(user_input[2]))
            else:
                counter.hours_chats()
