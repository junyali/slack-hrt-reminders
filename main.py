import os
import pytz
from dotenv import load_dotenv
from slack_sdk.models.messages.message import message

from config import USER_ID, CHANNEL_ID, TIMEZONE
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime

load_dotenv()

app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

TIMEZONE = pytz.timezone(TIMEZONE)

last_reminder = {
    "ts": None,
    "channel": None,
    "state": "initial"
}

def send_reminder():
    global last_reminder

    if last_reminder["ts"] and last_reminder["channel"]:
        try:
            app.client.chat_delete(
                channel=last_reminder["channel"],
                ts=last_reminder["ts"]
            )
        except Exception as e:
            print(e)

    try:
        response = app.client.chat_postMessage(
            channel=CHANNEL_ID,
            text="HRT Reminder!",
            blocks=[
                {
                    "type": "Section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "HRT Reminder! Poke me :3"
                    }
                },
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "poke!"
                            },
                            "style": "primary",
                            "action_id": "reminder_first_click"
                        }
                    ]
                }
            ]
        )

        last_reminder = {
            "ts": response["ts"],
            "channel": CHANNEL_ID,
            "state": "initial"
        }

        print(f"Reminder sent at {datetime.now(TIMEZONE)}")
    except Exception as e:
        print(e)

@app.action("reminder_first_click")
def handle_first_click(ack, body, client):
    ack()

    user_id = body["user"]["id"]
    message_ts = body["message"]["ts"]
    channel_id = body["channel"]["id"]

    try:
        client.chat_update(
            channel=channel_id,
            ts=message_ts,
            text="Poke!",
            blocks=[
                {
                    "type": "Section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"<@{USER_ID}>, <@{user_id}> poked you!"
                    }
                },
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "done"
                            },
                            "style": "danger",
                            "action_id": "reminder_complete"
                        }
                    ]
                }
            ]
        )

        last_reminder["state"] = "first_clicked"
    except Exception as e:
        print(e)

@app.action("reminder_complete")
def handle_complete(ack, body, client):
    ack()

    user_id = body["user"]["id"]
    message_ts = body["message"]["ts"]
    channel_id = body["channel"]["id"]

    if user_id != USER_ID:
        try:
            client.chat_postEphemeral(
                channel=channel_id,
                user=user_id,
                text="you can't do that, silly! >.<"
            )
        except Exception as e:
            print(e)
        return

    try:
        client.chat_update(
            channel=channel_id,
            ts=message_ts,
            text="Done!",
            blocks=[
                {
                    "type": "Section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "Done!"
                    }
                }
            ]
        )

        last_reminder["state"] = "completed"
    except Exception as e:
        print(e)

def setup_scheduler():
    scheduler = BackgroundScheduler(timezone=TIMEZONE)

    scheduler.start()
    return scheduler

def main():
    handler = SocketModeHandler(app, os.environ.get("SLACK_APP_TOKEN"))
    handler.start()

if __name__ == '__main__':
    main()
