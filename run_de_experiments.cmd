@ECHO OFF
setlocal
for /F "tokens=1,2*" %%i in (experiments\de_experiments.txt) do (
    echo Run de %1 experiments %%~nj in %%~ni
    start cmd /k "echo Run de experiment %%~nj in %%~ni & env\Scripts\python.exe -m qtar.optimization.de images\%%i images\%%j %1 -q 10 -rc 256 256 -rw 256 256 -xls xls\de.xlsx > logs\de_%%~nj_in_%%~ni_q10_r256.log"
)