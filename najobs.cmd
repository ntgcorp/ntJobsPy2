SET PY_TYPE=X64

@REM DIFFERENTE PER VARI COMPUTER 
SET PY_EXEC=X:\_NTGCORP\PythonX64\App\Python
IF "%COMPUTERNAME%"=="LENOVOMINI1" SET PY_EXEC=D:\Applic\PythonX64\App\Python
IF "%COMPUTERNAME%"=="ACERMINI" SET PY_EXEC=C:\Applic\PythonX64\App\Python

@REM DIFFERENTE PER VARI COMPUTER 
SET PY_NTJOBS=G:\My Drive\Progetti\ntJobsPy
ECHO Python ntJobsPy Start 

:START
REM DELETE OLD RESTART
IF EXIST "%PY_NTJOBS%\ntjobs.restart" DEL "%PY_NTJOBS%\ntjobs.restart"
%PY_EXEC% najobs %1 %2 %3

@REM EVENTUALE RESTART
IF EXIST "%PY_NTJOBS%\ntjobs.restart" GOTO :RESTART