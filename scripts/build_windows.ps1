Write-Host "Building ForgeOAgent for Windows..."
pyinstaller --noconfirm --onedir --windowed --name "ForgeOAgent" --add-data "forgeoagent;forgeoagent" "forgeoagent/gui/app.py"
Write-Host "Build complete! Check the dist/ folder."
