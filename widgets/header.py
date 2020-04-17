import tkinter as tk


class Header(tk.Frame):
    def __init__(self, root, *args, **kwargs):
        super().__init__(root, bg="#585858", height=50, pady=10)
        self.activate_today_frame = kwargs.pop('today_action')
        self.activate_schedule_frame = kwargs.pop('schedule_action')
        self.grid(row=0, column=0, sticky=tk.W + tk.E, ipadx=10)
        self.columnconfigure(0, weight=1, uniform="fred")
        self.columnconfigure(1, weight=1, uniform="fred")
        self.button_today, self.button_scheduled = self.build_control_buttons()
        self.button_today.grid(row=0, column=0, sticky=tk.E)
        self.button_scheduled.grid(row=0, column=1, sticky=tk.W)
        print(self.grid_size())

    def build_control_buttons(self):
        today = tk.Button(self, text='Today', bg="#585858", fg="white", activebackground="#424141",
                          bd=0, highlightbackground="#2a2b2d", relief=tk.GROOVE, width=8,
                          command=self.activate_today_frame, activeforeground="white")
        scheduled = tk.Button(self, text='Scheduled', bg="#585858", fg="white", activebackground="#424141",
                              bd=0, highlightbackground="#2a2b2d", relief=tk.RAISED, width=8,
                              command=self.activate_schedule_frame, activeforeground="white")

        return today, scheduled


