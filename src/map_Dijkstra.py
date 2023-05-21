import os
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen
from kivy.uix.button import Button
from kivy.graphics import Color
from kivy.lang import Builder
from kivy.uix.filechooser import FileChooserListView
from webview import WebView
#webview from https://github.com/Android-for-Python/Webview-Example/blob/main/webview.py

Builder.load_string("""
<Dijkstra_Screen>:
    BoxLayout:
        orientation: 'vertical'

        FileChooserListView:
            id: file_chooser
            canvas.before:
                Color:
                    rgb: 0, 0, 0
                Rectangle:
                    pos: self.pos
                    size: self.size
""")

class Dijkstra_Screen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical')
        self.file_chooser = FileChooserListView(path="/storage/emulated/0/Download")
        self.file_chooser.filters = [lambda folder, filename: filename.endswith('.html')]
        #self.file_chooser.background_color = (0, 0, 0, 1)
        self.layout.add_widget(self.file_chooser)
        b2 = Button(text='Click to Redirect to Map')
        b2.bind(on_press=self.view_local_file)
        self.layout.add_widget(b2)
        self.add_widget(self.layout)
        self.browser = None

    def view_local_file(self, instance):
        selected_file = self.file_chooser.selection and self.file_chooser.selection[0]
        if selected_file:
            self.browser = WebView(selected_file, enable_javascript=True, enable_zoom=True)

class BrowserApp(App):
    def build(self):
        screen = Dijkstra_Screen()
        return screen

if __name__ == '__main__':
    BrowserApp().run()