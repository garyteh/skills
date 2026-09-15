#!/bin/sh
# PreToolUse gate: landing a change goes through the documented procedure.
#
# Denies an ad hoc git commit or git push and points at the git-solo-trunk
# skill, which reads the default branch from the remote, picks a route from
# where the change actually sits, and verifies the landing with a separate
# read.
#
# Escape: prefix the command with TRUNK_GATE=off. The skill's own commands
# need it, since they are the commands this gate matches.

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

# True where the gate variable is set to off as an environment prefix, before
# the command word. Matched anywhere in the string instead, a quoted mention
# inside a real write turns the gate off.
gate_off_prefix() {
    _rest=$1
    while :; do
        case "$_rest" in
            " "*) _rest=${_rest# }; continue ;;
        esac
        _word=${_rest%% *}
        case "$_word" in
            "$2") return 0 ;;
            *=*) ;;
            *) return 1 ;;
        esac
        case "$_rest" in
            *" "*) _rest=${_rest#* } ;;
            *) return 1 ;;
        esac
    done
}

tool=$(field '.tool_name' 'tool_name')
cmd=$(field '.tool_input.command' 'command')

[ "$tool" = "Bash" ] || exit 0

# Escape hatch, as an environment prefix on the command or in the hook's own
# environment.
[ "${TRUNK_GATE:-}" = "off" ] && exit 0
gate_off_prefix "$cmd" "TRUNK_GATE=off" && exit 0

case "$cmd" in
    *"git commit"*|*"git push"*) ;;
    *) exit 0 ;;
esac

deny "Landing a change goes through the git-solo-trunk skill, which reads the default branch from the remote rather than assuming one, picks a route from where the change currently sits, and confirms the landing with a separate read. Read it, then re-run with TRUNK_GATE=off in front of the command."
