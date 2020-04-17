import tkinter as tki


class DialogBox(tki.Frame):

    root = None

    def __init__(self, **kwargs):
        """
        msg = <str> the message to be displayed
        dict_key = <sequence> (dictionary, key) to associate with user input
        (providing a sequence for dict_key creates an entry for user input)
        """
        top = self.open_top_window()
        super().__init__(top, bg="#ffffff", borderwidth=1, relief="raised",
                         width=450, height=270)
        self.grid(row=1, column=0, sticky=tki.NS, padx=4, ipady=10)
        self.columnconfigure(0, weight=1, uniform="fred")
        self.columnconfigure(1, weight=1, uniform="fred")
        self.date_button_selected = None
        self.task_id = kwargs.pop("task_id")
        self.on_edit_save = kwargs.pop("save")
        self.on_edit_delete = kwargs.pop("delete")

        # note widget frame
        self.render_notes_widget()

        # Label for the right option widget
        due_date_label = tki.Label(self, text="Due Date", bg="#ffffff", fg="#a0a0a0")
        due_date_label.grid(row=0, column=1, sticky=tki.W, ipadx=9, pady=(10,0))

        # right frame widget containing options for choosing dates and Save/Delete buttons
        self.render_option_select_frame()

    def _render_custom_date_input_field(self, right_dialog_frame):
        custom_date_label = tki.Label(right_dialog_frame, text="Date", bg="#ffffff", fg="#a0a0a0")
        custom_date_label.grid(row=1, column=0, sticky=tki.W, padx=(6,0), pady=(15,0))
        date_format_label = tki.Label(right_dialog_frame, text="day/month/year", bg="#ffffff", fg="#a0a0a0")
        date_format_label.grid(row=1, column=2, sticky=tki.W, pady=(15, 0))

        self.custom_date = tki.Text(right_dialog_frame, width=14, bd=0, height=1)
        self.custom_date.grid(row=2, column=0, columnspan=3, sticky=tki.EW, padx=(8,0))


    def _render_day_buttons(self, right_dialog_frame):
        self.end_of_week = tki.Button(right_dialog_frame, text='End of Week', bg="#f4f2f2", bd=0, activebackground="#dcd6d6",
                           relief=tki.RAISED, command=lambda: self.set_button_date_selected(2))
        self.today = tki.Button(right_dialog_frame, text='Today', bg="#f4f2f2", bd=0, activebackground="#dcd6d6",
                           relief=tki.RAISED, command=lambda: self.set_button_date_selected(0))
        self.tommorow = tki.Button(right_dialog_frame, text='Tommorow', bg="#f4f2f2", bd=0, activebackground="#dcd6d6",
                              relief=tki.RAISED, command=lambda: self.set_button_date_selected(1))
        self.today.grid(row=0, column=0, sticky=tki.EW, padx=(8, 0))
        self.tommorow.grid(row=0, column=1, sticky=tki.EW)
        self.end_of_week.grid(row=0, column=2, sticky=tki.EW)

    def _render_priority_selection(self, right_dialog_frame):
        priority_label = tki.Label(right_dialog_frame, text="Priority", bg="#ffffff", fg="#a0a0a0")
        priority_label.grid(row=3, column=0, sticky=tki.W, ipadx=9, pady=(15,0))

        self.current_select = tki.IntVar()
        high = tki.Radiobutton(right_dialog_frame, text="High", variable=self.current_select, value=1,
                               bg="#f4f2f2", borderwidth=0)
        middle = tki.Radiobutton(right_dialog_frame, text="Middle", variable=self.current_select, value=2,
                                 bg="#f4f2f2", borderwidth=0)
        low = tki.Radiobutton(right_dialog_frame, text="Low", variable=self.current_select, value=3,
                              bg="#f4f2f2", borderwidth=0)

        high.grid(row=4, column=0, sticky=tki.W, padx=8, pady=(5,0))
        middle.grid(row=4, column=1, sticky=tki.W, pady=(5,0), padx=(10,0))
        low.grid(row=4, column=2, sticky=tki.W, pady=(5,0))

    def render_option_select_frame(self):
        right_dialog_frame = tki.Frame(self, borderwidth=4, bg="#ffffff")
        right_dialog_frame.grid(row=1, column=1, sticky=tki.NSEW)

        # set buttons for choosing due date
        self._render_day_buttons(right_dialog_frame)

        # set custom input field for entering due date
        self._render_custom_date_input_field(right_dialog_frame)

        # set checkboxes for selecting task priority
        self._render_priority_selection(right_dialog_frame)

        # buttons to save or delete the task
        save_btn = tki.Button(right_dialog_frame, text='Save', bg="#99ff99", bd=0, activebackground="#99ff99",
                              relief=tki.RAISED, command=self.on_edit_save)
        delete_btn = tki.Button(right_dialog_frame, text='Delete', bg="#ff8080", bd=0, fg="white",
                                activebackground="#ff8080", relief=tki.RAISED, command=self.on_edit_delete)
        save_btn.grid(row=5, column=0, sticky=tki.S, pady=(82, 0))
        delete_btn.grid(row=5, column=2, sticky=tki.S + tki.E, pady=(82, 0))

    def render_notes_widget(self):
        notes_label = tki.Label(self, text="Notes", bg="#ffffff", fg="#a0a0a0")
        notes_label.grid(row=0, column=0, sticky=tki.W, padx=(5, 0), pady=(10, 0))
        self.note = tki.Text(self, bd=2, height=15)
        self.note.grid(row=1, column=0, padx=(5, 0))

    def open_top_window(self):
        top = tki.Toplevel(DialogBox.root)
        position_x = int(top.winfo_screenwidth() / 2 - 250)
        position_y = int(top.winfo_screenheight() / 2 - 150)
        top.geometry("620x380+{}+{}".format(position_x, position_y))
        top.columnconfigure(0, weight=1)

        # set color on Frame border
        self.set_top_border_color(top)

        return top

    @staticmethod
    def set_top_border_color(window):
        border_frame = tki.Frame(window, borderwidth=0, width=611, height=7, bg="#ea6a44", relief="raised")
        border_frame.grid(row=0, column=0, padx=4, sticky=tki.NS, pady=(5, 0))

    def set_button_date_selected(self, option):
        self.today.config(bg="#f4f2f2", relief="raised")
        self.tommorow.config(bg="#f4f2f2", relief="raised")
        self.end_of_week.config(bg="#f4f2f2", relief="raised")
        if self.date_button_selected == option:
            option = None
            self.date_button_selected = None
        else:
            self.date_button_selected = option

        if option == 0:
            self.today.config(bg="#dcd6d6", relief="sunken")
        elif option == 1:
            self.tommorow.config(bg="#dcd6d6", relief="sunken")
        elif option == 2:
            self.end_of_week.config(bg="#dcd6d6", relief="sunken")

    def get_normalized_values(self):
        data = dict(
            note=self.note.get('0.0', tki.END).strip("\n"),
            button_option=self.date_button_selected,
            custom_date=self.custom_date.get('0.0', tki.END).strip("\n"),
            priority=self.current_select.get(),
            task_id=self.task_id
        )

        return data

    def window_close(self):
        self.master.destroy()
