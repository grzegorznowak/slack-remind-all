import os
import sys
import hmac
import logging
import hashlib

from threading import Thread
from utils.duckling_mod import DucklingWrapperMod

from flask import Flask, request, jsonify, abort
from slackclient import SlackClient
from requests import post


app = Flask(__name__)
duckling_wrapper = DucklingWrapperMod()

slack_signing_secret = os.environ["SLACK_SIGNING_SECRET"]
slack_oauth_token    = os.environ["SLACK_OAUTH_TOKEN"]

slack_client = SlackClient(slack_oauth_token)

remind_replace_tokens = ['about', 'to', 'that']

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def get_channel_members(channel_id):
    gathered_uids = []
    members_response = slack_client.api_call("conversations.members", channel=channel_id)

    if members_response['ok'] is True:
        gathered_uids.extend(members_response['members'])
        while members_response['ok'] and members_response['response_metadata']['next_cursor'] != '':
            members_response = slack_client.api_call("conversations.members", channel=channel_id)
            gathered_uids.extend(members_response['members'])

        members_data = [result for result in
                        [slack_client.api_call("users.info", user=member_uid) for member_uid in gathered_uids]
                        if result['ok'] is True and result['user']['deleted'] is False]
        return members_data
    else:
        return []


def extract_remind_body(text):
    for remind_replace_token in remind_replace_tokens:
        if text.startswith(remind_replace_token):
            text = text[len(remind_replace_token):]

    return text.strip()


def date_extract(text):

    parsed = duckling_wrapper.parse_time(text)
    date = None
    date_text = None
    if parsed is not None and len(parsed):
        if type(parsed[-1]['value']['value']) is dict:
            date = parsed[-1]['value']['value']['from']
        else:
            date = parsed[-1]['value']['value']

        date_text = parsed[-1]['text']
    elif parsed is None:
        logger.error("Cannot parse a date in text: {}".format(text))
        date = "now"
        date_text = "now"

    return text.replace(date_text, "").strip(), date, date_text


def setup_reminder(user_id, remind_body, remind_time, remind_time_text):
    logger.info("setting up reminder {}, {} for {}".format(remind_body, remind_time, user_id))
    result = slack_client.api_call("reminders.add", text=remind_body, time=remind_time_text, user=user_id)

    if result['ok'] is False:
        logger.error("Error calling API: \nBody:{} \nTime:{} \nResponse: {}"
                     .format(remind_body, remind_time_text, result))

    return result


def slash_actions_thread(text, channel_id, channel_name, response_url,
                         remind_body, remind_time, remind_time_text):
    with app.app_context():

        if channel_name == 'directmessage':
            setup_reminder(channel_id, remind_body, remind_time, remind_time_text)
            post(response_url, json={
                    "text": "Have setup a reminder for this person",
                    "attachments": [
                        {
                            "text": text
                        }
                    ]
                }
            )
        else:
            channel_members = get_channel_members(channel_id)

            if len(channel_members):
                reminders = [setup_reminder(channel_member['user']['id'], remind_body,
                                            remind_time, remind_time_text)
                             for channel_member in channel_members]

                ok_attachments = [
                    {
                        "text": "@{}".format(channel_member['user']['name'])
                    } for reminder, channel_member in zip(reminders, channel_members)
                    if reminder['ok'] is True
                ]
                failed_attachments = [
                    {
                        "text": "@{}".format(channel_member['user']['name'])
                    } for reminder, channel_member in zip(reminders, channel_members)
                    if reminder['ok'] is False
                ]
                if len(ok_attachments):
                    post(response_url, json={
                            "text": "Ok, have setup the reminder for:",
                            "attachments": ok_attachments
                    })

                if len(failed_attachments):
                    post(response_url, json={
                        "text": "Ups! I failed setting up the reminder for those folks:",
                        "attachments": failed_attachments
                    })

            else:
                post(response_url, json={
                        "text": "Sorry, I had problem finding out who belongs to this channel. "
                                "No reminders were set :/"
                    }
                )


@app.route('/slack/slash', methods=['POST'])
def slash_actions():
    raw_payload = request.get_data()

    req_timestamp = request.headers.get('X-Slack-Request-Timestamp')
    req_signature = request.headers.get('X-Slack-Signature')

    if not verify_signature(raw_payload, req_timestamp, req_signature, slack_signing_secret):
        abort(403)
    else:
        slack_post = request.form

        if slack_post['command'] == '/remindall':
            text         = slack_post['text']
            channel_id   = slack_post['channel_id']
            channel_name = slack_post['channel_name']
            response_url = slack_post['response_url']

            remind_body, remind_time, remind_time_text = date_extract(extract_remind_body(text))

            thread = Thread(target=slash_actions_thread,
                            args=(text, channel_id, channel_name,
                                  response_url, remind_body,
                                  remind_time, remind_time_text))

            # respond to the caller already so slack doesn't time out, and do relevant processing in a thread
            thread.start()
            return jsonify(
                {
                    "text": "Setting up reminder for all the channel's members...",
                    "attachments": [
                        {
                            "text": "do: {}".format(remind_body),
                        },
                        {
                            "text": "when: {}".format(remind_time_text),
                        }
                    ]
                }
            )


def verify_signature(request_data, timestamp, signature, secret):
    """@see https://api.slack.com/docs/verifying-requests-from-slack"""

    # Verify the request signature of the request sent from Slack
    # Generate a new hash using the app's signing secret and request data

    # Compare the generated hash and incoming request signature
    # Python 2.7.6 doesn't support compare_digest
    # It's recommended to use Python 2.7.7+
    # noqa See https://docs.python.org/2/whatsnew/2.7.html#pep-466-network-security-enhancements-for-python-2-7
    if hasattr(hmac, "compare_digest"):
        req = str.encode('v0:' + str(timestamp) + ':') + request_data
        request_hash = 'v0=' + hmac.new(
            str.encode(secret),
            req, hashlib.sha256
        ).hexdigest()
        # Compare byte strings for Python 2
        if sys.version_info[0] == 2:
            return hmac.compare_digest(bytes(request_hash), bytes(signature))
        else:
            return hmac.compare_digest(request_hash, signature)
    else:
        # So, we'll compare the signatures explicitly
        req = str.encode('v0:' + str(timestamp) + ':') + request_data
        request_hash = 'v0=' + hmac.new(
            str.encode(secret),
            req, hashlib.sha256
        ).hexdigest()

        if len(request_hash) != len(signature):
            return False
        result = 0
        if isinstance(request_hash, bytes) and isinstance(signature, bytes):
            for x, y in zip(request_hash, signature):
                result |= x ^ y
        else:
            for x, y in zip(request_hash, signature):
                result |= ord(x) ^ ord(y)
        return result == 0


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=3000)
