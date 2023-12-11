from tkinter.filedialog import askopenfilename
from src.counter import MessengerCounter
from src.stats import statistics
import plotly.offline as pyo
import tkinter as tk
import webview
import re


class GUI:
    def __init__(self):
        self.counter = None
        self.file = ''
        self.data = {
            'messages': {},
            'chars': {},
            'words': {}
        }
        self.window = None

    def choose_file(self):
        root = tk.Tk()
        root.attributes('-topmost', True)
        root.iconify()
        self.file = askopenfilename(title='Messenger Counter',
                                    parent=root,
                                    filetypes=[('Zip files', '*.zip')])
        # folder = askdirectory(title='...', parent=root)
        root.destroy()
        return self.file.split('/')[-1]

    def update_progress(self, value):
        self.window.evaluate_js(f"""document.getElementById('p').value = {value};
        document.querySelector('[for=p]').value = Math.round({value});""")

    def count(self, data_type='messages'):
        self.data[data_type] = self.counter.count(data_type, self.update_progress)

    def set_source(self):
        try:
            self.counter = MessengerCounter(self.file, gui=True)
            return True
        except FileNotFoundError:
            return False

    def get_plot(self, nav):
        if nav == 'stats':
            data, fig = statistics(self.data['messages'], data_type='messages')
        elif nav == 'chars':
            data, fig = statistics(self.data['chars'], data_type='chars')
        elif nav == 'words':
            data, fig = statistics(self.data['words'], data_type='words')
        else:
            data, fig = statistics(self.data['messages'], data_type='messages')
        return data.to_json(), generate_plot(fig)


def generate_plot(fig):
    plot_html = pyo.plot(fig, output_type='div', include_plotlyjs=False,
                         config={'displayModeBar': False, 'scrollZoom': True})
    div = re.search(r'<div id.*?</div>', plot_html).group()
    script = re.search(r'<script type="text/javascript">(.+)</script>', plot_html).group(1)
    return div, script

if __name__ == '__main__':
    gui = GUI()
    gui.window = webview.create_window("Messenger Counter",  'gui/index.html', js_api=gui,
                                       width=1280, height=720, min_size=(800, 600), background_color='#111111')
    webview.start(debug=False)
