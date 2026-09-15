#!/bin/sh
# PreToolUse gate: the primary checkout is not for editing.
#
# Denies a write issued from the repository's primary checkout and points at
# the git-worktree skill. Allows inside a linked worktree, where the isolation
# the skill asks for already holds, so the gate cannot block the worktree it
# just told you to create.
#
# Escape: prefix the command with WORKTREE_GATE=off.
#
# Shell writes are matched by pattern, so the list below catches the common
# in-place writers and is not exhaustive. This raises the floor; it does not
# seal it.

set -u

payload=$(cat)

# Read a string field from the payload. jq where it exists; the sed fallback
# keeps the gate working without it, at the cost of not handling escaped
# quotes inside a value.
field() {
    if command -v jq >/dev/null 2>&1; then
        printf '%s' "$payload" | jq -r "${1} // empty"
    else
        printf '%s' "$payload" |
            sed -n "s/.*\"${2}\"[[:space:]]*:[[:space:]]*\"\([^\"]*\)\".*/\1/p" |
            head -1
    fi
}

# Reasons are written here and contain no double quotes or backslashes, so
# they need no JSON escaping.
deny() {
    printf '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"%s"}}\n' "$1"
    exit 0
}

tool=$(field '.tool_name' 'tool_name')
cmd=$(field '.tool_input.command' 'command')
cwd=$(field '.cwd' 'cwd')

# Escape hatch, as an environment prefix on the command or in the hook's own
# environment.
[ "${WORKTREE_GATE:-}" = "off" ] && exit 0
case "$cmd" in
    *WORKTREE_GATE=off*) exit 0 ;;
esac

[ -n "$cwd" ] && [ -d "$cwd" ] && cd "$cwd" 2>/dev/null

# Outside a git repository there is nothing to isolate.
git_dir=$(git rev-parse --git-dir 2>/dev/null) || exit 0
git_common=$(git rev-parse --git-common-dir 2>/dev/null) || exit 0

# A linked worktree keeps these two apart. The primary checkout has them equal.
[ "$git_dir" != "$git_common" ] && exit 0

writes=0
case "$tool" in
    Edit|Write|NotebookEdit|apply_patch)
        writes=1
        # A write landing outside this checkout is not what the gate is for.
        # Scratch files, notes and plans live elsewhere and isolating them
        # buys nothing. A path the payload does not carry stays denied,
        # because the gate cannot tell where the write would land.
        target=$(field '.tool_input.file_path' 'file_path')
        if [ -n "$target" ]; then
            case "$target" in
                /*) target_abs=$target ;;
                *)  target_abs=$PWD/$target ;;
            esac
            # Strip the filename with parameter expansion rather than
            # dirname, which is one more binary to depend on.
            target_dir=${target_abs%/*}
            [ -n "$target_dir" ] || target_dir=/
            # Compare both sides as physical paths. A temp directory or a
            # home directory reached through a symlink spells one location
            # two ways, and a textual prefix test reads that as outside.
            resolved=$(CDPATH= cd -- "$target_dir" 2>/dev/null && pwd -P) &&
                target_dir=$resolved
            top=$(git rev-parse --show-toplevel 2>/dev/null) || top=
            if [ -n "$top" ]; then
                resolved=$(CDPATH= cd -- "$top" 2>/dev/null && pwd -P) && top=$resolved
                case "$target_dir/" in
                    "$top"/*) : ;;
                    *) writes=0 ;;
                esac
            fi
        fi
        ;;
    Bash)
        case "$cmd" in
            *"sed -i"*|*"perl -i"*|*tee\ *|*"dd of="*|*truncate\ *|\
            *patch\ *|*"git apply"*|*"git checkout --"*|*"git restore"*)
                writes=1 ;;
        esac
        # Redirection into anything but a throwaway path.
        case "$cmd" in
            *">/dev/null"*|*"> /dev/null"*|*">/tmp/"*|*"> /tmp/"*) : ;;
            *">>"*|*">"*)
                case "$cmd" in
                    *"2>&1"*|*"2>/dev/null"*|*"2> /dev/null"*) : ;;
                    *) writes=1 ;;
                esac
                ;;
        esac
        ;;
esac

[ "$writes" -eq 0 ] && exit 0

deny "This is the primary checkout, which is not for editing. Another stream of work may be running against it. Use the git-worktree skill to start an isolated checkout, then work there. To write here anyway, re-run with WORKTREE_GATE=off in front of the command."
