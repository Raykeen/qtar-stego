@ECHO OFF
setlocal enabledelayedexpansion

for /F "tokens=1,2*" %%i in (experiments\de_experiments.txt) do (
    set _params=%%k
    set _short=!_params:-=_%!
    set _short=!_short: =%!
    echo Run de %1 experiments %%~nj in %%~ni !_params!
    start cmd /k "echo Run de experiment %%~nj in %%~ni & env\Scripts\python.exe -m qtar.optimization.de images\%%i images\%%j %1 !_params! -xls xls\de.xlsx > logs\de%1_%%~nj_in_%%~ni!_short!.log"
)