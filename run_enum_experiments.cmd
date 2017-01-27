@ECHO OFF
setlocal
for /F "tokens=1,2*" %%i in (experiments\enum_experiments.txt) do (
    echo Run enum experiment %%j in %%i
    start cmd /k "echo Run enum experiment %%j in %%i & env\Scripts\python.exe -m qtar.optimization.enumeration images\%%i images\%%j > logs\enum_%%j_in_%%i.log"
)
