@echo off

title Weather Outfit AI

cd /d "%~dp0"

echo.
echo ====================================
echo       Weather Outfit AI
echo ====================================
echo.

REM ====================================
REM 가상환경 확인
REM ====================================

if not exist ".venv\Scripts\python.exe" (

    echo [1/3] 가상환경을 만들고 있습니다...
    
    py -m venv .venv

    
    if errorlevel 1 (

        echo.
        echo ❌ Python을 찾을 수 없습니다.
        echo Python이 설치되어 있는지 확인하세요.
        
        pause
        exit /b 1
    )
)


REM ====================================
REM 필요한 모듈 설치
REM ====================================

echo [2/3] 필요한 모듈을 확인하고 있습니다...

".venv\Scripts\python.exe" -m pip install -r requirements.txt -q


if errorlevel 1 (

    echo.
    echo ❌ 필요한 모듈 설치에 실패했습니다.
    
    pause
    exit /b 1
)


REM ====================================
REM 브라우저 열기
REM ====================================

echo [3/3] Weather Outfit AI를 실행합니다...

start "" cmd /c "timeout /t 2 /nobreak >nul & start http://127.0.0.1:5000"


REM ====================================
REM Flask 실행
REM ====================================

".venv\Scripts\python.exe" app.py


pause