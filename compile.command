#!/bin/zsh
cd "$(dirname "$0")"
pyinstaller --onefile --upx-dir="./upx-5.1.1-arm64_macho" Diablo_Immortal_Calculator.pyw