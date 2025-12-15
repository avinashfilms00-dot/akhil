# Build script for SmartWash (Windows PowerShell)
# Run in project folder: .\build.ps1

python -m pip install --upgrade pip
pip install -r requirements.txt
pyinstaller --onefile --windowed --name "SmartWash" "laundry_app.py"

Write-Host "Build finished. See dist\SmartWash.exe"