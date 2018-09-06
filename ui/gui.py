import tkinter as tk


class Gui:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("ADL3 Action Language with Durations")
        self.root.geometry("650x650")

        main_frame = tk.Frame(self.root)
        engine_frame = tk.Frame(main_frame)

        scenario_frame = tk.Frame(engine_frame)
        scenario_label = tk.Label(scenario_frame, text="Input Scenario").pack()
        self.scenario_text_box = tk.Text(scenario_frame, height="5").pack()
        scenario_frame.pack()

        domain_frame = tk.Frame(engine_frame)
        domain_label = tk.Label(domain_frame, text="Input Domain Description").pack()
        self.domain_text_box = tk.Text(domain_frame, height="5").pack()
        domain_frame.pack()

        engine_init_button = tk.Button(engine_frame, text="Initialise the Engine").pack()

        query_frame = tk.Frame(main_frame)
        query_label = tk.Label(query_frame, text="Input Query").pack()
        self.query_text_box = tk.Text(query_frame, height="5").pack()
        query_test_button = tk.Button(query_frame, text="Test the Query").pack()

        output_label = tk.Label(query_frame, text="Output").pack()
        self.output_textbox = tk.Text(query_frame, height="10")
        self.output_textbox.pack()

        engine_frame.pack()
        main_frame.pack()
        query_frame.pack()

        self.root.mainloop()

    def print(self, text: str):
        self.output_textbox.insert(tk.END, text)


gui = Gui()


