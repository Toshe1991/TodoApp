import tkinter as tk
from widgets.header import Header
from widgets.today import Today
from widgets.schedule import Schedule

from db.sqlite import open_db_connection, create_db_table


class TodoApp(tk.Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cursor, self.connection = open_db_connection()
        create_db_table(self.cursor, self.connection)
        self._set_main_frame_attrs()
        self.header = Header(self, today_action=self.open_today_frame, schedule_action=self.open_schedule_frame)
        self.today_frame = None
        self.schedule_frame = None

    def _set_main_frame_attrs(self):
        self.title("ToDo App")
        position_x = int(self.winfo_screenwidth()/2 - 400)
        position_y = int(self.winfo_screenheight()/2 - 300)
        self.geometry("800x600+{}+{}".format(position_x, position_y))
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.configure(background='#ffffff')

    def open_today_frame(self, **kwargs):
        if self.children.get("!schedule"):
            self.children["!schedule"].destroy()
        self.today_frame = Today(self, self.connection)
        self.header.button_scheduled.config(bg="#585858")
        self.header.button_today.config(bg="#424141")

    def open_schedule_frame(self):
        if self.children.get("!today"):
            self.children["!today"].destroy()
        self.schedule_frame = Schedule(self, self.connection)
        self.header.button_today.config(bg="#585858")
        self.header.button_scheduled.config(bg="#424141")

    def destroy(self):
        super().destroy()
        self.connection.close()


todo_app = TodoApp()
todo_app.mainloop()
