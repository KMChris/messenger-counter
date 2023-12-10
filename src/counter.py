from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import Counter, defaultdict
from matplotlib import pyplot as plt
from .source import Source
from queue import Queue
from tqdm import tqdm
import plotly.express as px
import pandas as pd
import logging
import json
import math


class MessengerCounter:
    def __init__(self, file):
        self.source = Source(file)
        self.threads = 1

    # Counting messages and characters

    def count_messages(self):
        """
        Counts messages and returns dictionary.
        """
        total, senders = {}, self.source.senders
        if len(senders) == 0:
            logging.error('No messages found.')
            return
        for sender in tqdm(senders):
            messages, i = Counter(), 0
            for file in self.source.files[sender]:
                with self.source.open(file) as f:
                    df = pd.DataFrame(json.loads(f.read())['messages'])
                    messages += Counter(df['sender_name'])
            total[sender] = {k.encode('iso-8859-1').decode('utf-8'): v for k, v in messages.items()}
            total[sender]['total'] = sum(messages.values())
        return total

    def count_words(self):
        """
        Counts words from messages and returns dictionary.
        """
        senders = self.source.senders
        if len(senders) == 0:
            logging.error('No messages found.')
            return

        queue = Queue()
        for sender in senders:
                queue.put(sender)
        progress = tqdm(total=queue.qsize(), desc='Counting words', unit='conv.')

        def count_sender():
            counted = {}
            while not queue.empty():
                sender = queue.get()
                counted[sender] = {}
                for file in self.source.files[sender]:
                    with self.source.open(file) as f:
                        df = pd.DataFrame(json.loads(f.read())['messages'])
                        if 'content' in df.columns:
                            df = df[['sender_name', 'content']].dropna()
                            df['sender_name'] = df['sender_name'].str.encode('iso-8859-1').str.decode('utf-8')
                            df['content'] = df['content'].str.encode('iso-8859-1') \
                                .str.decode('utf-8').str.lower().str.split()
                            for name, words in zip(df['sender_name'], df['content']):
                                if name not in counted[sender]:
                                    counted[sender][name] = defaultdict(int)
                                for word in words:
                                    word = word.strip('.,?!:;()[]{}"\'')
                                    counted[sender][name][word] += 1
                queue.task_done()
                progress.update()
            return counted

        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            futures = [executor.submit(count_sender)
                       for _ in range(self.threads)]
            total = {sender: result for future in as_completed(futures)
                     for sender, result in future.result().items()}
            queue.join()
        progress.close()
        return total

    def count_characters(self):
        """
        Counts characters from messages and returns dictionary.
        """
        def count_row(row):
            row = str(row['content']).encode('iso-8859-1').decode('utf-8')
            return Counter(row)

        total, senders = {}, self.source.senders
        if len(senders) == 0:
            logging.error('No messages found.')
            return
        for sender in tqdm(senders):
            counted_all, i = Counter(), 0
            for file in self.source.files[sender]:
                with self.source.open(file) as f:
                    df = pd.DataFrame(json.loads(f.read())['messages'])
                    if 'content' in df.columns:
                        df['counted'] = df.apply(count_row, axis=1)
                        counted_all += sum(df['counted'], Counter())
            total[sender] = dict(counted_all)
        return total

    def count(self, data_type='messages'):
        """
        Counts messages, characters or words.

        :param data_type: type of data to count (default 'messages')
        :return: None
        """
        if data_type == 'messages':
            return self.count_messages()
        elif data_type == 'chars':
            return self.count_characters()
        elif data_type == 'words':
            return self.count_words()


    # Statistics

    def statistics(self, data_source, conversation=None, data_type='messages'):
        """
        Prints statistics of given data source.

        :param data_source: dictionary containing prepared data generated
                            by the get_data() function
        :param conversation: conversation id or None for overall statistics
                             (default None)
        :param data_type:
        :return: None
        """
        if conversation is None:
            if data_type== 'chars':
                self.characters_statistics(data_source)
            elif data_type== 'words':
                self.words_statistics(data_source)
            else:
                self.messages_statistics(data_source)
        else:
            if data_type== 'chars':
                self.characters_conversation_statistics(data_source, conversation)
            elif data_type== 'words':
                self.words_conversation_statistics(data_source, conversation)
            else:
                print(conversation)
                self.conversation_statistics(data_source, conversation)

    def messages_statistics(self, data_source):
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

    def conversation_statistics(self, data_source, conversation):
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

    def characters_statistics(self, data_source):
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

    def characters_conversation_statistics(self, data_source, conversation):
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

    def words_statistics(self, data_source):
        pass

    def words_conversation_statistics(self, data_source, user):
        data_source = pd.DataFrame(data_source)
        print(data_source.columns)
        for key in data_source.columns:
            if key.startswith(user):
                data_source = data_source[key].dropna()
                data_source = data_source.sort_values(ascending=False).astype('int')
                pd.set_option('display.max_rows', 100)
                print(data_source) # TODO show number of occurrences
                print(f'Total words: {data_source.sum()}')
        else:
            print('User not found.')


    # User statistics

    def user_statistics(self, data_source, user_name):
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

    def interval_count(self, inbox_name, function, delta=0.0):
        """
        Counts number of messages based on given timeframe function

        :param inbox_name: directory name that contains requested messages
                           (usually conversation id)
        :param function: pandas function that returns requested time part
        :param delta: number of hours to time shift by
                      and count messages differently (default 0.0)
        :return: dictionary of number of messages grouped by timeframe
        """
        messages, i = Counter(), 0
        for file in self.source.files[inbox_name]:
            with self.source.open(file) as f:
                df = pd.DataFrame(json.loads(f.read())['messages'])
                df = pd.to_datetime(df.iloc[:, 1], unit='ms')
                df = df.dt.tz_localize(None)
                df = df.add(pd.Timedelta(hours=-delta))
                messages += Counter(function(df))
        return messages

    def interval_plot(self, messages):
        """
        Shows chart based on previously defined timeframe

        :param messages: dictionary of number of messages
                         grouped by timeframe
        :return: None
        """
        messages = pd.Series(messages).sort_index()
        print(messages.describe())
        fig = px.bar(x=messages.index, y=messages.values,
                     title='Messages per day',
                     labels={'x': 'Date', 'y': 'Messages'})
        fig.update_yaxes(fixedrange=True)
        # fig.update_xaxes(rangeselector={
        #     'buttons': [
        #         dict(count=1, label='1m', step='month', stepmode='backward'),
        #         dict(count=6, label='6m', step='month', stepmode='backward'),
        #         dict(count=1, label='YTD', step='year', stepmode='todate'),
        #         dict(count=1, label='1y', step='year', stepmode='backward'),
        #         dict(step='all')
        #     ]
        # })
        fig.update_layout(dragmode='zoom', hovermode='x', bargap=0)
        # fig.show(config={
        #     'displayModeBar': False,
        #     'scrollZoom': True
        # })
        return fig
        # plt.bar(messages.index, messages)
        # plt.show()


    # Hours

    def hours(self, difference, conversation=None):
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
            self.hours_chats(difference)
        else:
            data = json.loads(open('messages.json', 'r', encoding='utf-8').read())
            for key in data.keys():
                if key.lower().startswith(conversation.lower()):
                    self.hours_conversation(key, difference)
                    break
            else:
                print('Conversation not found.')

    def hours_conversation(self, conversation, delta=0.0):
        """
        Shows chart of average number of messages send
        in specific conversation by hour throughout the day.

        :param conversation: conversation id, or key from get_data() function
        :param delta: number of hours to time shift by
                      and show statistics differently (default 0.0)
        :return: None
        """
        self.hours_plot(self.interval_count(conversation, lambda x: x.dt.hour, delta), delta)

    def hours_chats(self, delta=0.0):
        """
        Shows chart of average number of messages send
        across all conversations by hour throughout the day.

        :param delta: number of hours to time shift by
                      and show statistics differently (default 0.0)
        :return: None
        """
        messages = Counter()
        for sender in self.source.senders:
            messages += self.interval_count(sender, lambda x: x.dt.hour, delta)
        self.hours_plot(messages, delta)

    def hours_plot(self, messages, delta):
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
        plt.show()


    # Daily

    def daily(self, difference, conversation=None):
        """
        Shows chart of number of messages per day.

        :param difference: number of hours to time shift by
                           and show statistics differently
        :param conversation: conversation id or None for statistics
                             from all conversations (default None)
        :return: None
        """
        if conversation is None:
            self.daily_chats(difference)
        else:
            data = json.loads(open('messages.json', 'r', encoding='utf-8').read())
            for key in data.keys():
                if key.lower().startswith(conversation.lower()):
                    self.daily_conversation(key, difference)
                    break
            else:
                print('Conversation not found.')

    def daily_conversation(self, conversation, delta=0.0):
        """
        Shows chart of number of messages per day
        from the beginning of the conversation.

        :param conversation: conversation id, or key from get_data() function
        :param delta: number of hours to time shift by
                      and show statistics differently (default 0.0)
        :return: None
        """
        return self.interval_plot(self.interval_count(conversation, lambda x: x.dt.date, delta))

    def daily_chats(self, delta=0.0):
        """
        Shows chart of number of messages per day
        across all conversation.

        :param delta: number of hours to time shift by
                      and show statistics differently (default 0.0)
        :return: None
        """
        messages = Counter()
        for sender in self.source.senders:
            messages += self.interval_count(sender, lambda x: x.dt.date, delta)
        self.interval_plot(messages)


    # Monthly (not working)

    def monthly_conversation(self, conversation):  # TODO not working charts for monthly
        """
        Shows chart of number of messages per month.

        :param conversation: conversation id or None for statistics
                             from all conversations (default None)
        :return: None
        """
        self.interval_plot(self.interval_count(conversation, lambda x: x.dt.to_period("M").astype('datetime64[ns]')))

    def monthly_chats(self):
        """
        Shows chart of number of messages per month
        across all conversation.

        :return: None
        """
        messages = Counter()
        for sender in self.source.senders:
            messages += self.interval_count(sender, lambda x: x.dt.to_period("M").astype('datetime64[ns]'))
        self.interval_plot(messages)


    # Yearly

    def yearly(self, conversation=None):
        """
        Shows chart of number of messages per year.

        :param conversation: conversation id or None for statistics
                             from all conversations (default None)
        :return: None
        """
        if conversation is None:
            self.yearly_chats()
        else:
            data = json.loads(open('messages.json', 'r', encoding='utf-8').read())
            for key in data.keys():
                if key.lower().startswith(conversation.lower()):
                    self.yearly_conversation(key)
                    break
            else:
                print('Conversation not found.')

    def yearly_conversation(self, conversation):
        """
        Shows chart of number of messages per year
        from the beginning of the conversation.

        :param conversation: conversation id, or key from get_data() function
        :return: None
        """
        self.interval_plot(self.interval_count(conversation, lambda x: x.dt.year))

    def yearly_chats(self):
        """
        Shows chart of number of messages per year
        across all conversation.

        :return: None
        """
        messages = Counter()
        for sender in self.source.senders:
            messages += self.interval_count(sender, lambda x: x.dt.year)
        messages = pd.DataFrame(messages, index=[0])
        print(messages.iloc[0].describe())
        plt.bar(messages.columns, messages.iloc[0])
        plt.show()

    def close(self):
        self.source.close()
