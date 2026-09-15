#!/bin/sh
# PreToolUse gate: landing a change goes through the documented procedure.
#
# Denies an ad hoc landing, git commit or git push however the invocation is spelled,
# and points at the git-solo-trunk
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

# True where the command runs git with commit or push as its subcommand.
#
# Global options sit between the binary and the subcommand, so a directory or
# config option in front of the verb is still a landing. Testing for the two
# words next to each other missed every one of those forms. Walk the words
# instead: find git, step over its global options, and look at the first word
# that is not one.
lands_a_change() {
    # Shell operators become separators, so a landing later in a chain is still
    # found. Globbing is off while the words are split, or a * in the command
    # would expand against the working directory.
    _words=$(printf '%s' "$1" | sed -e 's/[;&|()]/ /g')
    _hunting=1
    set -f
    # shellcheck disable=SC2086
    set -- $_words
    set +f
    while [ "$#" -gt 0 ]; do
        _w=$1
        shift
        if [ "$_hunting" -eq 1 ]; then
            case "$_w" in
                git|*/git) _hunting=0 ;;
            esac
            continue
        fi
        case "$_w" in
            # Global options taking a separate value; drop that value too.
            -C|-c|--git-dir|--work-tree|--namespace|--exec-path|--super-prefix)
                [ "$#" -gt 0 ] && shift
                ;;
            -*) ;;
            commit|push) return 0 ;;
            # Any other subcommand: this invocation is not a landing.
            *) _hunting=1 ;;
        esac
    done
    return 1
}

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

lands_a_change "$bare" || exit 0

deny "Landing a change goes through the git-solo-trunk skill, which reads the default branch from the remote rather than assuming one, picks a route from where the change currently sits, and confirms the landing with a separate read. Read it, then set TRUNK_GATE=off in the environment to land from here."
