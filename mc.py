import MessengerCounter
import argparse


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Messenger Counter - counts messages from Facebook Messenger '
                    'and can show various statistics')
    subparsers = parser.add_subparsers(metavar='command', dest='command',
        help='Available commands:')

    parser_count = subparsers.add_parser('count',
        help='counts all messages and saves to .json file')
    parser_count.add_argument('file',
        help='path to .zip file downloaded from Facebook')
    parser_count.add_argument('-m', '--messages', action='store_true',
        help='count messages (default if no argument is specified)')
    parser_count.add_argument('-c', '--chars', action='store_true',
        help='count characters')
    parser_count.add_argument('-w', '--words', action='store_true',
        help='count words')

    parser_stats = subparsers.add_parser('stats',
        help='displays statistics for counted messages, '
             'specify conversation for detailed statistics, '
             'use -c for character statistics')
    parser_stats.add_argument('conversation', nargs='?', type=str, const=None,
        help='name of the conversation (optional), '
             'leave blank to show statistics summary of all conversations')
    parser_stats.add_argument('-c', '--chars', action='store_true',
        help='refer to characters instead of messages')

    parser_user = subparsers.add_parser('user',
        help='detailed statistics for specific user')
    parser_user.add_argument('conversation', type=str,
        help='name of a user')

    parser_yearly = subparsers.add_parser('yearly',
        help='number of messages per year')
    parser_yearly.add_argument('file',
        help='path to .zip file downloaded from Facebook')
    parser_yearly.add_argument('conversation', nargs='?', type=str, const=None,
        help='name of the conversation with specific user')

    parser_daily = subparsers.add_parser('daily',
        help='number of messages per day')
    parser_daily.add_argument('file',
        help='path to .zip file downloaded from Facebook')
    parser_daily.add_argument('conversation', nargs='?', type=str, const=None,
        help='name of the conversation with specific user')
    parser_daily.add_argument('-d', '--difference', type=float, default=0.0,
        help='time shift in hours to show statistics differently')

    parser_hours = subparsers.add_parser('hours',
        help='average number of messages by hour')
    parser_hours.add_argument('file',
        help='path to .zip file downloaded from Facebook')
    parser_hours.add_argument('conversation', nargs='?', type=str, const=None,
        help='name of the conversation with specific user')
    parser_hours.add_argument('-d', '--difference', type=float, default=0.0,
        help='time shift in hours to show statistics differently')

    args = parser.parse_args()

    if args.command == 'count':
        MessengerCounter.set_source(args.file)
        types = []
        if args.messages or not (args.messages or args.chars or args.words):
            types.append('messages')
        if args.chars:
            types.append('chars')
        if args.words:
            types.append('words')
        MessengerCounter.count(types)
    elif args.command == 'stats':
        MessengerCounter.statistics(
            *MessengerCounter.get_data(
                args.conversation,
                args.chars
            ),
            args.chars #TODO: support all types
        )
    elif args.command == 'user':
        MessengerCounter.user_statistics(
            *MessengerCounter.get_data(args.conversation, user=True)
        )
    elif args.command == 'yearly':
        MessengerCounter.set_source(args.file)
        MessengerCounter.yearly(args.conversation)
    elif args.command == 'daily':
        MessengerCounter.set_source(args.file)
        MessengerCounter.daily(args.difference, args.conversation)
    elif args.command == 'hours':
        MessengerCounter.set_source(args.file)
        MessengerCounter.hours(args.difference, args.conversation)
