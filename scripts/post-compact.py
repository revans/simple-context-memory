#!/usr/bin/env python3
"""
post-compact.py — PostCompact hook
Fires after context compaction completes. Prompts the user to run /opening
to restore working context from the session document written before compaction.
"""

import json
import os
import glob
import sys
import time

# PreCompact only *asks* the model (via injected text) to write a session
# doc — it can't force a tool call, and higher-priority harness instructions
# (e.g. a "no tool calls" compaction directive) can silently override that
# ask. So the mere presence of a file in docs/sessions/ does not mean one
# was written for *this* compaction — it could be stale from days/weeks ago.
# Only trust it if its mtime falls inside the compaction window.
RECENT_WRITE_WINDOW_SECONDS = 300

hook_input = {}
try:
    hook_input = json.load(sys.stdin)
except (json.JSONDecodeError, ValueError):
    pass

# Use cwd from the hook payload — os.getcwd() reflects the hook process's working
# directory, which may not be the project root for global hooks in ~/.claude/settings.json.
project_dir = hook_input.get("cwd") or os.getcwd()
sessions_dir = os.path.join(project_dir, "docs", "sessions")
pattern = os.path.join(sessions_dir, "*.md")
files = sorted(glob.glob(pattern))

latest_path = files[-1] if files else None
wrote_this_cycle = (
    latest_path is not None
    and (time.time() - os.path.getmtime(latest_path)) <= RECENT_WRITE_WINDOW_SECONDS
)

if wrote_this_cycle:
    latest = os.path.basename(latest_path)
    print(
        f"🔄 Compaction complete. Context has been compressed.\n"
        f"   A session document was written before compaction: {latest}\n"
        f"   Run /opening to restore your working context."
    )
elif latest_path:
    latest = os.path.basename(latest_path)
    print(
        f"🔄 Compaction complete. Context has been compressed.\n"
        f"   ⚠️  No session document appears to have been written for this compaction —\n"
        f"   the most recent file (itself possibly stale) is: {latest}\n"
        f"   The context that was just compacted may not be captured anywhere.\n"
        f"   Consider writing a session doc from memory now, or run /closing."
    )
else:
    print(
        "🔄 Compaction complete. Context has been compressed.\n"
        "   No session document found in docs/sessions/.\n"
        "   Run /closing now to capture what remains before continuing."
    )
