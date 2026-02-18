@echo off
chcp 65001 > nul
cd /d "s:\VSCODE\CodeX\MaiBot-Plugin-Kit"

echo Setting git user config...
git -c safe.directory=* config user.name "Slapq"
git -c safe.directory=* config user.email "slapq@users.noreply.github.com"

echo Adding all files...
git -c safe.directory=* add .
if errorlevel 1 (echo FAIL: git add & exit /b 1)

echo Committing...
git -c safe.directory=* commit -m "feat: MaiBot Plugin Kit v1.0 initial release"
if errorlevel 1 (echo FAIL: git commit & exit /b 1)

echo Setting remote...
git -c safe.directory=* remote add origin https://github.com/Slapq/MaiBot-Plugin-Kit.git 2>nul
git -c safe.directory=* remote set-url origin https://github.com/Slapq/MaiBot-Plugin-Kit.git

echo Pushing to GitHub...
git -c safe.directory=* push -u origin main
if errorlevel 1 (echo FAIL: git push & exit /b 1)

echo.
echo === SUCCESS: https://github.com/Slapq/MaiBot-Plugin-Kit ===
