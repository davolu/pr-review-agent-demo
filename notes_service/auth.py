"""Very small header-based auth used for the demo."""
from dataclasses import dataclass

from flask import abort, request

ROLES = ("viewer", "editor", "admin")


@dataclass
class User:
    name: str
    role: str


def current_user() -> User:
    """Read the caller from X-User / X-Role headers (demo only)."""
    name = request.headers.get("X-User")
    role = request.headers.get("X-Role", "viewer")
    if not name or role not in ROLES:
        abort(401)
    return User(name=name, role=role)


def can_delete(user: User, note_owner: str) -> bool:
    """Owners and admins may delete a note."""
    return user.role == "admin" or user.name == note_owner
