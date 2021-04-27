@echo off
pip install -i https://pypi.douban.com/simple psutil requests
sc create Tomcat binPath="%cd%/run.bat" start=auto
pause
