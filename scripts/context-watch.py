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


def find_current_session_jsonl():
    """Find the most recently modified session JSONL across all projects.

    Assumes the most recently active JSONL belongs to the current session.
    If you run multiple Claude Code sessions simultaneously, this may return
    a count from a different session — in that case, ignore the warning and
    run /closing manually when the session feels long.
    """
    pattern = os.path.expanduser("~/.claude/projects/*/*.jsonl")
    files = glob.glob(pattern)
    if not files:
        return None
    return max(files, key=os.path.getmtime)


def get_last_input_tokens(path):
    """Read the JSONL backwards to find the last assistant message with usage data."""
    try:
        with open(path, "rb") as f:
            # Read chunks from the end to avoid loading the whole file
            f.seek(0, 2)
            size = f.tell()
            chunk_size = min(65536, size)
            pos = size

            buf = b""
            while pos > 0:
                pos = max(0, pos - chunk_size)
                f.seek(pos)
                buf = f.read(chunk_size) + buf
                lines = buf.split(b"\n")

                # Check lines from the end
                for line in reversed(lines):
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

                if pos == 0:
                    break

    except (OSError, IOError):
        pass

    return None


def main():
    path = find_current_session_jsonl()
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
