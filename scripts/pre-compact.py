#!/usr/bin/env python3
"""
pre-compact.py — PreCompact hook
Fires before context compaction. Instructs Claude to write a session
archaeology document before the context window is compressed.
"""

print("""⚠️  COMPACTION IMMINENT — write a session document before proceeding.

Context compaction is about to compress this conversation and discard the detailed reasoning. Write a session archaeology document to docs/sessions/ in the current working directory NOW, before compaction runs.

Steps:
1. Run: date +"%Y-%m-%d-%H%M" to get the timestamp
2. Infer a 2–4 word kebab-case slug from the session content
3. Run: mkdir -p docs/sessions
4. Write docs/sessions/{{timestamp}}-{{slug}}.md with this structure:

---
project: {{current directory name}}
date: {{YYYY-MM-DD}}
time: {{HH:MM}}
working_directory: {{absolute path}}
previous_session: {{most recent file from ls -t docs/sessions/*.md 2>/dev/null | head -1, or null}}
---

# Session: {{slug in title case}}

## What We Did
{{Specific things built, changed, or decided — file paths, function names, design choices}}

## Why We Did It This Way
{{Reasoning behind key decisions. What made the alternatives worse.}}

## Roads Not Taken
{{Everything considered and rejected. What was proposed, argued for, and set aside. Most important section.}}

## Threads We Pulled
{{Lines of thought explored even without a final decision}}

## Open Questions
{{What was explicitly deferred or left unresolved}}

## Files Changed
{{List of files created or modified, one line each}}

---
*Note: Written under compaction pressure. Sections marked [uncertain] reflect incomplete recall.*

Write the file now. Compaction will proceed after.""")
