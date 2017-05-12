@ECHO OFF
setlocal
for /F "tokens=1,2*" %%i in (experiments\de_experiments.txt) do (
    echo Run de %1 experiments %%~nj in %%~ni
    start cmd /k "echo Run de experiment %%~nj in %%~ni & env\Scripts\python.exe -m qtar.optimization.de images\%%i images\%%j %1 -xls xls\de.xlsx > logs\qtarpm\pm_de_%%~nj_in_%%~ni.log"
)