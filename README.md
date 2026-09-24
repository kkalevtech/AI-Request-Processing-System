# AI Request Processing System

A Flask web app that simulates submitting and processing requests to an AI model. Requests are queued based on priority — standard requests (1–3) go to a FIFO queue, high-priority requests (4–5) go to a LIFO stack. Processed requests move to a sortable, searchable history.

## Features

- **Submit requests** — username and priority (1–5)
- **Dual routing** — priority 4–5 → stack (LIFO), priority 1–3 → queue (FIFO)
- **Process requests** — stack processed first, then queue
- **History** — sort by time or priority (ascending/descending), search by user or ID
- **Pagination** — 5 items per page with numbered navigation
- **Dark theme** — amber/teal palette, Space Grotesk + Inter fonts, Material Symbols icons
- **AJAX-driven** — no page reloads on submit, process, sort, search, or clear
- **Toast notifications** — slide-in, auto-dismiss after 5 seconds, dismissible with ×

## Setup

```bash
pip install -r requirements.txt
python app.py
```

Open **http://127.0.0.1:5000**.

## Data Structures

| Structure | Implementation       | Purpose                          |
|-----------|----------------------|----------------------------------|
| Queue     | `collections.deque`  | Standard pending (FIFO)          |
| Stack     | `collections.deque`  | Priority pending (LIFO)          |
| List      | `list`               | History of processed requests    |

All data lives in memory — resets on server restart.

## Routes

| Method | Route       | Description                             |
|--------|-------------|-----------------------------------------|
| GET    | `/`         | Main page                               |
| GET    | `/state`    | JSON state (for AJAX sort)              |
| POST   | `/submit`   | Submit a new request (JSON)             |
| POST   | `/process`  | Process one request (JSON)              |
| POST   | `/clear`    | Clear history (JSON)                    |

## Request Model

```json
{
    "id": 1,
    "user": "Alice",
    "priority": 3,
    "timestamp": "24.09.2026, 14:30:00",
    "status": "pending"
}
```

## Tech Stack

- **Backend**: Python, Flask
- **Frontend**: Jinja2, vanilla JS, CSS
- **Fonts**: Space Grotesk, Inter, Material Symbols (Google Fonts)
- **No database**, no external JS frameworks
