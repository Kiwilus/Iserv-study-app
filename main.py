from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import StringProperty, ListProperty

class LoginScreen(Screen):
    error_text = StringProperty("")

    def login(self):
        # Implement your login logic here
        pass

    def _connect(self):
        # Implement your connection logic here
        pass

    def _on_success(self):
        # Handle successful login
        pass

    def _on_error(self, err):
        # Handle login error
        self.error_text = str(err)

class LoadingScreen(Screen):
    def go_main(self):
        # Navigate to the main screen after loading
        pass

class MainScreen(Screen):
    username_label = StringProperty("")
    tasks = ListProperty([])
    notifs = ListProperty([])

    def load_data(self):
        # Load data from API or other source
        pass

    def _fetch(self):
        # Fetch data logic here
        pass

    def _apply(self, unread, active, overdue, others):
        # Apply fetched data to the UI
        self.tasks = unread + active + overdue + others

    def _apply_error(self, err):
        # Handle error during data application
        print(f"Error applying data: {err}")

    def refresh(self):
        # Refresh data logic here
        pass

    def logout(self):
        # Logout logic here
        pass

class StudyLearnApp(App):
    api = None

    def build(self):
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(LoadingScreen(name='loading'))
        sm.add_widget(MainScreen(name='main'))
        return sm

if __name__ == '__main__':
    StudyLearnApp().run()
