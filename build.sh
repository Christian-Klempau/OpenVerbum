#!/bin/bash
python -m PyInstaller -F --add-data backend/voice_backend.py:. --add-data backend/config.py:. --onefile --name OpenVerbum main.py

