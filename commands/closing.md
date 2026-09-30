---
name: Closing
description: End-of-session archaeology document. Captures a summary, what was built and why, alternatives rejected with forward Do-Not constraints, key discoveries as Q→A pairs, implicit assumptions made, where the agent struggled, and open questions with next steps. Saved to docs/sessions/ with a timestamp filename so future sessions can continue without re-deriving context. Accepts an optional scope argument to limit capture to a specific topic, and an optional --fast flag to skip the transcript-based narrative audit.
color: purple
arguments:
  - scope (optional)
  - --fast (optional) — skip Step 6's independent transcript audit for a quicker close. Step 5's mechanical git check still runs either way.
---

# Session Closing

Write a detailed session archaeology document and save it to `docs/sessions/` in the current working directory.

---

## Step 0 — Determine scope and mode

Check the arguments for a `--fast` flag (anywhere in the argument string, in any position). If present, strip it out and set fast mode — Step 6's narrative audit will be skipped later. Fast mode trades away the audit's independent check for speed: Step 6 spawns a subagent that reads the full session transcript, which scales with session length and can take several minutes on a long session. Use `--fast` when you want a quick close and are willing to accept the narrative sections unaudited; leave it off for sessions where the reasoning is worth double-checking before it's the permanent record.

Whatever remains after stripping `--fast` is the `$scope` argument — check whether it's non-empty.

**No scope:** capture the full session — everything built, decided, explored, and rejected across the entire conversation.

**Scope provided:** the value of `$scope` is the topic focus. Only capture conversation content that relates to that topic. Treat the rest of the session as background — do not include it in any section. The slug is derived from `$scope` (kebab-case, 2–4 words), not inferred from the full session.

Carry the scope (or "full session" if none) and the fast-mode flag forward — the scope determines what content is eligible for each section in Step 4; fast mode determines whether Step 6 runs at all.

---

## Step 1 — Get the timestamp, session ID, and find the previous session

Run:
```bash
date +"%Y-%m-%d-%H%M"
```

This is the timestamp for the filename.

Then run:
```bash
echo "$CLAUDE_CODE_SESSION_ID"
```

This is the current session's resumable ID — the same ID `claude --resume <id>` takes to reopen this exact conversation later. If it's empty (running outside the Claude Code CLI, or the variable is unavailable), record `session_id: null` in the frontmatter instead — do not fabricate one.

Then check if `docs/sessions/` already exists and find the most recently modified session file:
```bash
ls -t docs/sessions/*.md 2>/dev/null | head -1
```

Note that filename — it becomes `previous_session` in the frontmatter.

---

## Step 2 — Derive the slug and one-line description

If a scope argument was provided, derive the slug directly from `$scope` (kebab-case, 2–4 words).

If no argument, infer the slug from the session content. Examples: `agent-studio-toolchain`, `hero-skill-extraction-intents`, `hub-session-lifecycle`.

The filename is: `{{timestamp}}-{{slug}}.md`

Also write a one-line `session_description` (a single plain sentence, commit-subject length — under ~100 characters). This is distinct from the `## Summary` section in the body: the description is for scanning many sessions at a glance (e.g. by `/reopen`) without parsing markdown; the Summary section is the fuller 2-3 sentence orientation for a human or agent reading this one document.

---

## Step 3 — Create the directory if needed

```bash
mkdir -p docs/sessions
```

---

## Step 4 — Write the document

Before populating any section, apply this memory discipline: **recall what you believed at the start of this session, then write a memory only when the outcome contradicts it.** When something does contradict, write the corrected belief, not the event: not "I tried X and Y happened" but "X does not cause Y" or "actually Z is how this works." This keeps the document from becoming an event log and keeps it useful as a belief system a future session can actually build on.

Before writing, reason through the session using SBAR-C as a completeness check:

