from tkinter.filedialog import askopenfilename
from src.counter import MessengerCounter
import plotly.offline as pyo
import plotly.express as px
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
        px.defaults.template = 'plotly_dark'

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

    def count(self):
        self.counter.count('messages', self.update_progress)

    def set_source(self):
        try:
            self.counter = MessengerCounter(self.file, gui=True)
            return True
        except FileNotFoundError:
            return False

    def get_plot(self):
        fig = self.counter.daily_conversation('conversation_id')
        return generate_plot(fig)


def generate_plot(fig):
    plot_html = pyo.plot(fig, output_type='div', include_plotlyjs=False, # TODO add script to html
                         config={'displayModeBar': False, 'scrollZoom': True})
    div = re.search(r'<div id.*?</div>', plot_html).group()
    script = re.search(r'<script type="text/javascript">(.+)</script>', plot_html).group(1)
    return div, script

if __name__ == '__main__':
    gui = GUI()
    gui.window = webview.create_window("Messenger Counter",  'gui/index.html', js_api=gui,
                                       width=1280, height=720, min_size=(800, 600), background_color='#111111')
    webview.start(debug=False)
