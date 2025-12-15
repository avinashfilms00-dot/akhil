Smart Wash - Desktop Deployment

This folder contains the desktop GUI app `laundry_app.py` (Tkinter).

Options to deploy on Windows:

1) Create a single-file executable (recommended)

- Open PowerShell in this folder and run:

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
pyinstaller --onefile --windowed --name "SmartWash" "laundry_app.py"
```

- The resulting executable will be at `dist\SmartWash.exe`.

Notes:
- The app uses WhatsApp Web to send messages; ensure you're logged in to WhatsApp Web.
- The SQLite DB `smart_wash_laundry.db` will be created in the same folder as the executable at runtime.

2) Quick build script

Run the provided `build.ps1` in PowerShell (may require execution policy):

```powershell
.\\build.ps1
```

3) Creating an installer (optional)

After producing the single `SmartWash.exe`, you can use tools like Inno Setup or WiX to create an installer.

If you want, I can run the build now here (installing PyInstaller and running the command). Reply: `yes, build now` to allow me to run the packaging commands in the workspace, or `just add files` to stop here.