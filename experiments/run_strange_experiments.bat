@ECHO OFF
setlocal
for /F "tokens=*" %%a in (strange_experiments.txt) do (
  start cmd /k run_strange_experiment.bat %%a
)