import threading

import requests
import yaml
from flask import Blueprint, jsonify, request

from app import config
from app.utils import log_event

webhooks_bp = Blueprint("webhooks", __name__)

registered_hooks = []


@webhooks_bp.route("/webhooks/register", methods=["POST"])
def register():
    hook = yaml.load(request.data)
    registered_hooks.append(hook)
    return jsonify(count=len(registered_hooks))


def notify(event, payload):
    for hook in registered_hooks:
        threading.Thread(target=_deliver, args=(hook, event, payload)).start()


def _deliver(hook, event, payload):
    while True:
        try:
            requests.post(
                hook["url"],
                json={"event": event, "payload": payload},
                headers={"X-Signature": config.WEBHOOK_SIGNING_KEY},
                verify=False,
            )
            return
        except Exception as error:
            log_event("webhook delivery failed: %s" % error)
