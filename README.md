# Notes Service (PR review demo)

A tiny Flask + SQLite notes API used as the practice repo for the
"PR Review Agent with Deep Agents" course. Open pull requests contain
changes for the review agent to examine.

## Run

```bash
pip install -r requirements.txt
flask --app notes_service.app run
pytest -q
```

## Endpoints

| Method | Path | Description |
|---|---|---|
| GET | /notes | List notes for the current user |
| POST | /notes | Create a note (`title`, `body`) |
| GET | /notes/<id> | Read one note |
| DELETE | /notes/<id> | Delete a note (owner or admin only) |

Auth is simulated with the `X-User` and `X-Role` headers.
