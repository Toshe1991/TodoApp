import tkinter as tk
from widgets.base import BaseFrame


class Today(BaseFrame):
    def __init__(self, root, connection, *args, **kwargs):
        super().__init__(root, connection, *args, **kwargs)
        self.fetch_todos()
        self.grid(row=1, column=0, sticky=tk.N + tk.W + tk.E + tk.S)
        self.rowconfigure(1, weight=1)
        self.columnconfigure(1, weight=1)
        self.fill_tasks_frame()

    def fetch_todos(self):
        self.tasks = self.cursor.execute("""SELECT * FROM todo WHERE scheduled_date = date()
                                         AND NOT is_done ORDER BY id DESC""").fetchall()