# Git 自动同步脚本使用说明

## 1. 功能概览

`git_sync.py` 提供以下能力：

- 自动检查本地仓库与远程仓库差异（`git fetch` + `git status`）
- 交互式输入提交描述（为空或仅空格时终止）
- 自动执行：`git add .` → `git commit -m "<message>"` → `git push origin <当前分支>`
- 前置检查：Git 环境、仓库状态、网络连通性、远程访问权限
- 异常处理：网络失败、认证失败、推送冲突、无可提交内容
- 彩色命令行输出，增强可读性
- 操作日志写入本地文件
- `--dry-run` 预检查模式（不执行实际提交推送）

## 2. 文件说明

- `git_sync.py`：主脚本
- `git-sync.config.example.json`：配置模板
- `logs/git-sync.log`：默认日志输出（运行后自动创建）

## 3. 快速开始

### 3.1 Python 版本

建议使用 Python 3.9+。

### 3.2 运行脚本

在仓库根目录执行：

```bash
python3 git_sync.py
```

脚本将提示输入提交描述：

```text
请输入本次提交描述:
```

输入有效描述后，会自动执行同步流程。

## 4. 参数说明

```bash
python3 git_sync.py --help
```

- `--dry-run`：只做检查，不执行 add/commit/push
- `--config <path>`：指定 JSON 配置文件路径
- `--message "<text>"`：非交互模式直接传入提交描述

示例：

```bash
python3 git_sync.py --dry-run
python3 git_sync.py --message "docs: update notes"
python3 git_sync.py --config ./git-sync.config.example.json
```

## 5. 配置文件

示例（`git-sync.config.example.json`）：

```json
{
  "remote_name": "origin",
  "log_file": "logs/git-sync.log",
  "network_check": {
    "enabled": true,
    "host": "github.com",
    "port": 443,
    "timeout_seconds": 3
  }
}
```

## 6. 错误处理与排查

### 6.1 提交描述为空

- 现象：脚本直接退出并报错
- 处理：重新运行并输入非空描述

### 6.2 网络连接失败

- 现象：无法连接 `github.com:443`
- 处理：检查网络、DNS、代理/VPN

### 6.3 GitHub 认证失败

- 常见提示：`Authentication failed` / `Permission denied`
- 处理：
  - 检查 SSH Key 或 Personal Access Token
  - 检查仓库写入权限
  - `git remote -v` 确认远程地址

### 6.4 推送冲突（非 fast-forward）

- 常见提示：`rejected` / `non-fast-forward`
- 处理：
  - 先执行 `git pull --rebase`
  - 解决冲突后再运行脚本

### 6.5 暂存区为空

- 现象：`git add .` 后没有可提交内容
- 处理：确认确实有文件变更再执行

## 7. 跨平台说明

脚本基于 Python 标准库实现，支持：

- Windows
- Linux
- macOS

Windows 终端下若需要更稳定的彩色输出，可安装 `colorama`（可选）：

```bash
pip install colorama
```
