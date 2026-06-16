---
name: Closing
description: End-of-session archaeology document. Captures a summary, what was built and why, alternatives rejected with forward Do-Not constraints, key discoveries as Q→A pairs, and open questions with next steps. Saved to docs/sessions/ with a timestamp filename so future sessions can continue without re-deriving context. Accepts an optional scope argument to limit capture to a specific topic.
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

Before writing, reason through the session using SBAR-C as a completeness check:

- **Situation** — what is the current state? What happened this session?
- **Background** — what led to the key decisions? What made the alternatives worse?
- **Assessment** — what did we figure out that we didn't know before?
- **Recommendation** — what needs to happen next? What's unresolved or deferred?
- **Contingency** — what assumptions did we make that, if they change, would reopen a closed decision? Embed these as conditionals in Roads Not Taken: *Do not X because Y — unless Z, in which case reconsider.*

This reasoning does not produce additional sections. It surfaces content for the sections that follow.

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

## Summary

{{2-3 sentences. What was this session about, what is the most important thing that
changed, and what does the next session pick up? Write this as if it's the only thing
a future session might read — enough to orient immediately without reading anything else.}}

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

End each entry with a bold constraint line stating the forward-binding rule:
**Do not [X] because [Y].** This is what a future session needs to see before it
starts reasoning about the problem — a guard rail, not just an explanation.

If nothing was rejected, say so. If you're uncertain whether something was raised and
rejected vs. never considered, say so.}}

## Key Discoveries

{{Questions we didn't know the answer to at the start and figured out during the session.
Format as question → answer pairs. Include:
- Root causes traced ("why does X happen?" → "because Y")
- Empirical findings from testing or research
- Misconceptions corrected
- Anything a future session would need to know so it doesn't re-discover it

If nothing new was learned, say so.}}

## Open Questions & Next Steps

{{What was explicitly deferred, left unresolved, flagged as "talk about this next time,"
or suggested but not acted on. Include:
- Unresolved questions or half-decisions (note which half is settled)
- Action items identified but not tackled this session
- Suggestions raised (by either party) that weren't followed up on
- Review findings or potential issues noted but left for later

If nothing is pending, say so explicitly.}}

## Files Changed

{{List of files created or modified this session. For each file, record what changed
AND any constraint or intent a future session needs to know before touching it again —
specifically anything that looks like it could be safely reverted but shouldn't be.

Format:
- `path/to/file.md` — what changed. [Constraint if applicable: why this can't be undone / what to not change back.]
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
