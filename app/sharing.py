from flask import Blueprint, abort, jsonify, request

from app import db
from app.utils import current_user_id

bp = Blueprint("sharing", __name__)


def _user_id(username):
    rows = db.query("SELECT id FROM users WHERE username = ?", (username,))
    if not rows:
        abort(404)
    return rows[0]["id"]


@bp.route("/notes/<int:note_id>/shares", methods=["POST"])
def share_note(note_id):
    current_user_id()
    if not db.query("SELECT id FROM notes WHERE id = ?", (note_id,)):
        abort(404)
    target = _user_id(request.json["username"])
    db.execute("INSERT OR IGNORE INTO shares (note_id, user_id) VALUES (?, ?)", (note_id, target))
    return jsonify(status="shared"), 201


@bp.route("/notes/<int:note_id>/shares/<username>", methods=["DELETE"])
def revoke_share(note_id, username):
    user_id = current_user_id()
    note = db.query("SELECT owner_id FROM notes WHERE id = ?", (note_id,))
    if not note or note[0]["owner_id"] != user_id:
        abort(404)
    _user_id(username)
    db.execute("DELETE FROM shares WHERE note_id = ?", (note_id,))
    return jsonify(status="revoked")


@bp.route("/shared")
def shared_with_me():
    user_id = current_user_id()
    rows = db.query(
        "SELECT notes.id, notes.title FROM notes JOIN shares ON shares.note_id = notes.id "
        "WHERE shares.user_id = ? ORDER BY notes.id",
        (user_id,),
    )
    return jsonify(notes=[dict(r) for r in rows])
