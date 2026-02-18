@echo off
chcp 65001 > nul
cd /d "s:\VSCODE\CodeX\MaiBot-Plugin-Kit"

echo [1/4] git add ...
git -c safe.directory=* add .
if errorlevel 1 goto fail

echo [2/4] git commit ...
git -c safe.directory=* commit -m "feat: MaiBot Plugin Kit v1.0 - mai_advanced + advanced template + docs"
if errorlevel 1 goto fail

echo [3/4] check remote ...
git -c safe.directory=* remote -v
if errorlevel 1 (
    echo No remote set - will set origin
    git -c safe.directory=* remote add origin https://github.com/Slapq/MaiBot-Plugin-Kit.git
)

echo [4/4] git push ...
git -c safe.directory=* push -u origin main
if errorlevel 1 goto fail

echo.
echo === Done! Pushed to https://github.com/Slapq/MaiBot-Plugin-Kit ===
goto end

:fail
echo.
echo === FAILED - check output above ===
:end
pause
