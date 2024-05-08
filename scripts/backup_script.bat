@echo off
setlocal

REM Set the backup directory path
set "backup_dir=D:\RayScrapMgmt\backup"

REM Create the backup directory if it doesn't exist
if not exist "%backup_dir%" mkdir "%backup_dir%"

REM Get today's date in YYYY-MM-DD format
for /f "tokens=1-3 delims=-" %%a in ('echo %date%') do (
    set "year=%%c"
    set "month=%%b"
    set "day=%%a"
)

REM Create the backup file name with today's date
set "backup_file=%backup_dir%\employee_%year%-%month%-%day%.db"

REM Copy the employee.db file to the backup location with today's date
copy "D:\RayScrapMgmt\employee.db" "%backup_file%"

echo Backup created successfully: %backup_file%

endlocal
