import plotly.express as px
import pandas as pd
px.defaults.template = 'plotly_dark'


def statistics(data_source, conversation=None, data_type='messages'):
    """
    Returns statistics of given data source.

    :param data_source: dictionary containing prepared data
    :param conversation: conversation id or None for overall
                         statistics (default None)
    :param data_type: type of data to be displayed (default 'messages')
    :return: (DataFrame, fig)
    """
    if conversation is None:
        if data_type== 'chars':
            return characters_statistics(data_source)
        elif data_type== 'words':
            return words_statistics(data_source)
        else:
            return messages_statistics(data_source)
    else:
        if data_type== 'chars':
            return characters_conversation_statistics(data_source, conversation)
        elif data_type== 'words':
            return words_conversation_statistics(data_source, conversation)
        else:
            return conversation_statistics(data_source, conversation)

def messages_statistics(data_source):
    """
    Prints messages overall statistics of given data source.

    :param data_source: dictionary containing prepared data generated
                        by the get_data() function
    :return: None
    """
    # TODO split by your messages and others
    data_source = pd.DataFrame(data_source).loc[['id', 'total']].T
    pd.set_option('display.max_rows', None)
    data_source['total'] = data_source['total'].fillna(0).astype('int')
    data_source = data_source.sort_values(by='total')
    print(data_source)
    print(data_source.describe()) # TODO add to gui
    # TODO allow to choose date range (in future)
    fig = px.bar(data_source, x='total', y=data_source.index, orientation='h',
                 title='Messages statistics', labels={'x': 'Number of messages', 'y': 'User'},
                 color_discrete_sequence=['#ffab40'])
    # swap y axis
    fig.update_yaxes(title=None, tickvals=data_source.index, ticktext=data_source['id'],
                     range=[len(data_source)-40, len(data_source)], minallowed=0, maxallowed=len(data_source))
    fig.update_xaxes(title=None, minallowed=0, maxallowed=data_source['total'].max(), fixedrange=True)
    fig.update_layout(dragmode='pan')
    # fig.show(config={
    #     'scrollZoom': True
    # })
    return data_source, fig

def conversation_statistics(data_source, conversation):
    """
    Prints messages statistics for specific conversation of given data source.

    :param data_source: dictionary containing prepared data generated
                        by the get_data() function
    :param conversation: conversation id, or key from get_data() function
    :return: None
    """
    print(conversation)
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

def words_statistics(data_source):
    pass

def words_conversation_statistics(data_source, user):
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
