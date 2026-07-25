#!/usr/bin/env bash
set -e

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo ""
echo "Installing simple-context-memory..."
echo ""

# Commands
mkdir -p ~/.claude/commands
cp "$REPO_DIR/commands/opening.md"  ~/.claude/commands/opening.md
cp "$REPO_DIR/commands/closing.md"  ~/.claude/commands/closing.md
cp "$REPO_DIR/commands/report.md"   ~/.claude/commands/report.md
cp "$REPO_DIR/commands/reopen.md"   ~/.claude/commands/reopen.md
echo "  [ok] Commands installed to ~/.claude/commands/"

# Hook scripts
mkdir -p ~/.claude/hooks
cp "$REPO_DIR/scripts/context-watch.py" ~/.claude/hooks/context-watch.py
cp "$REPO_DIR/scripts/pre-compact.py"   ~/.claude/hooks/pre-compact.py
cp "$REPO_DIR/scripts/post-compact.py"  ~/.claude/hooks/post-compact.py
echo "  [ok] Hook scripts installed to ~/.claude/hooks/"

# claude-reopen — standalone shell tool, not a slash command or a hook.
# It has to run from a plain terminal (not from inside an active session)
# so it can exec() into `claude --resume <id>` in place; a slash command
# can't do that since it runs inside the session process it would need to replace.
mkdir -p ~/.local/bin
cp "$REPO_DIR/scripts/claude-reopen" ~/.local/bin/claude-reopen
chmod +x ~/.local/bin/claude-reopen
echo "  [ok] claude-reopen installed to ~/.local/bin/"

case ":$PATH:" in
    *":$HOME/.local/bin:"*) ;;
    *) echo "  [action required] ~/.local/bin is not on your \$PATH — add it (e.g. in ~/.bashrc or ~/.zshrc):"
       echo "      export PATH=\"\$HOME/.local/bin:\$PATH\"" ;;
esac

# Check whether hooks are already wired in settings.json
SETTINGS="$HOME/.claude/settings.json"
NEEDS_HOOK_CONFIG=true

if [ -f "$SETTINGS" ]; then
    if grep -q "context-watch.py" "$SETTINGS" \
    && grep -q "pre-compact.py"   "$SETTINGS" \
    && grep -q "post-compact.py"  "$SETTINGS"; then
        NEEDS_HOOK_CONFIG=false
        echo "  [ok] Hook configuration already present in ~/.claude/settings.json"
    fi
fi

if [ "$NEEDS_HOOK_CONFIG" = true ]; then
    echo ""
    echo "  [action required] Add the following to the \"hooks\" block in ~/.claude/settings.json:"
    echo ""
    cat << 'EOF'
    "UserPromptSubmit": [
      {
        "matcher": "",
        "hooks": [{ "type": "command", "command": "python3 ~/.claude/hooks/context-watch.py" }]
      }
    ],
    "PreCompact": [
      {
        "matcher": "",
        "hooks": [{ "type": "command", "command": "python3 ~/.claude/hooks/pre-compact.py" }]
      }
    ],
    "PostCompact": [
      {
        "matcher": "",
        "hooks": [{ "type": "command", "command": "python3 ~/.claude/hooks/post-compact.py" }]
      }
    ]
EOF
    echo ""
    echo "  If ~/.claude/settings.json does not exist, create it with:"
    echo ""
    cat << 'EOF'
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "matcher": "",
        "hooks": [{ "type": "command", "command": "python3 ~/.claude/hooks/context-watch.py" }]
      }
    ],
    "PreCompact": [
      {
        "matcher": "",
        "hooks": [{ "type": "command", "command": "python3 ~/.claude/hooks/pre-compact.py" }]
      }
    ],
    "PostCompact": [
      {
        "matcher": "",
        "hooks": [{ "type": "command", "command": "python3 ~/.claude/hooks/post-compact.py" }]
      }
    ]
  }
}
EOF
fi

echo ""
echo "Done. Open any project in Claude Code and run /opening to load session context."
echo ""
