@echo off
echo Iniciando servicios del Sistema de Prestamos...

:: Activar entorno virtual
call venv_new\Scripts\activate.bat

:: Matar cualquier proceso de Python existente
taskkill /F /IM python.exe 2>NUL

:: Esperar un momento para asegurar que los puertos se liberen
timeout /t 2 /nobreak

:: Iniciar Auth Service (puerto 8000)
start "Auth Service" cmd /k "cd auth_service && python app.py"
timeout /t 3 /nobreak

:: Iniciar Resource Service (puerto 8001)
start "Resource Service" cmd /k "cd resource_service && python app.py"
timeout /t 3 /nobreak

:: Iniciar Student Service (puerto 8002)
start "Student Service" cmd /k "cd student_service && python app.py"
timeout /t 3 /nobreak

:: Iniciar Loan Service (puerto 8003)
start "Loan Service" cmd /k "cd loan_service && python app.py"
timeout /t 3 /nobreak

:: Iniciar Web Interface (puerto 5000)
start "Web Interface" cmd /k "cd web_interface && python app.py"

echo.
echo Servicios iniciados:
echo - Auth Service: http://localhost:8000
echo - Resource Service: http://localhost:8001
echo - Student Service: http://localhost:8002
echo - Loan Service: http://localhost:8003
echo - Web Interface: http://localhost:5000
echo.
echo Presiona cualquier tecla para abrir la interfaz web...
pause > nul
start http://localhost:5000
