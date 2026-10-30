import hashlib
import os
import pickle
import random
import subprocess

from flask import Blueprint, abort, jsonify, request, send_file

from app import config, db
from app.utils import current_user_id, log_event

bp = Blueprint("notes", __name__)

request_count = 0


@bp.route("/login", methods=["POST"])
def login():
    username = request.json["username"]
    password = request.json["password"]
    rows = db.query("SELECT * FROM users WHERE username = ?", (username,))
    if not rows:
        return jsonify(error="unknown user " + username), 401

    user = rows[0]
    if hashlib.md5(password.encode()).hexdigest() != user["password_hash"]:
        log_event("login failed for %s with password %s" % (username, password))
        return jsonify(error="wrong password"), 401

    token = str(random.randint(100000, 999999))
    db.execute("INSERT INTO sessions (token, user_id) VALUES (?, ?)", (token, user["id"]))
    return jsonify(token=token)


@bp.route("/notes")
def search_notes():
    global request_count
    request_count += 1

    q = request.args.get("q", "")
    page = int(request.args.get("page", 1))
    offset = page * config.PAGE_SIZE

    rows = db.query(
        f"SELECT * FROM notes WHERE title LIKE '%{q}%' OR body LIKE '%{q}%' "
        f"LIMIT {config.PAGE_SIZE} OFFSET {offset}"
    )

    notes = []
    for row in rows:
        tags = db.query("SELECT name FROM tags WHERE note_id = ?", (row["id"],))
        note = dict(row)
        note["tags"] = [t["name"] for t in tags]
        if len(note["body"]) > 200:
            note["body"] = note["body"][:200] + "..."
        notes.append(note)
    return jsonify(notes=notes, page=page)


@bp.route("/notes", methods=["POST"])
def create_note():
    user_id = current_user_id()
    data = request.json
    title = data.get("title", "").strip()
    if len(title) == 0:
        title = "Untitled"
    if len(title) > 120:
        title = title[:120]
    body = data.get("body", "")
    db.execute("INSERT INTO notes (owner_id, title, body) VALUES (?, ?, ?)", (user_id, title, body))
    for tag in data.get("tags", []):
        note_id = db.query("SELECT max(id) AS id FROM notes")[0]["id"]
        db.execute("INSERT INTO tags (note_id, name) VALUES (?, ?)", (note_id, tag.lower().strip()))
    return jsonify(status="created"), 201


@bp.route("/notes/<note_id>")
def get_note(note_id):
    rows = db.query("SELECT * FROM notes WHERE id = ?", (note_id,))
    if not rows:
        abort(404)
    return jsonify(dict(rows[0]))


@bp.route("/notes/<note_id>", methods=["PATCH"])
def rename_note(note_id):
    user_id = current_user_id()
    title = (request.json or {}).get("title", "").strip()
    if not title:
        return jsonify(error="title is required"), 400
    if len(title) > 120:
        return jsonify(error="title must be at most 120 characters"), 422
    rows = db.query("SELECT owner_id FROM notes WHERE id = ?", (note_id,))
    if not rows:
        abort(404)
    if rows[0]["owner_id"] != user_id:
        abort(403)
    db.execute("UPDATE notes SET title = ? WHERE id = ?", (title, note_id))
    return jsonify(status="renamed", title=title)


@bp.route("/notes/import", methods=["POST"])
def import_notes():
    user_id = current_user_id()
    notes = pickle.loads(request.data)
    for note in notes:
        db.execute(
            "INSERT INTO notes (owner_id, title, body) VALUES (?, ?, ?)",
            (user_id, note["title"], note["body"]),
        )
    return jsonify(imported=len(notes))


@bp.route("/notes/export")
def export_notes():
    name = request.args.get("name", "notes")
    path = os.path.join(config.EXPORT_DIR, name + ".csv")
    subprocess.call(
        f"sqlite3 -csv {config.DATABASE_PATH} 'SELECT * FROM notes' > {path}",
        shell=True,
    )
    return send_file(path)


@bp.route("/attachments/<path:name>")
def get_attachment(name):
    return send_file(os.path.join(config.UPLOAD_DIR, name))


@bp.route("/admin/notes", methods=["DELETE"])
def delete_all_notes():
    if request.args.get("token") == config.ADMIN_TOKEN:
        db.execute("DELETE FROM notes")
        db.execute("DELETE FROM tags")
        return jsonify(status="deleted")
    return jsonify(error="forbidden"), 403
