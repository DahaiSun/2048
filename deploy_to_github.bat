@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul

echo ========================================================
echo         Word2048 GitHub 部署助手 (Token 版)
echo ========================================================
echo.
echo [重要提示] GitHub 不再支持使用密码登录，必须使用 Token。
echo 本脚本将引导您免费获取 Token 并自动完成上传。
echo.

:ask_user
set /p gh_user="1. 请输入您的 GitHub 用户名 (例如 DahaiSun): "
if "%gh_user%"=="" goto ask_user

:ask_repo
set /p gh_repo="2. 请输入您的 仓库名称 (例如 2048): "
if "%gh_repo%"=="" goto ask_repo

echo.
echo --------------------------------------------------------
echo [第三步] 获取上传权限 (Token)
echo 正在为您打开 GitHub Token 创建页面...
echo.
echo 请在打开的网页中：
echo 1. 滚动到页面底部，找到 'Select scopes' 区域
echo 2. [关键] 务必勾选 'workflow' (Update GitHub Action workflows) 选项
echo 3. 勾选 'repo' (Full control of private repositories) 选项
echo 4. 点击页面最底部的绿色 'Generate token' 按钮
echo 5. 复制生成的以 'ghp_' 开头的长字符串
echo --------------------------------------------------------
timeout /t 3 >nul
:: 将 URL 中的 scope 参数更新，请求 workflow 权限
start https://github.com/settings/tokens/new?scopes=repo,workflow^&description=Word2048_Deploy_With_Actions
echo.

:ask_token
set /p gh_token="4. 请在此处粘贴 Token 并回车: "
if "%gh_token%"=="" goto ask_token

echo.
echo [第五步] 正在连接 GitHub 并上传...
echo 目标仓库: https://github.com/%gh_user%/%gh_repo%.git
echo.

:: 清理旧的连接
git remote remove origin 2>nul

:: 使用带 Token 的安全地址重新连接
git remote add origin https://%gh_user%:%gh_token%@github.com/%gh_user%/%gh_repo%.git

:: 确保分支正确
git branch -M main

:: 推送代码
git push -u origin main

if %errorlevel% neq 0 (
    echo.
    echo ========================================================
    echo [错误] 推送失败！
    echo 可能原因：
    echo 1. Token 复制错误或已过期
    echo 2. 仓库名称输入错误 (仓库必须先在网页上创建好)
    echo 3. 用户名输入错误
    echo ========================================================
    pause
    exit /b
)

echo.
echo ========================================================
echo [成功] 代码已上传！游戏已部署到 GitHub。
echo.
echo 现在请去 GitHub 仓库页面 -> Settings -> Pages
echo 在 'Build and deployment' 下选择 'Deploy from a branch'
echo Branch 选择 'main' -> Save
echo ========================================================
pause
