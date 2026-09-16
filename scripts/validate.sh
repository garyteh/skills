#!/bin/sh
# Validate every skill in a skills container against the contract in AGENTS.md.
#
#   sh scripts/validate.sh [skills-dir]
#
# Defaults to both of this repository's trees: skills/ published, and
# .agents/skills/ harness. Given a directory, checks that one as a published
# tree, which is how another repository's skills get linted.
# Exits 0 when no FAIL was recorded, 1 otherwise. WARN never changes the exit.
#
# Tallies go to files, not shell variables: most checks run inside pipelines,
# and a variable incremented in a subshell is lost when the subshell exits.

set -u

script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
repo_root=$(CDPATH= cd -- "$script_dir/.." && pwd)
skills_dir=${1:-$repo_root/skills}
harness_dir=$repo_root/.agents/skills

fail_patterns=$script_dir/banned-fail.txt
warn_patterns=$script_dir/banned-warn.txt

tally=$(mktemp -d) || exit 1
trap 'rm -rf "$tally"' EXIT INT TERM
: > "$tally/fail"
: > "$tally/warn"
: > "$tally/checked"

TAB=$(printf '\t')

fail() {
    printf 'FAIL %s: %s\n' "$1" "$2" >&2
    echo x >> "$tally/fail"
}

warn() {
    printf 'WARN %s: %s\n' "$1" "$2" >&2
    echo x >> "$tally/warn"
}

count() { wc -l < "$tally/$1" | tr -d ' '; }

rel_of() { printf '%s' "${1#"$repo_root"/}"; }

# Strip comments and blank lines from a pattern file.
patterns_from() {
    [ -f "$1" ] || return 0
    sed -e 's/#.*$//' -e 's/[[:space:]]*$//' "$1" | grep -v '^$'
}

# Emit the value of a frontmatter key, folded to one line, quotes stripped.
fm_value() {
    printf '%s\n' "$1" |
        awk -v key="$2" '
            $0 ~ "^" key ":" {
                sub("^" key ":[[:space:]]*", "")
                found = 1
                if (length($0)) print
                next
            }
            found && /^[A-Za-z_][A-Za-z0-9_-]*:/ { exit }
            found && /^[[:space:]]/ {
                sub(/^[[:space:]]+/, "")
                print
            }
        ' |
        tr '\n' ' ' |
        sed -e 's/[[:space:]]*$//' -e 's/^[>|][-+0-9]*[[:space:]]*//' \
            -e 's/^"\(.*\)"$/\1/' -e "s/^'\(.*\)'\$/\1/"
}

# The same value, unnormalised. fm_value strips the quotes and block indicators
# that decide how YAML reads the rest of the line, so a check on quoting has to
# read the raw text. $1 frontmatter, $2 key.
fm_raw() {
    printf '%s\n' "$1" |
        awk -v key="$2" '
            $0 ~ "^" key ":" {
                sub("^" key ":[[:space:]]*", "")
                found = 1
                print
                next
            }
            found && /^[A-Za-z_][A-Za-z0-9_-]*:/ { exit }
            found { print }
        '
}

# Report banned phrases in a block of text. $1 text, $2 label, $3 line offset.
check_phrases() {
    _text=$1
    _label=$2
    _offset=$3

    patterns_from "$fail_patterns" | while read -r pat; do
        printf '%s\n' "$_text" | grep -inE "$pat" |
            while IFS=: read -r ln text; do
                snippet=$(printf '%s' "$text" | sed 's/^[[:space:]]*//' | cut -c1-60)
                fail "$_label:$((ln + _offset))" "banned phrase in \"$snippet\""
            done
    done

    patterns_from "$warn_patterns" | while read -r pat; do
        printf '%s\n' "$_text" | grep -inE "$pat" |
            while IFS=: read -r ln text; do
                snippet=$(printf '%s' "$text" | sed 's/^[[:space:]]*//' | cut -c1-60)
                warn "$_label:$((ln + _offset))" "\"$snippet\""
            done
    done

    printf '%s\n' "$_text" | grep -nE '(^|[^A-Za-z])(MUST|ALWAYS|NEVER)([^A-Za-z]|$)' |
        while IFS=: read -r ln text; do
            snippet=$(printf '%s' "$text" | sed 's/^[[:space:]]*//' | cut -c1-60)
            warn "$_label:$((ln + _offset))" "all-caps imperative states a rule with no rubric: \"$snippet\""
        done
}

