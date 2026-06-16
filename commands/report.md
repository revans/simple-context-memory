---
name: Report
description: Reads session documents and produces a project state report — consolidated open deferrals and Do Not constraints, each linked back to their source session. Always writes to docs/reports/report.md (single file, overwritten each run). Incremental by default — only reads sessions since the last report. Use /report full to force a complete rebuild.
color: blue
arguments:
  - full (optional) — force a complete rebuild from all sessions
---

# Session Report

Produce a project state report and write it to `docs/reports/report.md`. This file is always overwritten — there is only ever one report.

---

## Step 1 — Determine mode

Check whether `full` was passed as an argument.

**`/report full`** — read every session file. Ignore any existing report.

**`/report` (default)** — check for an existing report at `docs/reports/report.md`. If it exists, read its `last_session` frontmatter field to find the cursor. Only sessions with filenames that sort after the cursor are new — process only those. If no existing report is found, fall back to a full rebuild.

---

## Step 2 — Find session files

```bash
ls docs/sessions/*.md 2>/dev/null | sort
```

If `docs/sessions/` does not exist or has no `.md` files, say so and stop.

Filenames sort alphabetically, which is chronological — they begin with `YYYY-MM-DD-HHMM`.

**For incremental mode:** filter to only files whose name sorts after the `last_session` cursor from the existing report. If this yields zero new sessions, say "Report is already up to date" and stop.

**For full mode:** use all files.

---

## Step 3 — Get the timestamp and create the output directory

```bash
date +"%Y-%m-%d-%H%M"
mkdir -p docs/reports
```

---

## Step 4 — Delegate to a subagent

Always delegate — do not read session files yourself.

Spawn a subagent using the Agent tool with a self-contained prompt that includes:

1. The mode (full or incremental)
2. For incremental mode: the existing report content (paste it in full)
3. The list of new session file paths to read (oldest to newest)
4. The synthesis instructions from Step 5, verbatim

**Subagent prompt template:**

> You are a project state synthesizer. Your job is to produce a project state report. Do not ask clarifying questions. Return only the finished report body — no frontmatter. The orchestrating agent writes the file.
>
> **Mode:** {{full | incremental}}
>
> {{If incremental: "**Existing report (your baseline):**\n{{paste full content of docs/reports/report.md}}"}}
>
> **New session files to read (oldest to newest):**
> {{list of absolute file paths}}
>
> {{Paste the synthesis instructions from Step 5 here, verbatim}}
>
> After producing the report body, output one confirmation line:
> _Report covers N session(s). Last session: `{{filename of newest session processed}}`._

---

## Step 5 — Synthesis instructions

### Full rebuild

Read all sessions oldest to newest. Collect every item from **Open Questions & Next Steps** across all sessions. Cross-reference each item against later sessions to determine if it was resolved.

An item is **resolved** if a later session's **What We Did**, **Key Discoveries**, or **Why We Did It This Way** explicitly addresses it. When uncertain, mark it as still open.

An item is **still open** if no later session references it, or if a later session's **Open Questions & Next Steps** carries it forward.

Collect every **Do not [X] because [Y]** constraint from **Roads Not Taken** across all sessions.

Produce the two sections described below.

---

### Incremental update

You have an existing report (the baseline) and a set of new sessions to process.

**For Open Deferrals:**
1. Start with the existing report's Open Deferrals list as your working set
2. Read each new session in order
3. For each item in the working set, check whether the new session resolves it — remove it if resolved
4. Collect any new items from each new session's **Open Questions & Next Steps** and add them to the working set

**For Do Not Constraints:**
1. Start with the existing report's Do Not Constraints list
2. Collect any new constraints from each new session's **Roads Not Taken** and add them
3. If a new constraint is substantively identical to an existing one, keep it once and note it recurred

Produce the two sections described below with the fully updated content.

---

### What to produce

Two sections. For each item, include a markdown link to the source session using a relative path from `docs/reports/` — e.g. `[2026-05-19-stripe-webhook](../sessions/2026-05-19-1531-stripe-webhook.md)`.

---

### Open Deferrals

Every item from **Open Questions & Next Steps** across sessions that has not been resolved. Group by theme if multiple items cluster naturally. Otherwise list chronologically, oldest first.

For each item:
- The deferral in plain language (1–2 sentences)
- Source: `[session-slug](../sessions/filename.md)`

If there are no open deferrals, say so explicitly.

---

### Do Not Constraints

Every **Do not [X] because [Y]** constraint from **Roads Not Taken** across all sessions covered. If the same constraint recurs across sessions, list it once and note the recurrence.

For each constraint:
- The constraint (verbatim or paraphrased if verbose)
- Source: `[session-slug](../sessions/filename.md)`

If there are no Do Not constraints, say so explicitly.

---

## Step 6 — Write the report

Overwrite `docs/reports/report.md` with:

```markdown
---
project: {{name of current working directory / project}}
date: {{YYYY-MM-DD}}
time: {{HH:MM}}
sessions_covered: {{total N sessions this report reflects}}
spanning: {{oldest session filename}} → {{newest session filename}}
last_session: {{filename of newest session included}}
---

# Project Report

{{subagent output here}}
```

The `last_session` field is the cursor for the next incremental run.

---

## Step 7 — Confirm

Output:
- The file path written
- Mode used (full or incremental)
- Number of sessions processed this run
- Total sessions the report now reflects
- Number of open deferrals
- Number of Do Not constraints
