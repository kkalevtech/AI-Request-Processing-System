from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timezone

from flask import Flask, jsonify, render_template, request

app = Flask(__name__)
app.secret_key = "replace-with-random-secret"


@app.template_filter("format_ts")
def format_ts(iso_string):
    dt = datetime.fromisoformat(iso_string)
    local = dt.replace(tzinfo=timezone.utc).astimezone()
    return local.strftime("%d.%m.%Y, %H:%M:%S")


@dataclass
class Request:
    id: int
    user: str
    priority: int
    timestamp: str = ""
    status: str = "pending"

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()

    def to_dict(self):
        return {
            "id": self.id,
            "user": self.user,
            "priority": self.priority,
            "timestamp": self.timestamp,
            "status": self.status,
        }

    def serialize(self):
        return {
            "id": self.id,
            "user": self.user,
            "priority": self.priority,
            "timestamp": format_ts(self.timestamp),
            "status": self.status,
        }


class RequestManager:
    def __init__(self):
        self._queue = deque()
        self._stack = deque()
        self._history = []
        self._next_id = 1

    @property
    def queue(self):
        return self._queue

    @property
    def stack(self):
        return self._stack

    @property
    def history(self):
        return self._history

    def submit(self, user, priority):
        req = Request(id=self._next_id, user=user, priority=priority)
        self._next_id += 1

        if priority >= 4:
            self._stack.append(req)
        else:
            self._queue.append(req)

        return req

    def process(self):
        if self._stack:
            req = self._stack.pop()
        elif self._queue:
            req = self._queue.popleft()
        else:
            return None

        req.status = "processed"
        self._history.append(req)
        return req

    def clear_history(self):
        self._history.clear()

    def get_sorted_history(self, sort_key=None):
        h = list(self._history)
        if sort_key == "time-asc":
            h.sort(key=lambda r: r.timestamp)
        elif sort_key == "time-desc":
            h.sort(key=lambda r: r.timestamp, reverse=True)
        elif sort_key == "priority-asc":
            h.sort(key=lambda r: r.priority)
        elif sort_key == "priority-desc":
            h.sort(key=lambda r: r.priority, reverse=True)
        return h

    def get_filtered_history(self, term):
        term = term.lower()
        return [r for r in self._history if term in r.user.lower() or term == str(r.id)]

    def has_pending(self):
        return len(self._queue) + len(self._stack) > 0

    def to_state(self):
        return {
            "queue": [r.serialize() for r in self._queue],
            "stack": [r.serialize() for r in self._stack],
            "history": [r.serialize() for r in self._history],
            "has_pending": self.has_pending(),
        }

    def all_history_serialized(self):
        return [r.serialize() for r in self._history]

    def all_queue_serialized(self):
        return [r.serialize() for r in self._queue]

    def all_stack_serialized(self):
        return [r.serialize() for r in self._stack]


manager = RequestManager()


@app.route("/")
def index():
    return render_template(
        "index.html",
        pending_queue=manager.queue,
        pending_stack=manager.stack,
        history=manager.history,
        all_history=manager.all_history_serialized(),
        all_queue=manager.all_queue_serialized(),
        all_stack=manager.all_stack_serialized(),
        sort=request.args.get("sort"),
        q=request.args.get("q", "").strip(),
    )


@app.route("/state")
def state():
    sort = request.args.get("sort")
    h = manager.get_sorted_history(sort)
    return jsonify({
        "history": [r.serialize() for r in h],
        "has_pending": manager.has_pending(),
    })


@app.route("/submit", methods=["POST"])
def submit():
    user = request.form.get("user", "").strip()
    if not user:
        return jsonify({"ok": False, "message": "Username is required.", "category": "error"})

    try:
        priority = int(request.form["priority"])
    except (ValueError, TypeError):
        return jsonify({"ok": False, "message": "Priority must be a number between 1 and 5.", "category": "error"})

    if priority < 1 or priority > 5:
        return jsonify({"ok": False, "message": "Priority must be between 1 and 5.", "category": "error"})

    req = manager.submit(user, priority)
    msg = f"Request #{req.id} from {user} submitted."
    return jsonify({"ok": True, "message": msg, "category": "success", **manager.to_state()})


@app.route("/process", methods=["POST"])
def process():
    req = manager.process()
    if req is None:
        return jsonify({"ok": True, "message": "No pending requests.", "category": "info"})

    msg = f"Request #{req.id} from {req.user} processed."
    return jsonify({"ok": True, "message": msg, "category": "success", **manager.to_state()})


@app.route("/clear", methods=["POST"])
def clear():
    manager.clear_history()
    return jsonify({"ok": True, "message": "History cleared.", "category": "info", **manager.to_state()})


if __name__ == "__main__":
    app.run(debug=True)
