from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.properties import (
    StringProperty, NumericProperty,
    ListProperty, ColorProperty
)
from bs4 import BeautifulSoup
import threading
from datetime import datetime, timezone


# Dynamic list widgets #
class TaskList(BoxLayout):
    """Dynamic list of task cards."""
    tasks        = ListProperty([])
    accent_color = ColorProperty([0.18, 0.48, 0.9, 1])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.spacing = dp(10)
        self.size_hint_y = None
        self.height = dp(0)
        self.bind(tasks=self._rebuild)

    def _rebuild(self, *_):
        self.clear_widgets()
        if not self.tasks:
            placeholder = Label(
                text="No tasks found.",
                font_size="14sp",
                color=(0.55, 0.6, 0.7, 1),
                size_hint_y=None,
                height=dp(36),
                halign="left",
            )
            placeholder.bind(width=lambda inst, w: setattr(inst, "text_size", (w, None)))
            self.add_widget(placeholder)
            self.height = dp(36)
            return

        total_h = 0
        for task in self.tasks:
            title = task.get("title", "no title")
            if len(title) > 80:
                title = title[:77] + "…"
            date_text = task.get("date_fmt", task.get("date", ""))
            msg_text  = task.get("message", "")[:100]

            row = Builder.load_string(f"""
TaskRow:
    title_text: {repr(title)}
    date_text:  {repr(date_text)}
    msg_text:   {repr(msg_text)}
    accent:     {list(self.accent_color)}
""")
            self.add_widget(row)
            total_h += dp(94) + dp(10)

        # subtract last spacing
        self.height = max(total_h - dp(10), dp(0))


class NotifList(BoxLayout):
    """Dynamic list of other notifications."""
    notifs = ListProperty([])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.spacing = dp(8)
        self.size_hint_y = None
        self.height = dp(0)
        self.bind(notifs=self._rebuild)

    def _rebuild(self, *_):
        self.clear_widgets()
        if not self.notifs:
            placeholder = Label(
                text="No more notifications.",
                font_size="14sp",
                color=(0.55, 0.6, 0.7, 1),
                size_hint_y=None,
                height=dp(36),
                halign="left",
            )
            placeholder.bind(width=lambda inst, w: setattr(inst, "text_size", (w, None)))
            self.add_widget(placeholder)
            self.height = dp(36)
            return

        total_h = 0
        for n in self.notifs:
            ntype = n.get("type", "?")
            title = n.get("title", "")
            msg   = n.get("message", "")
            text  = f"[{ntype}]  {title}"
            if msg:
                text += f"  —  {msg}"

            row = Builder.load_string(f"""
NotifRow:
    notif_text: {repr(text)}
""")
            self.add_widget(row)
            total_h += dp(52) + dp(8)

        self.height = max(total_h - dp(8), dp(0))




class EmailList(BoxLayout):
    """Dynamic list of recent emails."""
    emails = ListProperty([])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.spacing = dp(6)
        self.size_hint_y = None
        self.height = dp(0)
        self.bind(emails=self._rebuild)

    def _rebuild(self, *_):
        self.clear_widgets()
        if not self.emails:
            placeholder = Label(
                text="No E-Mails loaded.",
                font_size="14sp",
                color=(0.55, 0.6, 0.7, 1),
                size_hint_y=None,
                height=dp(36),
                halign="left",
            )
            placeholder.bind(width=lambda inst, w: setattr(inst, "text_size", (w, None)))
            self.add_widget(placeholder)
            self.height = dp(36)
            return

        total_h = 0
        for mail in self.emails:
            subject  = mail.get("title", "(No subject)")
            date     = mail.get("date", "")
            seen     = mail.get("seen", True)
            attach   = mail.get("attach", False)
            flagged  = mail.get("flagged", False)
            icons = ""
            if not seen:   icons += "● "
            if flagged:    icons += "★ "
            if attach:     icons += "📎 "
            row = Builder.load_string(f"""
EmailRow:
    subject_text: {repr(icons + subject)}
    date_text:    {repr(date)}
    is_unread:    {not seen}
""")
            self.add_widget(row)
            total_h += dp(52) + dp(6)
        self.height = max(total_h - dp(6), dp(0))


# IServAPI import
try:
    from IServAPI import IServAPI
except ImportError:
    IServAPI = None

# Screens
class LoginScreen(Screen):
    error_text = StringProperty("")

    def login(self):
        url      = self.ids.url_input.text.strip()
        username = self.ids.username_input.text.strip()
        password = self.ids.password_input.text.strip()

        if not url or not username or not password:
            self.error_text = "Please fill in all fields."
            return

        if IServAPI is None:
            self.error_text = "IServAPI not installed."
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
                iserv_url=app.iserv_url,
            )
            Clock.schedule_once(lambda dt: self._on_success(), 0)
        except Exception as e:
            Clock.schedule_once(lambda dt, err=str(e): self._on_error(err), 0)

    def _on_success(self):
        self.manager.current = "main"
        App.get_running_app().root.get_screen("main").load_data()

    def _on_error(self, err):
        self.manager.current = "login"
        self.error_text = f"Error: {err}"


class LoadingScreen(Screen):
    status_text = StringProperty("connecting to IServ…")


