# BD TUI Setup Guide

## Clipboard Support (Copy Issue ID)

The `i` key in bdui-compact copies the selected issue's ID to your clipboard. This feature requires specific terminal configuration to work, especially over SSH.

### Requirements

#### iTerm2 Settings (Local Machine)

1. **Prefs > General > Selection**
   - Enable "Applications in terminal may access clipboard"

2. **Prefs > Advanced** (search "insecure")
   - Set "Disable potentially insecure escape sequences" to **No**

#### tmux Settings (Remote/Local)

If you use tmux, add these lines to `~/.tmux.conf`:

```bash
# Enable clipboard passthrough for OSC 52 escape sequences
set -g set-clipboard on
set -g allow-passthrough on
```

Then reload tmux config:
```bash
tmux source-file ~/.tmux.conf
```

### How It Works

bdui-compact uses [OSC 52](https://invisible-island.net/xterm/ctlseqs/ctlseqs.html#h3-Operating-System-Commands) escape sequences to copy text to your clipboard. This works:

- Locally in iTerm2
- Over SSH (the escape sequence travels through the SSH connection to your local terminal)
- Through tmux (with the settings above)

### Troubleshooting

**Test if OSC 52 works in your terminal:**
```bash
printf '\x1b]52;c;dGVzdA==\x07'
```
Then Cmd+V - should paste "test"

**If clipboard doesn't work:**

1. Verify iTerm2 settings are correct
2. If using tmux, verify the config is loaded: `tmux show -g set-clipboard`
3. Try outside of tmux first to isolate the issue
4. The ID is also saved to `/tmp/bd-id` as a fallback

### Alternative: iTerm2 Shell Integration

If OSC 52 doesn't work, you can install iTerm2 shell integration which provides `it2copy`:

```bash
curl -L https://iterm2.com/shell_integration/install_shell_integration_and_utilities.sh | bash
source ~/.iterm2_shell_integration.zsh
```

Then you can manually copy with:
```bash
cat /tmp/bd-id | it2copy
```
