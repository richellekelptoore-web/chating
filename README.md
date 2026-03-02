# ChatGlyo [GUI] + [BROWSER] (Python)

This project has 3 Python files:

1. `chatglyo_gui.py` → Desktop GUI chat app for PC.
2. `chatglyo_browser.py` → Browser chat app using **Python WSGI + HTML templates**.
3. `chatglyo_download_hub.py` → Bundle helper to zip project files.

## Browser app now uses HTML + Python scripts

- HTML pages are in `web/templates/`:
  - `signin.html`
  - `lobby.html`
  - `chat.html`
  - `downloads.html`
- Python server handles routing, sign-in checks, lobby, chat posting, and file downloads.

## Theme and flow

- Green + white style
- Sign-in page with animated green wave and 3/3 validation
- Lobby with `+ New Chat`
- Chat with back button, pfp area, call/video icons, emoji/GIF/attachment placeholder buttons
- Downloads page with links for GUI/browser/download-hub scripts

## Run

### GUI app (PC)

```bash
python chatglyo_gui.py
```

### Browser app (all devices on your network)

```bash
python chatglyo_browser.py
```

Open:

```text
http://localhost:5000
```

### Build zip bundle

```bash
python chatglyo_download_hub.py
```

## Optional native executable build (GUI)

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name ChatGlyoGUI chatglyo_gui.py
```
