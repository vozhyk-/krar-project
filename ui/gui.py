import tkinter as tk
import sys
import parsing.scenario, parsing.domain_description, parsing.query
from engine.engine import Engine


class Gui(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.pack()
        self.create_widgets()

    def create_widgets(self):
        self.master.title("ADL3 Action Language with Durations")
        self.master.geometry("800x800")

        self.scenario_label = tk.Label(self, text="Input Scenario").pack()
        self.scenario_text_box = tk.Text(self, height="10", width="780")
        self.scenario_text_box.pack()

        self.domain_label = tk.Label(self, text="Input Domain Description").pack()
        self.domain_text_box = tk.Text(self, height="5", width="780")
        self.domain_text_box.pack()

        self.engine_init_button = tk.Button(self, text="Initialise the Engine", command=self.init_engine).pack()

        self.query_label = tk.Label(self, text="Input Query").pack()
        self.query_text_box = tk.Text(self, height="10", width="780")
        self.query_text_box.pack()
        self.query_test_button = tk.Button(self, text="Test the Query", command=self.test_query).pack()

        self.output_label = tk.Label(self, text="Output").pack()
        self.output_textbox = tk.Text(self, height="15", state="disabled", width="780")

        sys.stdout = StdRedirector(self.output_textbox)
        sys.stderr = StdRedirector(self.output_textbox)

        self.output_textbox.pack()

    def retrieve_content(self, text_widget: tk.Text):
        content = text_widget.get("1.0", tk.END)
        return str(content)

    def init_engine(self):
        print("Engine Initialising")
        self.scenario_content = self.retrieve_content(self.scenario_text_box)
        self.domain_content = self.retrieve_content(self.domain_text_box)
        self.scenario = parsing.scenario.parse_text(self.scenario_content)
        self.domain_description = parsing.domain_description.parse_text(self.domain_content)
        if (self.scenario is not None) and (self.domain_description is not None):
            print("Scenario and Domain Description parsed successfully")
            self.engine = Engine()
            if self.engine.run(scenario=self.scenario, domain_desc=self.domain_description):
                print("Models found: ", len(self.engine.models))
                i = 0
                for model in self.engine.models:
                    print('Final model:', i, '\n', model)
                    print('Action history for model', i, 'is:', model.action_history)
                    i += 1

    def test_query(self):
        print("Testing Query")
        self.query_content = self.retrieve_content(self.query_text_box)
        self.queries = parsing.query.parse_text(self.query_content)

        for query in self.queries:
            print('Query:', query, 'was evaluated to:', query.validate(self.engine.models, self.scenario))


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
