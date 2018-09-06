import tkinter as tk
import sys


class Gui(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.pack()
        self.create_widgets()

    def create_widgets(self):
        self.master.title("ADL3 Action Language with Durations")
        self.master.geometry("650x650")

        self.scenario_label = tk.Label(self, text="Input Scenario").pack()
        self.scenario_text_box = tk.Text(self, height="5")
        self.scenario_text_box.pack()

        self.domain_label = tk.Label(self, text="Input Domain Description").pack()
        self.domain_text_box = tk.Text(self, height="5")
        self.domain_text_box.pack()

        self.engine_init_button = tk.Button(self, text="Initialise the Engine", command=self.init_engine).pack()

        self.query_label = tk.Label(self, text="Input Query").pack()
        self.query_text_box = tk.Text(self, height="5")
        self.query_text_box.pack()
        self.query_test_button = tk.Button(self, text="Test the Query", command=self.test_query).pack()

        self.output_label = tk.Label(self, text="Output").pack()
        self.output_textbox = tk.Text(self, height="10", state="disabled")

        sys.stdout = StdRedirector(self.output_textbox)
        sys.stderr = StdRedirector(self.output_textbox)

        self.output_textbox.pack()

    def retrieve_content(self, text_widget: tk.Text):
        content = text_widget.get("1.0", tk.END)
        return str(content)

    def init_engine(self):
        print("Engine Initialising")

    def test_query(self):
        print("Testing Query")


class StdRedirector(object):
    def __init__(self, text_widget):
        self.text_space = text_widget

    def write(self, string):
        self.text_space.config(state=tk.NORMAL)
        self.text_space.insert("end", string)
        self.text_space.see("end")
        self.text_space.config(state=tk.DISABLED)


root = tk.Tk()
gui = Gui(master=root)
gui.mainloop()
