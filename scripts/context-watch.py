#!/usr/bin/env python3
"""
context-watch.py — UserPromptSubmit hook
Reads the current session's JSONL to find the latest input token count.
Warns Claude when context is approaching the compaction threshold.
"""

import json
import os
import glob
import sys

CONTEXT_WINDOW = 200_000  # claude-sonnet-4-6

WARN_THRESHOLD  = 0.60   # 60% — first notice
URGENT_THRESHOLD = 0.75  # 75% — run /closing now


def find_current_session_jsonl(hook_input):
    # Prefer the transcript_path from the hook payload — exact and race-free.
    path = hook_input.get("transcript_path")
    if path and os.path.exists(path):
        return path
    # Fallback for environments where stdin payload is unavailable.
    # Warning: this picks the most-recently-modified JSONL across all projects,
    # which is wrong when multiple Claude sessions are active simultaneously.
    pattern = os.path.expanduser("~/.claude/projects/*/*.jsonl")
    files = glob.glob(pattern)
    if not files:
        return None
    return max(files, key=os.path.getmtime)


def get_last_input_tokens(path):
    try:
        with open(path, "rb") as f:
            f.seek(0, 2)
            pos = f.tell()
            tail = b""  # partial line carried from the more-recent chunk

            while pos > 0:
                read_size = min(65536, pos)
                pos -= read_size
                f.seek(pos)
                lines = (f.read(read_size) + tail).split(b"\n")
                tail = lines[0]  # may be partial — will be prepended on next iteration

                for line in reversed(lines[1:]):
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        d = json.loads(line)
                        if d.get("type") == "assistant":
                            usage = d.get("message", {}).get("usage", {})
                            if usage:
                                total = (
                                    usage.get("input_tokens", 0)
                                    + usage.get("cache_read_input_tokens", 0)
                                    + usage.get("cache_creation_input_tokens", 0)
                                )
                                if total > 0:
                                    return total
                    except (json.JSONDecodeError, KeyError):
                        continue

            # handle the very first line of the file
            if tail.strip():
                try:
                    d = json.loads(tail.strip())
                    if d.get("type") == "assistant":
                        usage = d.get("message", {}).get("usage", {})
                        if usage:
                            total = (
                                usage.get("input_tokens", 0)
                                + usage.get("cache_read_input_tokens", 0)
                                + usage.get("cache_creation_input_tokens", 0)
                            )
                            if total > 0:
                                return total
                except (json.JSONDecodeError, KeyError):
                    pass

    except (OSError, IOError):
        pass

    return None


def main():
    hook_input = {}
    try:
        hook_input = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        pass

    path = find_current_session_jsonl(hook_input)
    if not path:
        return

    tokens = get_last_input_tokens(path)
    if tokens is None:
        return

    pct = tokens / CONTEXT_WINDOW

    if pct >= URGENT_THRESHOLD:
        used_k = tokens // 1000
        print(
            f"⚠️  CONTEXT {int(pct * 100)}% FULL ({used_k}k / {CONTEXT_WINDOW // 1000}k tokens). "
            f"Run /closing NOW before compaction discards this session."
        )
    elif pct >= WARN_THRESHOLD:
        used_k = tokens // 1000
        print(
            f"📊 Context at {int(pct * 100)}% ({used_k}k / {CONTEXT_WINDOW // 1000}k tokens). "
            f"Consider running /closing soon to capture this session before compaction."
        )


if __name__ == "__main__":
    main()
