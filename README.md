# simple-context-memory

Every time you start a Claude Code session, Claude wakes up with complete amnesia. Not "a little forgetful" — total blank slate. The project you've been building for three weeks, the decision you made on Thursday about why you're *not* using Redis, the half-finished design sitting in your last conversation — gone.

The reflex solution is to save everything. Dump the whole context into memory files. Write system prompts with the entire project history. But that's just moving noise. Claude can't tell which of the forty remembered facts is the one that matters right now, and you end up with a model that confidently re-litigates decisions you already settled.

What you actually need is what surgeons use during a shift handoff: not a diary, not a log — a **handoff note**. What did we do, why did we do it this way, what did we explicitly reject, and what's still open? That's it. Everything else is reconstruction that Claude can do from the code.

This repo gives you two Claude Code slash commands that implement exactly that system.

---

## The Commands

### `/opening` — Load context at the start of a session

Reads session archaeology documents from `docs/sessions/` and gives you a structured brief: what the project currently is, what decisions are settled, what's pending, and what threads were live when you left off.

Think of it like reading the previous surgeon's handoff note before you scrub in. You don't read the patient's full chart — you read what changed on the last shift and what's still unresolved.

### `/closing` — Write an archaeology document at the end of a session

Captures everything worth preserving from the session: what was built, why it was done this way (including the reasoning that prevents future sessions from re-litigating it), what was considered and rejected, and what's explicitly open. Saves it to `docs/sessions/` with a timestamp filename so the chain of sessions becomes traceable.

"Archaeology" is the right word here — the document records the *decisions*, not just the *artifacts*. The code already shows you what was built. Only this document shows you why the obvious alternative wasn't chosen.

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
```

**User-level (global)** — available in every project on your machine:
```
~/.claude/
└── commands/
    ├── opening.md
    └── closing.md
```

### Steps

Install globally — these commands are useful in every project, not just one.

1. Clone this repo:
   ```bash
   git clone https://github.com/mrgrampz/simple-context-memory
   ```

2. Copy the commands to your global Claude Code commands directory:
   ```bash
   mkdir -p ~/.claude/commands
   cp simple-context-memory/commands/opening.md ~/.claude/commands/
   cp simple-context-memory/commands/closing.md ~/.claude/commands/
   ```

3. That's it. Claude Code picks up `.md` files in `commands/` directories automatically — no config, no restart.

If you only want them in a single project instead:
```bash
mkdir -p your-project/.claude/commands
cp simple-context-memory/commands/opening.md your-project/.claude/commands/
cp simple-context-memory/commands/closing.md your-project/.claude/commands/
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

**Subagents for the heavy modes** — `summary`, `search`, `last-week`, and `all` spin up a subagent to do the reading and synthesis. Think of a subagent like a research assistant you send to the library: they read all the session files, compile the answer, and hand you a summary — without any of that raw material ever entering your current context window. The default `/opening` and small numeric modes (`/opening 2`) load directly into context because they're small enough that it doesn't matter.

### Ending a session

Before you close Claude Code — or before the context window fills up — run:

```
/closing
```

**Don't wait until the end.** Claude Code compacts the context window automatically when it gets full, and compaction is lossy — it summarizes rather than preserves. Once compaction happens, the fine-grained reasoning about *why* decisions were made is gone. Run `/closing` before that happens.

Think of it like saving a document: you don't wait until your computer crashes. If the session has been long, run `/closing` while the context is still intact, then keep going.

#### Hook: get a warning before compaction

You can configure Claude Code to check the context window on every turn and warn you before it fills. The hook type is `UserPromptSubmit` — it fires on every message you send, like a pulse check. The command needs to be a script that reads the current session's token count and prints a warning if it's above a threshold.

The script works by reading `~/.claude/projects/*/*.jsonl` (Claude Code logs every session there), finding the most recent assistant message with usage data, and comparing the token count against the context window size. Two thresholds make sense: a first notice around 60% ("consider running `/closing` soon") and an urgent warning around 75% ("run it now").

Wire it up in `~/.claude/settings.json`:

```json
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "python3 /path/to/your/context-watch.py"
          }
        ]
      }
    ]
  }
}
```

This repo does not ship a context-watch script — how you implement it is personal preference. The key things the script needs to do: find the most recently modified JSONL in `~/.claude/projects/`, parse backwards through it for the last assistant `usage` block (which contains `input_tokens`, `cache_read_input_tokens`, and `cache_creation_input_tokens`), sum them, and divide by your model's context window size. Hardcode the context window for your model — `200_000` for claude-sonnet-4-6.

Claude writes a session document to `docs/sessions/` with a timestamp filename. The document covers six sections:

- **What We Did** — specific things built or decided (file paths, function names, design choices)
- **Why We Did It This Way** — the reasoning, so future sessions don't re-litigate it
- **Roads Not Taken** — what was proposed and rejected, and why. This is the most important section — it's the institutional memory that doesn't appear in the code or git history
- **Threads We Pulled** — lines of thinking explored even if no decision was reached
- **Open Questions** — what was explicitly deferred
- **Files Changed** — what changed and where

**Scoped closing** — if you only want to capture one specific decision or topic rather than the full session:

```
/closing webhook-auth-decision
```

This writes a focused document covering only the conversation around that topic, with a slug derived from your argument. Useful when a session covered multiple unrelated things and you only want to preserve one of them cleanly.

---

## The docs/sessions/ directory

`docs/sessions/` is created in **whichever directory you started Claude Code from** — not in `~/.claude/` where the commands live. The commands are global; the session files are local to the project. If you start Claude Code inside `~/projects/my-api/`, your sessions land in `~/projects/my-api/docs/sessions/`. Different project, different directory.

Sessions accumulate as plain Markdown files with timestamp filenames:

```
docs/sessions/
├── 2026-05-15-1042-initial-schema-design.md
├── 2026-05-16-0914-auth-middleware-decision.md
├── 2026-05-19-1531-dropped-redis-approach.md
└── 2026-05-20-0748-webhook-auth-decision.md
```

These are human-readable. You can open them, grep them, or read them yourself — they don't require Claude to interpret. The timestamp-first naming means they sort chronologically by default, so `ls docs/sessions/` gives you the project timeline.

Commit them to your repo. The session history *is* the institutional memory of the project — it belongs in version control next to the code.

---

## Why this works

A note on how Claude reads context: when Claude gets a 2,000-word session document, it doesn't just "know" everything in it equally. It treats recent sentences more heavily than earlier ones, and it weights things that look like explicit decisions over things that look like musings. The archaeology format plays into this — every section ends with something settled or something open, which Claude can slot directly into its working understanding.

Contrast this with dumping raw chat history or a massive project-state memory file: Claude sees a wall of text with no signal about what's load-bearing and what's background noise. The structured document does the compression work *before* it enters the context window.

One session document ≈ one surgical handoff note. Surgical handoff notes are short. They exist because the alternative — reading the full chart — takes too long and buries the critical detail in noise. Same physics here.
