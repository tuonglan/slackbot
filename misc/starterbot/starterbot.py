import os, time, re, pprint
from slackclient import SlackClient


RTM_READ_DELAY = 1
EXAMPLE_COMMAND = ' do'
MENTION_REGEX = "^<@(|[WU].+?)>(.*)"

slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))
starterbot_id = None


def handle_command(command, channel, user_id):
    default_response = "Not sure what you mean. Try *{}*.".format(EXAMPLE_COMMAND)

    response = None
    if command.startswith(EXAMPLE_COMMAND):
        response = "Sure...<@%s> write some more code then I can do that" % user_id

    rt = slack_client.api_call("chat.postMessage", channel=channel, text=response or default_response)

def parse_direct_mention(text):
    matches = re.search(MENTION_REGEX, text)
    return (matches.group(1), matches.group(2)) if matches else (None, None)

def parse_bot_commands(slack_events):
    for event in slack_events:
        print event
        if event['type'] == 'message' and not 'subtype' in event:
            tagged_id, message = parse_direct_mention(event['text'])
            print "-----> Starterbot id: %s, User id: %s, channel: %s, message: %s" % (
                            starterbot_id, tagged_id, event['channel'], message)
            #pprint.pprint(event)
            if tagged_id == starterbot_id:
                return message, event['channel'], event['user']
    
    return None, None, None


if __name__ == '__main__':
    if slack_client.rtm_connect(with_team_state=False):
        print "Starter Bot connected and running"

        starterbot_id = slack_client.api_call("auth.test")['user_id']
        while True:
            command, channel, user_id = parse_bot_commands(slack_client.rtm_read())
            if command:
                handle_command(command, channel, user_id)
            time.sleep(RTM_READ_DELAY)
    else:
        print "Connection failed: Exception traceback printed above"


