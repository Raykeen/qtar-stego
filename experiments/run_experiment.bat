@ECHO OFF
ECHO Running DE experiment %2 in %1:
..\env\Scripts\python.exe ..\qtar\testqtar.py ..\images\%1 ..\images\%2 -ns > logs\exp%3_%2_in_%1.log
ECHO Testing done...
..\env\Scripts\python.exe ..\qtar\optimisation\de.py ..\images\%1 ..\images\%2 %3 >> logs\exp%3_%2_in_%1.log
ECHO Issue %3 done...
ECHO DE Experiment %2 in %1 DONE