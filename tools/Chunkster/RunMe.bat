@echo off

FOR /F "skip=2 tokens=2*" %%A IN ('REG QUERY "HKLM\Software\JavaSoft\Java Runtime Environment" /v CurrentVersion') DO set CurVer=%%B

FOR /F "skip=2 tokens=2*" %%A IN ('REG QUERY "HKLM\Software\JavaSoft\Java Runtime Environment\%CurVer%" /v JavaHome') DO set JAVA_HOME=%%B

if "%JAVA_HOME%".==. (
    @echo java.exe not found
    pause
    exit
) else (
    @echo Java found! %JAVA_HOME%\bin\java.exe
)

"%JAVA_HOME%\bin\java.exe" -jar Chunkster.jar

pause