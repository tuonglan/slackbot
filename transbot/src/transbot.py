import os, time, re
from threading import Thread
from slackclient import SlackClient

from papago_trans import PapagoTranslator

TAG_PTT = re.compile("\<@(|[WU].+?)\>")
RTM_READ_DELAY = 0.5


def _detag_user(text):
    


class TranslatorBot:
    def __init__(self, token, papago_client_id, papago_client_secret, **kwargs):
        self._client = SlackClient(token)
        if not self._client.rtm_connect():
            raise Exception("Can't establish Slack direct message connection")
        self._bot_id = self._client.api_call('auth.test')['user_id']
        self._user_id = self._init_users(kwargs.get('username', None))
        self._trans_channels = self._init_translated_channels(kwargs.get('channel_pairs', None))

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
            display_name = user['profile']['display_name']
            display_name = None if display_name == '' else display_name
            self._users[user['id']] = {
                    'name': user['name'], 
                    'display_name': user['profile']['display_name']}
            if username and (user['name'] == username or user['profile']['display_name'] == username):
                user_id =  user['id']
       
        if username and (not user_id):
            raise Exception("Can't find user %s in the user list" % username)
        return user_id

    def _init_translated_channels(self, channel_pairs):
        if not channel_pairs:
            return None

        workspace_channels = self._client.api_call('channels.list')
        if not workspace_channels['ok']:
            raise Exception("Can't get channel list: %s" % workspace_channels['error'])
        private_channels = self._client.api_call('groups.list')
        if not private_channels['ok']:
            raise Exception("Can't get private channel list: %s" % private_channels['error'])
        
        # Channel names -> id and id -> names
        self._ch_names = {}
        self._ch_ids = {}
        for ch in workspace_channels['channels']:
            self._ch_names[ch['name']] = ch['id']
            self._ch_ids[ch['id']] = ch['name']
        for ch in private_channels['groups']:
            self._ch_names[ch['name']] = ch['id']
            self._ch_ids[ch['id']] = ch['name']

        # Create translated_channel_ids
        trans_channels = {}
        for (from_ch ,to_ch) in channel_pairs:
            trans_channels[self._ch_names[from_ch]] = self._ch_names[to_ch]

        return trans_channels

    def _handle_command(self, event):
        print "-----> Command: %s" % event['text']

    def _post_ephemeral(self, trans_text, user_id, event):
        display_name = self._users[event['user']]['display_name'] or self._users[event['user']]['name']
        atts = [{'pretext': "%s said: \"%s...\"" % (display_name, event['text'][:23]),
                'text': trans_text['text'],
                'color': "#7CD197"
                }]
        res = self._client.api_call('chat.postEphemeral', attachments=atts, user=user_id, 
                                    channel=event['channel'])
        if not res['ok']:
            print "Can't post message: %s to the slack channel %s" % (trans_text['text'], event['channel'])

    def _post_channel_message(self, trans_text, channel_id, event):
        display_name = self._users[event['user']]['display_name'] or self._users[event['user']]['name']
        atts = [{'pretext': "*`%s`* (<#%s>): \"%s...\"" % (display_name, event['channel'],
                                                           event['text'][:23]),
                'text': trans_text['text'],
                'color': "#7CD197"
                }]
        res = self._client.api_call('chat.postMessage', attachments=atts,
                                    channel=self._trans_channels[event['channel']])
        if not res['ok']:
            print "Can't post message: %s to the slack channel %s" % (trans_text['text'], 
                                                                      self._trans_channels[event['channel']])


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
        
        # Post ephemeral message if user id specified
        if self._user_id:
            self._post_ephemeral(trans_text, self._user_id, event)

        # Post translated message in the channel if configured
        if self._trans_channels and event['channel'] in self._trans_channels:
            self._post_channel_message(trans_text, event['channel'], event)

    def _start(self):
        while self._running:
            try:
                events = self._client.rtm_read()
                map(self._handle_event, events)
            except Exception as e:
                print "Translator Bot ERROR: %s" % e

            time.sleep(self._rtm_read_delay)

    def start(self):
        self._running = True
        self._trans_thread = Thread(target=self._start)
        self._trans_thread.start()

    def stop(self):
        self._running = False
        self._trans_thread.join()


