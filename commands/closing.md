---
name: Closing
description: End-of-session archaeology document. Captures what was built, why, what was explored and rejected, and open questions. Saved to docs/sessions/ with a timestamp filename so future LLM sessions can trace how the codebase arrived at its current state. Accepts an optional scope argument to limit capture to a specific topic or decision from the session.
color: purple
arguments:
  - scope (optional)
---

# Session Closing

Write a detailed session archaeology document and save it to `docs/sessions/` in the current working directory.

---

## Step 0 — Determine scope

Check whether a `$scope` argument was provided.

**No argument:** capture the full session — everything built, decided, explored, and rejected across the entire conversation.

**Argument provided:** the value of `$scope` is the topic focus. Only capture conversation content that relates to that topic. Treat the rest of the session as background — do not include it in any section. The slug is derived from `$scope` (kebab-case, 2–4 words), not inferred from the full session.

Carry the scope (or "full session" if none) forward — it determines what content is eligible for each section in Step 4.

---

## Step 1 — Get the timestamp and find the previous session

Run:
```bash
date +"%Y-%m-%d-%H%M"
```

This is the timestamp for the filename.

Then check if `docs/sessions/` already exists and find the most recently modified session file:
```bash
ls -t docs/sessions/*.md 2>/dev/null | head -1
```

Note that filename — it becomes `previous_session` in the frontmatter.

---

## Step 2 — Derive the slug

If a scope argument was provided, derive the slug directly from `$scope` (kebab-case, 2–4 words).

If no argument, infer the slug from the session content. Examples: `agent-studio-toolchain`, `hero-skill-extraction-intents`, `hub-session-lifecycle`.

The filename is: `{{timestamp}}-{{slug}}.md`

---

## Step 3 — Create the directory if needed

```bash
mkdir -p docs/sessions
```

---

## Step 4 — Write the document

The document must include all of the following sections. Do not skip any. If a section has nothing to report, say so explicitly rather than omitting it — "nothing deferred" is more useful than a missing section.

```markdown
---
project: {{name of current working directory / project}}
date: {{YYYY-MM-DD}}
time: {{HH:MM}}
working_directory: {{absolute path}}
previous_session: {{filename of previous session, or null}}
---

# Session: {{slug in title case}}

## What We Did

{{Concrete list of what was built, changed, or decided. Be specific — file paths,
function names, design decisions. Not "we improved the flow" but "we rewrote
hero-skill-gen Step 4 to branch on extraction intent (perspective/framework/principles)
and assign the right tool to each."}}

## Why We Did It This Way

{{The reasoning behind the key decisions made this session. Not just what was chosen
but why the alternatives were worse. This is the section that prevents future sessions
from re-litigating settled questions.}}

## Roads Not Taken

{{Everything that was considered but deliberately rejected. This is the most important
section — it's what won't appear in the code or git history. Be specific about what
was proposed, what the argument for it was, and why it was set aside.

If nothing was rejected, say so. If you're uncertain whether something was raised and
rejected vs. never considered, say so.}}

## Threads We Pulled

{{Lines of thought that were explored during the session — even if they didn't produce
a final decision. Design questions discussed, analogies used to reason about the problem,
rabbit holes entered and exited. This is the thinking-out-loud record.}}

## Open Questions

{{What was explicitly deferred, left unresolved, or flagged as "talk about this next time."
Include anything the session ended without answering. If something is half-decided,
note which half is settled and which isn't.}}

## Files Changed

{{List of files created or modified this session, with one line on what changed in each.
Format:
- `path/to/file.md` — what changed
}}

---
*Note: This document was written from conversation context. Sections marked [uncertain]
reflect areas where context compression may have affected recall accuracy.*
```

---

## Step 5 — Compress uncertain sections honestly

This command runs at the end of a potentially long session. The harness compresses long conversations. If you are uncertain about the exact reasoning behind something — especially from early in the session — say so in the relevant section rather than reconstructing it confidently. Append `[uncertain]` to any bullet or paragraph where memory may be incomplete.

---

## Step 6 — Confirm

After writing the file, output:
- The full file path
- The word count
- The previous session filename (if any), so the user can see the chain
