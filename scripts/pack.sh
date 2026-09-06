#!/bin/sh
# Zip each skill in this repository into an archive for a Cowork upload.
#
#   sh scripts/pack.sh [-s <name>]
#
# Every skill by default. Pass -s <name> to pack just one.
#
# Archives land in build/<name>.zip. Each carries a single top-level folder
# named for the skill, which is the shape the uploader installs.

set -eu

script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
repo_root=$(CDPATH= cd -- "$script_dir/.." && pwd)
skills_dir=$repo_root/skills
out_dir=$repo_root/build

command -v zip >/dev/null 2>&1 || {
    echo "zip not found" >&2
    exit 1
}

only=""
while [ $# -gt 0 ]; do
    case $1 in
        -s) shift; only=${1:-}; [ -n "$only" ] || { echo "-s needs a name" >&2; exit 1; } ;;
        *)  echo "unknown argument: $1" >&2; exit 1 ;;
    esac
    shift
done

[ -d "$skills_dir" ] || {
    echo "no skills directory at $skills_dir" >&2
    exit 1
}

mkdir -p "$out_dir"

# Names come from what is on disk, never a list in this script.
packed=0
for dir in "$skills_dir"/*/; do
    [ -d "$dir" ] || continue
    name=$(basename "$dir")
    [ -z "$only" ] || [ "$name" = "$only" ] || continue

    [ -f "$dir/SKILL.md" ] || {
        echo "skills/$name has no SKILL.md" >&2
        exit 1
    }

    out=$out_dir/$name.zip
    # zip adds to an existing archive rather than replacing it, so a file
    # deleted or renamed inside the skill would survive in every later
    # archive. Remove the target first.
    rm -f "$out"

    (cd "$skills_dir" && zip -r -q "$out" "$name" -x '*.DS_Store')
    echo "$out"
    packed=$((packed + 1))
done

[ "$packed" -gt 0 ] || {
    if [ -n "$only" ]; then
        echo "no skills/$only" >&2
    else
        echo "skills/ holds no skills" >&2
    fi
    exit 1
}
