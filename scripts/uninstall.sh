#!/bin/sh
# Remove skills this repository defines from every agent holding them.
#
#   sh scripts/uninstall.sh [skill-name...]
#
# With no argument, removes every skill under skills/. With names, removes only
# those, whether or not skills/<name> still exists: a renamed skill keeps
# routing under its old name until it is removed.
#
# No -a flag, so the CLI cleans the link in every agent directory rather than
# only the agents listed in agents.txt. An agent dropped from that list still
# holds a live copy otherwise.
#
# Names are always passed explicitly. The CLI's --all removes every installed
# skill from every agent, other sources included, so it is never used here.

set -eu

script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
repo_root=$(CDPATH= cd -- "$script_dir/.." && pwd)

command -v npx >/dev/null 2>&1 || {
    echo "npx not found; install Node to use the skills CLI" >&2
    exit 1
}

if [ "$#" -gt 0 ]; then
    names=$*
else
    names=""
    for dir in "$repo_root"/skills/*/; do
        [ -d "$dir" ] || continue
        name=$(basename -- "$dir")
        if [ -n "$names" ]; then
            names="$names $name"
        else
            names=$name
        fi
    done
    [ -n "$names" ] || {
        echo "no skills under $repo_root/skills" >&2
        exit 1
    }
fi

echo "Removing skills defined in $repo_root"
printf 'Skills: %s\n\n' "$names"

# shellcheck disable=SC2086
exec npx skills remove -g -y $names
