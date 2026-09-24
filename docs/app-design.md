# AI Request Processing System — Design Document

## Overview

A simple Flask web app that simulates submitting and processing requests to an AI model. Each request has an ID, username, priority, and timestamp. Requests are queued and processed either as standard (FIFO via **queue**) or priority (LIFO via **stack**). Processed requests move into a **list**-based history, which supports sorting by time/priority and searching.

---

## Data Structures (Required)

| Structure | Purpose                                      |
|-----------|----------------------------------------------|
| Queue     | Standard-mode pending requests (FIFO)         |
| Stack     | Priority-mode pending requests (LIFO)         |
| List      | History of all processed requests             |

All three are implemented using Python's `collections.deque` (for queue/stack) and built-in `list` — no external libraries beyond Flask.

---

## Request Model

```python
{
    "id":        int,       # auto-incremented
    "user":      str,       # who submitted
    "priority":  int,       # 1 (low) .. 5 (critical)
    "timestamp": str,       # ISO format, auto-set on submit
    "status":    str,       # "pending" | "processed"
}
```

---

## Routes (Flask)

| Method | Route            | Description                                      |
|--------|------------------|--------------------------------------------------|
| GET    | `/`              | Main page — form to submit, view queues, history |
| POST   | `/submit`        | Submit a new request                             |
| POST   | `/process`       | Process one request (pop from queue or stack)    |
| GET    | `/history`       | View processed requests (supports ?sort= & ?q=)  |

### `/submit` (POST)
- Accepts `user` and `priority` from form.
- Generates `id`, sets `timestamp`, `status="pending"`.
- If `priority >= 4` → push to **stack**. Else → enqueue to **queue**.

### `/process` (POST)
- If stack is not empty → pop from stack (priority first).
- Else if queue is not empty → dequeue from queue (FIFO).
- Mark as `status="processed"`, append to **history list**.
- If both empty → show message "No pending requests."

### `/history` (GET)
- Optional query params:
  - `?sort=time` → sort history by timestamp (newest first)
  - `?sort=priority` → sort history by priority (highest first)
  - `?q=term` → search by user name or request ID (substring match)
- Default: shows all processed requests in order of processing.

---

## Algorithms

### Sorting
- Bubble sort or Python's built-in `sorted()` on the history list by `timestamp` or `priority` key.

### Searching
- Linear search over the history list by `id` or partial match on `user`.

---

## In-Memory State

```python
pending_queue  = deque()    # standard-priority requests
pending_stack  = deque()    # high-priority requests
history        = []         # all processed requests
next_id        = 1          # auto-increment
```

No database — all data lives in memory and resets on server restart.

---

## UI (Server-Rendered HTML)

Single-page app style (no JS frameworks):

1. **Submit form** — fields for username and priority (1–5 slider or dropdown).
2. **Pending section** — two tables side by side:
   - "Standard Queue" — pending requests with priority 1–3.
   - "Priority Stack" — pending requests with priority 4–5.
3. **Process button** — processes one request at a time.
4. **History section** — table with sort links and a search box.

---

## File Structure

```
AI-requests-system/
├── app.py              # Flask routes, data structures, logic
├── templates/
│   └── index.html      # single Jinja2 template
├── static/
│   └── style.css       # minimal styling
└── docs/
    └── app-design.md   # this file
```

---

## Example Flow

1. User submits: `user="Alice"`, `priority=3` → enqueued to **queue**.
2. User submits: `user="Bob"`, `priority=5` → pushed to **stack**.
3. Click "Process" → pops Bob from stack (priority first).
4. Click "Process" → dequeues Alice from queue.
5. Both appear in history, sortable and searchable.
