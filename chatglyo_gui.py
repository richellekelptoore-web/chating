import math
import tkinter as tk
from tkinter import filedialog, messagebox


class ChatGlyoGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ChatGlyo GUI")
        self.geometry("1160x760")
        self.minsize(980, 680)
        self.configure(bg="#f4f8f5")

        self.user = {"username": "", "email": "", "password": "", "pfp": "👤"}
        self.rooms = {}

        self.container = tk.Frame(self, bg="#f4f8f5")
        self.container.pack(fill="both", expand=True)
        self.show_signin()

    def clear(self):
        for w in self.container.winfo_children():
            w.destroy()

    def show_signin(self):
        self.clear()
        SignInPage(self.container, self).pack(fill="both", expand=True)

    def show_lobby(self):
        self.clear()
        LobbyPage(self.container, self).pack(fill="both", expand=True)

    def show_chat(self, room_name):
        if room_name not in self.rooms:
            self.rooms[room_name] = []
        self.clear()
        ChatPage(self.container, self, room_name).pack(fill="both", expand=True)


class SignInPage(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg="#ffffff")
        self.app = app
        self.phase = 0

        tk.Label(self, text="ChatGlyo [GUI]", font=("Segoe UI", 28, "bold"), bg="#ffffff", fg="#1d4d38").pack(pady=(20, 4))
        tk.Label(self, text="Green + White style | Sign in to continue", font=("Segoe UI", 12), bg="#ffffff", fg="#4f6b5f").pack(pady=(0, 8))

        self.wave = tk.Canvas(self, height=170, bg="#ffffff", highlightthickness=0)
        self.wave.pack(fill="x", padx=20)

        card = tk.Frame(self, bg="#ffffff", bd=1, relief="solid", highlightbackground="#dbe8df")
        card.pack(fill="x", padx=180, pady=10)

        self.username = tk.StringVar()
        self.email = tk.StringVar()
        self.password = tk.StringVar()
        self.show_pw = tk.BooleanVar(value=False)

        self.states = {k: tk.StringVar(value="🔴") for k in ("username", "email", "password")}

        self._field(card, "Enter your Username", self.username, "username")
        self._field(card, "Enter your Email", self.email, "email")
        self._field(card, "Enter your Password", self.password, "password", pw=True)

        bar = tk.Frame(card, bg="#ffffff")
        bar.pack(fill="x", padx=26, pady=(6, 16))

        self.progress = tk.Label(bar, text="Done 0/3 (locked)", bg="#ffffff", fg="#6c7f73", font=("Segoe UI", 11, "bold"))
        self.progress.pack(side="left")

        self.done_btn = tk.Button(bar, text="0<-- Done -->0", state="disabled", bg="#9ecfaf", fg="white", relief="flat", font=("Segoe UI", 11, "bold"), command=self.finish)
        self.done_btn.pack(side="right")

        for var in (self.username, self.email, self.password):
            var.trace_add("write", lambda *_: self.validate())

        self.bind("<Configure>", lambda _e: self.draw_wave())
        self.after(30, self.animate)

    def _field(self, parent, label, var, key, pw=False):
        box = tk.Frame(parent, bg="#ffffff")
        box.pack(fill="x", padx=26, pady=9)
        tk.Label(box, text=label, bg="#ffffff", fg="#22382c", font=("Segoe UI", 11)).pack(anchor="w")

        row = tk.Frame(box, bg="#ffffff")
        row.pack(fill="x", pady=(4, 0))

        ent = tk.Entry(row, textvariable=var, font=("Segoe UI", 11), show="*" if pw else "", bd=1, relief="solid", highlightthickness=1, highlightcolor="#24a05b")
        ent.pack(side="left", fill="x", expand=True)

        tk.Label(row, textvariable=self.states[key], bg="#ffffff", font=("Segoe UI", 13, "bold")).pack(side="left", padx=8)

        if pw:
            tk.Checkbutton(box, text="hide/show", variable=self.show_pw, bg="#ffffff", selectcolor="#ffffff", command=lambda e=ent: e.config(show="" if self.show_pw.get() else "*")).pack(anchor="w", pady=(4, 0))

    def validate(self):
        checks = {
            "username": len(self.username.get().strip()) >= 3,
            "email": "@" in self.email.get() and "." in self.email.get(),
            "password": len(self.password.get()) >= 6,
        }
        done = 0
        for k, ok in checks.items():
            self.states[k].set("🟢" if ok else "🔴")
            done += int(ok)

        if done == 3:
            self.progress.config(text="Done 3/3 (unlocked)", fg="#139b52")
            self.done_btn.config(state="normal", bg="#139b52")
        else:
            self.progress.config(text=f"Done {done}/3 (locked)", fg="#6c7f73")
            self.done_btn.config(state="disabled", bg="#9ecfaf")

    def finish(self):
        self.app.user["username"] = self.username.get().strip()
        self.app.user["email"] = self.email.get().strip()
        self.app.user["password"] = self.password.get()
        self.app.show_lobby()

    def draw_wave(self):
        self.wave.delete("all")
        w = self.wave.winfo_width()
        h = self.wave.winfo_height()
        pts = []
        for x in range(0, w + 10, 10):
            y = 90 + math.sin((x / 90) + self.phase) * 22
            pts.extend([x, y])
        poly = [0, h] + pts + [w, h]
        self.wave.create_polygon(poly, fill="#2bcb71", outline="")
        self.wave.create_polygon([0, h] + [v if i % 2 == 0 else v + 14 for i, v in enumerate(pts)] + [w, h], fill="#149b50", outline="", stipple="gray50")

    def animate(self):
        self.phase += 0.15
        self.draw_wave()
        self.after(40, self.animate)


