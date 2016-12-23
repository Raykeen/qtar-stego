@ECHO OFF
ECHO Running experiment %2 in %1:
..\env\Scripts\python.exe ..\test_qtar.py ..\images\%1 ..\images\%2 -ns > logs\exp%3_%2_in_%1.log
ECHO Testing done...
..\env\Scripts\python.exe ..\differetial_evolution.py ..\images\%1 ..\images\%2 %3 >> logs\exp%3_%2_in_%1.log
ECHO Issue %3 done...
ECHO Experiment %2 in %1 DONE