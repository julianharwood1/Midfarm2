
MidFarm - Lucy & Julian (GitHub Actions build-ready)
---------------------------------------------------

This is a lightweight farming prototype built with Python + pygame. It is prepared to be built into a Windows .exe via GitHub Actions (workflow included).

How to get a clickable Windows .exe without installing Python:
1. Create a new GitHub repository on your account.
2. Upload all files from this folder (or push via git).
3. Go to Actions tab on GitHub, select the "Build Windows EXE" workflow (it runs automatically on push).
4. Wait for the workflow to complete and download the artifact named "midfarm-windows-exe". Inside you'll find MidFarm.exe.

Local run (if you want to test locally):
1. Install Python 3.10+
2. pip install -r requirements.txt
3. python main.py

Controls:
- Arrow keys / WASD: move active character
- SPACE: interact (plant/harvest or talk to NPC if near)
- D: advance day
- F: toggle profanity ON/OFF
- TAB: switch active character (Lucy <-> Julian)
- F5: save, F9: load, Esc: quit

Notes:
- The game contains mild->strong profanity; it's toggleable with F.
- The GitHub Actions workflow uses PyInstaller to bundle the exe and includes the assets folder.
