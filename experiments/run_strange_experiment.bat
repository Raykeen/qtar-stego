@ECHO OFF

ECHO Running strange experiment %2 in %1:
..\env\Scripts\python.exe ..\qtar\optimisation\enumeration.py ..\images\%1 ..\images\%2 >> logs\sexp_%2_in_%1.log
ECHO Strange experiment %2 in %1 DONE