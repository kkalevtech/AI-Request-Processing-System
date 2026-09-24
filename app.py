from collections import deque
from datetime import datetime, timezone

from flask import Flask, jsonify, render_template, request

app = Flask(__name__)
app.secret_key = "replace-with-random-secret"


@app.template_filter("format_ts")
def format_ts(iso_string):
    dt = datetime.fromisoformat(iso_string)
    local = dt.replace(tzinfo=timezone.utc).astimezone()
    return local.strftime("%d.%m.%Y, %H:%M:%S")


def _serialize(item):
    return {
        "id": item["id"],
        "user": item["user"],
        "priority": item["priority"],
        "timestamp": format_ts(item["timestamp"]),
        "status": item["status"],
    }


def _state():
    return {
        "queue": [_serialize(i) for i in pending_queue],
        "stack": [_serialize(i) for i in pending_stack],
        "history": [_serialize(i) for i in history],
        "has_pending": len(pending_queue) + len(pending_stack) > 0,
    }


pending_queue = deque()
pending_stack = deque()
history = []
next_id = 1


@app.route("/")
def index():
    return render_template(
        "index.html",
        pending_queue=pending_queue,
        pending_stack=pending_stack,
        history=history,
        all_history=list(history),
        sort=request.args.get("sort"),
        q=request.args.get("q", "").strip(),
    )


@app.route("/state")
def state():
    sort = request.args.get("sort")
    h = list(history)
    if sort == "time-asc":
        h = sorted(h, key=lambda x: x["timestamp"])
    elif sort == "time-desc":
        h = sorted(h, key=lambda x: x["timestamp"], reverse=True)
    elif sort == "priority-asc":
        h = sorted(h, key=lambda x: x["priority"])
    elif sort == "priority-desc":
        h = sorted(h, key=lambda x: x["priority"], reverse=True)

    return jsonify({
        "history": [_serialize(i) for i in h],
        "has_pending": len(pending_queue) + len(pending_stack) > 0,
    })


@app.route("/_index")
def _index():
    sort = request.args.get("sort")
    q = request.args.get("q", "").strip()

    result = list(history)

    if sort == "time-asc":
        result = sorted(result, key=lambda x: x["timestamp"])
    elif sort == "time-desc":
        result = sorted(result, key=lambda x: x["timestamp"], reverse=True)
    elif sort == "priority-asc":
        result = sorted(result, key=lambda x: x["priority"])
    elif sort == "priority-desc":
        result = sorted(result, key=lambda x: x["priority"], reverse=True)

    if q:
        result = [
            item
            for item in result
            if q.lower() in item["user"].lower() or q == str(item["id"])
        ]

    all_sorted = list(history)
    if sort == "time-asc":
        all_sorted = sorted(all_sorted, key=lambda x: x["timestamp"])
    elif sort == "time-desc":
        all_sorted = sorted(all_sorted, key=lambda x: x["timestamp"], reverse=True)
    elif sort == "priority-asc":
        all_sorted = sorted(all_sorted, key=lambda x: x["priority"])
    elif sort == "priority-desc":
        all_sorted = sorted(all_sorted, key=lambda x: x["priority"], reverse=True)

    return render_template(
        "index.html",
        pending_queue=pending_queue,
        pending_stack=pending_stack,
        history=result,
        all_history=all_sorted,
        sort=sort,
        q=q,
    )


@app.route("/submit", methods=["POST"])
def submit():
    global next_id

    user = request.form.get("user", "").strip()
    if not user:
        msg = "Username is required."
        return jsonify({"ok": False, "message": msg, "category": "error"})

    try:
        priority = int(request.form["priority"])
    except (ValueError, TypeError):
        msg = "Priority must be a number between 1 and 5."
        return jsonify({"ok": False, "message": msg, "category": "error"})

    if priority < 1 or priority > 5:
        msg = "Priority must be between 1 and 5."
        return jsonify({"ok": False, "message": msg, "category": "error"})

    item = {
        "id": next_id,
        "user": user,
        "priority": priority,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status": "pending",
    }
    next_id += 1

    if priority >= 4:
        pending_stack.append(item)
    else:
        pending_queue.append(item)

    msg = f"Request #{item['id']} from {user} submitted."
    return jsonify({"ok": True, "message": msg, "category": "success", ** _state()})


@app.route("/process", methods=["POST"])
def process():
    if pending_stack:
        item = pending_stack.pop()
    elif pending_queue:
        item = pending_queue.popleft()
    else:
        msg = "No pending requests."
        return jsonify({"ok": True, "message": msg, "category": "info"})

    item["status"] = "processed"
    history.append(item)

    msg = f"Request #{item['id']} from {item['user']} processed."
    return jsonify({"ok": True, "message": msg, "category": "success", ** _state()})


@app.route("/clear", methods=["POST"])
def clear():
    history.clear()
    msg = "History cleared."
    return jsonify({"ok": True, "message": msg, "category": "info", ** _state()})


if __name__ == "__main__":
    app.run(debug=True)
