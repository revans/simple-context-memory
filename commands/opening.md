---
name: Opening
description: Start-of-session context loader. Reads session archaeology documents from docs/sessions/ to orient the agent for the current session.
color: green
arguments:
  - mode (none) | 2 | <N> | today | yesterday | last-week | all | summary | search <question> | file <path>
---

# Session Opening

Orient yourself by reading session archaeology documents from `docs/sessions/` in the current working directory. Parse the argument to determine mode, then proceed accordingly.

---

## Step 1 — Determine the mode

The argument (if any) determines behavior:

| Argument | Mode | File selection |
|----------|------|---------------|
| _(none)_ | **last-1** | Most recent 1 file |
| `2` | **last-2** | Most recent 2 files |
| `3` or higher | **last-N** | Most recent N files |
| `today` | **today** | Files with today's date prefix |
| `yesterday` | **yesterday** | Files with yesterday's date prefix |
| `last-week` | **last-week** | Files from the past 7 days (not including today) |
| `all` | **all** | Every file |
| `summary` | **arc** | Every file, narrative output |
| `search <question>` | **search** | Grep-narrowed candidates, then subagent answers the question |
| `file <path>` or bare path | **file** | The single specified file (absolute or relative path) |

**Path detection:** if the argument is not one of the named keywords above and it either contains `/` or ends with `.md`, treat it as **file** mode automatically — no `file` prefix required.

---

## Step 2 — Find the session files for the requested mode

All session files live in `docs/sessions/` and follow the naming convention `YYYY-MM-DD-HHMM-slug.md`.

If `docs/sessions/` does not exist or has no `.md` files, say so and stop.

### For last-1, last-2, last-N, all:

```bash
ls -t docs/sessions/*.md 2>/dev/null
```

Take the first 1, 2, N, or all files from this list.

### For today:

```bash
ls docs/sessions/$(date +%Y-%m-%d)-*.md 2>/dev/null | sort
```

### For yesterday:

```bash
ls docs/sessions/$(python3 -c "from datetime import date, timedelta; print(date.today() - timedelta(days=1))")-*.md 2>/dev/null | sort
```

### For last-week:

Generate the 7 date prefixes for the past 7 days (not including today) and filter matching files:

```bash
python3 -c "
from datetime import date, timedelta
for i in range(1, 8):
    print(date.today() - timedelta(days=i))
" | xargs -I{} sh -c 'ls docs/sessions/{}-*.md 2>/dev/null' | sort
```

### For arc / summary:

```bash
ls docs/sessions/*.md 2>/dev/null | sort
```

(Oldest-to-newest for coherent narrative.)

### For file:

Resolve the path:
- If the argument starts with `file `, strip that prefix to get the path.
- Otherwise use the argument as-is.
- If the path is relative, resolve it from the current working directory.
- If the file does not exist at that path, also try `docs/sessions/<path>` in case only the filename or slug was given.

If the file cannot be found, say so and stop.

---

### For search:

Extract the query — everything after `search` in the argument. Then grep all session docs for keywords from the query to find candidate files:

```bash
grep -rilE "<keyword1>|<keyword2>|<keyword3>" docs/sessions/ 2>/dev/null
```

Pull 2–4 keywords from the query. Cast wide — better to read a false-positive than to miss the relevant session. If grep returns no candidates, fall back to all session docs. Always delegate search to a subagent regardless of candidate count.

---

## Step 3 — Determine context strategy and execute

Count the files selected in Step 2. Then apply this rule:

| File count | Strategy |
|------------|----------|
| 1–2 files | Read inline in this conversation |
| 3+ files | Delegate to a subagent |

This applies regardless of which mode was used. `today` with one session reads inline. `yesterday` with four sessions delegates. The count drives the decision, not the mode name.

**Exception: `search` always delegates**, even if only one candidate file is found. The subagent is the right unit for question-answering — it reads the candidates and returns a precise answer, keeping the main context clean.

**Exception: `file` always reads inline**, regardless of file size. The point of naming a specific file is to load it directly into the current context window — no subagent indirection.

---

### Inline (1–2 files): Read directly

Read the files in this conversation. Then proceed to Step 4.

---

### Delegated (3+ files): Spawn a subagent

Do not read the session files yourself. Spawn a subagent using the Agent tool with a self-contained prompt that includes:

