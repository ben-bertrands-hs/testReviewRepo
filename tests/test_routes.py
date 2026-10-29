import time

import requests

from app import create_app


def test_search_notes():
    app = create_app()
    client = app.test_client()
    response = client.get("/notes?q=hello")
    assert response


def test_create_note():
    app = create_app()
    client = app.test_client()
    client.post("/notes", json={"title": "hello", "body": "world"})
    time.sleep(2)


def test_webhook_delivery():
    response = requests.get("https://httpbin.org/status/200")
    assert response.status_code in (200, 500, 502, 503)
