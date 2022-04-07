import os
from datetime import datetime, date, time, timedelta
from importlib import resources
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.scrolledtext import ScrolledText

from tkcalendar import Calendar, DateEntry

from src.utils import *
from src.config import DEFAULT_SINCE


def main():
    since = datetime.fromisoformat(DEFAULT_SINCE)
    until = datetime.now()
    files = run(since=since, until=until, root_path=".", channel_name="all_share")

    start_gui(files)


def start_gui(files):
    win = tk.Tk()
    win.resizable(width=False, height=False)  # ウィンドウを固定サイズに
    app = Application(master=win, files=files)
    app.mainloop()


class Application(tk.Frame):
    def __init__(self, master, files):
        super().__init__(master)
        self.pack(padx=20, pady=15, fill="both", expand=True)
        self.files = files
        self.chk = []
        self.chk_value = []
        self.since = datetime.fromisoformat(DEFAULT_SINCE)
        self.until = datetime.now()
        self.icon_path = self.get_icon_path()

        w = 400
        h = 480
        sw = self.master.winfo_screenwidth()
        sh = self.master.winfo_screenheight()
        wx = int((sw / 2) - (w / 2))
        wy = int((sh / 2) - (h / 2))
        self.master.geometry(f"{w}x{h}+{wx}+{wy}")
        self.master.title("Slackcat")
        self.master.iconbitmap(self.icon_path)
        self.create_frames()

    def get_icon_path(self):
        # return f"{os.path.dirname(os.path.abspath(__file__))}/../imgs/slack_cat.ico"
        with resources.path("imgs", "slack_cat.ico") as icon:
            return icon.absolute()

    def create_frames(self):
        global frame0, frame1

        frame0 = tk.LabelFrame(
            self,
            text="Console",
            borderwidth=5,
            bg="darkblue",
            fg="white",
            font=("arial", 10, "bold"),
            relief="flat",
            bd=1,
        )
        frame1 = tk.LabelFrame(
            self, text="File select", borderwidth=5, font=("arial", 10, "bold"), relief="solid", bd=1,
        )

        tk.Button(frame0, text="Date Select", font=("arial", 10, "bold"), command=self.make_cals,).pack(
            side="left", ipadx=30, padx=20
        )
        tk.Button(frame0, text="Download", font=("arial", 10, "bold"), command=self.downloadButtonClick,).pack(
            side="right", ipadx=30, padx=20
        )

        text = ScrolledText(frame1, cursor="arrow")
        text.pack(side="bottom", padx=10, pady=5)

        select_all_btn = tk.Button(frame1, text="All", font=("arial", 10, "bold"), command=self.select_all)
        deselect_all_btn = tk.Button(frame1, text="Clear", font=("arial", 10, "bold"), command=self.deselect_all)
        select_all_btn.pack(side="left", expand=False, padx=10, pady=5, ipadx=5)
        deselect_all_btn.pack(side="left", expand=False, pady=5, ipadx=5)

        self.chk = []
        self.chk_value = []
        for file in self.files:
            bvar = tk.BooleanVar()
            bvar.set(False)
            cb = tk.Checkbutton(text, text=file[0], variable=bvar, anchor="w", bg="white")

            self.chk_value.append(bvar)
            self.chk.append(cb)

            text.window_create("end", window=cb)
            text.insert("end", "\n")
        text.configure(state="disabled")

        frame0.pack(fill="x", pady=5)
        frame1.pack(fill="both", expand=True, pady=5)

    def select_all(self):
        for cb in self.chk:
            cb.select()

    def deselect_all(self):
        for cb in self.chk:
            cb.deselect()

    def delete_frames(self):
        frame0.destroy()
        frame1.destroy()

    def upload_pane(self):
        self.delete_frames()
        self.create_frames()

    def make_cals(self):
        def set_files():
            self.since = cal1.get_date()
            self.until = cal2.get_date()
            log()

            messages = get_history(since=self.since, until=self.until)
            thread_messages = get_threads_all(messages=messages)
            self.files = get_file_url(thread_messages=thread_messages)

            self.upload_pane()
            root.destroy()

        def log():
            print(f"Until : {self.until}")
            print(f"Since : {self.since}")

        root = tk.Toplevel()
        root.title("Date")
        w = 200
        h = 180
        sw = self.master.winfo_screenwidth()
        sh = self.master.winfo_screenheight()
        x = int((sw / 2) - (w / 2))
        y = int((sh / 2) - (h / 2))
        root.geometry(f"{w}x{h}+{x}+{y}")
        root.iconbitmap(self.icon_path)

        ttk.Label(root, text="Since").pack()
        cal1 = DateEntry(
            root, width=12, background="darkblue", foreground="white", borderwidth=2, year=date.today().year,
        )
        cal1.pack(padx=10, pady=10)
        ttk.Label(root, text="Until").pack()
        cal2 = DateEntry(
            root, width=12, background="darkblue", foreground="white", borderwidth=2, year=date.today().year,
        )
        cal2.pack(padx=10, pady=10)
        ttk.Button(root, text="OK", command=set_files).pack(padx=10, pady=10)

    def downloadButtonClick(self):
        checked_files = []
        for i, value in enumerate(self.chk_value):
            if value.get():
                checked_files.append(self.files[i])

        if checked_files:
            # true means len(checked_files) != 0
            try:
                file_download(checked_files)
            except Exception as e:
                # show error message
                messagebox.showerror(message=f"ダウンロードに失敗しました。\n{e}")
            else:
                # show success message
                messagebox.showinfo(message="Completed.")
                self.deselect_all()


if __name__ == "__main__":
    main()