check_shell_script() {
    f=$1
    rel=$(rel_of "$f")

    head -n 1 "$f" | grep -qx -- '#!/bin/sh' ||
        fail "$rel:1" 'shebang must be exactly #!/bin/sh'

    [ -x "$f" ] || fail "$rel" 'not executable (chmod +x)'

    sh -n "$f" 2>/dev/null || fail "$rel" 'does not parse as POSIX sh'

    # '[[' is only the bash test builtin when whitespace follows; '[[:alpha:]]'
    # is a POSIX character class. '<{3}' rather than the literal herestring, so
    # this line does not match itself.
    grep -nE '\[\[[[:space:]]|<{3}|^[[:space:]]*function[[:space:]]' "$f" |
        while IFS=: read -r ln _rest; do
            fail "$rel:$ln" 'bashism, not POSIX sh'
        done

    grep -nE '^[[:space:]]*local[[:space:]]' "$f" |
        while IFS=: read -r ln _rest; do
            warn "$rel:$ln" "uses 'local', which is not in POSIX"
        done
}

# Structural sanity check. Not a YAML parse: the validator stays POSIX shell,
# so it checks the shape the eval format requires rather than the whole grammar.
check_evals() {
    f=$1
    rel=$(rel_of "$f")

    grep -q "$TAB" "$f" &&
        fail "$rel" 'contains a tab; YAML forbids tabs for indentation'

    grep -qE '^cases:' "$f" || {
        fail "$rel" 'no top-level cases: key'
        return
    }

    n=$(grep -cE '^  - ' "$f")
    [ "$n" -ge 3 ] ||
        fail "$rel" "$n case(s); write at least 3"

    awk '
        /^  - / {
            if (started && !assert) print start
            started = 1; start = NR; assert = 0; next
        }
        /^    (expect|expect_contains|expect_absent|expect_fires):/ { assert = 1 }
        END { if (started && !assert) print start }
    ' "$f" | while read -r ln; do
        fail "$rel:$ln" 'case has no assertion'
    done

    grep -nE '^    kind:' "$f" | grep -vE 'kind:[[:space:]]*(behaviour|trigger)[[:space:]]*$' |
        while IFS=: read -r ln _rest; do
            fail "$rel:$ln" 'kind must be behaviour or trigger'
        done
}

check_config() {
    f=$1
    rel=$(rel_of "$f")

    grep -nE ':[[:space:]]*(no|yes|on|off|No|Yes|On|Off|NO|YES|ON|OFF)[[:space:]]*$' "$f" |
        while IFS=: read -r ln _rest; do
            warn "$rel:$ln" 'unquoted yes/no/on/off parses as a boolean; quote it'
        done

    grep -nE ':[[:space:]]*[0-9]+\.[0-9]+[[:space:]]*$' "$f" |
        while IFS=: read -r ln _rest; do
            warn "$rel:$ln" 'bare version number parses as a float; quote it'
        done
}

check_reference() {
    f=$1
    rel=$(rel_of "$f")

    lines=$(wc -l < "$f" | tr -d ' ')
    if [ "$lines" -gt 200 ] && ! grep -qiE '^#+[[:space:]]*(contents|table of contents)' "$f"; then
        warn "$rel" "$lines lines with no contents list; a reader who stops early cannot see the scope"
    fi

    grep -nE 'references/[A-Za-z0-9._-]+' "$f" |
        while IFS=: read -r ln _rest; do
            warn "$rel:$ln" 'points at another reference; keep references one level deep'
        done

    # No phrase checks here. A reference teaches a rule by quoting what the rule
    # forbids, so banned-phrase matching makes correct content unsatisfiable.
}

