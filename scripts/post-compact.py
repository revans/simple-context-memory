#!/usr/bin/env python3
"""
post-compact.py — PostCompact hook
Fires after context compaction completes. Prompts the user to run /opening
to restore working context from the session document written before compaction.
"""

import os
import glob

sessions_dir = os.path.join(os.getcwd(), "docs", "sessions")
pattern = os.path.join(sessions_dir, "*.md")
files = sorted(glob.glob(pattern))

if files:
    latest = os.path.basename(files[-1])
    print(
        f"🔄 Compaction complete. Context has been compressed.\n"
        f"   A session document was written before compaction: {latest}\n"
        f"   Run /opening to restore your working context."
    )
else:
    print(
        "🔄 Compaction complete. Context has been compressed.\n"
        "   No session document found in docs/sessions/.\n"
        "   Run /closing now to capture what remains before continuing."
    )