- **Situation** — what is the current state? What happened this session?
- **Background** — what led to the key decisions? What made the alternatives worse?
- **Assessment** — what did we figure out that we didn't know before?
- **Recommendation** — what needs to happen next? What's unresolved or deferred?
- **Contingency** — what assumptions did we make that, if they change, would reopen a closed decision? Embed these as conditionals in Roads Not Taken: *Do not X because Y — unless Z, in which case reconsider.*

Two of these five surface a different kind of signal than the rest — not what was decided, but how reliable what was produced actually is. **Assessment** should surface struggle, not just discoveries: what took multiple attempts, what was genuinely ambiguous, what got produced with lower confidence than the rest. **Contingency** surfaces two related but distinct things — assumptions tied to a reversible decision (embed as a conditional in the Do Not line, as above) *and* standalone implicit assumptions that were never explicitly decided at all, just filled in silently (surface these in Assumptions Made below, even when no decision hangs on them).

This reasoning does not produce additional sections beyond the two named below. It surfaces content for the sections that follow.

The document must include all of the following sections. Do not skip any. If a section has nothing to report, say so explicitly rather than omitting it — "nothing deferred" is more useful than a missing section.

```markdown
---
project: {{name of current working directory / project}}
date: {{YYYY-MM-DD}}
time: {{HH:MM}}
working_directory: {{absolute path}}
previous_session: {{filename of previous session, or null}}
session_id: {{value of $CLAUDE_CODE_SESSION_ID, or null}}
session_description: {{one-line plain-sentence description, distinct from Summary below}}
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

For each entry, ask: what would have to be true about the world for this to have been
the right call instead? That answer becomes the conditional.

End each entry with a bold constraint line stating the forward-binding rule:
**Do not [X] because [Y] — unless [Z], in which case reconsider.** This is what a
future session needs to see before it starts reasoning about the problem — a guard
rail, not just an explanation. If there is no realistic reversal condition, omit the
unless clause.

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

## Assumptions Made

{{Implicit choices filled in without explicit deliberation — distinct from Roads Not Taken,
which covers alternatives that were actually named and considered before one was rejected.
An assumption is a gap that got filled one way without anyone consciously choosing it: a
default value picked, a scope boundary inferred, a format assumed compatible, a dependency
assumed available. State each one plainly and note what would break if it turns out wrong.
This is what lets a future reader audit a choice nobody flagged as a choice.

If nothing was assumed beyond what's already explicit elsewhere in this document, say so.}}

## Where the Agent Struggled

{{Not a claim about the work — a confidence signal about it. Which specific parts of this
session's output took multiple attempts, hit genuine ambiguity, or were produced with lower
confidence than the rest, even though an answer was still delivered. Distinct from Key
Discoveries (settled learnings) and Open Questions (deferred items still to resolve) — this
flags where a future session or reviewer should apply extra scrutiny before building on top
of what's here, even though it isn't literally unresolved or unknown.

If nothing this session was genuinely difficult, say so.}}

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

## Agent Notes

{{Free-form. Anything you, the agent writing this document, think the next session should
know that doesn't fit the sections above: hunches, things that felt off, user preferences
you picked up, gotchas, places you're unsure this document is faithful, or advice to your
future self. Mark guesses as [uncertain]. Not audited in Step 6 — this is your own voice,
not a claim about the session. Omit this section only if you truly have nothing to add.}}

---
*Note: This document was written from conversation context. Sections marked [uncertain]
reflect areas where context compression may have affected recall accuracy.*
```

---

## Step 5 — Verify Files Changed against git (mechanical, no re-reasoning)

The "Files Changed" section is the one section in this document with independent ground truth — the working tree itself. Check the draft against it before anything else, and before any narrative auditing in Step 6.

```bash
git rev-parse --is-inside-work-tree 2>/dev/null
```

If this fails (not a git repo), skip this step and note in the document itself: "Files Changed could not be verified against git — no repository present."

If it succeeds, run:
```bash
git status --porcelain
git diff --stat HEAD 2>/dev/null
```

