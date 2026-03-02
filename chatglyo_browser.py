from html import escape
from pathlib import Path
from urllib.parse import parse_qs, quote, urlparse
from wsgiref.simple_server import make_server

BASE_DIR = Path(__file__).resolve().parent
TEMPLATE_DIR = BASE_DIR / "web" / "templates"

state = {
    "user": {"username": "", "email": "", "password": "", "pfp": "👤"},
    "rooms": {},
}

DOWNLOAD_MAP = {
    "gui": BASE_DIR / "chatglyo_gui.py",
    "browser": BASE_DIR / "chatglyo_browser.py",
    "download-hub": BASE_DIR / "chatglyo_download_hub.py",
}


def read_template(name: str) -> str:
    return (TEMPLATE_DIR / name).read_text(encoding="utf-8")


def checks(user):
    result = {
        "username": len((user.get("username") or "").strip()) >= 3,
        "email": "@" in (user.get("email") or "") and "." in (user.get("email") or ""),
        "password": len((user.get("password") or "")) >= 6,
    }
    done = sum(1 for v in result.values() if v)
    return result, done


def html_response(start_response, body: str, status="200 OK"):
    data = body.encode("utf-8")
    start_response(status, [("Content-Type", "text/html; charset=utf-8"), ("Content-Length", str(len(data)))])
    return [data]


def redirect(start_response, location: str):
    start_response("302 Found", [("Location", location)])
    return [b""]


def parse_post(environ):
    try:
        size = int(environ.get("CONTENT_LENGTH", "0") or "0")
    except ValueError:
        size = 0
    raw = environ["wsgi.input"].read(size).decode("utf-8")
    return {k: v[0] for k, v in parse_qs(raw).items()}


def render_signin(start_response):
    c, done = checks(state["user"])
    html = read_template("signin.html")
    html = html.replace("{{username}}", escape(state["user"].get("username", "")))
    html = html.replace("{{email}}", escape(state["user"].get("email", "")))
    html = html.replace("{{password}}", escape(state["user"].get("password", "")))
    html = html.replace("{{u_dot}}", "🟢" if c["username"] else "🔴")
    html = html.replace("{{e_dot}}", "🟢" if c["email"] else "🔴")
    html = html.replace("{{p_dot}}", "🟢" if c["password"] else "🔴")
    html = html.replace("{{done}}", str(done))
    html = html.replace("{{done_state}}", "unlocked" if done == 3 else "locked")
    html = html.replace("{{done_disabled}}", "" if done == 3 else "disabled")
    return html_response(start_response, html)


def render_lobby(start_response):
    html = read_template("lobby.html")
    rooms_html = "".join(f'<li><a href="/chat/{quote(room)}">{escape(room)}</a></li>' for room in state["rooms"].keys())
    if not rooms_html:
        rooms_html = "<li>(Empty lobby) Use + New Chat</li>"
    html = html.replace("{{pfp}}", escape(state["user"].get("pfp", "👤")))
    html = html.replace("{{username}}", escape(state["user"].get("username", "")))
    html = html.replace("{{rooms}}", rooms_html)
    return html_response(start_response, html)


def render_chat(start_response, room):
    state["rooms"].setdefault(room, [])
    html = read_template("chat.html")
    messages_html = "".join(
        f"<p><strong>{escape(sender)}:</strong> {escape(msg)}</p>" for sender, msg in state["rooms"][room]
    ) or "<p>You can chat any if can!</p>"
    html = html.replace("{{pfp}}", escape(state["user"].get("pfp", "👤")))
    html = html.replace("{{room}}", escape(room))
    html = html.replace("{{messages}}", messages_html)
    html = html.replace("{{room_url}}", quote(room))
    return html_response(start_response, html)


def render_downloads(start_response):
    html = read_template("downloads.html")
    return html_response(start_response, html)


def download_file(start_response, key):
    path = DOWNLOAD_MAP.get(key)
    if not path or not path.exists():
        return html_response(start_response, "<h2>File not found</h2>", status="404 Not Found")
    data = path.read_bytes()
    headers = [
        ("Content-Type", "application/octet-stream"),
        ("Content-Disposition", f'attachment; filename="{path.name}"'),
        ("Content-Length", str(len(data))),
    ]
    start_response("200 OK", headers)
    return [data]


def app(environ, start_response):
    method = environ.get("REQUEST_METHOD", "GET")
    path = urlparse(environ.get("PATH_INFO", "/")).path

    if method == "GET" and path == "/":
        return render_signin(start_response)

    if method == "POST" and path == "/signin":
        data = parse_post(environ)
        state["user"].update(
            username=data.get("username", "").strip(),
            email=data.get("email", "").strip(),
            password=data.get("password", ""),
        )
        _, done = checks(state["user"])
        return redirect(start_response, "/lobby") if done == 3 else render_signin(start_response)

    if method == "GET" and path == "/lobby":
        return render_lobby(start_response)

    if method == "GET" and path == "/new-room":
        room = f"chat-{len(state['rooms']) + 1}"
        state["rooms"].setdefault(room, [])
        return redirect(start_response, f"/chat/{quote(room)}")

    if method == "POST" and path == "/edit-profile":
        data = parse_post(environ)
        username = data.get("username", "").strip()
        if len(username) >= 3:
            state["user"]["username"] = username
        state["user"]["pfp"] = data.get("pfp", "👤")
        return redirect(start_response, "/lobby")

    if path.startswith("/chat/"):
        room = path.split("/chat/", 1)[1]
        if method == "POST":
            data = parse_post(environ)
            msg = data.get("message", "").strip()
            if msg:
                state["rooms"].setdefault(room, []).append((state["user"].get("username") or "me", msg))
            return redirect(start_response, f"/chat/{quote(room)}")
        return render_chat(start_response, room)

    if method == "GET" and path == "/downloads":
        return render_downloads(start_response)

    if method == "GET" and path.startswith("/download/"):
        key = path.split("/download/", 1)[1]
        return download_file(start_response, key)

    return html_response(start_response, "<h2>404 Not Found</h2>", status="404 Not Found")


if __name__ == "__main__":
    with make_server("0.0.0.0", 5000, app) as server:
        print("ChatGlyo Browser running at http://localhost:5000")
        server.serve_forever()
