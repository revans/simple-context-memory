---
name: Report
description: Reads all session documents and produces a project state report — consolidated open deferrals and Do Not constraints, each linked back to their source session. Saves to docs/reports/.
color: blue
---

# Session Report

Read all session archaeology documents from `docs/sessions/` and produce a project state report. Save it to `docs/reports/`.

---

## Step 1 — Find all session files

```bash
ls docs/sessions/*.md 2>/dev/null | sort
```

If `docs/sessions/` does not exist or has no `.md` files, say so and stop.

Sort order is alphabetical, which is chronological — session filenames begin with `YYYY-MM-DD-HHMM`.

---

## Step 2 — Get the timestamp and create the output directory

```bash
date +"%Y-%m-%d-%H%M"
mkdir -p docs/reports
```

---

## Step 3 — Delegate to a subagent

Always delegate — this reads every session file. Do not read the sessions yourself.

Spawn a subagent using the Agent tool with a self-contained prompt that includes:

1. The list of absolute file paths (oldest to newest)
2. The synthesis instructions from Step 4, verbatim

**Subagent prompt template:**

> You are a project state synthesizer. Your job is to read session archaeology documents and produce a project state report. Do not ask clarifying questions. Return only the finished report body — no frontmatter, no file headers. The orchestrating agent writes the file.
>
> **Files to read (oldest to newest):**
> {{list of absolute file paths}}
>
> {{Paste the synthesis instructions from Step 4 here, verbatim}}
>
> After producing the report body, output one confirmation line:
> _Report synthesized from N session(s). Spanning: `{{oldest filename}}` → `{{newest filename}}`._

---

## Step 4 — Synthesis instructions

### How to determine if a deferral is still open

Read all sessions in chronological order. Collect every item from **Open Questions & Next Steps** sections across all sessions.

For each collected item, scan every *later* session's **What We Did**, **Key Discoveries**, and **Why We Did It This Way** to check whether it was resolved. An item is resolved if a later session explicitly addresses it — not merely mentions the topic. When uncertain, mark it as still open.

An item is still open if:
- No later session references it
- A later session's **Open Questions & Next Steps** carries it forward unchanged

An item is resolved if:
- A later session's **What We Did** describes completing or deciding it
- A later session's **Key Discoveries** answers the question
- A later session explicitly notes it was closed

### What to produce

Two sections. For each item, include a markdown link to the source session using a relative path from `docs/reports/` — e.g. `[2026-05-19-stripe-webhook](../sessions/2026-05-19-1531-stripe-webhook.md)`.

---

### Open Deferrals

Every item from **Open Questions & Next Steps** across all sessions that has not been resolved in a later session.

Group by theme if multiple items cluster naturally. Otherwise list chronologically, oldest first.

For each item:
- The deferral in plain language (1–2 sentences)
- Source link: `[session-slug](../sessions/filename.md)`

If there are no open deferrals, say so explicitly.

---

### Do Not Constraints

Every **Do not [X] because [Y]** constraint from **Roads Not Taken** across all sessions. Do not deduplicate constraints that address the same topic from different angles — list each one. If the same constraint recurs across multiple sessions, list it once and note the recurrence.

For each constraint:
- The constraint (verbatim or paraphrased if the original was verbose)
- Source link: `[session-slug](../sessions/filename.md)`

If there are no Do Not constraints, say so explicitly.

---

## Step 5 — Write the report file

Write the report to `docs/reports/{{timestamp}}-report.md`:

```markdown
---
project: {{name of current working directory / project}}
date: {{YYYY-MM-DD}}
time: {{HH:MM}}
sessions_covered: {{N}}
spanning: {{oldest session filename}} → {{newest session filename}}
---

# Project Report: {{YYYY-MM-DD}}

{{subagent output here}}
```

---

## Step 6 — Confirm

Output:
- The full file path written
- Number of sessions read
- Number of open deferrals found
- Number of Do Not constraints found
