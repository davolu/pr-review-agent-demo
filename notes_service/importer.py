import csv
import io
import json

from .db import get_db


def proc(d, u, f="json"):
    res = {"ok": 0, "bad": 0, "errs": []}
    tmp = []
    if f == "json":
        try:
            x = json.loads(d)
        except:
            x = []
        for i in x:
            tmp.append(i)
    elif f == "csv":
        r = csv.DictReader(io.StringIO(d))
        for i in r:
            tmp.append(i)
    else:
        tmp = []
    db = get_db()
    n = 0
    for t in tmp:
        n = n + 1
        a = t.get("title")
        b = t.get("body")
        if a == None:
            res["bad"] = res["bad"] + 1
            res["errs"].append("row " + str(n) + " no title")
            continue
        if b == None:
            b = ""
        a2 = a.strip()
        if a2 == "":
            res["bad"] = res["bad"] + 1
            res["errs"].append("row " + str(n) + " empty title")
            continue
        tg = t.get("tags")
        if tg:
            if type(tg) == list:
                tg2 = ",".join(tg)
            else:
                tg2 = str(tg)
            b = b + "\n\ntags: " + tg2
        dup = db.execute(
            "SELECT id FROM notes WHERE owner = ? AND title = ?", (u, a2)
        ).fetchone()
        if dup:
            if t.get("overwrite"):
                db.execute(
                    "UPDATE notes SET body = ? WHERE id = ?", (b, dup["id"])
                )
                res["ok"] = res["ok"] + 1
            else:
                res["bad"] = res["bad"] + 1
                res["errs"].append("row " + str(n) + " dup")
            continue
        try:
            db.execute(
                "INSERT INTO notes (owner, title, body) VALUES (?, ?, ?)",
                (u, a2, b),
            )
            res["ok"] = res["ok"] + 1
        except:
            pass
    db.commit()
    if res["bad"] > 0:
        res["status"] = "partial"
    else:
        res["status"] = "done"
    return res
