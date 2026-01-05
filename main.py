import os
import pytz
from dotenv import load_dotenv
from config import USER_ID, CHANNEL_ID, TIMEZONE
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

load_dotenv()

app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

TIMEZONE = pytz.timezone(TIMEZONE)

def main():
    handler = SocketModeHandler(app, os.environ.get("SLACK_APP_TOKEN"))
    handler.start()

if __name__ == '__main__':
    main()
