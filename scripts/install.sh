#!/bin/sh
# Install skills from this repository into each agent listed in agents.txt.
#
#   sh scripts/install.sh [extra skills-cli args...]
#
# Every skill by default. Pass -s <name> to install just one.
#
# The CLI copies each skill into a canonical store, then symlinks the directories
# of agents that insist on their own location at that copy. This repository is
# never linked into the install, so editing a skill here changes nothing until
# this runs again. Re-run after every edit, not only when adding a skill or an
# agent.

set -eu

script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
repo_root=$(CDPATH= cd -- "$script_dir/.." && pwd)
agents_file=$repo_root/agents.txt

command -v npx >/dev/null 2>&1 || {
    echo "npx not found; install Node to use the skills CLI" >&2
    exit 1
}

[ -f "$agents_file" ] || {
    echo "no agents.txt at $agents_file" >&2
    exit 1
}

set -- "$@"
agent_args=""
while read -r line; do
    agent=$(printf '%s' "$line" | sed -e 's/#.*$//' -e 's/[[:space:]]//g')
    [ -n "$agent" ] || continue
    agent_args="$agent_args -a $agent"
done < "$agents_file"

[ -n "$agent_args" ] || {
    echo "agents.txt lists no agents" >&2
    exit 1
}

echo "Installing skills from $repo_root"
printf 'Targets:%s\n\n' "$agent_args"

# shellcheck disable=SC2086
cd "$repo_root" && exec npx skills add . -g -y $agent_args "$@"
