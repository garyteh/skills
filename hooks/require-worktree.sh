#!/bin/sh
# PreToolUse gate: the primary checkout is not for editing.
#
# Changes an agent makes to this repository belong in a linked worktree, so
# several tasks can run at once without treading on each other. This denies an
# edit issued from the primary checkout and points at the git-worktree skill.
#
# It gates the edit tools and nothing else. The gate does not have to catch
# every write, only the first one: once a session is working in a worktree,
# everything it does after that is already isolated, shell included. Guessing
# whether a shell command writes means parsing shell, which cannot be done
# reliably here and denied ordinary reads when it was tried.
#
# Escape: set WORKTREE_GATE=off in the environment.

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
cwd=$(field '.cwd' 'cwd')

# 1. An edit tool, or there is nothing to gate.
case "$tool" in
    Edit|Write|NotebookEdit|apply_patch) ;;
    *) exit 0 ;;
esac

# 2. Escape hatch. A hook runs before the command, so an assignment written in
# front of a command never reaches here; only the real environment does.
[ "${WORKTREE_GATE:-}" = "off" ] && exit 0

[ -n "$cwd" ] && [ -d "$cwd" ] && cd "$cwd" 2>/dev/null

# 3. Outside a git repository there is nothing to isolate, and a linked
# worktree already is the isolation. The primary checkout keeps these equal.
git_dir=$(git rev-parse --git-dir 2>/dev/null) || exit 0
git_common=$(git rev-parse --git-common-dir 2>/dev/null) || exit 0
[ "$git_dir" != "$git_common" ] && exit 0

# 4. A target outside this checkout is not what the gate is for. Scratch files,
# notes and plans live elsewhere and isolating them buys nothing. A payload
# carrying no path stays denied, because a gate that cannot place a write
# should not wave it through.
target=$(field '.tool_input.file_path' 'file_path')
if [ -n "$target" ]; then
    case "$target" in
        /*) target_abs=$target ;;
        *)  target_abs=$PWD/$target ;;
    esac
    # Strip the filename with parameter expansion rather than dirname, which
    # is one more binary to depend on.
    target_dir=${target_abs%/*}
    [ -n "$target_dir" ] || target_dir=/
    # Compare both sides as physical paths. A temp directory or a home
    # directory reached through a symlink spells one location two ways, and a
    # textual prefix test reads the second spelling as outside.
    resolved=$(CDPATH= cd -- "$target_dir" 2>/dev/null && pwd -P) && target_dir=$resolved
    top=$(git rev-parse --show-toplevel 2>/dev/null) || top=
    if [ -n "$top" ]; then
        resolved=$(CDPATH= cd -- "$top" 2>/dev/null && pwd -P) && top=$resolved
        case "$target_dir/" in
            "$top"/*) ;;
            *) exit 0 ;;
        esac
    fi
fi

deny "This is the primary checkout, which is not for editing. Another stream of work may be running against it. Use the git-worktree skill to start an isolated checkout, then work there. To edit here anyway, set WORKTREE_GATE=off in the environment."
