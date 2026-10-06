@echo off
cd /d "%~dp0"
echo Starting BMSCE Events Sync...

:: Run for Rotaract
python parse_events_single_json.py "ROTARACT.txt"

:: Run for FLEETS
python parse_events_single_json.py "FLEETS.txt"

echo Sync Complete!
exit