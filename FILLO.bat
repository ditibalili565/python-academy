@REM @echo off
@REM echo.
@REM echo  Python Academy - Duke u nisur...
@REM echo.

@REM cd /d "%~dp0"

@REM python --version >nul 2>&1
@REM if errorlevel 1 (
@REM     echo  GABIM: Python nuk eshte instaluar!
@REM     echo  Shko tek https://python.org dhe instalo Python.
@REM     pause
@REM     exit
@REM )

@REM python -c "import pygame" >nul 2>&1
@REM if errorlevel 1 (
@REM     echo  Duke instaluar pygame...
@REM     pip install pygame
@REM )

@REM start "" python server.py

@REM timeout /t 2 /nobreak >nul

@REM start "" "http://localhost:8000/home.html"

@REM echo  Serveri u nis! Browser-i po hapet...
@REM echo  (Mbyll kete dritare per te ndalur serverin)
@REM echo.

@echo off
echo.
echo  Python Academy - Duke u nisur...
echo.

cd /d "%~dp0"

:: Kontrollo nese Python eshte instaluar
python --version >nul 2>&1
if errorlevel 1 (
    echo  GABIM: Python nuk eshte instaluar!
    echo  Shko tek https://python.org dhe instalo Python.
    pause
    exit
)

:: Instalo pygame nese mungon
python -c "import pygame" >nul 2>&1
if errorlevel 1 (
    echo  Duke instaluar pygame...
    pip install pygame
)

:: Nis serverin ne sfond
start "" python server.py

:: Prit 2 sekonda qe serveri te nise
timeout /t 2 /nobreak >nul

:: Hap faqen e regjistrimit ne browser
start "" "http://localhost:8000/registry.html"

echo  Serveri u nis! Browser-i po hapet...
echo  (Mbyll kete dritare per te ndalur serverin)
echo.