@echo off
set DIR=\%~dp0..\
set DIR=%DIR:\=/%
set DIR=%DIR::=%
set IMAGE=docker-bundle
echo Enter Docker env...may wait...................
docker build "%~dp0." -f "%~dp0Dockerfile.w" -t %IMAGE%
docker run --rm -it -v //var/run/docker.sock:/var/run/docker.sock -v "%DIR%:%DIR%" -w "%DIR%" %IMAGE% %*
