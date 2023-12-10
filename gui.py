from src.counter import MessengerCounter
from tkinter.filedialog import askopenfilename
import tkinter as tk
import plotly.offline as pyo
import plotly.express as px
import eel
import re


def generate_plot(fig):
    plot_html = pyo.plot(fig, output_type='div', include_plotlyjs=False,
                         config={'displayModeBar': False, 'scrollZoom': True})
    div = re.search(r'<div id.*?</div>', plot_html).group()
    script = re.search(r'<script type="text/javascript">(.+)</script>', plot_html).group(1)
    return div, script

class GUI:
    def __init__(self):
        self.counter = None
        self.file = ''
        self.data = {
            'messages': {},
            'chars': {},
            'words': {}
        }
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

    def set_source(self):
        try:
            self.counter = MessengerCounter(self.file, gui=True)
            return True
        except FileNotFoundError:
            return False

    def count(self, what='messages'):
        self[what] = self.counter.count(what)

    def get_plot(self):
        fig = self.counter.daily_conversation()
        return generate_plot(fig)

    def __getitem__(self, item):
        return self.data[item]

    def __setitem__(self, item, value):
        self.data[item] = value

eel.init('gui')
gui = GUI()

@eel.expose
def choose_file():
    return gui.choose_file()

@eel.expose
def set_source():
    return gui.set_source()

@eel.expose
def count(what):
    gui.count(what)

@eel.expose
def get_plot():
    return gui.get_plot()

eel.start('main.html', size=(1280, 720))
