from collections import deque

from flask import Flask, render_template

app = Flask(__name__)

pending_queue = deque()
pending_stack = deque()
history = []
next_id = 1


@app.route("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