class MainScreen(Screen):
    username_label = StringProperty("")
    unread_count   = NumericProperty(0)
    total_emails   = NumericProperty(0)
    email_list     = ListProperty([])
    active_tasks   = ListProperty([])
    overdue_tasks  = ListProperty([])
    other_notifs   = ListProperty([])
    status_text    = StringProperty("")
    is_loading     = StringProperty("loading data…")

    def load_data(self):
        app = App.get_running_app()
        self.username_label = app.username
        self.is_loading = "loading data…"
        threading.Thread(target=self._fetch, daemon=True).start()

    def _fetch(self):
        app = App.get_running_app()
        api = app.api
        try:
            # E-Mails: {unseen, recordsTotal, data:[{uid,subject,date,seen,attachment,...}]}
            emails    = api.get_emails()
            unread    = emails.get("unseen", 0) if isinstance(emails, dict) else 0
            total     = emails.get("recordsTotal", 0) if isinstance(emails, dict) else 0
            raw_mails = emails.get("data", []) if isinstance(emails, dict) else []
            email_items = []
            for m in raw_mails[:20]:
                email_items.append({
                    "title":   m.get("subject", "(no subject)"),
                    "date":    m.get("date", ""),
                    "seen":    m.get("seen", True),
                    "attach":  m.get("attachment", False),
                    "flagged": m.get("flagged", False),
                })

            # Tasks via HTML scraping
            base_url = "https://" + app.iserv_url.replace("https://","").replace("http://","").rstrip("/")
            exercise_r = api._session.get(f"{base_url}/iserv/exercise")
            soup = BeautifulSoup(exercise_r.text, "html.parser")

            now = datetime.now(timezone.utc)
            active, overdue = [], []

            # Tasks are in table rows
            for row in soup.select("table tbody tr"):
                cols = row.find_all("td")
                if len(cols) < 2:
                    continue
                title_tag = row.select_one("a")
                title     = title_tag.get_text(strip=True) if title_tag else cols[0].get_text(strip=True)

                # Find a Due Date
                date_text = ""
                date_fmt  = ""
                is_past   = False
                for col in cols:
                    txt = col.get_text(strip=True)
                    # IServ Datum-Format: "12.04.2026 23:59" oder ISO
                    import re
                    m = re.search(r"(\d{2}\.\d{2}\.\d{4} \d{2}:\d{2})", txt)
                    if m:
                        date_text = m.group(1).strip()
                        try:
                            dt        = datetime.strptime(date_text, "%d.%m.%Y %H:%M")
                            now_local = datetime.now()
                            date_fmt  = dt.strftime("%d.%m.%Y %H:%M")
                            is_past   = dt < now_local
                        except Exception:
                            date_fmt = date_text

                # Status column (submitted/open)
                status = ""
                status_tag = row.select_one(".badge, .label, td:last-child")
                if status_tag:
                    status = status_tag.get_text(strip=True)

                entry = {
                    "title":    title,
                    "date":     date_text,
                    "date_fmt": date_fmt,
                    "message":  status,
                    "type":     "exercise",
                }
                if is_past:
                    overdue.append(entry)
                else:
                    active.append(entry)

            # other notifications
            notifs_raw = api.get_notifications()
            all_notifs = (
                notifs_raw.get("data", {}).get("notifications", [])
                if isinstance(notifs_raw, dict) else []
            )
            others = []
            for n in all_notifs:
                raw_date = n.get("date", "")
                try:
                    dt       = datetime.fromisoformat(raw_date)
                    date_fmt = dt.strftime("%d.%m.%Y %H:%M")
                except Exception:
                    date_fmt = raw_date
                others.append(dict(n, date_fmt=date_fmt))

            Clock.schedule_once(
                lambda dt: self._apply(unread, total, email_items, active, overdue, others), 0
            )

        except Exception as e:
            Clock.schedule_once(lambda dt, err=str(e): self._apply_error(err), 0)

    def _apply(self, unread, total, email_items, active, overdue, others):
        self.unread_count  = unread
        self.total_emails  = total
        self.email_list    = email_items
        self.active_tasks  = active
        self.overdue_tasks = overdue
        self.other_notifs  = others
        self.is_loading    = ""
        self.status_text   = f"Last Updated: {datetime.now().strftime('%H:%M:%S')}"

    def _apply_error(self, err):
        self.is_loading  = ""
        self.status_text = f"Loading error: {err}"

    def refresh(self):
        self.is_loading = "Update…"
        threading.Thread(target=self._fetch, daemon=True).start()

    def logout(self):
        app = App.get_running_app()
        app.api      = None
        app.username = ""
        app.password = ""
        self.manager.current = "login"

# App
class IServDashboardApp(App):
    api       = None
    username  = ""
    password  = ""
    iserv_url = ""

    def build(self):
        self.title = "IServ Dashboard"
        import os
        kv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "studylearn.kv")
        Builder.load_file(kv_path)
        sm = ScreenManager(transition=FadeTransition())
        sm.add_widget(LoginScreen(name="login"))
        sm.add_widget(LoadingScreen(name="loading"))
        sm.add_widget(MainScreen(name="main"))
        return sm


if __name__ == "__main__":
    IServDashboardApp().run()
