@echo off
REM ============================================================
REM build.bat
REM Gera o executavel FlashCards.exe para Windows usando PyInstaller.
REM
REM Como usar:
REM   1. Instale o Python (https://www.python.org/downloads/) marcando
REM      a opcao "Add Python to PATH" durante a instalacao.
REM   2. De dois cliques neste arquivo (build.bat), ou rode-o pelo
REM      Prompt de Comando dentro desta mesma pasta.
REM   3. O executavel final vai aparecer em: dist\FlashCards.exe
REM ============================================================

echo Instalando o PyInstaller...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo.
echo Compilando o FlashCards.exe (isso pode levar 1-2 minutos)...
python -m PyInstaller --noconfirm --onefile --windowed ^
    --name "FlashCards" ^
    main.py

echo.
if exist dist\FlashCards.exe (
    echo ============================================
    echo  SUCESSO! O executavel esta em: dist\FlashCards.exe
    echo  Voce pode copiar esse arquivo para onde quiser.
    echo ============================================
) else (
    echo ============================================
    echo  Algo deu errado. Veja as mensagens acima.
    echo ============================================
)
pause
