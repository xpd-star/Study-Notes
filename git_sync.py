#!/usr/bin/env python3
"""Cross-platform Git sync helper with logging, dry-run and interactive commit message."""

from __future__ import annotations

import argparse
import json
import logging
import os
import re
import socket
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple


DEFAULT_CONFIG: Dict[str, object] = {
    "remote_name": "origin",
    "log_file": "logs/git-sync.log",
    "network_check": {
        "enabled": True,
        "host": "github.com",
        "port": 443,
        "timeout_seconds": 3,
    },
}


class Colors:
    RESET = "\033[0m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    CYAN = "\033[36m"


def init_colors() -> None:
    """Enable ANSI colors on Windows when colorama is available."""
    if os.name != "nt":
        return
    try:
        import colorama  # type: ignore

        colorama.just_fix_windows_console()
    except Exception:
        pass


def color_text(text: str, color: str) -> str:
    return f"{color}{text}{Colors.RESET}"


def print_info(msg: str) -> None:
    print(color_text(f"[INFO] {msg}", Colors.CYAN))


def print_ok(msg: str) -> None:
    print(color_text(f"[OK] {msg}", Colors.GREEN))


def print_warn(msg: str) -> None:
    print(color_text(f"[WARN] {msg}", Colors.YELLOW))


def print_error(msg: str) -> None:
    print(color_text(f"[ERROR] {msg}", Colors.RED))


@dataclass
class CommandResult:
    returncode: int
    stdout: str
    stderr: str


class GitSyncError(RuntimeError):
    pass


def load_config(path: Optional[str]) -> Dict[str, object]:
    config = dict(DEFAULT_CONFIG)
    if not path:
        return config
    file_path = Path(path)
    if not file_path.exists():
        raise GitSyncError(f"配置文件不存在: {file_path}")
    try:
        loaded = json.loads(file_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise GitSyncError(f"配置文件 JSON 解析失败: {exc}") from exc
    return deep_merge(config, loaded)


def deep_merge(base: Dict[str, object], incoming: Dict[str, object]) -> Dict[str, object]:
    merged = dict(base)
    for key, value in incoming.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = deep_merge(merged[key], value)  # type: ignore[arg-type]
        else:
            merged[key] = value
    return merged


def setup_logger(log_file: str) -> logging.Logger:
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("git_sync")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    return logger


def run_command(
    command: List[str],
    logger: logging.Logger,
    dry_run: bool = False,
    check: bool = False,
) -> CommandResult:
    cmd_text = " ".join(command)
    logger.info("Run command: %s", cmd_text)
    if dry_run:
        logger.info("Dry-run enabled, skipped command: %s", cmd_text)
        return CommandResult(returncode=0, stdout="", stderr="")
    proc = subprocess.run(
        command,
        text=True,
        capture_output=True,
        encoding="utf-8",
    )
    logger.info("Command exit code: %s", proc.returncode)
    if proc.stdout.strip():
        logger.info("STDOUT:\n%s", proc.stdout.strip())
    if proc.stderr.strip():
        logger.info("STDERR:\n%s", proc.stderr.strip())
    if check and proc.returncode != 0:
        raise GitSyncError(format_command_error(command, proc.stderr or proc.stdout))
    return CommandResult(proc.returncode, proc.stdout, proc.stderr)


def format_command_error(command: List[str], output: str) -> str:
    base = f"命令执行失败: {' '.join(command)}"
    output_lower = output.lower()
    if "authentication failed" in output_lower or "permission denied" in output_lower:
        return (
            f"{base}\n可能原因: GitHub 认证失败或无权限。\n"
            "建议: 检查 SSH Key/Token、仓库权限，或执行 `git remote -v` 确认远程地址。"
        )
    if (
        "could not resolve host" in output_lower
        or "failed to connect" in output_lower
        or "timed out" in output_lower
    ):
        return (
            f"{base}\n可能原因: 网络不可用或 DNS 异常。\n"
            "建议: 检查网络连接，尝试访问 github.com，必要时配置代理。"
        )
    if "non-fast-forward" in output_lower or "rejected" in output_lower:
        return (
            f"{base}\n可能原因: 本地分支落后于远程，推送被拒绝。\n"
            "建议: 先执行 `git pull --rebase` 解决冲突后再推送。"
        )
    if "merge conflict" in output_lower or "conflict" in output_lower:
        return f"{base}\n可能原因: 存在代码冲突。\n建议: 解决冲突后再执行同步。"
    return f"{base}\n输出: {output.strip()}"


def check_network(config: Dict[str, object], logger: logging.Logger) -> None:
    net = config.get("network_check", {})
    if not isinstance(net, dict):
        return
    if not net.get("enabled", True):
        logger.info("Network check disabled by config.")
        return
    host = str(net.get("host", "github.com"))
    port = int(net.get("port", 443))
    timeout = float(net.get("timeout_seconds", 3))
    try:
        with socket.create_connection((host, port), timeout=timeout):
            logger.info("Network check passed: %s:%s", host, port)
    except OSError as exc:
        raise GitSyncError(
            f"网络检查失败，无法连接 {host}:{port}。\n"
            "建议: 检查网络/VPN/代理后重试。"
        ) from exc


def ensure_git_repo(logger: logging.Logger, dry_run: bool) -> None:
    run_command(["git", "--version"], logger, dry_run=dry_run, check=True)
    result = run_command(
        ["git", "rev-parse", "--is-inside-work-tree"],
        logger,
        dry_run=dry_run,
        check=True,
    )
    if not dry_run and result.stdout.strip().lower() != "true":
        raise GitSyncError("当前目录不是 Git 仓库。")


def get_current_branch(logger: logging.Logger, dry_run: bool) -> str:
    result = run_command(
        ["git", "branch", "--show-current"],
        logger,
        dry_run=dry_run,
        check=True,
    )
    branch = result.stdout.strip() or "main"
    return branch


def ensure_remote_access(remote_name: str, logger: logging.Logger, dry_run: bool) -> None:
    run_command(["git", "remote", "get-url", remote_name], logger, dry_run=dry_run, check=True)
    run_command(
        ["git", "ls-remote", "--heads", remote_name],
        logger,
        dry_run=dry_run,
        check=True,
    )


def git_fetch(remote_name: str, logger: logging.Logger, dry_run: bool) -> None:
    run_command(["git", "fetch", remote_name], logger, dry_run=dry_run, check=True)


def parse_status(status_output: str) -> Dict[str, int]:
    """Parse `git status --porcelain=v1 --branch` output."""
    lines = status_output.splitlines()
    ahead = 0
    behind = 0
    local_changes = 0
    first_line = lines[0] if lines else ""
    ahead_match = re.search(r"ahead (\d+)", first_line)
    behind_match = re.search(r"behind (\d+)", first_line)
    if ahead_match:
        ahead = int(ahead_match.group(1))
    if behind_match:
        behind = int(behind_match.group(1))
    for line in lines[1:]:
        if line.strip():
            local_changes += 1
    return {"ahead": ahead, "behind": behind, "local_changes": local_changes}


def get_status(logger: logging.Logger, dry_run: bool) -> Tuple[str, Dict[str, int]]:
    result = run_command(
        ["git", "status", "--porcelain=v1", "--branch"],
        logger,
        dry_run=dry_run,
        check=True,
    )
    stats = parse_status(result.stdout)
    return result.stdout, stats


def get_commit_message(cli_message: Optional[str]) -> str:
    if cli_message is not None:
        message = cli_message
    else:
        message = input("请输入本次提交描述: ")
    if not message.strip():
        raise GitSyncError("提交描述为空，已终止同步流程。请重新运行并输入有效描述。")
    return message.strip()


def git_add_commit_push(
    message: str,
    remote_name: str,
    branch: str,
    logger: logging.Logger,
    dry_run: bool,
) -> None:
    run_command(["git", "add", "."], logger, dry_run=dry_run, check=True)
    staged = run_command(["git", "diff", "--cached", "--name-only"], logger, dry_run=dry_run, check=True)
    if not dry_run and not staged.stdout.strip():
        raise GitSyncError("没有可提交的变更（git add 后暂存区为空）。")
    run_command(["git", "commit", "-m", message], logger, dry_run=dry_run, check=True)
    run_command(["git", "push", remote_name, branch], logger, dry_run=dry_run, check=True)


def print_status_summary(branch: str, stats: Dict[str, int], dry_run: bool) -> None:
    print_info(f"当前分支: {branch}")
    print_info(
        f"状态摘要: 本地变更 {stats['local_changes']}，领先 {stats['ahead']}，落后 {stats['behind']}"
    )
    if stats["behind"] > 0:
        print_warn("检测到远程有更新且本地落后，可能导致推送失败，建议先 `git pull --rebase`。")
    if dry_run:
        print_warn("当前为 dry-run 模式，仅预检查不执行实际提交/推送。")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="自动化 Git 同步脚本")
    parser.add_argument("--config", default=None, help="配置文件路径（JSON）")
    parser.add_argument("--dry-run", action="store_true", help="仅做预检查，不执行 add/commit/push")
    parser.add_argument("--message", default=None, help="非交互模式下直接传入提交描述")
    return parser.parse_args()


def main() -> int:
    init_colors()
    args = parse_args()

    try:
        config = load_config(args.config)
        log_file = str(config.get("log_file", DEFAULT_CONFIG["log_file"]))
        logger = setup_logger(log_file)

        print_info("开始执行 Git 同步流程...")
        logger.info("Start git sync, dry_run=%s", args.dry_run)

        ensure_git_repo(logger, dry_run=args.dry_run)
        check_network(config, logger)

        remote_name = str(config.get("remote_name", "origin"))
        branch = get_current_branch(logger, dry_run=args.dry_run)
        ensure_remote_access(remote_name, logger, dry_run=args.dry_run)
        git_fetch(remote_name, logger, dry_run=args.dry_run)

        _, stats = get_status(logger, dry_run=args.dry_run)
        print_status_summary(branch, stats, dry_run=args.dry_run)

        message = get_commit_message(args.message)
        print_info(f"提交描述: {message}")

        if args.dry_run:
            print_ok("dry-run 检查完成，未执行实际同步。")
            logger.info("Dry-run finished.")
            return 0

        git_add_commit_push(message, remote_name, branch, logger, dry_run=False)
        print_ok("同步成功：已完成 add / commit / push。")
        print_ok(f"日志文件: {log_file}")
        return 0
    except KeyboardInterrupt:
        print_error("用户取消操作。")
        return 130
    except GitSyncError as exc:
        print_error(str(exc))
        return 1
    except Exception as exc:
        print_error(f"未知错误: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
