# Iserv-study-app

## CLI version coming soon...

---

## Open Source Notice

This code is **free to modify, improve, and adapt**.  
Feel free to enhance it, change it, or use it in your projects.  
It is **completely free and open-source**.

---

## Dependencies

```bash
IServAPI
kivy
beautifulsoup4
```

---

## Create desktop icon on Linux

1. **create file**
```bash
nano ~/Desktop/IServDashboard.desktop
```
2. **contents of the file**
```bash
[Desktop Entry]
Type=Application
Name=IServDashboard
Exec= #path to your venv and main python file e.g /home/you/projects/myprojekt/.venv /home/you/projects/myproject/main.py
Icon= #path to you icon
Terminal=false
Categories=Development;
```
3. **make the .desktop file executable**
```bash
chmod +x ~/Desktop/IServDashboard.desktop
```

## Create desktop icon on Windows
1. **create file**
```bash
notepad start_IServDashboard.bat
```
2. **contents of the file**
```bash
@echo off
C:\Users\YOURNAME\projects\IServDashboard\.venv\Scripts\python.exe C:\Users\YOURNAME\projects\IServDashboard\main.py
```
3. **create desktop shortcut**
```bash
Right-click the .bat file
Click → Send to → Desktop (create shortcut)
```