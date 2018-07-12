import os, time
from threading import Thread
from slackclient import SlackClient

from papago_trans import PapagoTranslator

RTM_READ_DELAY = 0.5

class TranslatorBot:
    def __init__(self, token, papago_client_id, papago_client_secret, username, **kwargs):
        self._client = SlackClient(token)
        if not self._client.rtm_connect():
            raise Exception("Can't establish Slack direct message connection")
        self._bot_id = self._client.api_call('auth.test')['user_id']
        self._user_id = self._init_users(username)

        self._rtm_read_delay = float(kwargs.get('rtm_read_delay', RTM_READ_DELAY))
        self.s_lang = kwargs.get('source_lang', 'ko')
        self.t_lang = kwargs.get('target_lang', 'en')
        self._trans = PapagoTranslator(papago_client_id, papago_client_secret, self.s_lang, self.t_lang)

        self._running = False

    def _init_users(self, username):
        workspace_users = self._client.api_call('users.list')
        if not workspace_users['ok']:
            raise Exception("Can't get user id list")

        user_id = None
        self._users = {}
        for user in workspace_users['members']:
            display_name = user['profile']['display_name'] == '' ? None :  user['profile']['display_name']
            self._users[user['id']] = {
                    'name': user['name'], 
                    'display_name': user['profile']['display_name']}
            if user['name'] == username or user['profile']['display_name'] == username:
                user_id =  user['id']
       
        if not user_id:
            raise Exception("Can't find user %s in the user list" % username)
        return user_id

    def _handle_command(self, event):
        print "-----> Command: %s" % event['text']

    def _handle_event(self, event):
        # If it's not a message or include 'subtype', ignore
        if event['type'] != 'message' or 'subtype' in event:
            return
        
        # If that's an mentioned message, parse as a command
        if event['text'].find("<@%s>" % self._bot_id) != -1:
            self._handle_command(event)
            return

        # Translate & post the message
        try:
            trans_text = self._trans.translate(event['text'])
        except Exception as e:
            print "Error when trying to translate \"%s\" from %s to %s: %s" % (event['text'], self.s_lang,
                                                                               self.t_lang, e)
            trans_text = {'text': "Error at translation: %s" % e.message}
        
        atts = [{'pretext': "%s said" % event['user'],
                'text': trans_text['text'],
                'color': "#7CD197"
                }]
        res = self._client.api_call('chat.postEphemeral', attachments=atts, user=self._user_id, 
                                    channel=event['channel'])
        if not res['ok']:
            print "Can't post message: %s to the slack channel %s" % (trans_text['text'], event['channel'])

    def _start(self):
        while self._running:
            try:
                events = self._client.rtm_read()
                map(self._handle_event, events)
            except Exception as e:
                print "Translator ERROR: %s" % e

            time.sleep(self._rtm_read_delay)

    def start(self):
        self._running = True
        self._trans_thread = Thread(target=self._start)
        self._trans_thread.start()

    def stop(self):
        self._running = False
        self._trans_thread.join()


