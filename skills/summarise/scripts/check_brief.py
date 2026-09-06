#!/usr/bin/env python3
"""Deterministic gate checks for a summarise brief.

Grades only the rules a script can decide with no judgement. Judgement gates
(layering, compression, flattened trade-offs) are not checked here.

EXECUTE this file. Nothing in the skill needs to read it.

Usage:
    python3 check_brief.py DRAFT.md [--english-variant Australian]
                                    [--allow-diagram-type class]
                                    [--today YYYY-MM-DD]

Exit code 0 if every mechanical gate passes, 1 otherwise.

Thresholds come from the skill's config.yaml, read at run time. A command-line
flag overrides config; a missing or unreadable config falls back to the defaults
named beside each value below.

The language variant is not a config value: it belongs to the reader, resolved
per run. Without --english-variant the spelling check is skipped and the verdict
says so, because enforcing a variant nobody named is worse than enforcing none.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, asdict
from datetime import date

# Gate A2. Headings that describe a document's furniture rather than this
# source's content, so the reader has to open the section to find out if they
# care. Config points at this list rather than restating it.
BANNED_HEADINGS = {
    "background", "conclusion", "context", "details", "follow up", "follow-up",
    "next steps", "notes", "open questions", "overview", "risks", "rollout",
    "summary", "trade-offs", "tradeoffs",
}
# Gate A5/A6. First token of a mermaid block mapped to the diagram family it
# declares, so an unknown header is treated as a parse failure rather than
# silently skipped.
KNOWN_DIAGRAM_HEADERS = {
    "flowchart": "flowchart", "graph": "flowchart",
    "c4container": "c4", "c4component": "c4", "c4context": "c4",
    "statediagram-v2": "state", "timeline": "timeline",
    "sequencediagram": "sequence", "classdiagram": "class",
}
KNOWN_DIAGRAM_FAMILIES = frozenset(KNOWN_DIAGRAM_HEADERS.values())
# Fallbacks used only when config.yaml cannot be read.
DEFAULT_BOLD_BUDGET = 5
DEFAULT_RESTATEMENT_THRESHOLD = 0.65
DEFAULT_ON_REQUEST_ONLY = frozenset({"class"})
# Gate A4. "one" is omitted deliberately: it reads as an article ("one idea per
# paragraph") far more often than as a quantity, so flagging it is noise.
SPELLED_NUMBERS = re.compile(
    r"\b(two|three|four|five|six|seven|eight|nine|ten)\b", re.I)
# Gate A4. The -ize/-or spellings that most often leak into a brief written in a
# non-US variant. Checked only when the run names such a variant.
US_SPELLINGS = re.compile(
    r"\b(organiz\w*|color\w*|behavior\w*|prioritiz\w*|analyz\w*|optimiz\w*"
    r"|center|centers|recognize\w*|summarize\w*)\b", re.I)
# Gate A4. Variants for which the check above is wrong rather than helpful, so
# naming one of these skips the spelling check instead of inverting it.
US_VARIANTS = frozenset({
    "american", "america", "us", "u.s.", "usa", "en-us", "us english",
    "american english",
})
# Gates A3/A4. A bold label opening a bullet or line is structure, not emphasis
# and not a mid-sentence colon, so it is stripped before both gates run.
BOLD_LABEL_LEAD_IN = re.compile(r"^\s*(?:[-*]\s+)?\*\*[^*]+:\*\*")
# Gates A3/A9. The mandated reader-action label. Strict text, because A9 matches
# it exactly and because a scanner who stops at layer 2 has to find it by shape
# rather than by reading. Structural like the diagram label, so A3 exempts it.
YOUR_MOVE = re.compile(r"^\s*(?:[-*]\s+)?\*\*Your move:\*\*\s*(.*)$")
# Gate A9. Near misses on the label. The label stays strict because it is a
# structural anchor the reader finds by shape, but a brief that wrote
# "**Your Move:**" needs to be told that rather than told no line exists.
YOUR_MOVE_LOOSE = re.compile(
    r"^\s*(?:[-*]\s+)?\*\*\s*your\s+move\s*:?\s*\*\*", re.I)
# Gate A3. The mandated diagram label is required by the skill, so counting it
# would make the bold budget unpassable on any brief with several diagrams.
DIAGRAM_LABEL = re.compile(r"\*\*Diagram \(AI-generated\)[^*]*\*\*")
# Gates A1/A8. Sentence boundary is a terminator followed by whitespace and an
# opening capital or markup character, which avoids splitting on "v3." or "~1M."
SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+(?=[A-Z`*\[])")
# Gate A7. 3-letter month prefixes, so both "Sep" and "September" resolve.
MONTHS = {m: i for i, m in enumerate(
    ["jan", "feb", "mar", "apr", "may", "jun",
     "jul", "aug", "sep", "oct", "nov", "dec"], start=1)}
# Gate A7. The 3 date shapes a brief realistically carries: ISO, US-style and
# day-first. Order matters only in that each pattern's groups are read by index.
DATE_PATTERNS = (
    re.compile(r"\b(\d{4})-(\d{2})-(\d{2})\b"),
    re.compile(r"\b([A-Z][a-z]{2})[a-z]*\.?\s+(\d{1,2}),?\s+(\d{4})\b"),
    re.compile(r"\b(\d{1,2})\s+([A-Z][a-z]{2})[a-z]*\.?\s+(\d{4})\b"),
)
# Gate A7. Words that show the line already tells the reader the date has gone
# by, which is the whole thing the gate is asking for.
STALE_MARKER = re.compile(r"\b(ago|passed|overdue|already|elapsed|slipped)\b", re.I)


@dataclass
class Gate:
    id: str
    name: str
    passed: bool
    evidence: list[str]


def default_config_path() -> str:
    """config.yaml sits beside the skill root, one level above this script."""
    return os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "config.yaml")


def read_config(path: str) -> dict:
    """Pull the flat scalars and short lists this script needs from config.yaml.

    Deliberately not a YAML parser: the values needed are 2 levels deep, so a
    line scanner is enough and adds no dependency. Anything it cannot read falls
    back to the documented default rather than failing the run.
    """
    values: dict = {}
    section = key = None
    try:
        with open(path, encoding="utf-8") as fh:
            lines = fh.readlines()
    except OSError:
        return values
    for raw in lines:
        line = raw.rstrip("\n")
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        line = re.sub(r"\s+#.*$", "", line)
        top = re.match(r"^([A-Za-z_][A-Za-z0-9_-]*):\s*(.*)$", line)
        if top:
            section, key = top.group(1), None
            continue
        nested = re.match(r"^\s{2}([A-Za-z_][A-Za-z0-9_-]*):\s*(.*)$", line)
        if nested and section:
            key = nested.group(1)
            val = nested.group(2).strip().strip('"').strip("'")
            values[(section, key)] = val if val else []
            continue
        item = re.match(r"^\s+-\s*(.*)$", line)
        if item and section and key is not None:
            bucket = values.get((section, key))
            if isinstance(bucket, list):
                bucket.append(item.group(1).strip().strip('"').strip("'"))
    return values


def config_int(cfg: dict, section: str, key: str, fallback: int) -> int:
    try:
        return int(str(cfg[(section, key)]).strip())
    except (KeyError, TypeError, ValueError):
        return fallback


def config_float(cfg: dict, section: str, key: str, fallback: float) -> float:
    try:
        return float(str(cfg[(section, key)]).strip())
    except (KeyError, TypeError, ValueError):
        return fallback


def config_families(cfg: dict) -> frozenset:
    """Diagram families config marks on-request-only.

    Config lists these in the reader's words, so entries naming something the
    script has no family for are ignored rather than guessed at.
    """
    raw = cfg.get(("diagrams", "on_request_only"))
    if not isinstance(raw, list) or not raw:
        return DEFAULT_ON_REQUEST_ONLY
    named = {v.strip().lower() for v in raw}
    picked = {f for f in KNOWN_DIAGRAM_FAMILIES if f in named}
    return frozenset(picked) if picked else DEFAULT_ON_REQUEST_ONLY


def strip_fences(lines: list[str]) -> tuple[list[tuple[int, str]], list[tuple[str, list[str]]]]:
    """Return (prose lines with 1-based numbers, fenced blocks as (lang, body))."""
    prose: list[tuple[int, str]] = []
    blocks: list[tuple[str, list[str]]] = []
    lang, body, in_fence = "", [], False
    for n, raw in enumerate(lines, start=1):
        line = raw.rstrip("\n")
        fence = re.match(r"^\s*(?:```|\u200b```)(\w*)\s*$", line)
        if fence:
            if in_fence:
                blocks.append((lang, body))
                lang, body, in_fence = "", [], False
            else:
                lang, in_fence = fence.group(1).lower(), True
            continue
        if in_fence:
            body.append(line)
        else:
            prose.append((n, line))
    if in_fence:
        blocks.append((lang, body))
    return prose, blocks


def gate_lead_line(prose: list[tuple[int, str]]) -> Gate:
    title_idx = next((i for i, (_, l) in enumerate(prose)
                      if l.startswith("## ")), None)
    if title_idx is None:
        return Gate("A1", "lead line", False, ["no '## ' title found"])
    title = prose[title_idx][1][3:].strip()
    if not title.lower().startswith("summary:"):
        return Gate("A1", "lead line", False,
                    [f"title must start with 'Summary:', got {title[:60]!r}"])
    lead: list[str] = []
    for _, line in prose[title_idx + 1:]:
        if not line.strip():
            if lead:
                break
            continue
        if line.startswith("#"):
            return Gate("A1", "lead line", False,
                        ["a heading sits between the title and any lead line"])
        lead.append(line.strip())
    text = " ".join(lead)
    if not text:
        return Gate("A1", "lead line", False, ["no lead line under the title"])
    count = len(SENTENCE_SPLIT.split(text))
    # 2 sentences is the skill's stated limit: 1 for the spine, at most 1 more
    # to scope it.
    ok = count <= 2
    return Gate("A1", "lead line", ok,
                [] if ok else [f"lead line runs {count} sentences: {text[:90]}..."])


def gate_headings(prose: list[tuple[int, str]]) -> Gate:
    bad = [f"L{n}: {l.strip()}" for n, l in prose
           if l.startswith("#")
           and l.lstrip("#").strip().lower().rstrip(":") in BANNED_HEADINGS]
    return Gate("A2", "informative headings", not bad, bad)


def gate_bold(prose: list[tuple[int, str]], budget: int) -> Gate:
    """Bold budget for emphasis only.

    The mandated diagram label and the mandated "Your move:" label are
    structural, not emphasis, so both are exempt. Counting them would make the
    gate unpassable on a brief with several structural sections, since every
    diagram carries a label by rule and every full brief carries a move line.
    """
    spans = [m for _, l in prose
             for m in re.findall(
                 r"\*\*[^*]+\*\*",
                 YOUR_MOVE_LOOSE.sub("", DIAGRAM_LABEL.sub("", l)))]
    ok = len(spans) <= budget
    return Gate("A3", "bold budget", ok,
                [] if ok else
                [f"{len(spans)} bold spans against a budget of {budget}: "
                 + ", ".join(spans[:8])])


def spelling_enforced(variant: str) -> bool:
    """Whether A4 should run its US-spelling check for this variant.

    An unnamed variant means nobody chose one, so the check is skipped rather
    than defaulted: a gate that quietly imposes a variant fails a brief for
    being written correctly.
    """
    return bool(variant.strip()) and variant.strip().lower() not in US_VARIANTS


def gate_style(prose: list[tuple[int, str]], check_spelling: bool) -> Gate:
    bad: list[str] = []
    for n, line in prose:
        s = line.strip()
        if not s or s.startswith("#") or s.startswith("|"):
            continue
        body = BOLD_LABEL_LEAD_IN.sub("", s)
        body = re.sub(r"`[^`]*`", "", body)
        if "\u2014" in body:
            bad.append(f"L{n}: em dash in sentence")
        # A bullet label runs at most 24 characters before its colon; anything
        # longer is a sentence that swallowed a colon rather than a label.
        if re.search(r"\w:\s+\S", body) and not re.match(r"^\s*[-*]\s*\w[\w ]{0,24}:\s", s):
            bad.append(f"L{n}: colon inside sentence")
        if SPELLED_NUMBERS.search(body):
            bad.append(f"L{n}: spelled-out number '{SPELLED_NUMBERS.search(body).group(0)}'")
        if check_spelling and US_SPELLINGS.search(body):
            bad.append(f"L{n}: US spelling '{US_SPELLINGS.search(body).group(0)}'")
    name = "style" if check_spelling else "style (spelling not checked)"
    return Gate("A4", name, not bad, bad)


def gate_diagrams(blocks: list[tuple[str, list[str]]], allowed: set,
                  on_request_only: frozenset) -> list[Gate]:
    mermaid = [b for lang, b in blocks if lang == "mermaid"]
    parse_bad: list[str] = []
    type_bad: list[str] = []
    for i, body in enumerate(mermaid, start=1):
        head = next((l.strip() for l in body if l.strip()), "")
        key = head.split()[0].lower() if head else ""
        kind = KNOWN_DIAGRAM_HEADERS.get(key)
        if kind is None:
            parse_bad.append(f"diagram {i}: unrecognised header '{head[:40]}'")
            continue
        text = "\n".join(body)
        # Unbalanced brackets are the failure mode mermaid reports as a bare
        # syntax error, so they are checked before anything subtler.
        for open_c, close_c in (("[", "]"), ("(", ")"), ("{", "}")):
            if text.count(open_c) != text.count(close_c):
                parse_bad.append(
                    f"diagram {i}: unbalanced '{open_c}{close_c}'")
        if text.count('"') % 2:
            parse_bad.append(f"diagram {i}: odd number of quotes")
        if kind in on_request_only and kind not in allowed:
            type_bad.append(f"diagram {i}: '{kind}' is on-request-only and was not requested")
    return [
        Gate("A5", "mermaid parses", not parse_bad, parse_bad),
        Gate("A6", "diagram type permitted", not type_bad, type_bad),
    ]


def parse_date(m: re.Match, which: int) -> "date | None":
    from datetime import date as _date
    try:
        if which == 0:
            y, mo, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
        elif which == 1:
            mo = MONTHS.get(m.group(1).lower())
            if mo is None:
                return None
            d, y = int(m.group(2)), int(m.group(3))
        else:
            mo = MONTHS.get(m.group(2).lower())
            if mo is None:
                return None
            d, y = int(m.group(1)), int(m.group(3))
        return _date(y, mo, d)
    except ValueError:
        return None


def gate_stale_dates(prose: list[tuple[int, str]], today: "date") -> Gate:
    """Any date already in the past must be flagged as past on the same line.

    Catches the failure where a brief repeats a source's due date as if it is
    still ahead, when it has already gone by.
    """
    bad: list[str] = []
    for n, line in prose:
        if line.strip().startswith("|") or line.strip().startswith("#"):
            continue
        for which, pat in enumerate(DATE_PATTERNS):
            for m in pat.finditer(line):
                d = parse_date(m, which)
                if d is None or d >= today:
                    continue
                if STALE_MARKER.search(line):
                    continue
                bad.append(
                    f"L{n}: '{m.group(0)}' is in the past as of {today} "
                    f"and the line does not say so")
    return Gate("A7", "no unflagged past date", not bad, bad)


# Gate A8. Words carrying no topic signal, removed so overlap measures subject
# matter rather than grammar.
STOPWORDS = frozenset("""
a an and are as at be been but by can could did do does for from had has have how
if in into is it its may might must not of on or should so than that the their
then there these they this those to was were what when which who will with would
you your it's we our us also only just still both each per via
""".split())


def content_words(text: str) -> set:
    text = re.sub(r"`[^`]*`", " ", text)
    text = re.sub(r"[*_\[\]()<>|#]", " ", text)
    words = re.findall(r"[A-Za-z][A-Za-z'-]+", text.lower())
    # Words of 3 characters or more, since shorter tokens are almost all
    # grammar and inflate overlap between unrelated statements.
    return {w for w in words if len(w) > 2 and w not in STOPWORDS}


def prose_units(prose: list[tuple[int, str]]) -> list[tuple[int, str]]:
    """Sentences and bullets a reader would experience as separate statements."""
    units: list[tuple[int, str]] = []
    for n, line in prose:
        s = line.strip()
        if not s or s.startswith("#") or s.startswith("|") or s.startswith(">"):
            continue
        # The move line restates a layer 2 fact as an action by design, so it
        # overlaps the bullet it acts on. A9 owns it; counting it here would make
        # the mandated line trip the restatement gate.
        if YOUR_MOVE_LOOSE.match(s):
            continue
        s = re.sub(r"^[-*]\s+", "", s)
        s = BOLD_LABEL_LEAD_IN.sub("", s).strip()
        for part in SENTENCE_SPLIT.split(s):
            part = part.strip()
            if part:
                units.append((n, part))
    return units


def gate_restatement(prose: list[tuple[int, str]], threshold: float) -> Gate:
    """Flag statements that say the same thing twice in different places.

    The recurring failure is a fact appearing once in a diagram caption and
    again in a bullet. Overlap of content words catches that without judging
    style. The threshold is deliberately high, so it reports duplication rather
    than mere topical similarity.
    """
    units = [(n, t, content_words(t)) for n, t in prose_units(prose)]
    # Statements with fewer than 5 content words are too short for an overlap
    # ratio to mean anything, so they are excluded rather than false-flagged.
    units = [(n, t, w) for n, t, w in units if len(w) >= 5]
    bad: list[str] = []
    seen: set = set()
    for i in range(len(units)):
        for j in range(i + 1, len(units)):
            n1, t1, w1 = units[i]
            n2, t2, w2 = units[j]
            if n1 == n2:
                continue
            overlap = len(w1 & w2) / len(w1 | w2)
            if overlap >= threshold and (n1, n2) not in seen:
                seen.add((n1, n2))
                bad.append(
                    f"L{n1} and L{n2} overlap {overlap:.0%}: "
                    f"{t1[:48]!r} vs {t2[:48]!r}")
    return Gate("A8", "no restatement", not bad, bad)


def gate_your_move(prose: list[tuple[int, str]]) -> Gate:
    """A9. The brief names what the reader does next, high enough to be seen.

    A reader who stops after layer 2 is the common case, so a move buried at the
    end of layer 4 is a move they never read. The label is fixed text so the gate
    can find it and so the reader can find it by shape while scanning.

    An explicit "none, informed only" passes. Silence does not, because the
    reader cannot tell silence from an oversight.
    """
    name = "reader's move named"
    hits = [(n, m.group(1).strip())
            for n, l in prose if (m := YOUR_MOVE.match(l))]
    if not hits:
        near = [(n, l.strip()) for n, l in prose if YOUR_MOVE_LOOSE.match(l)]
        if near:
            n, txt = near[0]
            return Gate("A9", name, False,
                        [f"L{n}: label must read exactly '**Your move:**', got "
                         f"{txt[:40]!r}"])
        return Gate("A9", name, False,
                    ["no '**Your move:**' line found; add one inside layer 2, "
                     "above the first '###' section"])
    if len(hits) > 1:
        return Gate("A9", name, False,
                    [f"{len(hits)} '**Your move:**' lines, on L"
                     + ", L".join(str(n) for n, _ in hits)])
    line_no, body = hits[0]
    # Any section heading above the move line means it has sunk out of layer 2.
    # The title is the first '## ', so it is excluded; everything after it counts,
    # including '####' and a second '## '. Same shape as A1's rule that no
    # heading sits between the title and the lead.
    heads = [n for n, l in prose if re.match(r"^#{2,6}\s", l)]
    if not heads or line_no < heads[0]:
        return Gate("A9", name, False,
                    [f"L{line_no}: move line sits above the title, where the "
                     f"lead line belongs"])
    above = [n for n in heads[1:] if n < line_no]
    if above:
        return Gate("A9", name, False,
                    [f"L{line_no}: move line sits below the section starting on "
                     f"L{above[0]}, so a layer 2 reader never reaches it"])
    # 3 words is the floor at which a move can name an actor or an object, and
    # it is what the shortest legitimate answer, "none, informed only", needs.
    if len(body.split()) < 3:
        return Gate("A9", name, False,
                    [f"L{line_no}: move line carries {len(body.split())} word(s)"
                     f", too few to name a move: {body!r}"])
    return Gate("A9", name, True, [])


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("draft")
    ap.add_argument("--allow-diagram-type", default="",
                    help="comma-separated types the reader named, e.g. class")
    ap.add_argument("--today", default="",
                    help="YYYY-MM-DD override for the stale-date gate")
    ap.add_argument("--english-variant", default="",
                    help="the reader's variant, e.g. Australian, British, "
                         "American. Omitted, A4 skips its spelling check and "
                         "says so")
    ap.add_argument("--config", default="",
                    help="path to the skill's config.yaml (default: beside the "
                         "skill root)")
    ap.add_argument("--restatement-threshold", type=float, default=None,
                    help="content-word overlap at which 2 statements count as "
                         "restatement; overrides config")
    args = ap.parse_args()
    allowed = {t.strip().lower() for t in args.allow_diagram_type.split(",") if t.strip()}

    config_path = args.config or default_config_path()
    cfg = read_config(config_path)
    bold_budget = config_int(cfg, "gates", "bold_span_budget", DEFAULT_BOLD_BUDGET)
    threshold = (args.restatement_threshold if args.restatement_threshold is not None
                 else config_float(cfg, "gates", "restatement_threshold",
                                   DEFAULT_RESTATEMENT_THRESHOLD))
    on_request_only = config_families(cfg)

    try:
        with open(args.draft, encoding="utf-8") as fh:
            lines = fh.readlines()
    except OSError as exc:
        print(json.dumps({"error": f"cannot read draft: {exc}"}, indent=2))
        return 1
    prose, blocks = strip_fences(lines)

    from datetime import date, datetime
    try:
        today = (datetime.strptime(args.today, "%Y-%m-%d").date()
                 if args.today else date.today())
    except ValueError:
        print(json.dumps(
            {"error": f"--today must be YYYY-MM-DD, got {args.today!r}"}, indent=2))
        return 1

    check_spelling = spelling_enforced(args.english_variant)
    gates = [gate_lead_line(prose), gate_headings(prose),
             gate_bold(prose, bold_budget),
             gate_style(prose, check_spelling),
             *gate_diagrams(blocks, allowed, on_request_only),
             gate_stale_dates(prose, today),
             gate_restatement(prose, threshold),
             gate_your_move(prose)]
    failed = [g for g in gates if not g.passed]
    print(json.dumps({
        "config_read": config_path if cfg else f"{config_path} (unreadable, using defaults)",
        "thresholds": {"bold_span_budget": bold_budget,
                       "restatement_threshold": threshold,
                       "on_request_only": sorted(on_request_only)},
        "english_variant": (args.english_variant.strip() if args.english_variant.strip()
                            else "not named, so A4 checked no spelling"),
        "mechanical_gates": [asdict(g) for g in gates],
        "passed": len(gates) - len(failed),
        "total": len(gates),
        "verdict": "PASS" if not failed else "FAIL",
    }, indent=2))
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
