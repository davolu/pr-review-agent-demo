"""Full-text-ish search over a user's notes."""
from .db import get_db


def search_notes(owner: str, term: str, limit: int = 20):
    """Return notes whose title or body contains `term`."""
    query = (
        f"SELECT id, title, body FROM notes "
        f"WHERE owner = '{owner}' AND (title LIKE '%{term}%' OR body LIKE '%{term}%') "
        f"ORDER BY id DESC LIMIT {limit}"
    )
    return [dict(r) for r in get_db().execute(query).fetchall()]
