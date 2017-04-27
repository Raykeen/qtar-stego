@ECHO OFF
setlocal
for /F "tokens=1,2*" %%i in (experiments\de_experiments.txt) do (
    echo Run de %1 experiments %%j in %%i
    start cmd /k "echo Run de experiment %%j in %%i & env\Scripts\python.exe -m qtar.optimization.de images\%%i images\%%j %1 > logs\de_%%j_in_%%i.log"
)