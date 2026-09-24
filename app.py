from collections import deque
from datetime import datetime, timezone

from flask import Flask, redirect, render_template, request

app = Flask(__name__)

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
    )


@app.route("/submit", methods=["POST"])
def submit():
    global next_id

    user = request.form["user"]
    priority = int(request.form["priority"])

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

    return redirect("/")


@app.route("/process", methods=["POST"])
def process():
    if pending_stack:
        item = pending_stack.pop()
    elif pending_queue:
        item = pending_queue.popleft()
    else:
        return redirect("/")

    item["status"] = "processed"
    history.append(item)

    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)