# $1 skill directory, $2 tree: published (default) or harness.
validate_skill() {
    dir=$1
    mode=${2:-published}
    dname=$(basename "$dir")
    f=$dir/SKILL.md
    rel=$(rel_of "$f")

    if [ ! -f "$f" ]; then
        fail "$(rel_of "$dir")" 'no SKILL.md'
        return
    fi
    echo x >> "$tally/checked"

    # --- one SKILL.md, at the root ------------------------------------------
    find "$dir" -mindepth 2 -name SKILL.md | while read -r nested; do
        fail "$(rel_of "$nested")" 'nested SKILL.md; the installer prefers the shallower file, so this one never loads'
    done

    # --- frontmatter block --------------------------------------------------
    if ! head -n 1 "$f" | grep -qx -- '---'; then
        fail "$rel:1" 'frontmatter must open with --- on line 1'
        return
    fi

    fm_end=$(awk 'NR > 1 && $0 == "---" { print NR; exit }' "$f")
    if [ -z "$fm_end" ]; then
        fail "$rel" 'frontmatter is never closed with ---'
        return
    fi

    fm=$(sed -n "2,$((fm_end - 1))p" "$f")
    body=$(sed -n "$((fm_end + 1)),\$p" "$f")

    if printf '%s\n' "$body" | grep -v '^$' | head -n 1 | grep -qx -- '---'; then
        fail "$rel:$((fm_end + 1))" 'second frontmatter block; exactly one is allowed'
    fi

    # --- keys ---------------------------------------------------------------
    # A harness skill also carries metadata, holding the internal marker checked
    # below. The marker's own line is indented, so the extraction here never
    # sees it and only the top-level key needs allowing.
    if [ "$mode" = harness ]; then
        allowed_keys='name|description|metadata'
        allowed_text='name, description and metadata'
    else
        allowed_keys='name|description'
        allowed_text='name and description'
    fi

    printf '%s\n' "$fm" | grep -E '^[A-Za-z_][A-Za-z0-9_-]*:' | sed 's/:.*$//' |
        grep -vxE "$allowed_keys" |
        while read -r key; do
            fail "$rel" "frontmatter key \"$key\" is not portable; only $allowed_text are allowed"
        done

    # --- harness marker -----------------------------------------------------
    # An install reads .agents/skills/ as a skills container like any other, and
    # this marker is the only thing keeping a harness skill out of the listing.
    # Losing it is silent, so it fails the build instead.
    if [ "$mode" = harness ]; then
        if ! printf '%s\n' "$fm" | grep -qE '^metadata:[[:space:]]*$' ||
           ! printf '%s\n' "$fm" | grep -qE '^[[:space:]]+internal:[[:space:]]*true[[:space:]]*$'; then
            fail "$rel" 'no metadata.internal: true; an install would offer this harness skill beside the published ones'
        fi
    fi

    # --- name ---------------------------------------------------------------
    name=$(fm_value "$fm" name)
    if [ -z "$name" ]; then
        fail "$rel" 'name is missing'
    else
        printf '%s' "$name" | grep -qE '^[a-z0-9]+(-[a-z0-9]+)*$' ||
            fail "$rel" "name \"$name\" must be lowercase alphanumeric and hyphens"
        [ "$(printf '%s' "$name" | wc -c | tr -d ' ')" -le 64 ] ||
            fail "$rel" 'name exceeds 64 characters'
        [ "$name" = "$dname" ] ||
            fail "$rel" "name \"$name\" does not match directory \"$dname\""
    fi

    # --- description --------------------------------------------------------
    desc=$(fm_value "$fm" description)
    if [ -z "$desc" ]; then
        fail "$rel" 'description is missing'
    else
        dlen=$(printf '%s' "$desc" | wc -m | tr -d ' ')
        if [ "$dlen" -gt 1024 ]; then
            fail "$rel" "description is $dlen characters, over the 1024 limit"
        elif [ "$dlen" -gt 900 ]; then
            warn "$rel" "description is $dlen characters; stay under 900 so the next edit does not breach 1024"
        fi
        # A plain YAML scalar ends at ': ' or ' #', and both failures are
        # silent: the first makes the parser read a nested mapping and skip the
        # file, so the skill never installs; the second starts a comment, so
        # the description installs with everything after it missing. Quoted and
        # block scalars carry to the end of the line either way.
        raw_desc=$(fm_raw "$fm" description)
        case $raw_desc in
            '"'*|"'"*|'>'*|'|'*) ;;
            *)
                printf '%s' "$raw_desc" | grep -q ': ' &&
                    fail "$rel" "description contains ': '; YAML reads a nested mapping there and the installer skips the skill"
                printf '%s' "$raw_desc" | grep -q ' #' &&
                    fail "$rel" "description contains ' #'; YAML reads the rest as a comment and truncates the description"
                ;;
        esac
        printf '%s' "$desc" | grep -q '[<>]' &&
            fail "$rel" "description contains '<' or '>'; write the description in plain text"
        printf '%s' "$desc" | grep -qiE 'use when|use this|when the|when a|when you|when creating|when working' ||
            warn "$rel" 'description states no trigger; say when to invoke the skill'
    fi

    # --- body phrasing ------------------------------------------------------
    check_phrases "$body" "$rel" "$fm_end"

    # --- size, body only ----------------------------------------------------
    total=$(wc -l < "$f" | tr -d ' ')
    body_lines=$((total - fm_end))
    [ "$body_lines" -le 500 ] ||
        warn "$rel" "$body_lines body lines; apply the usage test and split what a typical run does not read"

    # --- referenced paths ---------------------------------------------------
    printf '%s\n' "$body" |
        grep -oE '(references|scripts|assets|skills)/[A-Za-z0-9._/-]+[A-Za-z0-9]' |
        sort -u |
        while read -r ref; do
            [ -e "$dir/$ref" ] || [ -e "$repo_root/$ref" ] ||
                fail "$rel" "references $ref, which is not on disk"
        done

    # --- absolute paths -----------------------------------------------------
    printf '%s\n' "$body" | grep -qE '(^|[^A-Za-z0-9._-])(/Users/|/home/|~/)' &&
        warn "$rel" 'contains an absolute or home-relative path; keep paths relative to SKILL.md'

    # --- companion files ----------------------------------------------------
    if [ -f "$dir/evals.yaml" ]; then
        check_evals "$dir/evals.yaml"
    elif [ -d "$dir/references" ] || [ -d "$dir/scripts" ]; then
        warn "$rel" 'has references or scripts but no evals.yaml; rules nothing backs never get cut'
    fi

    [ -f "$dir/config.yaml" ] && check_config "$dir/config.yaml"

    if [ -d "$dir/references" ]; then
        find "$dir/references" -type f -name '*.md' | while read -r r; do
            check_reference "$r"
        done
    fi

    if [ -d "$dir/scripts" ]; then
        find "$dir/scripts" -type f -name '*.sh' | while read -r s; do
            check_shell_script "$s"
        done
    fi

    return 0
}

# --- run --------------------------------------------------------------------

if [ ! -d "$skills_dir" ]; then
    printf 'FAIL: no skills directory at %s\n' "$skills_dir" >&2
    exit 1
fi

for dir in "$skills_dir"/*/; do
    [ -d "$dir" ] || continue
    validate_skill "${dir%/}"
done

# Only on a default run. Given a directory, the caller is linting some other
# repository, which has no harness tree of this one's.
if [ "$skills_dir" = "$repo_root/skills" ] && [ -d "$harness_dir" ]; then
    for dir in "$harness_dir"/*/; do
        [ -d "$dir" ] || continue
        validate_skill "${dir%/}" harness
    done
fi

for s in "$script_dir"/*.sh; do
    [ -f "$s" ] || continue
    check_shell_script "$s"
done

printf '\n%s skill(s) checked, %s failure(s), %s warning(s)\n' \
    "$(count checked)" "$(count fail)" "$(count warn)"

[ "$(count fail)" -eq 0 ]
