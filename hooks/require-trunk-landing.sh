#!/bin/sh
# PreToolUse gate: landing a change goes through the documented procedure.
#
# Denies an ad hoc git commit or git push and points at the git-solo-trunk
# skill, which reads the default branch from the remote, picks a route from
# where the change actually sits, and verifies the landing with a separate
# read.
#
# Escape: set TRUNK_GATE=off in the environment. A hook runs before the
# command, so an assignment written in front of one never reaches here.

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

[ "$tool" = "Bash" ] || exit 0

# Escape hatch. Only the real environment counts: an assignment written in
# front of the command arrives as text, and matching it there let a command
# that merely quoted the words turn the gate off.
[ "${TRUNK_GATE:-}" = "off" ] && exit 0

# Strip quoted text before matching. A command that quotes the phrase is
# talking about it rather than running it, and denying a read teaches you to
# leave the gate off.
if command -v sed >/dev/null 2>&1; then
    bare=$(printf '%s' "$cmd" | sed -e "s/'[^']*'/Q/g" -e 's/"[^"]*"/Q/g')
else
    # Without sed the raw string stands. Denying a read costs less than
    # missing a landing.
    bare=$cmd
fi

case "$bare" in
    *"git commit"*|*"git push"*) ;;
    *) exit 0 ;;
esac

deny "Landing a change goes through the git-solo-trunk skill, which reads the default branch from the remote rather than assuming one, picks a route from where the change currently sits, and confirms the landing with a separate read. Read it, then set TRUNK_GATE=off in the environment to land from here."
