import os, time, re
from argparse import ArgumentParser

from transbot import TranslatorBot

CH_PAIR_PTT = re.compile('\(([\w|-]+,(?:\s)?[\w|-]+)\)')
CH_PTT = re.compile('[\w|-]+')

if __name__ == '__main__':
    # Get confiuration infos
    parser = ArgumentParser()
    parser.add_argument('--username', type=str, default=None,
                        help='Specify the username for slackbot to send private message to')
    parser.add_argument('--trans_delay', type=float, default=0.5, help='Delay of the bot between two scanning')
    parser.add_argument('--channel_pairs', type=str, default=None, 
                        help='Specify pairs of channels for translation: "(s,d),(s,d)"')

    args = parser.parse_args()

    slack_bot_token = os.environ.get('SLACK_BOT_TOKEN')
    papago_client_id = os.environ.get('PAPAGO_CLIENT_ID')
    papago_client_secret = os.environ.get('PAPAGO_CLIENT_SECRET')

    # Get the channel pairs
    channel_pairs = None
    if args.channel_pairs:
        ch_list = CH_PAIR_PTT.findall(args.channel_pairs)
        channel_pairs = [(x[0], x[1]) for x in [CH_PTT.findall(y) for y in ch_list]]

    # Initialization
    bot = TranslatorBot(slack_bot_token, papago_client_id, papago_client_secret, username=args.username,
                        rtm_read_delay=args.trans_delay, channel_pairs=channel_pairs)

    # Run and monitoring
    bot.start()
    print "Translator bot is running with delay: %s..." % args.trans_delay
    while True:
        try:
            time.sleep(3)
        except KeyboardInterrupt as e:
            print "Stoping translator bot..."
            bot.stop()
            break
        except Exception as e:
            print "ERROR: %s" % e
           
        