Cross-reference the actual touched files (staged, unstaged, and untracked) against the draft's "Files Changed" section:
- A file that was actually touched but is missing from the draft — add it.
- A file listed in the draft but not shown as touched by git — remove it, unless it changed outside this repo's working tree (e.g. files under `~/.claude/` synced by `init.sh`), in which case keep it but note it wasn't checked by this step.

This is arithmetic, not judgment — do not skip it because the draft "looks right." Looking right is exactly what an unverified claim does.

---

## Step 6 — Independent audit of Why We Did It This Way, Roads Not Taken, and Assumptions Made

Files Changed had a receipt to check against. These three sections don't — the only evidence that a decision was actually reasoned through, not just written to sound reasoned, is the conversation itself. Re-reading your own draft against your own memory of the conversation is not an audit — it's the same reasoning checking its own homework. Use a subagent instead, but a subagent starts blank; it does not inherit this conversation's history. Point it at the actual record on disk instead:

```
~/.claude/projects/{{cwd with every "/" replaced by "-"}}/{{session_id}}.jsonl
```

`{{cwd}}` is the absolute working directory from Step 1; `{{session_id}}` is the value already recorded in this document's frontmatter.

**Skip this step** if fast mode (`--fast`) was requested, if `session_id` is null, or if the transcript file doesn't exist at that path. Note which reason applies directly in the document — "Narrative sections unaudited — fast mode requested" or "Narrative sections unaudited — no session transcript available" — rather than silently skipping. Do not run a lighter version of the audit yourself as a compromise for fast mode: a partial self-check is exactly the "same reasoning checking its own homework" problem this step exists to avoid. Fast mode means no audit, not a cheaper one.

Otherwise, spawn a subagent (Agent tool) with this self-contained prompt:

> You are auditing a session document against the raw conversation it claims to summarize. You were not part of this conversation — read the transcript yourself, don't take the document's word for anything.
>
> **Transcript file:** `{{absolute path to the .jsonl file}}` — a JSONL conversation log, one JSON object per line. User and assistant turns carry a `message.content` array of text / tool_use / tool_result blocks. Read it directly. If it's large, you don't need every tool result verbatim — focus on user turns and assistant reasoning/text, and grep for specific keywords if you need to confirm one claim rather than reading front to back.
>
> **Claims to check** (from the draft's Why We Did It This Way, Roads Not Taken, and Assumptions Made sections):
> {{paste all three sections verbatim}}
>
> For each individual claim, decide: is there direct evidence in the transcript that this was actually said, decided, or reasoned through — not merely plausible, but actually present? Return the claims you could NOT find direct support for, each with a one-line reason.

Take the subagent's list and, for each unsupported claim, either:
- append `[unverified — not directly supported by the session transcript]` in place, or
- if it reads more like a default that was quietly filled in than an alternative that was actually considered and rejected, move it out of Roads Not Taken and into Assumptions Made — that's what that section is for.

Do not delete a flagged claim. An unverified claim is still information — its confidence just dropped, and now a future reader can see that instead of inheriting false certainty.

---

## Step 7 — Compress uncertain sections honestly

This command runs at the end of a potentially long session. The harness compresses long conversations. If you are uncertain about the exact reasoning behind something — especially from early in the session — say so in the relevant section rather than reconstructing it confidently. Append `[uncertain]` to any bullet or paragraph where memory may be incomplete.

This is a different failure mode than Step 6: Step 6 catches claims the transcript flatly doesn't support. This step covers claims you're personally unsure about even though a transcript exists and might support them — you just don't have confidence it does.

---

## Step 8 — Confirm

After writing the file, output:
- The full file path
- The word count
- The previous session filename (if any), so the user can see the chain
- The session_id recorded (or a note that it was unavailable), so the user knows whether `/reopen` can jump back into this exact conversation later
- Whether Files Changed was verified against git, and how many corrections Step 5 made (or why it was skipped)
- Whether the narrative audit ran, and how many claims Step 6 flagged as unverified (or why it was skipped)
