@ECHO OFF
ECHO Running experiment %2 in %1:
..\env\Scripts\python.exe ..\test_qtar.py ..\images\%1 ..\images\%2 -ns > logs\exp_%2_in_%1.log
..\env\Scripts\python.exe ..\differetial_evolution.py ..\images\%1 ..\images\%2 0 >> logs\exp_%2_in_%1.log
ECHO Experiment %2 in %1 DONE