1. The list of absolute file paths to read (oldest to newest)
2. Which mode was requested
3. The relevant synthesis instructions from Step 4, verbatim

The subagent reads all documents and returns the finished synthesis. You present that to the user. The raw document content never enters your context window.

**Subagent prompt template:**

> You are a session context synthesizer. Your only job is to read the session archaeology documents listed below and produce a finished brief or narrative as instructed. Do not ask clarifying questions. Return only the finished output.
>
> **Files to read (oldest to newest):**
> {{list of absolute file paths}}
>
> **Mode:** {{mode name}}
>
> **Query:** {{the extracted query text — only present when mode is search}}
>
> {{Paste the relevant synthesis instructions from Step 4 here, verbatim}}
>
> After the synthesis, output one confirmation line:
> _Context loaded from N session(s). Spanning: `{{oldest filename}}` → `{{most recent filename}}`._

---

## Step 4 — Synthesis instructions

Use the correct instructions for the mode. These are also what you embed in the subagent prompt when delegating.

---

### file

Same structured brief as last-1. The document is a specific one you were directed to — treat it as the authoritative source for the current session context.

**Active state** — what this document describes: what was being built, decided, or explored.

**Live decisions** — design decisions recorded as settled. Include the "why" so you don't accidentally reverse them.

**Pending / deferred** — what was explicitly left open, flagged for next time, or half-decided.

**Live threads** — lines of thinking that were active but not concluded.

---

### last-1 and last-2 (and date modes with 1–2 results)

Present a structured brief — not a raw dump. Include:

**Active state** — what the project currently is, what was being built or decided at the end of the last session.

**Live decisions** — design decisions that are settled and should not be re-litigated. Include the "why" so you don't accidentally reverse them.

**Pending / deferred** — what was explicitly left open, flagged for next time, or half-decided.

**Live threads** — lines of thinking that were active but not concluded.

If reading two sessions, synthesize across both — what changed, what got resolved, what was added to the pending list.

---

### last-N (3+), today, yesterday, last-week, all (when 3+ files)

Same structure as above, but organize by what's **still live** versus what's **resolved or shipped**. Resolved items get one line. Live items get the full treatment — state, why the decision was made, what's open.

For date-range modes (today, yesterday, last-week), group by session at the top — one line per session showing the slug and what it covered — then the synthesized brief below. This gives a "what happened in this period" overview before the detail.

---

### search

Answer the question directly from the session record. Do not summarize unrelated context.

**The question:** the query stated in the **Query** field above this synthesis block.

**Direct answer** — what was decided, chosen, or concluded, in 2–4 sentences. Be specific: name the decision, name the reason.

**The reasoning** — pull the exact reasoning from the session doc. Quote the relevant section if it's tight enough. Paraphrase if the doc is verbose. The goal is: the reader understands *why*, not just *what*.

**What was rejected** — if the session recorded alternatives that were considered and set aside, list them with their reasons. This is often the most useful part — it explains why the obvious alternative wasn't chosen.

**Source** — cite the session file(s) the answer came from: filename and section (e.g., `2026-05-20-0748-org-shape-discovery.md` → "Roads Not Taken"). If the answer spans multiple sessions, cite all of them.

If the question cannot be answered from the session record, say so plainly. Do not speculate or reconstruct reasoning that isn't written down.

---

### arc / summary

A narrative, not a brief. Plain prose, oldest-to-newest. Answer: **what is this project, how did it get to its current shape, and what is the unresolved frontier?**

**Origin** — what the project started as and why.

**Key forks** — the 2–4 decisions that most changed the direction. For each: what the alternatives were, what was chosen, and why it mattered.

**Roads not taken** — significant things deliberately rejected across the full history. These are the invisible guard rails — constraints that won't appear in the code.

**Current shape** — what the system looks like now, as of the most recent session.

**The frontier** — what's pending, what's half-decided, what threads are live. This is where the next session picks up.

Write it so someone who has never seen the project before could understand both the system and the reasoning behind its current form.

---

## Step 5 — Confirm

After presenting the brief or narrative, output one line:

> _Context loaded from N session(s). Spanning: `{{oldest filename}}` → `{{most recent filename}}`._

For single-session loads (including `file` mode), just: _Context loaded from 1 session: `{{filename}}`._

For search mode: _Searched N session(s). Answer sourced from: `{{filename(s)}}`._

For delegated modes, the subagent outputs this line — present it as-is.
