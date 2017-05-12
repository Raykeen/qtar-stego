@ECHO OFF
setlocal
for /F "tokens=1,2*" %%i in (experiments\enum_experiments.txt) do (
    echo Run enum experiment %%~nj in %%~ni
    start cmd /k "echo Run enum experiment %%~nj in %%~ni & env\Scripts\python.exe -m qtar.optimization.enumeration images\%%i images\%%j -q 10 -rc 256 256 -rw 256 256 > logs\qtarpm\pm_enum_%%~nj_in_%%~ni_q10_r256.log"
)
