
############################
##      Study App         ##
############################

from IServAPI import IServAPI
from datetime import datetime, timezone
import time


ISERV_URL = input("URL: ")
USERNAME = input("Username: ")
PASSWORD = input("Password: ")

print("Verbinde mit IServ...")
api = IServAPI(username=USERNAME, password=PASSWORD, iserv_url=ISERV_URL)
print(f"Eingeloggt als: {USERNAME}\n")

# --- Zustand ---
known_task_ids = set()
known_email_count = None

def check_new_emails(api, known_email_count):

    emails = api.get_emails()
    unread = emails.get('unseen', 0)

    if known_email_count is None:
        print(f"Ungelesene E-Mails beim Start: {unread}")
        return unread, False

    if unread > known_email_count:
        diff = unread - known_email_count
        print(f"*** NEUE E-MAIL! ({diff} neue ungelesene Nachrichten) ***")
        return unread, True

    print(f"E-Mails: {unread} ungelesen (keine neuen)")
    return unread, False


def check_unread_emails(api):
    emails = api.get_emails()
    unread = emails.get('unseen', 0)
    
    print(f"Ungelesene E-Mails: {unread}")
    
    if unread > 0:
        for mail in emails.get('data', []):
            if not mail.get('seen'):
                print(f"    [{mail['date']}] {mail['subject']}")
    return unread



def check_other_notifications(api):
    notifications = api.get_notifications()
    all_notifs = notifications.get('data', {}).get('notifications', [])
    others = [n for n in all_notifs if n.get('type') != 'exercise']

    if others:
        print(f"Sonstige Benachrichtigungen: {len(others)}")
        for n in others:
            print(f"   * [{n.get('type')}] {n.get('title', '')} — {n.get('message', '')}")
    print()


def check_tasks(api):
    notifications = api.get_notifications()
    all_notifs = notifications.get('data', {}).get('notifications', [])
    tasks = [n for n in all_notifs if n.get('type') == 'exercise']

    now = datetime.now(timezone.utc)
    active_tasks = []
    overdue_tasks = []

    for task in tasks:
        raw_date = task.get('date', '')
        try:
            dt = datetime.fromisoformat(raw_date)
            if dt < now:
                overdue_tasks.append(task)
            else:
                active_tasks.append(task)
        except Exception:
            active_tasks.append(task)

    print(f"Aktive Aufgaben (noch zu erledigen): {len(active_tasks)}")
    if active_tasks:
        for task in active_tasks:
            _print_task(task)
    else:
        print("   Keine aktiven Aufgaben!\n")

    print(f"Überfällige Aufgaben (abgelaufen): {len(overdue_tasks)}")
    if overdue_tasks:
        for task in overdue_tasks:
            _print_task(task)
    else:
        print("   Keine überfälligen Aufgaben!\n")
    return active_tasks, overdue_tasks


def _print_task(task):
    raw_date = task.get('date', '')
    try:
        dt = datetime.fromisoformat(raw_date)
        date_str = dt.strftime("%d.%m.%Y %H:%M")
    except Exception:
        date_str = raw_date

    title = task.get('title', 'Kein Titel')
    if len(title) > 60:
        title = title[:57] + "..."

    print(f"   * {title}")
    print(f"      Datum: {date_str}")
    print(f"      {task.get('message', '')}")
    print()



'''
def check_new_tasks(api, known_task_ids):
    active, overdue = check_tasks(api)

    for task in active:
        task_id = task.get('id')
        if task_id not in known_task_ids:
            known_task_ids.add(task_id)
            print(f"*** NEUE AUFGABE: {task.get('title', '???')[:60]} ***")

    return active, overdue
'''

def main():
    global known_task_ids, known_email_count

    # --- E-Mails ---
    #known_email_count = check_unread_emails(api)
    known_email_count, _ = check_new_emails(api, known_email_count)

    # --- Aufgaben ---
    check_tasks(api)
    #check_new_tasks(api, known_task_ids)

    # --- Sonstige Benachrichtigungen ---
    check_other_notifications(api)

main()