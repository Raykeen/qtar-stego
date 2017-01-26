@ECHO OFF
ECHO Running experiment %2 in %1:
..\env\Scripts\python.exe ..\testqtar.py ..\images\%1 ..\images\%2 -ns > logs\exp_%2_in_%1.log
ECHO Testing done...
FOR %%E IN (1 2 3 4 5 6) DO (
..\env\Scripts\python.exe ..\de.py ..\images\%1 ..\images\%2 %%E >> logs\exp_%2_in_%1.log
ECHO Issue %%E done...
)
ECHO Experiment %2 in %1 DONE