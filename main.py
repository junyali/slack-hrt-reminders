import os
import pytz
from dotenv import load_dotenv
from config import TIMEZONE, get_initial_reminder_message, get_acknowledged_reminder_message, get_completed_reminder_message
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime

load_dotenv()

app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

USER_ID = os.environ.get("USER_ID")
CHANNEL_ID = os.environ.get("CHANNEL_ID")
CANVAS_ID = os.environ.get("CANVAS_ID")
TIMEZONE = pytz.timezone(TIMEZONE)

last_reminder = {
    "ts": None,
    "channel": None,
    "state": "initial",
    "poked_who": None,
    "poked_when": None,
    "taken_when": None,
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
        message_content = get_initial_reminder_message()
        response = app.client.chat_postMessage(
            channel=CHANNEL_ID,
            **message_content
        )

        last_reminder = {
            "ts": response["ts"],
            "channel": CHANNEL_ID,
            "state": "initial",
            "poked_who": None,
            "poked_when": None,
            "taken_when": None,
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
        message_content = get_acknowledged_reminder_message(user_id, USER_ID)
        client.chat_update(
            channel=CHANNEL_ID,
            ts=message_ts,
            **message_content
        )

        last_reminder["state"] = "first_clicked"
        last_reminder["poked_who"] = user_id
        last_reminder["poked_when"] = datetime.now(TIMEZONE).isoformat()
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
        message_content = get_completed_reminder_message(user_id, USER_ID)
        client.chat_update(
            channel=CHANNEL_ID,
            ts=message_ts,
            **message_content
        )

        last_reminder["state"] = "completed"
        last_reminder["taken_when"] = datetime.now(TIMEZONE).isoformat()
    except Exception as e:
        print(e)

def setup_scheduler():
    scheduler = BackgroundScheduler(timezone=TIMEZONE)

    scheduler.add_job(
        send_reminder,
        CronTrigger(
            day_of_week="mon-fri",
            hour=7,
            minute=0,
            second=0,
            timezone=TIMEZONE
        ),
        id="weekday_morning",
        replace_existing=True
    )

    scheduler.add_job(
        send_reminder,
        CronTrigger(
            day_of_week="mon-fri",
            hour=19,
            minute=0,
            second=0,
            timezone=TIMEZONE
        ),
        id="weekday_evening",
        replace_existing=True
    )

    scheduler.add_job(
        send_reminder,
        CronTrigger(
            day_of_week="sat-sun",
            hour=10,
            minute=0,
            second=0,
            timezone=TIMEZONE
        ),
        id="weekend_morning",
        replace_existing=True
    )

    scheduler.add_job(
        send_reminder,
        CronTrigger(
            day_of_week="sat-sun",
            hour=22,
            minute=0,
            second=0,
            timezone=TIMEZONE
        ),
        id="weekend_evening",
        replace_existing=True
    )

    scheduler.start()
    return scheduler

def main():
    scheduler = setup_scheduler()
    handler = SocketModeHandler(app, os.environ.get("SLACK_APP_TOKEN"))
    handler.start()

if __name__ == '__main__':
    main()
