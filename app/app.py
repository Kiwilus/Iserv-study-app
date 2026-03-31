from kivy.app import App
from kivy.metrics import dp
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from numpy.ma.core import size


class BoxLayoutExample(BoxLayout):
    pass

    '''
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"

        b1 = Button(text="A")
        b2 = Button(text="B")
        b3 = Button(text="B")

        self.add_widget(b1)
        self.add_widget(b2)
        self.add_widget(b3)
    '''

class MainWidget(Widget):
    pass

class StudyLearnApp(App):
    pass

StudyLearnApp().run()