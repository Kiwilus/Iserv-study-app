from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder


# -------- Screens -------- #

class LoginScreen(Screen):
    def login(self):
        self.manager.current = "loading"



class LoadingScreen(Screen):
    def go_main(self):
        self.manager.current = "main"


class MainScreen(Screen):
    pass


# -------- App -------- #

class StudyLearnApp(App):
    def build(self):
        return Builder.load_file("studylearn.kv")


if __name__ == "__main__":
    StudyLearnApp().run()

'''
class BoxLayoutExample(BoxLayout):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)        # Hauptlayout
        self.orientation = "vertical"

        # Label
        label = Label(
            text="IServ App",
            size_hint=(0.5, None),
            height=60,
            pos_hint={"center_x": 0.5}
        )
        self.add_widget(label)

        # Inneres BoxLayout
        inner_layout = BoxLayout(
            orientation="vertical",
            spacing=15,
        )

        # Buttons
        btn_url = Button(
            text="URL",
            size_hint=(0.5, None),
            height=80,
            pos_hint={"center_x": 0.5}
        )

        btn_name = Button(
            text="name",
            size_hint=(0.5, None),
            height=80,
            pos_hint={"center_x": 0.5}
        )

        btn_password = Button(
            text="password",
            size_hint=(0.5, None),
            height=80,
            pos_hint={"center_x": 0.5}
        )

        inner_layout.add_widget(btn_url)
        inner_layout.add_widget(btn_name)
        inner_layout.add_widget(btn_password)

        self.add_widget(Widget())
        self.add_widget(inner_layout)
        self.add_widget(Widget())

'''
