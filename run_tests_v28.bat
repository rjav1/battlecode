@echo off
setlocal
set PYTHON=C:\Users\rahil\AppData\Local\Programs\Python\Python313\python.exe
set CAMBC=%PYTHON% -c "from cambc.cli import main; main()"
set OUT=C:\Users\rahil\downloads\battlecode\test_v28_results.txt

echo Running v28 tests... > %OUT%
echo. >> %OUT%

echo === buzzing vs buzzing_prev on galaxy === >> %OUT%
%CAMBC% run buzzing buzzing_prev galaxy >> %OUT% 2>&1

echo === buzzing_prev vs buzzing on galaxy === >> %OUT%
%CAMBC% run buzzing_prev buzzing galaxy >> %OUT% 2>&1

echo === buzzing vs buzzing_prev on arena === >> %OUT%
%CAMBC% run buzzing buzzing_prev arena >> %OUT% 2>&1

echo === buzzing_prev vs buzzing on arena === >> %OUT%
%CAMBC% run buzzing_prev buzzing arena >> %OUT% 2>&1

echo === buzzing vs buzzing_prev on default_medium1 === >> %OUT%
%CAMBC% run buzzing buzzing_prev default_medium1 >> %OUT% 2>&1

echo === buzzing_prev vs buzzing on default_medium1 === >> %OUT%
%CAMBC% run buzzing_prev buzzing default_medium1 >> %OUT% 2>&1

echo Done! Results in test_v28_results.txt
