import os
import pytz
import logging
from dotenv import load_dotenv
from config import TIMEZONE, LOG_TO_CANVAS, get_initial_reminder_message, get_acknowledged_reminder_message, get_completed_reminder_message
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

# stolen right from one of my old discord bots: https://github.com/junyali/Anya/blob/main/main.py
def setup_logging():
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="[%Y-%m-%d %H:%M:%S]"
    )

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)

    file_handler = logging.FileHandler("latest.log")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)

    logger = logging.getLogger(__name__)

def log_to_canvas(reminder_data):
    if not LOG_TO_CANVAS or not CANVAS_ID:
        return

    try:
        time = datetime.now(TIMEZONE).isoformat()
        poked_who = f"<@{reminder_data["poked_who"]}>" if reminder_data["poked_who"] else "N/A"
        poked_when = reminder_data["poked_when"] or "N/A"
        taken_when = reminder_data["taken_when"] or "N/A"
        duration = "N/A"

        if reminder_data["poked_when"] and reminder_data["taken_when"]:
            try:
                start = datetime.fromisoformat(poked_who)
                end = datetime.fromisoformat(taken_when)
                duration = round((end - start).total_seconds() / 60, 1)
            except:
                duration = "N/A"

        table_row = f"\n{time},{poked_who},{poked_when},{taken_when},{duration}"

        app.client.canvases_edit(
            canvas_id=CANVAS_ID,
            changes=[
                {
                    "operation": "insert_at_end",
                    "document_content": {
                        "type": "markdown",
                        "markdown": table_row
                    }
                }
            ]
        )
        logging.info(f"[CANVAS] Logged to {CANVAS_ID}")
    except Exception as e:
        logging.error(f"[CANVAS] Failed to log to {CANVAS_ID}: {e}")

def send_reminder():
    global last_reminder

    if last_reminder["state"] == "completed" and last_reminder["taken_when"]:
        log_to_canvas(last_reminder)

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

        logging.info(f"[REMINDER] Sent to {CHANNEL_ID}")
    except Exception as e:
        logging.error(f"[REMINDER] Failed to send to {CHANNEL_ID}: {e}")

@app.action("reminder_first_click")
def handle_first_click(ack, body, client):
    ack()

    user_id = body["user"]["id"]
    message_ts = body["message"]["ts"]
    channel_id = body["channel"]["id"]

    try:
        message_content = get_acknowledged_reminder_message(user_id, USER_ID)
        client.chat_update(
            channel=channel_id,
            ts=message_ts,
            **message_content
        )

        last_reminder["state"] = "first_clicked"
        last_reminder["poked_who"] = user_id
        last_reminder["poked_when"] = datetime.now(TIMEZONE).isoformat()
        logging.info(f"[REMINDER] Poked by {user_id}")
    except Exception as e:
        logging.error(f"[REMINDER] Failed update reminder: {e}")

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
            channel=channel_id,
            ts=message_ts,
            **message_content
        )

        last_reminder["state"] = "completed"
        last_reminder["taken_when"] = datetime.now(TIMEZONE).isoformat()
        logging.info(f"[REMINDER] Taken!")
    except Exception as e:
        logging.error(f"[REMINDER] Failed update reminder: {e}")

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
    setup_logging()
    logging.info("Starting!")
    scheduler = setup_scheduler()
    handler = SocketModeHandler(app, os.environ.get("SLACK_APP_TOKEN"))
    handler.start()

if __name__ == '__main__':
    main()
