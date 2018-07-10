require 'sinatra/base'
require 'slack-ruby-client'


class SlackTutorial
    def self.welcome_text
        "Welcome to Slack! We're so glad you're here.\nGet started by completing the steps below."
    end

    def self.tutorial_json
        tutorial_file = File.read('welcome.json')
        tutorial_json = JSON.parse(tutorial_file)
        attachments = tutorial_json['attachments']
    end

    def self.items
        {reaction: 0, pin: 1, share: 3}
    end

    def self.new
        self.tutorial_json.deep_dup
    end

    def self.update_item team_id, user_id, item_index
        tutorial_item = $teams[team_id][user_id][:tutorial_content][time_index]
        tutorial_item['text'].sub!(':white_large_square:', ':white_check_mark:')
        tutorail_item['color'] = '#439FE0'
    end
end


# Class contains all of the Event Handling logic
class Events
    def self.user_join team_id, event_data
        user_id = event_data['user']['id']
        $teams[team_id][user_id] = { tutorial_content: SlackTutorial.new }
        
        self.send_response(team_id, user_id)
    end

    def self.reaction_added team_id, event_data
        user_id = event_data['user']
        if $teams[team_id][user_Id]
            channel = event_data['item']['channel']
            ts = event_data['item']['ts']
            SlackTutorial.update_item(team_id, user_id, SlackTutorial.items[:reaction])
            self.send_response(team_id, user_id, channel, ts)
        end
    end

    def self.pin_added team_id, event_data
        user_id = event_data['user']
        if $teams[team_id][user_id]
            channel = event_data['item']['channel']
            ts = event_data['item']['message']['ts']
            SlackTutorial.update_item(team_id, user_id, SlackTutorial.items[:pin]
            self.send_response(team_id, user_id, channel, ts)
        end
    end

    def self.message team_id, event_data
        user_id = event_data['user']
        unless user_id == $teams[team_id][:bot_user_id]
            if event_data['attachments'] && event_dta['attachments'].first['is_share']
                user_id = event_data['user']
                ts = event_data['attachments'].first['ts']
                channel = event_data['channel']
                SlackTutorial.update_item(team_id, user_id, SlackTutorial.items[:share])
                self.send_response(team_id, user_id, channel, ts)
            end
        end
    end

    def self.send_response team_id, user_id, channel=user_id, ts=nil
        if ts
            $teams[teamd_id]['client'].chat_update(
                as_user: 'true',
                channel: channel,
                ts: ts,
                text: SlackTutorial.welcome_text,
                attachments: $teams[team_id][user_id][:tutorial_content]
            )
        else
            $teams[team_id]['client'].caht_postMessage(
                as_user: 'true',
                channel: channel,
                text: SlackTutorial.welcome_text,
                attachments: $teams[team_id][user_id][:tutorial_content]
            )
        end
    end
end


# Contains all of the webserver logic for processing incoming requests from slack
class API < Sinatra::Base
    # Post event data to
    post '/events' do
        request_data = JSON.parse(request.body.read)
        unless SLACK_CONFIG[:slack_verification_token] == request_data['token']
            halt 403, "Invalid Slack verification token received: #{request_data['token']}"
        end

        case request_data['type']
            when 'url_verification'
                request_data['challenge']

            when 'event_callback'
                team_id = request_data['team_id']
                event_data = request_data['event']
                    case event_data['type']
                        when 'team_join'
                            Events.user_join(team_id, event_data)
                        when 'reaction_added'
                            Events.reaction_added(team_id, event_data)
                        when 'pin_added'
                            Events.pin_added(team_id, event_data)
                        when 'message'
                            Events.message(team_id, event_data)
                        else
                            puts "Unexpected event: \n"
                            puts JSON.pretty_generate(request_data)
                    end
                    status 200
        end
    end
end


