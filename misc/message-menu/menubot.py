from flask import Flask, request, make_response, Response
from slackclient import SlackClient
import json, os

SLACK_BOT_TOKEN = os.environ['SLACK_BOT_TOKEN']
SLACK_VERIFICATION_TOKEN = os.environ['SLACK_VERIFICATION_TOKEN']
MENU_OPTIONS = {
    "options": [
        {
            'text': 'Cappuccino',
            'value': 'cappuccino'
        },
        {
            'text': 'Latte',
            'value': 'latte'
        }
    ]
}
ATTACHMENT_JSON = [
    {
        "fallback": "Upgrade your Slack client to use messages like these.",
        "color": "#3AA3E3",
        "attachment_type": "default",
        "callback_id": "menu_options_2319",
        "actions": [
            {
                "name": "bev_list",
                "text": "Pick a beverage...",
                "type": "select",
                "data_source": "external"
            }
        ]
    },
    {
        'fallback': 'Please select an option',
        'title': 'Please select your option',
        'callback_id': 'select_option',
        'color': '#3AA3E3',
        'attachment_type': 'default',
        'actions': [
            {
                'name': 'recommend',
                'text': 'Recommend',
                'type': 'button',
                'value': 'recommend'
            },
            {
                'name': 'no',
                'text': 'No',
                'type': 'button',
                'value': 'bad'
            }
        ]
    }
]

# Flask webserver for incoming traffic
slack_client = SlackClient(SLACK_BOT_TOKEN)
app = Flask(__name__)



# Verify the slack token
def verify_slack_token(token):
    if SLACK_VERIFICATION_TOKEN != token:
        print "Error: invalid verification token"
        print "Recevie %s but expecting %s" % (token, SLACK_VERIFICATION_TOKEN)
        return make_response("Request invalid Slack verificatio token", 403)

# Hello World
@app.route('/slack/status', methods=['GET'])
def hello_world():
    return make_response("Hello World", 200)


# Populate the menu choices
@app.route('/slack/message_options', methods=['POST'])
def message_options():
    form_json = json.loads(request.form['payload'])
    verify_slack_token(form_json['token'])

    return Response(json.dumps(MENU_OPTIONS), mimetype='application/json')

@app.route('/slack/message_actions', methods=['POST'])
def message_actions():
    print "--------------------> Arguments: %s" % request.args
    print "--------------------> Data is: %s" % request.form
    form_json = json.loads(request.form['payload'])
    verify_slack_token(form_json['token'])

    # Get selection
    selection = form_json['actions'][0]['selected_options'][0]['value']
    message_text = 'hot cappuccino' if selection == 'cappuccino' else 'hot latte'

    response = slack_client.api_call('chat.update', channel=form_json['channel']['id'],
                                     ts=form_json['message_ts'], 
                                     text="One %s, right coming up! :coffee:" % message_text,
                                     attachments=[])

    return make_response("", 200)


slack_client.api_call('chat.postMessage', channel='#bot_test', 
                      text='Would you like some coffee? :coffee:',
                      attachments=ATTACHMENT_JSON)

if __name__ == '__main__':
    app.run(host='0.0.0.0')

