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

## Summary
{{2-3 sentences: what this session was about, the most important thing that changed, and what the next session picks up.}}

## What We Did
{{Specific things built, changed, or decided — file paths, function names, design choices}}

## Why We Did It This Way
{{Reasoning behind key decisions. What made the alternatives worse.}}

## Roads Not Taken
{{Everything considered and rejected. What was proposed, argued for, and set aside.
End each entry with: **Do not [X] because [Y].**}}

## Key Discoveries
{{Questions answered this session. Format as question → answer pairs.
Root causes traced, misconceptions corrected, empirical findings.}}

## Open Questions & Next Steps
{{What was deferred, left unresolved, or suggested but not acted on. Include:
- Unresolved questions or half-decisions
- Action items not tackled this session
- Suggestions raised but not followed up on}}

## Files Changed
{{List of files created or modified. For each: what changed + any constraint a future
session needs before touching it again.
- `path/to/file` — what changed. [Constraint: why this can't be safely reverted.]}}

---
*Note: Written under compaction pressure. Sections marked [uncertain] reflect incomplete recall.*

Write the file now. Compaction will proceed after.""")
