@ECHO OFF
setlocal
for /F "tokens=1,2*" %%i in (experiments\robustness_experiments.txt) do (
    echo Run robustness experiment %%~nj in %%~ni
    start cmd /k "echo Run robustness experiment %%~nj in %%~ni & env\Scripts\python.exe -m qtar.robustness.robustness images\%%i images\%%j > logs\robustness_%%~nj_in_%%~ni.log"
)
