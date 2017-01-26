@ECHO OFF
setlocal
for /F "tokens=*" %%a in (de_experiments.txt) do (
  start cmd /k run_experiment.bat %%a %1
)