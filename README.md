# simple-context-memory

Every time you start a Claude Code session, Claude wakes up with complete amnesia. Not "a little forgetful" — total blank slate. The project you've been building for three weeks, the decision you made on Thursday about why you're *not* using Redis, the half-finished design sitting in your last conversation — gone.

The reflex solution is to save everything. Dump the whole context into memory files. Write system prompts with the entire project history. But that's just moving noise. Claude can't tell which of the forty remembered facts is the one that matters right now, and you end up with a model that confidently re-litigates decisions you already settled.

What you actually need is what surgeons use during a shift handoff: not a diary, not a log — a **handoff note**. What did we do, why did we do it this way, what did we explicitly reject, and what's still open? That's it. Everything else is reconstruction that Claude can do from the code.

This repo gives you three Claude Code slash commands that implement exactly that system.

---

## Contents

- [The Commands](#the-commands)
- [Installation](#installation)
- [Usage](#usage)
  - [Starting a session](#starting-a-session)
  - [Ending a session](#ending-a-session)
  - [Generating a report](#generating-a-report)
  - [Hooks](#hooks)
- [The docs/ directory](#the-docs-directory)
- [Why this works](#why-this-works)

---

## The Commands

### `/opening` — Load context at the start of a session

Reads session archaeology documents from `docs/sessions/` and gives you a structured brief: what the project currently is, what decisions are settled, what's pending, and what threads were live when you left off.

Think of it like reading the previous surgeon's handoff note before you scrub in. You don't read the patient's full chart — you read what changed on the last shift and what's still unresolved.

### `/closing` — Write an archaeology document at the end of a session

Captures everything worth preserving from the session: what was built, why it was done this way (including the reasoning that prevents future sessions from re-litigating it), what was considered and rejected, and what's explicitly open. Saves it to `docs/sessions/` with a timestamp filename so the chain of sessions becomes traceable.

"Archaeology" is the right word here — the document records the *decisions*, not just the *artifacts*. The code already shows you what was built. Only this document shows you why the obvious alternative wasn't chosen.

### `/report` — Synthesize open work across all sessions

Reads every session document and produces a single project state report at `docs/reports/report.md`. Two sections: every still-open deferral (cross-referenced against later sessions to confirm it was never resolved), and every Do Not constraint accumulated across all Roads Not Taken. Each item links back to the session it came from.

Run it when sessions start accumulating. At 20+ sessions, loading the report plus the 2-3 most recent sessions gives you the same orientation as loading everything — with a fraction of the token cost.

Incremental by default — tracks which sessions it has already processed and only reads new ones on subsequent runs. Use `/report full` to rebuild from scratch.

---

## Installation

Claude Code custom commands (slash commands you define yourself) live in a `.claude/commands/` directory. You can install them at two levels:

**Project-level** — available only inside one project:
```
your-project/
└── .claude/
    └── commands/
        ├── opening.md
        └── closing.md
        └── report.md
```

**User-level (global)** — available in every project on your machine:
```
~/.claude/
└── commands/
    ├── opening.md
    ├── closing.md
    └── report.md
```

### Steps

Install globally — these commands are useful in every project, not just one.

1. Clone this repo:
   ```bash
   git clone https://github.com/revans/simple-context-memory
   ```

2. Run the install script:
   ```bash
   bash simple-context-memory/init.sh
   ```

   This copies the commands to `~/.claude/commands/`, the hook scripts to `~/.claude/hooks/`, and checks whether the hooks are wired in `~/.claude/settings.json` — printing the required JSON snippet if not.

   **Note:** existing files are overwritten without prompting. If you have customized your local copies of these commands, back them up before running.

   **Or install manually:**
   ```bash
   mkdir -p ~/.claude/commands
   cp simple-context-memory/commands/opening.md ~/.claude/commands/
   cp simple-context-memory/commands/closing.md ~/.claude/commands/
   cp simple-context-memory/commands/report.md ~/.claude/commands/
   ```

3. _(Optional, manual only)_ Install the compaction hooks:
   ```bash
   mkdir -p ~/.claude/hooks
   cp simple-context-memory/scripts/context-watch.py ~/.claude/hooks/context-watch.py
   cp simple-context-memory/scripts/pre-compact.py ~/.claude/hooks/pre-compact.py
   cp simple-context-memory/scripts/post-compact.py ~/.claude/hooks/post-compact.py
   ```
   See [Hooks](#hooks) for the `~/.claude/settings.json` configuration and what each script does.

4. That's it. Claude Code picks up `.md` files in `commands/` directories automatically — no config, no restart.

If you only want them in a single project instead:
```bash
mkdir -p your-project/.claude/commands
cp simple-context-memory/commands/opening.md your-project/.claude/commands/
cp simple-context-memory/commands/closing.md your-project/.claude/commands/
cp simple-context-memory/commands/report.md your-project/.claude/commands/
```

---

## Usage

### Starting a session

At the beginning of any Claude Code session, run:

```
/opening
```

Claude reads the most recent session file from `docs/sessions/` and gives you a structured brief. If this is the first session, it tells you so.

**Modes** — you can pass an argument to control how far back to look:

| Command | What it loads |
|---|---|
| `/opening` | Last session (default) |
| `/opening 2` | Last 2 sessions |
| `/opening today` | All sessions from today |
| `/opening yesterday` | All sessions from yesterday |
| `/opening last-week` | Sessions from the past 7 days |
| `/opening all` | Every session — full arc |
| `/opening summary` | Every session, as a narrative ("how did we get here?") |
| `/opening search <question>` | Searches session history to answer a specific question |
| `/opening file docs/sessions/2026-05-20-0748-slug.md` | Loads a specific session file |

The `summary` mode is the one you want after a long break — it tells the story of how the project arrived at its current shape. The `search` mode is useful when you remember something was decided but not when: `/opening search why did we drop the webhook approach`.

**Subagents for large loads** — when a mode returns 3 or more session files, `/opening` delegates to a subagent rather than reading them directly. Think of a subagent like a research assistant you send to the library: they read all the files, compile the answer, and hand you a summary — without any of that raw content ever entering your current context window. Modes that return 1–2 files load inline because the volume is small enough that it doesn't matter. `search` always delegates regardless of file count — question-answering is exactly the kind of synthesis a subagent handles well.

### Ending a session

Before you close Claude Code — or before the context window fills up — run:

```
/closing
```

**Don't wait until the end.** Claude Code compacts the context window automatically when it gets full, and compaction is lossy — it summarizes rather than preserves. Once compaction happens, the fine-grained reasoning about *why* decisions were made is gone. Run `/closing` before that happens.

Think of it like saving a document: you don't wait until your computer crashes. If the session has been long, run `/closing` while the context is still intact, then keep going.

#### Hooks

Three scripts in `scripts/` work together to automate compaction protection:

| Script | Hook type | What it does |
|---|---|---|
| `context-watch.py` | `UserPromptSubmit` | Warns at 60% and 75% context — early notice to run `/closing` manually |
| `pre-compact.py` | `PreCompact` | Safety net: instructs Claude to write a session document immediately before compaction runs |
| `post-compact.py` | `PostCompact` | After compaction, tells you which session file was written and prompts you to run `/opening` |

The three work as a layered defence. `context-watch.py` gives you time to act. `pre-compact.py` acts automatically if you don't. `post-compact.py` reorients you after the context is compressed.

Copy the scripts to `~/.claude/hooks/` and wire them up in `~/.claude/settings.json`:

```bash
mkdir -p ~/.claude/hooks
cp simple-context-memory/scripts/context-watch.py ~/.claude/hooks/context-watch.py
cp simple-context-memory/scripts/pre-compact.py ~/.claude/hooks/pre-compact.py
cp simple-context-memory/scripts/post-compact.py ~/.claude/hooks/post-compact.py
```

```json
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "python3 ~/.claude/hooks/context-watch.py"
          }
        ]
      }
    ],
    "PreCompact": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "python3 ~/.claude/hooks/pre-compact.py"
          }
        ]
      }
    ],
    "PostCompact": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "python3 ~/.claude/hooks/post-compact.py"
          }
        ]
      }
    ]
  }
}
```

**`context-watch.py`** reads `transcript_path` from the hook's stdin payload to identify the exact JSONL for the current session, then parses it backwards for the last assistant `usage` block, summing `input_tokens`, `cache_read_input_tokens`, and `cache_creation_input_tokens`. The context window is hardcoded to `200_000` (claude-sonnet-4-6) — update the `CONTEXT_WINDOW` constant at the top of the file if you're running a different model.

**`pre-compact.py`** prints the full session document format as an instruction. Claude writes the file before compaction proceeds.

**`post-compact.py`** reads `cwd` from the hook's stdin payload to locate the correct project directory, then checks `docs/sessions/` for the most recent file. If one exists, it names it and tells you to run `/opening`. If not, it tells you to run `/closing` immediately to capture what remains.

### What /closing writes

Claude writes a session document to `docs/sessions/` with a timestamp filename. The document covers seven sections:

- **Summary** — 2-3 sentences: what the session was about, the most important change, and what the next session picks up. Written to orient in ten seconds without reading anything else.
- **What We Did** — specific things built or decided (file paths, function names, design choices)
- **Why We Did It This Way** — the reasoning, so future sessions don't re-litigate it
- **Roads Not Taken** — what was proposed and rejected, and why. Each entry ends with a bold **Do not [X] because [Y]** constraint — the guard rail a future session sees before it starts reasoning about the problem
- **Key Discoveries** — questions answered during the session, formatted as question → answer pairs. Root causes traced, misconceptions corrected, empirical findings. What a future session needs to know so it doesn't re-discover it
- **Open Questions & Next Steps** — what was deferred, left unresolved, or suggested but not acted on. Includes action items, half-decisions, and review findings noted for later
- **Files Changed** — what changed and where, plus any constraint a future session needs before touching that file again

#### Example output

```markdown
---
project: billing-api
date: 2026-05-19
time: 14:32
working_directory: /home/dev/projects/billing-api
previous_session: 2026-05-16-0914-stripe-webhook-setup.md
---

# Session: Drop Idempotency Table

## Summary

Removed the local idempotency table and switched to Stripe's native idempotency key
support. The table was duplicating protection Stripe already provides for free. Next
session: decide whether to log the Stripe idempotency keys we send for audit purposes.

## What We Did

- Removed the `idempotency_keys` table and `IdempotencyKey` model entirely
- Switched to Stripe's built-in idempotency key header (`Idempotency-Key`) on all
  POST requests to Stripe — passed directly from the incoming webhook payload's
  `stripe_event_id`
- Updated `app/services/payment_processor.rb` to pass the key on charge creation
- Removed the `20260518_create_idempotency_keys.rb` migration (rolled back before drop)

## Why We Did It This Way

We were maintaining a local idempotency table to prevent double-charging on retried
webhooks. Stripe already does this natively — passing the same `Idempotency-Key`
header on a Stripe API call returns the original response without re-executing the
charge. Our table was duplicating protection Stripe provides for free and adding a
write on every payment path. Deleting it was the right call.

## Roads Not Taken

**Redis-backed idempotency store** — proposed as a lighter alternative to Postgres.
Rejected: still solving a problem Stripe already solves, and adds an infrastructure
dependency for no gain. **Do not introduce a local idempotency store of any kind —
Stripe's native support covers all current payment paths.**

**Keeping the table for non-Stripe operations** — we only have one payment path right
now, so this was over-engineering for a hypothetical. If a second payment provider is
ever added, the table can be reintroduced then.

## Key Discoveries

**Does Stripe's idempotency window cover our retry policy?**
→ Yes. Stripe's window is 24 hours; our retry policy retries within 6 hours. Safe.
Would need revisiting if the retry window ever expands past 24 hours.

**What does Stripe actually do when it receives a duplicate idempotency key?**
→ Returns the original response without re-executing the charge. No side effects.
This is the core reason the local table was redundant.

## Open Questions & Next Steps

- Do we want to log the `Idempotency-Key` values we send to Stripe for audit purposes,
  or is Stripe's dashboard sufficient? Deferred — not a blocker for the current release.
- No action items outstanding.

## Files Changed

- `app/services/payment_processor.rb` — added `idempotency_key:` param to Stripe charge call. [Constraint: key must be the incoming `stripe_event_id`, not a generated UUID — ensures replay safety.]
- `app/models/idempotency_key.rb` — deleted
- `db/migrate/20260518_create_idempotency_keys.rb` — deleted
- `spec/services/payment_processor_spec.rb` — removed idempotency table fixtures
```

Notice what this document does that the code and git history don't: the Do Not constraint in Roads Not Taken tells a future session not to reintroduce a local store before it even starts thinking about the problem. The Key Discoveries section records that Stripe's 24-hour window was explicitly verified against the retry policy — not just assumed. Six months from now, when someone wonders "did we ever consider a Redis cache here?" — the answer is one grep away.

**Scoped closing** — if you only want to capture one specific decision or topic rather than the full session:

```
/closing webhook-auth-decision
```

This writes a focused document covering only the conversation around that topic, with a slug derived from your argument. Useful when a session covered multiple unrelated things and you only want to preserve one of them cleanly.

---

### Generating a report

Once sessions start accumulating, run:

```
/report
```

Claude reads all session documents, identifies every Open Questions & Next Steps item that was never resolved in a later session, collects every Do Not constraint from Roads Not Taken, and writes a single report to `docs/reports/report.md`. Each item links back to the session it came from.

The report is always one file — it overwrites on each run. The frontmatter tracks `last_session`, the filename of the newest session the report covers. On the next run, `/report` reads that cursor and only processes sessions after it, so you're not re-reading 50 files when 3 are new.

```
/report full   — ignore the cursor, rebuild from every session
```

Use `full` after a `/closing` that may have resolved items the report has as open, or any time you want a clean rebuild.

---

## The docs/ directory

All output lives under `docs/` in **whichever directory you started Claude Code from** — not in `~/.claude/` where the commands live. The commands are global; the output files are local to each project.

```
docs/
├── sessions/          ← individual session documents (one per /closing run)
│   ├── 2026-05-15-1042-initial-schema-design.md
│   ├── 2026-05-16-0914-auth-middleware-decision.md
│   ├── 2026-05-19-1531-dropped-redis-approach.md
│   └── 2026-05-20-0748-webhook-auth-decision.md
└── reports/
    └── report.md      ← synthesized project state (single file, overwritten each /report run)
```

**Session files** are the raw archaeology — one file per session, timestamp-named so they sort chronologically. Human-readable. You can open them, grep them, or read them directly.

**`report.md`** is the synthesized current state — open deferrals and Do Not constraints across all sessions, each linked back to its source. It's a checkpoint, not an archive. When you have 20+ sessions, loading the report plus 2-3 recent sessions gives the same orientation as loading everything.

Commit both to your repo. The session history and the report together are the institutional memory of the project — they belong in version control next to the code.

---

## Why this works

### Why `/closing` works

Think of a surgical shift handoff. When one surgeon hands off to another, they don't read the full patient chart — they write a one-page note: what changed on this shift, what decisions were made and why, what's still open. The incoming surgeon reads the note, not the chart.

`/closing` is that note. The structured format — Summary, What We Did, Why We Did It This Way, Roads Not Taken, Key Discoveries, Open Questions — does the compression work *before* the document enters context. Each section signals to Claude what's load-bearing. The Do Not constraints in Roads Not Taken front-load the guard rails so a future session sees them before it starts reasoning about the problem.

Contrast this with dumping raw chat history: Claude sees a wall of text with no signal about what matters. The structured document extracts the signal so Claude doesn't have to.

### Why `/opening` works

Reading a 2,000-word structured brief is not the same as reading raw history. Claude treats explicit decisions differently from musings — the archaeology format plays into this. Every section ends with something settled or something open, which Claude can slot directly into its working model of the project.

For large loads (3+ session files), `/opening` delegates to a subagent. The subagent reads all the documents and returns a finished synthesis. The raw archaeology never enters your context window — only the distilled brief does. This keeps the main context clean for actual work.

### Why `/report` works

At scale, the problem shifts. One session document answers "what happened last time?" Thirty session documents answer a harder question: "what is the accumulated state of all deferred work and locked constraints across the entire project history?" You can't load thirty files every session.

`/report` collapses that history into a single document: every still-open deferral, every Do Not constraint, each linked to its source session. The cursor mechanism (`last_session` in the frontmatter) means subsequent runs only process new sessions — you don't re-pay the synthesis cost on history already captured.

### How they work together

Each command operates at a different time horizon:

- `/closing` — session to session. The shift handoff. Captures what happened before the context is gone.
- `/opening` — note to context. Reads the handoff and orients the new session in seconds.
- `/report` — history to current state. Collapses accumulated sessions into one load when individual files become too many to read.

Together they mean no session starts cold and no decision gets re-litigated from scratch. The reasoning that was hard to arrive at the first time is preserved and surfaced automatically the next time it's relevant.