class LobbyPage(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg="#edf4ee")
        self.app = app

        top = tk.Frame(self, bg="#edf4ee")
        top.pack(fill="x", padx=18, pady=12)

        tk.Button(top, text="+ New Chat", command=self.new_room, bg="#149b50", fg="white", relief="flat", font=("Segoe UI", 11, "bold")).pack(side="left")
        tk.Button(top, text="Edit Username", command=self.edit_username, bg="#d9e8dc", relief="flat").pack(side="left", padx=8)
        tk.Button(top, text="Change PFP (image/gif)", command=self.change_pfp, bg="#d9e8dc", relief="flat").pack(side="left")

        tk.Label(top, text=f"Lobby | {self.app.user['pfp']} {self.app.user.get('username')}", bg="#edf4ee", fg="#1e3b2c", font=("Segoe UI", 13, "bold")).pack(side="left", padx=16)

        self.rooms_list = tk.Listbox(self, font=("Segoe UI", 11), bd=0)
        self.rooms_list.pack(fill="both", expand=True, padx=20, pady=(0, 18))
        self.rooms_list.bind("<Double-1>", self.open_room)
        self.refresh()

    def refresh(self):
        self.rooms_list.delete(0, tk.END)
        if not self.app.rooms:
            self.rooms_list.insert(tk.END, "(Empty lobby) Use + New Chat")
        else:
            for room in self.app.rooms:
                self.rooms_list.insert(tk.END, room)

    def new_room(self):
        pop = tk.Toplevel(self)
        pop.title("New chat")
        pop.geometry("320x170")
        tk.Label(pop, text="Username / room name", font=("Segoe UI", 11)).pack(pady=(14, 6))
        name = tk.StringVar()
        tk.Entry(pop, textvariable=name, font=("Segoe UI", 11)).pack(fill="x", padx=18)

        def save():
            n = name.get().strip()
            if not n:
                return
            self.app.rooms.setdefault(n, [])
            self.refresh()
            pop.destroy()

        tk.Button(pop, text="Create", command=save, bg="#149b50", fg="white", relief="flat").pack(pady=14)

    def open_room(self, _e=None):
        sel = self.rooms_list.curselection()
        if not sel:
            return
        room = self.rooms_list.get(sel[0])
        if room.startswith("(Empty lobby)"):
            return
        self.app.show_chat(room)

    def edit_username(self):
        pop = tk.Toplevel(self)
        pop.title("Edit username")
        pop.geometry("320x150")
        new_name = tk.StringVar(value=self.app.user.get("username", ""))
        tk.Label(pop, text="New username", font=("Segoe UI", 11)).pack(pady=(14, 6))
        tk.Entry(pop, textvariable=new_name, font=("Segoe UI", 11)).pack(fill="x", padx=18)

        def save():
            n = new_name.get().strip()
            if len(n) < 3:
                messagebox.showwarning("Invalid", "Username must be at least 3 characters.")
                return
            self.app.user["username"] = n
            pop.destroy()
            self.app.show_lobby()

        tk.Button(pop, text="Save", command=save, bg="#149b50", fg="white", relief="flat").pack(pady=12)

    def change_pfp(self):
        path = filedialog.askopenfilename(title="Choose image/gif", filetypes=[("Image/GIF", "*.png *.jpg *.jpeg *.gif"), ("All files", "*.*")])
        if path:
            self.app.user["pfp"] = "🖼️"
            messagebox.showinfo("PFP", f"Selected: {path}\n(Preview simplified in this demo)")
            self.app.show_lobby()


