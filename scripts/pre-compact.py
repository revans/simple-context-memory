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
For each entry, ask: what would have to be true for this to have been the right call?
End each entry with: **Do not [X] because [Y] — unless [Z], in which case reconsider.**
If there is no realistic reversal condition, omit the unless clause.}}

## Key Discoveries
{{Questions answered this session. Format as question → answer pairs.
Root causes traced, misconceptions corrected, empirical findings.}}

## Assumptions Made
{{Implicit choices filled in without explicit deliberation — distinct from Roads Not Taken, which covers alternatives that were actually named and rejected. A default picked, a scope boundary inferred, a dependency assumed available. State each plainly and note what would break if it's wrong. If nothing was assumed beyond what's explicit elsewhere, say so. Mark this section [unaudited] — it is not checked against the transcript.}}

## Where the Agent Struggled
{{A confidence signal, not a claim about the work. Which parts took multiple attempts, hit genuine ambiguity, or were produced with lower confidence than the rest, even though an answer was delivered. Tells a future session where to apply extra scrutiny. Be honest: "no issues" is only right if nothing was genuinely hard. Mark this section [unaudited] — it is self-reported and not checked against the transcript.}}

## Open Questions & Next Steps
{{What was deferred, left unresolved, or suggested but not acted on. Include:
- Unresolved questions or half-decisions
- Action items not tackled this session
- Suggestions raised but not followed up on}}

## Files Changed
{{List of files created or modified. For each: what changed + any constraint a future
session needs before touching it again.
- `path/to/file` — what changed. [Constraint: why this can't be safely reverted.]}}

## Agent Notes
{{Free-form. Anything you, the agent doing this compaction, think the next session should know that doesn't fit the sections above: hunches, things that felt off, user preferences you picked up, gotchas, where you're unsure the summary is faithful, or advice to your future self. Mark guesses as [uncertain]. Omit this section only if you truly have nothing to add.}}

---
*Note: Written under compaction pressure. Sections marked [uncertain] reflect incomplete recall.*

Write the file now. Compaction will proceed after.""")
