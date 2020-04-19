import tkinter as tk
from PIL import ImageTk, Image
from db.sqlite import insert_into_table, update_row
from widgets.dialog import DialogBox
import datetime
import os
from functools import partial
import configparser

config = configparser.ConfigParser()
config.read("main.conf")

palette = config["COLORS"]


class BaseFrame(tk.Frame):
    def __init__(self, root, connection, *args, **kwargs):
        super().__init__(root, bg=palette["background"])
        self.tasks = None
        self.connection = connection
        self.cursor = self.connection.cursor()
        self.all_tasks = {}
        self.img = self._parse_background_image()
        self.scroll_canvas = tk.Canvas(self, bg=palette["background"], width=600, bd=0, highlightthickness=0, relief='ridge')
        self.vscroll = tk.Scrollbar(self, orient=tk.VERTICAL)
        self.vscroll.config(command=self.scroll_canvas.yview)
        self.tasks_frame = tk.Frame(self.scroll_canvas, bg=palette["background"])
        self.scroll_canvas.create_window(0, 0, window=self.tasks_frame, anchor='nw')
        self.scroll_canvas.config(yscrollcommand=self.vscroll.set)
        self.no_tasks_frame = tk.Frame(self, bg=palette["background"])
        self._configure_entry_field()
        self.root = root
        self.root.bind('<Return>', self.on_submit)
        self._dialog_box = None

    def _parse_background_image(self):
        path = os.path.dirname(os.path.abspath(__file__))
        image_path = os.path.join(path, "images/check.png")
        im = Image.open(image_path)
        img = im.resize((156, 128), Image.ANTIALIAS)
        img = ImageTk.PhotoImage(img)

        return img

    def _configure_entry_field(self):
        self.entry = tk.Text(self, bd=0.5, width=74, height=1, spacing1=7, spacing3=7, fg=palette['fontColor'])
        self.entry.insert('1.0', 'Task Title')
        self.entry.grid(row=0, column=1, pady=(30, 30))
        self.entry.bind("<Button-1>", self.on_entry_clicked)

    def on_entry_clicked(self, event):
        self.entry.config(highlightcolor=palette["primary"])
        if self.entry.get('1.0', '10.0') == 'Task Title\n':
            self.entry.delete("1.0", "10.0")

    def set_default_background(self):
        panel = tk.Label(self.no_tasks_frame, image=self.img, bd=0)
        no_tasks = tk.Label(self.no_tasks_frame, text='No Tasks Found', bg=palette["background"], bd=0,
                            fg=palette["fontColor"])
        add_tasks = tk.Label(self.no_tasks_frame, text='You can add tasks using the input above',
                             bg=palette["background"], bd=0, fg=palette["fontColor"])
        panel.grid(columnspan=2, row=1, rowspan=2, pady=(60, 30))
        no_tasks.grid(columnspan=2, row=4)
        add_tasks.grid(columnspan=2, row=5)

    def on_submit(self, e):
        self.focus()
        data = self.entry.get('0.0', tk.END).strip('\n')

        if data and data != 'Task Title':
            insert_into_table(self.cursor, data, self.connection)
            self.no_tasks_frame.grid_remove()
            self.add_task_to_list()
            self.entry.delete('1.0', tk.END)
            self.entry.insert('1.0', 'Task Title')

    def add_task_to_list(self):
        id = self.cursor.lastrowid
        task = self.cursor.execute("SELECT * FROM todo WHERE id = %s LIMIT 1" % id).fetchone()
        if not self.tasks:
            self.scroll_canvas.grid(row=1, column=1, sticky=tk.NS)
        self.render_task(task, len(self.all_tasks), self.tasks_frame)

    def handle_edit_action(self, task_id):
        DialogBox.root = self.root
        self._dialog_box = DialogBox(save=self.on_edit_save, delete=self.on_edit_delete, task_id=task_id)

    def render_task(self, task, index, target_frame):
        task_fields = tk.Text(target_frame, bd=2, width=80, height=1, spacing1=7, spacing3=7, fg="white",
                              bg=palette["primary"], highlightbackground=palette["metallic"],
                              relief=tk.RAISED)
        task_fields.task_id = task['id']
        task_fields.insert('1.0', task['task'])
        task_fields.config(state=tk.DISABLED, cursor='hand1')
        task_fields.grid(row=index + 1, column=1, pady=(10, 10))
        extra_options = tk.Button(task_fields, text='✎', bg=palette["background"], fg="white",
                                  bd=0, relief="raised", command=lambda: self.handle_edit_action(task["id"]))
        extra_options.config(highlightbackground=palette["primary"], cursor='hand1',
                             activebackground=palette["secondary"], activeforeground=palette["fontColor"],
                             bg=palette["primary"])
        extra_options.pack(padx=(553, 0))
        self.all_tasks.update({task['id']: task_fields})
        task_fields.bind("<Button-1>", partial(self.on_task_done, task_fields))
        task_fields.bind("<Enter>", partial(self.task_on_hover, task_fields, extra_options,
                                            palette["laurel"], "black"))
        task_fields.bind("<Leave>", partial(self.task_on_hover, task_fields, extra_options,
                                            palette['primary'], "white"))

    @staticmethod
    def task_on_hover(widget, opt, color, font_color, ev):
        if ev.x > 558 and ev.type == tk.EventType.Enter:
            return
        widget.configure(bg=color, fg=font_color)
        opt.configure(bg=color, highlightbackground=color)

    def _calculate_scheduled_date(self, strict_opt, custom_opt):
        date = None
        current_date = datetime.date.today()
        if custom_opt:
            date = custom_opt.replace("/", "-")
        else:
            if strict_opt == 0:
                date = current_date.strftime('%Y-%m-%d')
            elif strict_opt == 1:
                date = (current_date + datetime.timedelta(days=1)).strftime('%Y-%m-%d')
            elif strict_opt == 2:
                date = (current_date + datetime.timedelta(7-current_date.weekday())).strftime('%Y-%m-%d')

        return date

    def on_edit_save(self):
        data = self._dialog_box.get_normalized_values()
        self._dialog_box.window_close()
        rowid = data.pop("task_id")
        scheduled_date = self._calculate_scheduled_date(data["button_option"], data["custom_date"])
        priority = data.pop("priority")
        data = dict(note=data.pop("note"),
                    scheduled_date=scheduled_date,
                    todo_date=scheduled_date,
                    priority=priority
                    )
        update_row(cursor=self.cursor, connection=self.connection, data=data, rowid=rowid)
        self.respawn_slaves()

    def on_edit_delete(self):
        data = self._dialog_box.get_normalized_values()
        self._dialog_box.window_close()
        rowid = data.pop("task_id")
        self.cursor.execute("DELETE FROM todo WHERE id=?", (rowid, ))
        self.connection.commit()
        self.all_tasks.pop(rowid).grid_remove()
        self.tasks = [task for task in self.tasks if task["id"] != rowid]

        # set default background if no tasks
        if not self.all_tasks:
            self.fill_tasks_frame()

    def respawn_slaves(self):
        for slave in self.tasks_frame.grid_slaves():
            slave.destroy()
        self.tasks_frame.grid_remove()
        self.vscroll.grid_remove()
        self.fetch_todos()
        self.fill_tasks_frame()

    def list_all_tasks(self):
        for i, task in enumerate(self.tasks):
            self.render_task(task, i, self.tasks_frame)

    def fill_tasks_frame(self):
        if self.tasks:
            self.scroll_canvas.grid(row=1, column=1, sticky=tk.NS)
            self.vscroll.grid(row=1, column=2, sticky='ns')
            self.tasks_frame.bind("<Configure>", self.update_scrollregion)
            self.tasks_frame.columnconfigure(1, weight=1)
            self.list_all_tasks()
        else:
            self.no_tasks_frame.grid(row=1, column=1, sticky=tk.NSEW)
            self.no_tasks_frame.columnconfigure(1, weight=1)
            self.set_default_background()

    def fetch_todos(self):
        pass

    def update_scrollregion(self, ev):
        self.scroll_canvas.configure(scrollregion=self.scroll_canvas.bbox("all"))

    def on_task_done(self, task, event):
        update_row(cursor=self.cursor, connection=self.connection, data={"is_done": 1}, rowid=task.task_id)
        task.grid_remove()


