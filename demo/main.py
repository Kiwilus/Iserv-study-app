from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.properties import StringProperty, NumericProperty, ListProperty, ColorProperty
import threading
from datetime import datetime, timezone


class TaskList(BoxLayout):
    """Dynamische Liste von Aufgaben-Karten."""
    tasks        = ListProperty([])
    accent_color = ColorProperty([0.18, 0.48, 0.9, 1])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.spacing = dp(8)
        self.size_hint_y = None
        self.bind(minimum_height=self.setter("height"))
        self.bind(tasks=self._rebuild)

    def _rebuild(self, *_):
        self.clear_widgets()
        for task in self.tasks:
            title = task.get("title", "Kein Titel")
            if len(title) > 60:
                title = title[:57] + "…"
            row = Builder.load_string(f"""
TaskRow:
    title_text: {repr(title)}
    date_text:  {repr(task.get("date_fmt", task.get("date", "")))}
    msg_text:   {repr(task.get("message", "")[:80])}
    accent:     {list(self.accent_color)}
""")
            self.add_widget(row)


class NotifList(BoxLayout):
    """Dynamische Liste sonstiger Benachrichtigungen."""
    notifs = ListProperty([])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.spacing = dp(6)
        self.size_hint_y = None
        self.bind(minimum_height=self.setter("height"))
        self.bind(notifs=self._rebuild)

    def _rebuild(self, *_):
        self.clear_widgets()
        for n in self.notifs:
            ntype = n.get("type", "?")
            title = n.get("title", "")
            msg   = n.get("message", "")
            lbl = Builder.load_string(f"""
Label:
    text: {repr(f"[{ntype}]  {title}  —  {msg}")}
    font_size: "13sp"
    color: 0.7, 0.72, 0.8, 1
    size_hint_y: None
    height: dp(22)
    halign: "left"
    text_size: self.width, None
""")
            self.add_widget(lbl)

# IServAPI import (muss installiert sein)
try:
    from IServAPI import IServAPI
except ImportError:
    IServAPI = None


# ─────────────────────────────────────────────
# Screens
# ─────────────────────────────────────────────

class LoginScreen(Screen):
    error_text = StringProperty("")

    def login(self):
        url      = self.ids.url_input.text.strip()
        username = self.ids.username_input.text.strip()
        password = self.ids.password_input.text.strip()

        if not url or not username or not password:
            self.error_text = "Bitte alle Felder ausfüllen."
            return

        if IServAPI is None:
            self.error_text = "IServAPI nicht installiert."
            return

        self.error_text = ""
        self.manager.current = "loading"

        app = App.get_running_app()
        app.iserv_url = url
        app.username  = username
        app.password  = password

        threading.Thread(target=self._connect, daemon=True).start()

    def _connect(self):
        app = App.get_running_app()
        try:
            app.api = IServAPI(
                username=app.username,
                password=app.password,
                iserv_url=app.iserv_url
            )
            Clock.schedule_once(lambda dt: self._on_success(), 0)
        except Exception as e:
            Clock.schedule_once(lambda dt, err=str(e): self._on_error(err), 0)

    def _on_success(self):
        self.manager.current = "main"
        App.get_running_app().root.get_screen("main").load_data()

    def _on_error(self, err):
        self.manager.current = "login"
        self.error_text = f"Fehler: {err}"


class LoadingScreen(Screen):
    status_text = StringProperty("Verbinde mit IServ…")


class MainScreen(Screen):
    username_label   = StringProperty("")
    unread_count     = NumericProperty(0)
    active_tasks     = ListProperty([])
    overdue_tasks    = ListProperty([])
    other_notifs     = ListProperty([])
    status_text      = StringProperty("")
    is_loading       = StringProperty("Daten werden geladen…")

    def load_data(self):
        app = App.get_running_app()
        self.username_label = app.username
        self.is_loading = "Daten werden geladen…"
        threading.Thread(target=self._fetch, daemon=True).start()

    def _fetch(self):
        app = App.get_running_app()
        api = app.api
        try:
            # Emails
            emails   = api.get_emails()
            unread   = emails.get("unseen", 0)

            # Notifications
            notifs_raw = api.get_notifications()
            all_notifs = notifs_raw.get("data", {}).get("notifications", [])

            now = datetime.now(timezone.utc)
            active, overdue, others = [], [], []

            for n in all_notifs:
                if n.get("type") == "exercise":
                    raw_date = n.get("date", "")
                    try:
                        dt = datetime.fromisoformat(raw_date)
                        formatted = dt.strftime("%d.%m.%Y %H:%M")
                        n = dict(n, date_fmt=formatted)
                        if dt < now:
                            overdue.append(n)
                        else:
                            active.append(n)
                    except Exception:
                        n = dict(n, date_fmt=raw_date)
                        active.append(n)
                else:
                    others.append(n)

            Clock.schedule_once(lambda dt: self._apply(unread, active, overdue, others), 0)

        except Exception as e:
            Clock.schedule_once(lambda dt, err=str(e): self._apply_error(err), 0)

    def _apply(self, unread, active, overdue, others):
        self.unread_count  = unread
        self.active_tasks  = active
        self.overdue_tasks = overdue
        self.other_notifs  = others
        self.is_loading    = ""
        self.status_text   = f"Zuletzt aktualisiert: {datetime.now().strftime('%H:%M:%S')}"

    def _apply_error(self, err):
        self.is_loading  = ""
        self.status_text = f"Fehler beim Laden: {err}"

    def refresh(self):
        self.is_loading = "Aktualisiere…"
        threading.Thread(target=self._fetch, daemon=True).start()

    def logout(self):
        app = App.get_running_app()
        app.api      = None
        app.username = ""
        app.password = ""
        self.manager.current = "login"


# ─────────────────────────────────────────────
# App
# ─────────────────────────────────────────────

class StudyLearnApp(App):
    api      = None
    username = ""
    password = ""
    iserv_url = ""

    def build(self):
        self.title = "IServ Dashboard"
        sm = ScreenManager(transition=FadeTransition())
        sm.add_widget(LoginScreen(name="login"))
        sm.add_widget(LoadingScreen(name="loading"))
        sm.add_widget(MainScreen(name="main"))
        return sm


if __name__ == "__main__":
    import os; Builder.load_file(os.path.join(os.path.dirname(os.path.abspath(__file__)), "studylearn.kv"))
    StudyLearnApp().run()