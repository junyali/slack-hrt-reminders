TIMEZONE = "Europe/London"

def get_initial_reminder_message():
    return {
        "text": "Daily Dose of Oestrogen!",
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "Daily Dose of Oestrogen!",
                    "emoji": True
                }
            },
            {
                "type": "rich_text",
                "elements": [
                    {
                        "type": "rich_text_section",
                        "elements": [
                            {
                                "type": "text",
                                "text": "Tell junya to take her meds! :3c:"
                            }
                        ]
                    },
                    {
                        "type": "rich_text_list",
                        "style": "bullet",
                        "indent": 0,
                        "elements": [
                            {
                                "type": "rich_text_section",
                                "elements": [
                                    {
                                        "type": "text",
                                        "text": "2mg oestradiol (transdermal spray) "
                                    },
                                    {
                                        "type": "emoji",
                                        "name": "estrogen"
                                    }
                                ]
                            }
                        ]
                    }
                ]
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
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": "view me on <https://github.com/junyali/slack-hrt-reminders|github> <3"
                    }
                ]
            }
        ]
    }

def get_acknowledged_reminder_message(user_id, owner_id):
    return {
        "text": "Daily Dose of Oestrogen!",
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "Daily Dose of Oestrogen!",
                    "emoji": True
                }
            },
            {
                "type": "rich_text",
                "elements": [
                    {
                        "type": "rich_text_section",
                        "elements": [
                            {
                                "type": "text",
                                "text": "Tell junya to take her meds! :3c:"
                            }
                        ]
                    },
                    {
                        "type": "rich_text_list",
                        "style": "bullet",
                        "indent": 0,
                        "elements": [
                            {
                                "type": "rich_text_section",
                                "elements": [
                                    {
                                        "type": "text",
                                        "text": "2mg oestradiol (transdermal spray) "
                                    },
                                    {
                                        "type": "emoji",
                                        "name": "estrogen"
                                    }
                                ]
                            }
                        ]
                    }
                ]
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"<@{owner_id}>, <@{user_id}> poked you! :neocat_boop_blush:"
                }
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "taken!"
                        },
                        "style": "danger",
                        "action_id": "reminder_complete"
                    }
                ]
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": "view me on <https://github.com/junyali/slack-hrt-reminders|github> <3"
                    }
                ]
            }
        ]
    }

def get_completed_reminder_message(user_id, owner_id):
    return {
        "text": "Daily Dose of Oestrogen!",
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "Daily Dose of Oestrogen!",
                    "emoji": True
                }
            },
            {
                "type": "rich_text",
                "elements": [
                    {
                        "type": "rich_text_section",
                        "elements": [
                            {
                                "type": "text",
                                "text": "Tell junya to take her meds! :3c:"
                            }
                        ]
                    },
                    {
                        "type": "rich_text_list",
                        "style": "bullet",
                        "indent": 0,
                        "elements": [
                            {
                                "type": "rich_text_section",
                                "elements": [
                                    {
                                        "type": "text",
                                        "text": "2mg oestradiol (transdermal spray) "
                                    },
                                    {
                                        "type": "emoji",
                                        "name": "estrogen"
                                    }
                                ]
                            }
                        ]
                    }
                ]
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"<@{owner_id}>, <@{user_id}> poked you! marked as taken :yay:"
                }
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": "view me on <https://github.com/junyali/slack-hrt-reminders|github> <3"
                    }
                ]
            }
        ]
    }
