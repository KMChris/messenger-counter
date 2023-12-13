from tkinter.filedialog import askopenfilename
from src.stats import statistics, interval
from src.counter import MessengerCounter
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

    def get_plot(self, nav, conversation=None):
        if conversation=='':
            conversation = None
        if nav == 'stats':
            data, fig = statistics(self.data['messages'], conversation, data_type='messages')
        elif nav == 'words':
            data, fig = statistics(self.data['words'], data_type='words')
        elif nav == 'user':
            data, fig = statistics(self.data['messages'], data_type='messages')
        elif nav == 'daily':
            data, fig = interval('daily', self.counter, conversation)
        elif nav == 'hours':
            data, fig = interval('hours', self.counter, conversation)
        else:
            return None, None
        return data.to_json(), generate_plot(fig)

def generate_plot(fig):
    plot_html = pyo.plot(fig, output_type='div', include_plotlyjs=False,
                         config={'displayModeBar': False, 'scrollZoom': True})
    div = re.search(r'<div id.*?</div>', plot_html).group()
    script = re.search(r'<script type="text/javascript">(.+)</script>', plot_html).group(1)
    return div, script

if __name__ == '__main__':
    gui = GUI()
    gui.window = webview.create_window("Messenger Counter",  'gui/index.html',
                                       js_api=gui, background_color='#111111',
                                       width=1280, height=720, min_size=(800, 600))
    webview.start(debug=False)