class ChatPage(tk.Frame):
    def __init__(self, parent, app, room):
        super().__init__(parent, bg="#dde5df")
        self.app = app
        self.room = room
        self.msg = tk.StringVar()

        head = tk.Frame(self, bg="#f8fbf8")
        head.pack(fill="x")
        tk.Button(head, text="←", command=app.show_lobby, bg="#f8fbf8", relief="flat", font=("Segoe UI", 12, "bold")).pack(side="left", padx=10, pady=12)
        tk.Label(head, text=f"{app.user['pfp']}", font=("Segoe UI", 24), bg="#f8fbf8").pack(side="left")
        tk.Label(head, text=room, font=("Segoe UI", 14, "bold"), bg="#f8fbf8", fg="#264132").pack(side="left", padx=8)
        tk.Button(head, text="📞", bg="#f8fbf8", relief="flat").pack(side="right", padx=8)
        tk.Button(head, text="📹", bg="#f8fbf8", relief="flat").pack(side="right")

        self.text = tk.Text(self, state="disabled", bg="white", font=("Segoe UI", 11), wrap="word")
        self.text.pack(fill="both", expand=True, padx=12, pady=12)

        foot = tk.Frame(self, bg="#f8fbf8")
        foot.pack(fill="x", padx=12, pady=(0, 12))

        e = tk.Entry(foot, textvariable=self.msg, font=("Segoe UI", 11))
        e.pack(side="left", fill="x", expand=True, ipady=6)
        e.bind("<Return>", lambda _ev: self.send())

        tk.Button(foot, text="😊", relief="flat").pack(side="left", padx=4)
        tk.Button(foot, text="GIF", relief="flat").pack(side="left", padx=4)
        tk.Button(foot, text="🧷", relief="flat").pack(side="left", padx=4)
        tk.Button(foot, text="Send", command=self.send, bg="#149b50", fg="white", relief="flat").pack(side="left", padx=(6, 0))

        self.render()

    def render(self):
        history = self.app.rooms.get(self.room, [])
        self.text.config(state="normal")
        self.text.delete("1.0", tk.END)
        if not history:
            self.text.insert(tk.END, "You can chat any if can!\n")
        for sender, message in history:
            self.text.insert(tk.END, f"{sender}: {message}\n")
        self.text.config(state="disabled")

    def send(self):
        m = self.msg.get().strip()
        if not m:
            return
        self.app.rooms[self.room].append((self.app.user.get("username") or "me", m))
        self.msg.set("")
        self.render()


if __name__ == "__main__":
    ChatGlyoGUI().mainloop()
