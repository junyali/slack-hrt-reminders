import os
import pytz
from dotenv import load_dotenv
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

def setup_scheduler():
    scheduler = BackgroundScheduler(timezone=TIMEZONE)

    scheduler.start()
    return scheduler

def main():
    handler = SocketModeHandler(app, os.environ.get("SLACK_APP_TOKEN"))
    handler.start()

if __name__ == '__main__':
    main()
