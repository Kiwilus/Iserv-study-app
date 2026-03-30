
############################
##Study App with Iserv API##
############################

from IServAPI import IServAPI
from datetime import datetime


ISERV_URL = input("Gebe zuerst deine Iserv Domain ein bsp. rhs.schule: ")
USERNAME = input("Jetzt dein Nutzername: ")
PASSWORD = input("gebe dein passwort ein: ")



if not all([USERNAME, PASSWORD, ISERV_URL]):
    raise ValueError("Das Programm hat nicht alle Werte!")

# connection
print("Verbinde mit IServ...")
api = IServAPI(username=USERNAME, password=PASSWORD, iserv_url=ISERV_URL)
print(f"Eingeloggt als: {USERNAME}\n")

# --- E-Mails prüfen ---
def check_unread_emails():
    emails = api.get_emails()
    unread = emails.get('unseen', 0)
    print(f"Ungelesene E-Mails: {unread}")
    if unread > 0:
        for mail in emails.get('data', []):
            if not mail.get('seen'):
                print(f"    [{mail['date']}] {mail['subject']}")
    return unread

# --- Aufgaben sauber auslesen ---
def check_tasks():
    notifications = api.get_notifications()
    all_notifs = notifications.get('data', {}).get('notifications', [])

    # Nur Aufgaben herausfiltern
    tasks = [n for n in all_notifs if n.get('type') == 'exercise']

    print(f"\nOffene Aufgaben: {len(tasks)}")
    if tasks:
        for task in tasks:
            # Datum formatieren
            raw_date = task.get('date', '')
            try:
                dt = datetime.fromisoformat(raw_date)
                date_str = dt.strftime("%d.%m.%Y %H:%M")
            except:
                date_str = raw_date

            title = task.get('title', 'Kein Titel')
            message = task.get('message', '')

            # Titel kürzen wenn zu lang
            if len(title) > 60:
                title = title[:57] + "..."

            print(f"   * {title}")
            print(f"        {date_str}")
            print(f"        {message}")
            print()
    else:
        print("   Keine offenen Aufgaben!")

    return tasks

# Alle anderen Benachrichtigungen
def check_other_notifications():
    notifications = api.get_notifications()
    all_notifs = notifications.get('data', {}).get('notifications', [])

    others = [n for n in all_notifs if n.get('type') != 'exercise']

    if others:
        print(f"Sonstige Benachrichtigungen: {len(others)}")
        for n in others:
            print(f"   * [{n.get('type')}] {n.get('title', '')} — {n.get('message', '')}")
    print()

def main():
    check_unread_emails()
    check_tasks()
    check_other_notifications()

main()