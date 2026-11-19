"""Flask application factory and routes."""
from flask import Flask, abort, jsonify, request

from .auth import can_delete, current_user
from .db import close_db, get_db, init_db
from .export import send_digest
from .search import search_notes

MAX_TITLE = 200


def create_app(database: str = "notes.db") -> Flask:
    """Build the Flask app."""
    app = Flask(__name__)
    app.config["DATABASE"] = database
    app.teardown_appcontext(close_db)
    with app.app_context():
        init_db()

    @app.get("/notes")
    def list_notes():
        user = current_user()
        rows = get_db().execute(
            "SELECT id, title, body FROM notes WHERE owner = ? ORDER BY id",
            (user.name,),
        ).fetchall()
        return jsonify([dict(r) for r in rows])

    @app.post("/notes")
    def create_note():
        user = current_user()
        data = request.get_json(silent=True) or {}
        title = str(data.get("title", "")).strip()
        if not title or len(title) > MAX_TITLE:
            abort(400, "title is required and must be <= 200 chars")
        db = get_db()
        cur = db.execute(
            "INSERT INTO notes (owner, title, body) VALUES (?, ?, ?)",
            (user.name, title, str(data.get("body", ""))),
        )
        db.commit()
        return jsonify({"id": cur.lastrowid}), 201

    @app.get("/notes/<int:note_id>")
    def get_note(note_id: int):
        user = current_user()
        row = get_db().execute(
            "SELECT id, owner, title, body FROM notes WHERE id = ?", (note_id,)
        ).fetchone()
        if row is None or row["owner"] != user.name:
            abort(404)
        return jsonify(dict(row))

    @app.delete("/notes/<int:note_id>")
    def delete_note(note_id: int):
        user = current_user()
        db = get_db()
        row = db.execute("SELECT owner FROM notes WHERE id = ?", (note_id,)).fetchone()
        if row is None:
            abort(404)
        if not can_delete(user, row["owner"]):
            abort(403)
        db.execute("DELETE FROM notes WHERE id = ?", (note_id,))
        db.commit()
        return "", 204

    @app.get("/notes/search")
    def search():
        user = current_user()
        term = request.args.get("q", "")
        return jsonify(search_notes(user.name, term))

    @app.post("/notes/export")
    def export_notes():
        user = current_user()
        data = request.get_json(silent=True) or {}
        notes = search_notes(user.name, "", limit=1000)
        status = send_digest(data.get("email", ""), notes)
        return jsonify({"sent": status == 200})

    return app
