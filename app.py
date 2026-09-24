from collections import deque
from datetime import datetime, timezone

from flask import Flask, flash, redirect, render_template, request

app = Flask(__name__)
app.secret_key = "replace-with-random-secret"


@app.template_filter("format_ts")
def format_ts(iso_string):
    dt = datetime.fromisoformat(iso_string)
    return dt.strftime("%d.%m.%Y, %H:%M:%S")

pending_queue = deque()
pending_stack = deque()
history = []
next_id = 1


@app.route("/")
def index():
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

    return render_template(
        "index.html",
        pending_queue=pending_queue,
        pending_stack=pending_stack,
        history=result,
        sort=sort,
        q=q,
    )


@app.route("/submit", methods=["POST"])
def submit():
    global next_id

    user = request.form.get("user", "").strip()
    if not user:
        flash("Username is required.", "error")
        return redirect("/")

    try:
        priority = int(request.form["priority"])
    except (ValueError, TypeError):
        flash("Priority must be a number between 1 and 5.", "error")
        return redirect("/")

    if priority < 1 or priority > 5:
        flash("Priority must be between 1 and 5.", "error")
        return redirect("/")

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

    flash(f"Request #{item['id']} from {user} submitted.", "success")
    return redirect("/")


@app.route("/process", methods=["POST"])
def process():
    if pending_stack:
        item = pending_stack.pop()
    elif pending_queue:
        item = pending_queue.popleft()
    else:
        flash("No pending requests.", "info")
        return redirect("/")

    item["status"] = "processed"
    history.append(item)

    flash(f"Request #{item['id']} from {item['user']} processed.", "success")
    return redirect("/")


@app.route("/clear", methods=["POST"])
def clear():
    history.clear()
    flash("History cleared.", "info")
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)
