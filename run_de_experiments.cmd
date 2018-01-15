@ECHO OFF
setlocal enabledelayedexpansion

for /F "tokens=1,2*" %%i in (experiments\experiments.txt) do (
    set _params=%*
    set _short=!_params: =%!
    set _short=!_short:-= %!
    echo Run de %1 experiments %%~nj in %%~ni !_short!
    start cmd /k "echo Run de experiment %%~nj in %%~ni & python -m qtar.optimization.de images\%%i images\%%j !_params! -x xls\de.xlsx > "logs\de!_short! %%~nj in %%~ni.log""
)
