import tkinter as tk
from PIL import ImageTk, Image
from db.sqlite import insert_into_table, update_row
from widgets.dialog import DialogBox
import datetime
import os
from tkinter.tix import ScrolledGrid


class BaseFrame(tk.Frame):
    def __init__(self, root, connection, *args, **kwargs):
        super().__init__(root, bg="#ffffff")
        self.tasks = None
        self.connection = connection
        self.cursor = self.connection.cursor()
        self.all_tasks = {}
        self.img = self._parse_background_image()
        self.tasks_frame = tk.Frame(self, bg="#ffffff")
        self.no_tasks_frame = tk.Frame(self, bg="#ffffff")
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
        self.entry = tk.Text(self, bd=0.5, width=74, height=1, spacing1=7, spacing3=7, fg="#585858")
        self.entry.insert('1.0', 'Task Title')
        self.entry.grid(row=0, column=1, pady=(30, 30))
        self.entry.bind("<Button-1>", self.on_entry_clicked)

    def on_entry_clicked(self, event):
        self.entry.config(highlightcolor="#585858")
        if self.entry.get('1.0', '10.0') == 'Task Title\n':
            self.entry.delete("1.0", "10.0")

    def set_default_background(self):
        panel = tk.Label(self.no_tasks_frame, image=self.img, bd=0)
        no_tasks = tk.Label(self.no_tasks_frame, text='No Tasks Found', bg="#ffffff", bd=0, fg="#585858")
        add_tasks = tk.Label(self.no_tasks_frame, text='You can add tasks using the + above', bg="#ffffff", bd=0, fg="#585858")
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
            self.tasks_frame.grid(row=1, column=1, sticky=tk.NSEW)
            self.tasks_frame.columnconfigure(1, weight=1)
        self.render_task(task, len(self.all_tasks), self.tasks_frame)

    def handle_edit_action(self, task_id):
        DialogBox.root = self.root
        self._dialog_box = DialogBox(save=self.on_edit_save, delete=self.on_edit_delete, task_id=task_id)

    def render_task(self, task, index, target_frame):
        # check_is_done = tk.Button(self, text='✎', bg="#ffffff",
        #                           bd=0, relief="raised", command=lambda: self.handle_edit_action(task["id"]))
        # check_is_done.grid(row=index + 1, column=0, sticky=tk.W)
        task_fields = tk.Text(target_frame, bd=2, width=80, height=1, spacing1=7, spacing3=7, fg="#585858")
        task_fields.task_id = task['id']
        task_fields.insert('1.0', task['task'])
        task_fields.config(state=tk.DISABLED)
        task_fields.grid(row=index + 1, column=1, pady=(10, 10))
        extra_options = tk.Button(task_fields, text='✎', bg="#ffffff",
                                  bd=0, relief="raised", command=lambda: self.handle_edit_action(task["id"]))
        extra_options.config(highlightbackground="#ffffff", cursor='hand1')
        extra_options.pack(padx=(553, 0))
        self.all_tasks.update({task['id']: task_fields})

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
        self.all_tasks[rowid].grid_remove()

    def respawn_slaves(self):
        for slave in self.tasks_frame.grid_slaves():
            slave.destroy()
        self.tasks_frame.grid_remove()
        self.fetch_todos()
        self.fill_tasks_frame()

    def list_all_tasks(self):
        for i, task in enumerate(self.tasks):
            self.render_task(task, i, self.tasks_frame)

    def fill_tasks_frame(self):
        if self.tasks:
            self.tasks_frame.grid(row=1, column=1, sticky=tk.NSEW)
            self.tasks_frame.columnconfigure(1, weight=1)
            self.list_all_tasks()
        else:
            self.no_tasks_frame.grid(row=1, column=1, sticky=tk.NSEW)
            self.no_tasks_frame.columnconfigure(1, weight=1)
            self.set_default_background()

    def fetch_todos(self):
        pass

