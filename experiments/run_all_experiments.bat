@ECHO OFF
setlocal
for /F "tokens=*" %%a in (experiments.txt) do (
  start cmd /k run_experiment_for.bat %%a
)