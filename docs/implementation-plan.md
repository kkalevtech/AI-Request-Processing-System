# Implementation Plan — AI Request Processing System

Plan is split into phases. **Each phase = 1 commit.** After each phase the AI Agent self-verifies (starts the app, hits the route, checks output), then commits.

---

## Phase 1: Project Scaffold & Flask Skeleton

**Goal:** Minimal Flask app that starts and serves a blank page.

### Tasks
- Create `app.py` with Flask import, a single route `/`, and `app.run(debug=True)`.
- Create `templates/index.html` — minimal HTML with a `<h1>` title.
- Create `static/style.css` — empty or minimal body font.
- Create `requirements.txt` with `flask`.
- Install dependencies (`pip install -r requirements.txt`).
- Start the app, verify `GET /` returns 200 and shows the title.

### Verification
- Run `python app.py`, open `http://127.0.0.1:5000/`, confirm page loads.

### Commit message
```
Phase 1: Flask skeleton with blank index page
```

---

## Phase 2: In-Memory Data Structures

**Goal:** Initialize queue, stack, list, and next_id counter in `app.py`. No routes yet — just the state objects.

### Tasks
- Add `from collections import deque` to `app.py`.
- Declare module-level variables:
  ```python
  pending_queue = deque()
  pending_stack = deque()
  history = []
  next_id = 1
  ```

### Verification
- Run `python -c "import app; print(app.pending_queue, type(app.pending_queue))"` — confirms deque exists.

### Commit message
```
Phase 2: Initialize in-memory data structures (queue, stack, list)
```

---

## Phase 3: Submit Request Logic

**Goal:** `/submit` POST route that creates a request and routes it to queue or stack.

### Tasks
- Add `/submit` POST route in `app.py`.
- Read `user` and `priority` from `request.form`.
- Generate `id` from `next_id` counter, set `timestamp` via `datetime.now().isoformat()`, `status = "pending"`.
- If `priority >= 4` → append to `pending_stack`. Else → append to `pending_queue`.
- Store item as a dict.
- Redirect back to `/`.

### Verification
- Submit a form via curl or browser, check `pending_queue`/`pending_stack` in memory.
- Submit priority 3 → appears in queue. Submit priority 5 → appears in stack.

### Commit message
```
Phase 3: POST /submit route with priority routing to queue or stack
```

---

## Phase 4: Process Request Logic

**Goal:** `/process` POST route that pops one request (stack first, then queue) and moves it to history.

### Tasks
- Add `/process` POST route.
- If `pending_stack` not empty → pop from stack.
- Else if `pending_queue` not empty → popleft from queue.
- Else → flash/return message "No pending requests."
- Set `status = "processed"`, append to `history` list.
- Redirect back to `/`.

### Verification
- Submit a request, hit `/process`, confirm it moves from pending to history.
- Submit both priority 3 and priority 5, process twice — confirm priority 5 is processed first.

### Commit message
```
Phase 4: POST /process route — stack-pop first, then queue-dequeue, move to history
```

---

## Phase 5: Main Page UI — Submit Form & Pending Display

**Goal:** `index.html` shows the submit form, the two pending tables (queue & stack), and a process button.

### Tasks
- Update `index.html` template:
  - Form with `user` text input and `priority` number input (1–5), posting to `/submit`.
  - "Process Next" button posting to `/process`.
  - Two tables: "Standard Queue" (items from `pending_queue`) and "Priority Stack" (items from `pending_stack`).
- Pass `pending_queue`, `pending_stack`, `history` to the template in `GET /`.
- Add basic CSS in `style.css` — two-column layout, table borders.

### Verification
- Submit requests, observe them appear in the correct table.
- Process requests, observe them disappear from pending.

### Commit message
```
Phase 5: UI for submit form and pending queue/stack display
```

---

## Phase 6: History Page — Display, Sort, Search

**Goal:** `/history` route and history table under the pending section, with sorting and search.

### Tasks
- Update `GET /` to pass `history` (already done).
- Add "History" table to `index.html`.
- Implement sorting:
  - Read `?sort=` query param from `request.args`.
  - `?sort=time` → sort `history` by `timestamp` descending.
  - `?sort=priority` → sort `history` by `priority` descending.
  - Pass sorted copy to template (do not mutate original history order).
- Implement search:
  - Read `?q=` query param.
  - Linear search over history: match if `q` is substring of `user` or matches `id` (as string).
  - Pass filtered list to template.
- Add sort links (column headers) and a search text input in the history section.
- Add some CSS styling for the history table, search box, sort links.

### Verification
- Process 3–4 requests with varying users and priorities.
- Sort by time — verify order.
- Sort by priority — verify order.
- Search by partial username — verify matching results.
- Search by ID — verify exact match.
- Combined sort + search — verify sort applies to filtered results.

### Commit message
```
Phase 6: History display with sort (time/priority) and search (user/id)
```

---

## Phase 7: Polish & Final Integration

**Goal:** Cleanup, error handling, flash messages, final verification.

### Tasks
- Add flash messages for: request submitted, request processed, no pending, invalid input.
- Validate `priority` is 1–5 integer on `/submit`; show error if not.
- Add a "Clear History" button (POST `/clear`) — empties `history` list.
- Improve CSS: spacing, colors, responsive layout.
- Final end-to-end test:
  1. Submit 5 requests with mixed priorities.
  2. Verify queue/stack placement.
  3. Process all 5 — verify stack (priority) goes first.
  4. Verify history sort/search works.
  5. Clear history.
- Ensure all required data structures are used throughout.

### Verification
- Full manual walkthrough of all features.

### Commit message
```
Phase 7: Polish — flash messages, validation, clear history, CSS cleanup
```

---

## Summary

| Phase | Focus                            | Routes          |
|-------|----------------------------------|-----------------|
| 1     | Flask skeleton                   | `GET /`         |
| 2     | Data structures                  | —               |
| 3     | Submit logic                     | `POST /submit`  |
| 4     | Process logic                    | `POST /process` |
| 5     | Submit form + pending UI         | `GET /`         |
| 6     | History sort + search            | `GET /`         |
| 7     | Polish, validation, final tests  | `POST /clear`   |

After Phase 7 the system is complete and fully functional.
