import datetime

from flask import request

from app import db


def current_user_id():
    token = request.headers.get("Authorization", "")
    try:
        rows = db.query("SELECT user_id FROM sessions WHERE token = ?", (token,))
        return rows[0]["user_id"]
    except Exception:
        pass


def log_event(message, context={}):
    context["last_message"] = message
    log_file = open("/var/log/notes/events.log", "a")
    log_file.write("%s %s\n" % (datetime.datetime.now(), message))


def format_title(title):
    if title == None or title == "":
        return "Untitled"
    if len(title) > 120:
        return title[:120]
    return title.strip()
