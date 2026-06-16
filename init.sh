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
echo "  [ok] Commands installed to ~/.claude/commands/"

# Hook scripts
mkdir -p ~/.claude/hooks
cp "$REPO_DIR/scripts/context-watch.py" ~/.claude/hooks/context-watch.py
cp "$REPO_DIR/scripts/pre-compact.py"   ~/.claude/hooks/pre-compact.py
cp "$REPO_DIR/scripts/post-compact.py"  ~/.claude/hooks/post-compact.py
echo "  [ok] Hook scripts installed to ~/.claude/hooks/"

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
