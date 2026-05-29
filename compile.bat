@echo off
cd /d "%~dp0"
pyinstaller --onefile --upx-dir=".\upx-5.1.1-win64" Diablo_Immortal_Calculator.pyw