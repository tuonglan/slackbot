import os, time
from argparse import ArgumentParser

from transbot import TranslatorBot


if __name__ == '__main__':
    # Get confiuration infos
    parser = ArgumentParser()
    parser.add_argument('--username', type=str, 
                        help='Specify the username for slackbot to send private message to')
    parser.add_argument('--trans_delay', type=float, default=0.5, help='Delay of the bot between two scanning')

    args = parser.parse_args()

    slack_bot_token = os.environ.get('SLACK_BOT_TOKEN')
    papago_client_id = os.environ.get('PAPAGO_CLIENT_ID')
    papago_client_secret = os.environ.get('PAPAGO_CLIENT_SECRET')

    # Initialization
    bot = TranslatorBot(slack_bot_token, papago_client_id, papago_client_secret, args.username,
                        rtm_read_delay=args.trans_delay)

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
           
        

