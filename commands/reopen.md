---
name: Reopen
description: Find a past Claude Code session by description or slug across docs/sessions/*.md and surface the `claude --resume <id>` command to jump back into that exact conversation.
color: purple
arguments:
  - query (optional) — keywords to search for; omit to list recent sessions instead
---

# Session Reopen

Find a specific past session — not a summary of it, the literal conversation, byte-for-byte — and hand back the command that reopens it. This command never resumes anything itself; it only looks up the ID and prints the command for the user to run.

---

## Step 0 — Why this can't be automatic

A slash command runs inside the current process. Reopening a session means starting a *new* `claude --resume <id>` process — this command cannot do that on your own behalf, the same way a running program can't relaunch itself as a different program while keeping control. Your job is only to find the right ID and print the ready-to-run command. Say this to the user if there's any ambiguity about why you didn't "just do it."

---

## Step 1 — Determine mode

Check whether a `$query` argument was provided.

**No argument (list mode):** show the 10 most recently modified files from `ls -t docs/sessions/*.md`.

**Argument provided (search mode):** pull 2–4 keywords from `$query`. Cast wide — better to surface a false positive than miss the right session. Search with:
```bash
grep -liE "<keyword1>|<keyword2>|<keyword3>" docs/sessions/*.md
```
If that returns nothing, fall back to listing all files (list mode) rather than reporting a dead end.

---

## Step 2 — Extract frontmatter for each candidate

For each candidate file, read its frontmatter and pull out:
- `session_id`
- `session_description`
- `date` / `time`
- the filename itself (slug)

If a file predates this feature and has no `session_id` field, treat it as `session_id: null` — it's a legacy doc that can be read but not resumed.

---

## Step 3 — Group by session_id, not by file

Multiple docs can share the same `session_id` — that's expected, it means the underlying conversation was checkpointed with `/closing` more than once. Group candidates by `session_id` before presenting anything, so the same conversation isn't shown twice as if it were two different sessions.

For each distinct `session_id` group, the description to show is the most recent doc's `session_description` (it reflects the latest checkpoint of that conversation).

---

## Step 4 — Resolve to exactly one session

- **Exactly one distinct `session_id` matched:** skip straight to Step 5.
- **Multiple distinct `session_id`s matched:** use `AskUserQuestion` to disambiguate. List each candidate as one option — label with the date and `session_description`, and in the description field mention how many checkpoint docs roll into it if more than one.
- **Zero matches, or the only matches have `session_id: null`:** say so plainly. If everything found is `null`, explain these are pre-dated docs written before session-ID capture existed — there's nothing to resume, only the written narrative to read (suggest `/opening file <path>` for that).

---

## Step 5 — Output the resume command

Once resolved to one session_id, output clearly, on its own line so it's easy to copy:

```
claude --resume {{session_id}} --dangerously-skip-permissions
```

Tell the user to run it themselves in a terminal — or, if they're invoking `/reopen` from inside another active session and want to run it immediately, remind them they can type `! claude --resume {{session_id}} --dangerously-skip-permissions` to execute it directly in this session's shell.

Also state which doc(s) that session_id came from (filename(s)) and its `session_description`, so the user can confirm it's the conversation they meant before running it.
