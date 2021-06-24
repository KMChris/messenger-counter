import MessengerCounter
import argparse


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Messenger Counter - counts messages from Facebook Messenger '
                    'and can show various statistics')
    subparsers = parser.add_subparsers(metavar='command', dest='command',
        help='Available commands:')

    parser_count = subparsers.add_parser('count',
        help='counts all messages and saves to messages.json')
    parser_count.add_argument('file',
        help='path to .zip file downloaded from Facebook, '
             'add -c argument to count chars')

    parser_stats = subparsers.add_parser('stats',
        help='displays statistics for counted messages, '
             'specify conversation for detailed statistics, '
             'use -c for character statistics')
    parser_stats.add_argument('conversation', nargs='?', type=str, const=None,
        help='name of the conversation')

    parser_user = subparsers.add_parser('user',
        help='detailed statistics for specific user')
    parser_user.add_argument('conversation', nargs='+', type=list,
        help='name of the conversation with specific user')

    parser_yearly = subparsers.add_parser('yearly',
        help='number of messages per year')
    parser_yearly.add_argument('conversation', nargs='?', type=str, const=None,
        help='name of the conversation with specific user')

    parser_daily = subparsers.add_parser('daily',
        help='average number of messages by day of the week')
    parser_daily.add_argument('conversation', nargs='?', type=str, const=None,
        help='name of the conversation with specific user')

    parser_hours = subparsers.add_parser('hours',
        help='average number of messages by hour')
    parser_hours.add_argument('conversation', nargs='?', type=str, const=None,
        help='name of the conversation with specific user')

    parser.add_argument('-c', '--chars', action='store_true',
        help='refer to characters instead of messages')
    parser.add_argument('-d', '--difference', type=float, default=0.0,
        help='time shift in hours to show statistics differently')

    args = parser.parse_args()

    if args.command == 'count':
        # TODO avoid setting source multiple times
        MessengerCounter.set_source(args.file)
        MessengerCounter.count(args.chars)
    elif args.command == 'stats':
        MessengerCounter.statistics(
            MessengerCounter.get_data(
                args.conversation,
                args.chars
            ),
            chars=args.chars
        )
    elif args.command == 'user':
        MessengerCounter.user_statistics(
            MessengerCounter.get_data(user=True)
        )
    elif args.command == 'yearly':
        MessengerCounter.yearly(args.conversation)
    elif args.command == 'daily':
        MessengerCounter.daily(args.difference, args.conversation)
    elif args.command == 'hours':
        MessengerCounter.hours(args.difference, args.conversation)
