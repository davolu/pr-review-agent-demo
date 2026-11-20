"""Flask application factory and routes."""
from flask import Flask, abort, jsonify, request

from .auth import can_delete, current_user
from .db import close_db, get_db, init_db
from .pagination import parse_page_args

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
        """List the caller's notes, one page at a time.

        Query params: `page` (1-based, default 1) and `per_page`
        (default 20, max 100).
        """
        user = current_user()
        page, per_page = parse_page_args(request.args)
        offset = page * per_page
        rows = get_db().execute(
            "SELECT id, title, body FROM notes WHERE owner = ? "
            "ORDER BY id LIMIT ? OFFSET ?",
            (user.name, per_page, offset),
        ).fetchall()
        return jsonify({"page": page, "per_page": per_page,
                        "items": [dict(r) for r in rows]})

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

    return app
