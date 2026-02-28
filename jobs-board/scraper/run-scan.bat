@echo off
REM Jobs Board Scanner for Windows
REM Run this to scan for new jobs

echo Starting job scan...
python jobs-board\scraper\scraper.py scan
pause
