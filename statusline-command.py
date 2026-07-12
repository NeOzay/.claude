#!/usr/bin/env python3
import json
import os
import subprocess
import sys
import time
from typing import TypedDict, cast

RESET = "\033[00m"


class Workspace(TypedDict, total=False):
    current_dir: str


class ModelInfo(TypedDict, total=False):
    display_name: str


class ContextWindow(TypedDict, total=False):
    used_percentage: float


class RateWindow(TypedDict, total=False):
    used_percentage: float
    resets_at: float


class RateLimits(TypedDict, total=False):
    five_hour: RateWindow


class StatuslineInput(TypedDict, total=False):
    workspace: Workspace
    cwd: str
    model: ModelInfo
    context_window: ContextWindow
    rate_limits: RateLimits


def color(code: str, text: str) -> str:
    return f"\033[{code}m{text}{RESET}"


def git_branch(cwd: str) -> str | None:
    try:
        out = subprocess.run(
            [
                "git",
                "-C",
                cwd,
                "--no-optional-locks",
                "symbolic-ref",
                "--short",
                "HEAD",
            ],
            capture_output=True,
            text=True,
            timeout=2,
        )
        branch = out.stdout.strip()
        return branch if out.returncode == 0 and branch else None
    except Exception:
        return None


def main() -> None:
    data = cast(StatuslineInput, json.load(sys.stdin))

    workspace = data.get("workspace") or {}
    cwd: str = workspace.get("current_dir") or data.get("cwd", "")
    model_info = data.get("model") or {}
    model: str | None = model_info.get("display_name")
    context_window = data.get("context_window") or {}
    ctx: float | None = context_window.get("used_percentage")
    rate_limits = data.get("rate_limits") or {}
    five_hour: RateWindow = rate_limits.get("five_hour") or {}
    five_pct: float | None = five_hour.get("used_percentage")
    five_reset: float | None = five_hour.get("resets_at")

    parts: list[str] = [color("01;34", os.path.basename(cwd))]

    branch = git_branch(cwd)
    if branch:
        parts.append(color("0;35", f"({branch})"))

    if model:
        parts.append(color("0;33", model))

    if ctx is not None:
        parts.append(color("0;37", f"[ctx: {round(ctx)}%]"))

    if five_pct is not None and five_reset is not None:
        remaining = int(five_reset) - int(time.time())
        time_str: str
        if remaining <= 0:
            time_str = "reset"
        else:
            time_str = f"{remaining // 60}min"
        parts.append(color("0;36", f"[{round(five_pct)}% | {time_str}]"))

    caveman_flag = os.path.join(
        os.environ.get("HOME", ""), ".claude", ".caveman-active"
    )
    if os.path.isfile(caveman_flag):
        mode: str
        try:
            with open(caveman_flag) as f:
                mode = f.read().strip()
        except Exception:
            mode = ""
        caveman_text: str
        if mode in ("full", ""):
            caveman_text = color("38;5;172", "[CAVEMAN]")
        else:
            caveman_text = color("38;5;172", f"[CAVEMAN:{mode.upper()}]")
        parts.append(caveman_text)

    _ = sys.stdout.write(" ".join(parts))


if __name__ == "__main__":
    main()
