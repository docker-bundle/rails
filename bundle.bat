@echo off
set file="%~dp0bundle.py"
python3 %file% %* || python %file% %*
