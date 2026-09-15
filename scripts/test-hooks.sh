#!/bin/sh
# Feed fixture payloads to each hook script and assert the decision.
#
#   sh scripts/test-hooks.sh
#
# No harness needed: a hook reads JSON on stdin and prints a decision, so the
# whole contract is testable from a shell.
#
# Every case runs twice, once with jq on PATH and once without, because the
# hooks carry a sed fallback for machines that lack it and an untested
# fallback is one that has already broken.

set -eu

script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
repo_root=$(CDPATH= cd -- "$script_dir/.." && pwd)
hooks=$repo_root/hooks

pass=0
fail=0

tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT INT TERM

# A throwaway repository with a linked worktree, so the worktree branch of the
# gate runs against real git plumbing rather than a stubbed path.
(
    cd "$tmp"
    git init -q primary
    cd primary
    git -c user.email=t@t -c user.name=t commit -q --allow-empty -m init
    git worktree add -q ../linked -b linked
) >/dev/null 2>&1
primary=$tmp/primary
linked=$tmp/linked

# A PATH holding what the hooks need and no jq, to exercise the sed fallback.
# jq sits in more than one system directory, so trimming PATH is not enough.
mkdir -p "$tmp/bin"
for b in sh cat sed head git; do
    ln -s "$(command -v "$b")" "$tmp/bin/$b"
done
jqless=$tmp/bin

# check <script> <expected: allow|deny> <label> <payload>
check() {
    _script=$1 _expect=$2 _label=$3 _payload=$4
    _case_fail=0
    for _mode in jq sed; do
        if [ "$_mode" = jq ]; then
            _out=$(printf '%s' "$_payload" | sh "$hooks/$_script" 2>/dev/null || true)
        else
            _out=$(printf '%s' "$_payload" |
                env -i PATH="$jqless" HOME="$HOME" "$jqless/sh" "$hooks/$_script" 2>&1) ||
                { printf 'FAIL  %-24s %s [sed] hook crashed: %s\n' \
                    "$_script" "$_label" "$_out"; fail=$((fail + 1)); _case_fail=1; continue; }
        fi
        case "$_out" in
            *'"permissionDecision":"deny"'*) _got=deny ;;
            *) _got=allow ;;
        esac
        if [ "$_got" = "$_expect" ]; then
            pass=$((pass + 1))
        else
            fail=$((fail + 1))
            _case_fail=1
            printf 'FAIL  %-24s %s [%s] (expected %s, got %s)\n' \
                "$_script" "$_label" "$_mode" "$_expect" "$_got"
        fi
    done
    if [ "$_case_fail" -eq 0 ]; then
        printf 'ok    %-24s %s\n' "$_script" "$_label"
    fi
}

payload() {
    printf '{"tool_name":"%s","cwd":"%s","tool_input":{"command":"%s"}}' \
        "$1" "$2" "$3"
}

# An edit payload carrying the path it would write, which is what decides
# whether the write lands inside this checkout.
file_payload() {
    printf '{"tool_name":"%s","cwd":"%s","tool_input":{"file_path":"%s"}}' \
        "$1" "$2" "$3"
}

# require-worktree.sh
check require-worktree.sh allow "read-only command in primary" \
    "$(payload Bash "$primary" 'ls -la')"
check require-worktree.sh deny "Edit in primary checkout" \
    "$(payload Edit "$primary" '')"
check require-worktree.sh allow "Edit inside a linked worktree" \
    "$(payload Edit "$linked" '')"
check require-worktree.sh deny "sed -i in primary checkout" \
    "$(payload Bash "$primary" 'sed -i s/a/b/ file.txt')"
check require-worktree.sh deny "redirect into a file in primary" \
    "$(payload Bash "$primary" 'echo hi > notes.txt')"
check require-worktree.sh allow "redirect to /dev/null in primary" \
    "$(payload Bash "$primary" 'grep -q x file 2>/dev/null')"
check require-worktree.sh deny "redirect into a file with stderr merged" \
    "$(payload Bash "$primary" 'echo hi > notes.txt 2>&1')"
check require-worktree.sh deny "redirect into a file with stderr discarded" \
    "$(payload Bash "$primary" 'echo hi > notes.txt 2>/dev/null')"
check require-worktree.sh allow "angle bracket inside a quoted argument" \
    "$(payload Bash "$primary" "git log --format='%an <%ae>'")"
check require-worktree.sh allow "redirect into tmp in primary" \
    "$(payload Bash "$primary" 'echo hi > /tmp/scratch.txt')"
check require-worktree.sh allow "escape hatch honoured" \
    "$(payload Bash "$primary" 'WORKTREE_GATE=off sed -i s/a/b/ file.txt')"
check require-worktree.sh allow "outside any repository" \
    "$(payload Edit "$tmp" '')"
check require-worktree.sh deny "Write into the primary checkout" \
    "$(file_payload Write "$primary" "$primary/notes.md")"
check require-worktree.sh allow "Write to a path outside the repository" \
    "$(file_payload Write "$primary" "$tmp/outside.md")"
check require-worktree.sh allow "Write to an absolute path elsewhere" \
    "$(file_payload Write "$primary" '/tmp/scratch-note.md')"

# require-trunk-landing.sh
check require-trunk-landing.sh allow "unrelated command" \
    "$(payload Bash "$primary" 'ls -la')"
check require-trunk-landing.sh deny "git push" \
    "$(payload Bash "$primary" 'git push')"
check require-trunk-landing.sh deny "git commit" \
    "$(payload Bash "$primary" 'git commit -m wip')"
check require-trunk-landing.sh allow "escape hatch honoured" \
    "$(payload Bash "$primary" 'TRUNK_GATE=off git push origin HEAD:master')"
check require-trunk-landing.sh allow "not a shell call" \
    "$(payload Edit "$primary" '')"

printf '\n%d passed, %d failed (each case run with and without jq)\n' "$pass" "$fail"
[ "$fail" -eq 0 ]
