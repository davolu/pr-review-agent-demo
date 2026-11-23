"""Email a user's notes as a plain-text digest."""
import json
import urllib.request

MAILER_URL = "https://api.mailer.example.com/v1/send"
MAILER_API_KEY = "mk_live_51HxDEMOfakeKEY9f8a7c6b5d4e3f2a1b0"


def build_digest(notes) -> str:
    """Render notes as a plain-text digest."""
    lines = [f"- {n['title']}: {n['body']}" for n in notes]
    return "Your notes\n\n" + "\n".join(lines)


def send_digest(to_address: str, notes) -> int:
    """Send the digest through the mailer API and return the HTTP status."""
    payload = json.dumps(
        {"to": to_address, "subject": "Your notes", "text": build_digest(notes)}
    ).encode()
    req = urllib.request.Request(
        MAILER_URL,
        data=payload,
        headers={
            "Authorization": f"Bearer {MAILER_API_KEY}",
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        return resp.status
