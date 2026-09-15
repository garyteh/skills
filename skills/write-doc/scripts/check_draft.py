#!/usr/bin/env python3
"""Deterministic gate checks for a write-doc draft.

Grades only the rules a script can decide with no judgement. The judgement pass
and the cold-reader simulation are not checked here and stay with the agent.

EXECUTE this file. Nothing in the skill needs to read it.

Usage:
    python3 check_draft.py DRAFT.md --genre argument
    python3 check_draft.py DRAFT.md --genre task [--english-variant Australian]
                                    [--allow-acronym DACI]

Exit code 0 if every gate for the genre passes, 1 otherwise. Findings print as
JSON.

The genre is not optional. The 2 genres hold opposite rules about bold, about
where detail goes and about how a document opens, so grading a how-to against
the argument gates reports failures that are correct behaviour.

Thresholds and word lists come from the skill's config.yaml, read at run time, so
no value is stated twice. A command-line flag overrides config; a missing or
unreadable config falls back to the defaults named beside each value below.

The English variant is not a config value: it belongs to the run, not the
install. Without --english-variant the spelling check is skipped and the verdict
says so, because enforcing a variant nobody named is worse than enforcing none.

No third-party imports, so the script runs anywhere Python 3 does.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, field

# --- documented fallbacks, used only when config.yaml cannot be read ---------

DEFAULT_SENTENCE_AVG_MAX = 20.0
DEFAULT_SENTENCE_HARD_MAX = 30
DEFAULT_ANCHOR_MIN_WORDS = 2
DEFAULT_ANCHOR_MAX_WORDS = 4
DEFAULT_BOLD_BUDGET = 8
DEFAULT_WORDS_PER_STEP = 20
DEFAULT_INTRO_SENTENCES = 2
DEFAULT_PROSE_BETWEEN_STEPS = 1

# Below this many sentences an average means nothing, so only the hard max
# applies.
MIN_SENTENCES_FOR_AVERAGE = 5

DEFAULT_BLOAT = {
    "utilise": "use", "utilize": "use", "leverage": "use",
    "in order to": "to", "due to the fact that": "because",
    "in the event that": "if", "commence": "start", "ascertain": "find out",
    "terminate": "stop", "endeavour": "try", "at this point in time": "now",
    "a number of": "state the number",
}
DEFAULT_SLOP = (
    "delve", "pivotal", "realm", "synergy", "seamlessly", "multifaceted",
    "game-changer", "robust solution", "best-in-class",
    "it is important to note that", "serves as", "stands as", "boasts",
)
# "just" is deliberately absent here and present in the task list: in argument
# prose it reads as "only" far more often than as a minimiser.
DEFAULT_MINIMISERS = (
    "simply", "obviously", "of course", "merely", "trivially",
    "needless to say",
)
DEFAULT_MINIMISERS_TASK = (
    "easy", "easily", "quick", "quickly", "just", "all you need to do",
    "it is that simple",
)
DEFAULT_WARM_CLOSERS = (
    "see you out there", "happy to help", "let me know if", "feel free to",
    "hope this helps", "thanks in advance",
)
DEFAULT_ACRONYM_ALLOWLIST = {
    "API", "CPU", "CSV", "DB", "GDPR", "HTTP", "HTTPS", "ID", "JSON", "PR",
    "QA", "SDK", "SLA", "SLO", "SQL", "TTL", "URL", "UTC", "UI", "UX", "YAML",
    "OK", "TODO", "FAQ", "AU", "US", "UK", "EU", "AM", "PM", "AI",
}
DEFAULT_STEP_VERBS = (
    "select", "choose", "clear", "enter", "open", "close", "go", "turn",
    "move", "drag", "copy", "save", "run", "check", "wait", "repeat",
    "review", "confirm",
)

# --- patterns ---------------------------------------------------------------

SPELLED_NUMBERS = re.compile(
    r"\b(two|three|four|five|six|seven|eight|nine|ten)\b", re.I)

# The -ize and -or spellings that most often leak into a draft written in a
# variant that does not use them. "licence" is deliberately absent: it is the
# correct spelling in every variant this check is aimed at, and matching it
# failed a correct draft.
US_SPELLINGS = re.compile(
    r"\b(organiz\w*|color\w*|behavior\w*|prioritiz\w*|analyz\w*|optimiz\w*"
    r"|recogniz\w*|summariz\w*|license\w*|center|centers|centered"
    r"|defense|offense|catalog|catalogs)\b", re.I)

ACRONYM = re.compile(r"\b[A-Z][A-Z0-9]{1,5}\b")

TOP_BULLET = re.compile(r"^[-*]\s+(?!\[[ xX]\])(.*)$")
BULLET_ANCHOR = re.compile(r"^\*\*([^*]+?)\*\*")

STRAWMAN = re.compile(r"\(strawman", re.I)
SOFT_MARKER = re.compile(r"\((assumption|gap|inferred|retrieved)", re.I)

HTML_TAG = re.compile(r"<(?!!--)/?[a-zA-Z][^>]*>")

LONG_DASH = re.compile(r"[—–]")
INLINE_CODE = re.compile(r"`[^`]*`")
URL = re.compile(r"https?://\S+")
BOLD_SPAN = re.compile(r"\*\*[^*]+\*\*")
# A bold label is structure, not a sentence, so its colon is exempt. Matched
# anywhere on the line, because a line can carry several.
BOLD_LABEL = re.compile(r"\*\*[^*]+:\*\*")
CLOCK_TIME = re.compile(r"\b\d{1,2}:\d{2}\b")
# The mandated prefix for an optional step. Its colon is structure, so it is
# exempt from the mid-sentence colon check the same way a bold label is.
OPTIONAL_PREFIX = re.compile(r"^\s*Optional:\s*", re.I)

APPENDIX_HEADING = re.compile(r"^#{1,6}\s+.*\bappendi(x|ces)\b", re.I)
BODY_SAFE_FENCES = {"", "text", "mermaid", "markdown", "md", "quote"}

OWNER_LABEL = re.compile(
    r"\*\*\s*(owner|owners|approver|driver|accountable|responsible|dri)\s*:?\s*\*\*",
    re.I)
UNASSIGNED = re.compile(r"\bUNASSIGNED\b")

BOTTOM_LINE = re.compile(r"^\s*(?:[-*>]\s+)?\*\*Bottom line:\*\*\s*\S")
BOTTOM_LINE_LOOSE = re.compile(r"\*\*\s*bottom\s+line\s*:?\s*\*\*", re.I)
BOTTOM_LINE_WINDOW = 25

NUMBERED_STEP = re.compile(r"^\s{0,3}\d+\.\s+(.*)$")
LIST_LINE = re.compile(r"^\s*(?:[-*+]|\d+\.|[a-z]\.)\s+")
BOLD_ONLY_LINE = re.compile(r"^\*\*[^*]+\*\*\s*$")

BANNED_INPUT_VERBS = re.compile(r"^(click|tap|hit|swipe)\b", re.I)
DIRECTIONAL = re.compile(
    r"\b(above|below|on the right|on the left|the green button|the red button"
    r"|at the top|at the bottom|see above|see below)\b", re.I)
BAD_LINK_TEXT = re.compile(
    r"\[\s*(click here|here|this page|read more|this document|link|more)\s*\]",
    re.I)
BARE_URL_LINK = re.compile(r"\[\s*https?://")
GERUND_HEADING = re.compile(r"^(how to\b|\w+ing\b)", re.I)
THROAT_CLEARING = re.compile(
    r"\b(this document describes|in this guide we will|before we begin"
    r"|this page is intended to|as you may know"
    r"|it is important to understand that)\b", re.I)
NEGATIVE_CONTRACTION = re.compile(
    r"\b(can't|don't|won't|shouldn't|doesn't|isn't|aren't|didn't|couldn't"
    r"|wouldn't|hasn't|haven't|wasn't|weren't)\b", re.I)
PARENTHETICAL_OPTIONAL = re.compile(r"\(optional\)", re.I)
PREREQ_HEADING = re.compile(
    r"\b(before you start|prerequisites|what you need|before you begin)\b", re.I)
VERIFY_HEADING = re.compile(
    r"\b(check it worked|verify|confirm it worked|how to tell it worked)\b", re.I)

SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+(?=[A-Z`*\[])")

# Advisory only. A be-verb plus a past participle is a decent passive signal and
# a poor passive detector, so it is reported and never failed on.
PASSIVE = re.compile(
    r"\b(is|are|was|were|be|been|being)\s+(\w+ed|done|made|given|taken|shown"
    r"|known|written|built|held|seen|sent|kept|found|set)\b", re.I)
NOMINALISATION = re.compile(
    r"\b\w{4,}(tion|sion|ment|ance|ence|ility)\b", re.I)


@dataclass
class Gate:
    id: str
    name: str
    passed: bool
    evidence: list[str] = field(default_factory=list)


# --- config -----------------------------------------------------------------

def default_config_path() -> str:
    """config.yaml sits beside the skill root, one level above this script."""
    return os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "config.yaml")


def read_config(path: str) -> dict:
    """Pull the scalars, lists and small maps this script needs from config.yaml.

    Deliberately not a YAML parser: the values needed are at most 3 levels deep,
    so a line scanner is enough and adds no dependency. Anything it cannot read
    falls back to the documented default rather than failing the run.

    Keys are (section, key). A value is a string, a list of strings, or a dict
    for the term-to-replacement maps.
    """
    values: dict = {}
    section = key = None
    try:
        with open(path, encoding="utf-8") as handle:
            lines = handle.readlines()
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
            val = top.group(2).strip().strip('"').strip("'")
            if val:
                values[(section, None)] = val
            continue
        nested = re.match(r"^\s{2}([A-Za-z_][A-Za-z0-9_-]*):\s*(.*)$", line)
        if nested and section:
            key = nested.group(1)
            val = nested.group(2).strip().strip('"').strip("'")
            values[(section, key)] = val if val else []
            continue
        item = re.match(r"^\s{4,}-\s*(.*)$", line)
        if item and section and key is not None:
            bucket = values.get((section, key))
            if isinstance(bucket, list):
                bucket.append(item.group(1).strip().strip('"').strip("'"))
            continue
        pair = re.match(r"^\s{4,}\"?([^\":]+)\"?:\s*(.*)$", line)
        if pair and section and key is not None:
            bucket = values.get((section, key))
            if isinstance(bucket, list) and not bucket:
                bucket = {}
                values[(section, key)] = bucket
            if isinstance(bucket, dict):
                bucket[pair.group(1).strip().strip('"')] = \
                    pair.group(2).strip().strip('"').strip("'")
    return values


def cfg_num(cfg, section, key, fallback, cast=int):
    try:
        return cast(str(cfg[(section, key)]).strip())
    except (KeyError, TypeError, ValueError):
        return fallback


def cfg_list(cfg, section, key, fallback):
    raw = cfg.get((section, key))
    if isinstance(raw, dict):
        raw = list(raw)
    if not isinstance(raw, list) or not raw:
        return tuple(fallback)
    return tuple(v.lower() for v in raw)


def cfg_map(cfg, section, key, fallback):
    raw = cfg.get((section, key))
    if not isinstance(raw, dict) or not raw:
        return dict(fallback)
    return {k.lower(): v for k, v in raw.items()}


# --- document splitting -----------------------------------------------------

def split_document(lines):
    """Return (prose, fences, headings) with 1-based line numbers.

    Frontmatter is dropped: it is machinery, not prose, and every gate below
    would misread it.
    """
    start = 0
    if lines and lines[0].strip() == "---":
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                start = i + 1
                break

    prose, fences, headings = [], [], []
    lang, in_fence = "", False

    for n, raw in enumerate(lines[start:], start=start + 1):
        line = raw.rstrip("\n")
        fence = re.match(r"^\s*```(\w*)\s*$", line)
        if fence:
            if in_fence:
                in_fence = False
            else:
                lang, in_fence = fence.group(1).lower(), True
                fences.append((n, lang))
            continue
        if in_fence:
            continue
        heading = re.match(r"^(#{1,6})\s+(.*)$", line)
        if heading:
            headings.append((n, len(heading.group(1)), heading.group(2).strip()))
        prose.append((n, line))
    return prose, fences, headings


def visible_text(line: str, strip_bold: bool = False) -> str:
    """Strip markup that no prose gate should read.

    strip_bold drops bold spans as well, for the gates that must not read an
    interface label. A task document quotes on-screen labels verbatim, including
    their spelling, so reading them as prose fails a correct draft.
    """
    out = INLINE_CODE.sub(" ", line)
    out = URL.sub(" ", out)
    if strip_bold:
        out = BOLD_SPAN.sub(" ", out)
    return out


def sentences(prose):
    """Sentences from body prose, skipping headings, tables and quotes.

    Consecutive lines are joined into their paragraph or list item before
    splitting, because a markdown draft is hard-wrapped and a sentence running
    across 2 lines is one sentence. Measuring line by line reports every wrap as
    a sentence boundary, which both understates the longest sentence and drags
    the average down, so the length gate would pass a draft of 40-word
    sentences. Each sentence is attributed to the line its block starts on.
    """
    found = []
    blocks = []
    start, buffer = None, []

    def flush():
        if buffer and start is not None:
            blocks.append((start, " ".join(buffer)))

    for n, line in prose:
        text = line.strip()
        skip = (not text or text.startswith("#") or text.startswith("|")
                or text.startswith(">") or re.match(r"^[-*+]\s*$", text))
        if skip:
            flush()
            start, buffer = None, []
            continue
        # A new list item or numbered step starts its own block, so 2 bullets
        # never merge into one long sentence.
        if LIST_LINE.match(line):
            flush()
            start, buffer = n, [re.sub(r"^\s*(?:[-*+]|\d+\.|[a-z]\.)\s+", "",
                                       visible_text(text))]
            continue
        if start is None:
            start = n
        buffer.append(visible_text(text))
    flush()

    for n, text in blocks:
        text = re.sub(r"\*\*|__|\*|_", "", text)
        for part in SENTENCE_SPLIT.split(text):
            part = part.strip()
            if part:
                found.append((n, part))
    return found


def word_count(text: str) -> int:
    return len(re.findall(r"[A-Za-z0-9][A-Za-z0-9'\-/$%.]*", text))


def count_sentences(text: str) -> int:
    text = re.sub(r"\*\*|__|\*|_", "", visible_text(text))
    return len([p for p in SENTENCE_SPLIT.split(text) if p.strip()])


# --- gates shared by both genres --------------------------------------------

def gate_sentences(sents, avg_max, hard_max) -> Gate:
    evidence = [f"line {n}: {word_count(s)} words"
                for n, s in sents if word_count(s) > hard_max]
    if len(sents) >= MIN_SENTENCES_FOR_AVERAGE:
        avg = sum(word_count(s) for _, s in sents) / len(sents)
        if avg > avg_max:
            evidence.insert(0, f"average {avg:.1f} words, limit {avg_max}")
    return Gate("G1", "sentence length", not evidence, evidence)


def gate_banned(prose, bloat, slop, minimisers, closers) -> Gate:
    evidence = []
    for n, line in prose:
        low = visible_text(line).lower()
        for term, repl in bloat.items():
            if re.search(rf"\b{re.escape(term)}\b", low):
                evidence.append(f"line {n}: '{term}', use '{repl}'")
        for term in slop:
            if re.search(rf"\b{re.escape(term)}\b", low):
                evidence.append(f"line {n}: '{term}', say the specific thing")
        for term in minimisers:
            if re.search(rf"\b{re.escape(term)}\b", low):
                evidence.append(f"line {n}: '{term}', remove it")
        for term in closers:
            if term in low:
                evidence.append(f"line {n}: '{term}', end on the ask or end")
    return Gate("G2", "banned words", not evidence, evidence)


def gate_numerals(prose) -> Gate:
    evidence = [f"line {n}: '{m.group(1)}'"
                for n, line in prose
                if not line.strip().startswith("#")
                for m in [SPELLED_NUMBERS.search(visible_text(line))] if m]
    return Gate("G3", "numerals not words", not evidence, evidence)


def gate_acronyms(prose, allowed) -> Gate:
    seen, evidence = set(), []
    for n, line in prose:
        # The level 1 heading names the artefact ("DACI - Checkout dedup"), so a
        # document type there is a label rather than undefined jargon.
        if re.match(r"^#\s+", line):
            continue
        text = visible_text(line)
        for m in ACRONYM.finditer(text):
            acr = m.group(0)
            if acr in allowed or acr in seen:
                continue
            seen.add(acr)
            expanded = (f"({acr})" in text
                        or re.search(rf"{re.escape(acr)}\s*\([^)]+\)", text))
            if not expanded:
                evidence.append(f"line {n}: '{acr}' never expanded on first use")
    return Gate("G4", "acronyms expanded", not evidence, evidence)


def gate_headings(headings) -> Gate:
    evidence = []
    h1 = [h for h in headings if h[1] == 1]
    if len(h1) != 1:
        evidence.append(f"{len(h1)} level 1 headings, expected exactly 1")
    previous = 0
    for n, level, _ in headings:
        if previous and level > previous + 1:
            evidence.append(f"line {n}: jumped from h{previous} to h{level}")
        previous = level
    return Gate("G5", "heading hierarchy", not evidence, evidence)


def gate_markdown_only(prose) -> Gate:
    evidence = [f"line {n}: raw HTML '{m.group(0)}'"
                for n, line in prose
                for m in [HTML_TAG.search(visible_text(line))] if m]
    return Gate("G8", "markdown only", not evidence, evidence)


def gate_spelling(prose, variant, strip_bold) -> Gate:
    if not variant:
        return Gate("G9", "english variant (skipped, none named)", True, [])
    evidence = [f"line {n}: '{m.group(1)}'"
                for n, line in prose
                for m in [US_SPELLINGS.search(visible_text(line, strip_bold))]
                if m]
    return Gate("G9", f"english variant ({variant})", not evidence, evidence)


def gate_punctuation(prose) -> Gate:
    evidence = []
    for n, line in prose:
        text = line.strip()
        if not text or text.startswith("#") or text.startswith("|"):
            continue
        text = visible_text(text)
        if LONG_DASH.search(text):
            evidence.append(f"line {n}: long dash, rewrite as 2 sentences")
        stripped = BOLD_LABEL.sub(" ", text)
        stripped = CLOCK_TIME.sub(" ", stripped)
        stripped = re.sub(r"^\s*(?:[-*+]|\d+\.)\s+", "", stripped)
        stripped = OPTIONAL_PREFIX.sub(" ", stripped)
        body = stripped.rstrip()
        # A trailing colon introduces a list and is fine. Anything earlier sits
        # inside a sentence.
        if body and ":" in body[:-1]:
            evidence.append(f"line {n}: colon inside a sentence")
    return Gate("G10", "sentence punctuation", not evidence, evidence)


def gate_ownership(prose) -> Gate:
    for _, line in prose:
        if OWNER_LABEL.search(line):
            return Gate("G12", "ownership stated", True, [])
        # An UNASSIGNED sitting inside a gap marker is a note about what is
        # missing, not a statement of ownership.
        if UNASSIGNED.search(line) and not SOFT_MARKER.search(line):
            return Gate("G12", "ownership stated", True, [])
    return Gate("G12", "ownership stated", False,
                ["no owner, approver or driver named, and no UNASSIGNED marker"])


def gate_markers(prose) -> Gate:
    evidence = [f"line {n}: unresolved strawman, resolve it or mark (assumption)"
                for n, line in prose if STRAWMAN.search(line)]
    return Gate("G15", "no unresolved strawmen", not evidence, evidence)


# --- argument-only gates ----------------------------------------------------

def gate_bullet_anchors(prose, appendix_line, min_words, max_words) -> Gate:
    evidence = []
    for n, line in prose:
        if appendix_line and n >= appendix_line:
            continue
        m = TOP_BULLET.match(line)
        if not m:
            continue
        body = m.group(1).strip()
        if not body or body.startswith("|"):
            continue
        anchor = BULLET_ANCHOR.match(body)
        if not anchor:
            evidence.append(f"line {n}: bullet has no bold skim anchor")
            continue
        words = word_count(anchor.group(1))
        if not min_words <= words <= max_words:
            evidence.append(f"line {n}: anchor is {words} words, "
                            f"want {min_words} to {max_words}")
    return Gate("G6", "bullet skim anchors", not evidence, evidence)


def gate_altitude(fences, appendix_line) -> Gate:
    evidence = [f"line {n}: '{lang}' block sits in the body, move it to an appendix"
                for n, lang in fences
                if lang not in BODY_SAFE_FENCES
                and (appendix_line is None or n < appendix_line)]
    return Gate("G11", "level 4 detail in an appendix", not evidence, evidence)


def gate_bottom_line(prose) -> Gate:
    body = [(n, line) for n, line in prose if line.strip()]
    if any(BOTTOM_LINE.match(line) for _, line in body[:BOTTOM_LINE_WINDOW]):
        return Gate("G13", "bottom line up front", True, [])
    near = [f"line {n}: found a near miss, the label is exactly '**Bottom line:**'"
            for n, line in body if BOTTOM_LINE_LOOSE.search(line)]
    return Gate("G13", "bottom line up front", False,
                near or [f"no '**Bottom line:**' in the first "
                         f"{BOTTOM_LINE_WINDOW} non-blank lines"])


def gate_bold_budget(prose, appendix_line, budget) -> Gate:
    count = 0
    for n, line in prose:
        if appendix_line and n >= appendix_line:
            continue
        text = line.strip()
        if text.startswith("#") or text.startswith("|"):
            continue
        spans = BOLD_SPAN.findall(text)
        bullet = TOP_BULLET.match(text)
        if bullet and BULLET_ANCHOR.match(bullet.group(1).strip()):
            spans = spans[1:]
        spans = [s for s in spans if not s.strip("*").rstrip().endswith(":")]
        count += len(spans)
    passed = count <= budget
    return Gate("G14", "bold budget", passed,
                [] if passed else [f"{count} emphasis bold spans, budget {budget}"])


# --- task-only gates --------------------------------------------------------

def steps_of(prose):
    """Numbered steps as (line, full text), continuation lines folded in.

    A step wrapped across 2 lines is one step. Reading only its first line
    understates its length, so the word cap would pass a step carrying 3
    actions.
    """
    steps = []
    for n, line in prose:
        m = NUMBERED_STEP.match(line)
        if m:
            steps.append([n, m.group(1).strip()])
            continue
        text = line.strip()
        if not steps or not text or text.startswith("#") or LIST_LINE.match(line):
            continue
        # An indented, non-list line directly under a step continues it.
        if line.startswith((" ", "\t")) and steps[-1][0] >= 0:
            steps[-1][1] += " " + text
    return [(n, text) for n, text in steps]


def gate_step_length(prose, cap) -> Gate:
    evidence = [f"line {n}: step is {word_count(visible_text(text))} words, "
                f"cap {cap}, so it carries a second action or an explanation"
                for n, text in steps_of(prose)
                if word_count(visible_text(text)) > cap]
    return Gate("T1", "step length", not evidence, evidence)


def gate_step_verbs(prose) -> Gate:
    evidence = []
    for n, text in steps_of(prose):
        opener = OPTIONAL_PREFIX.sub("", text).strip()
        opener = re.sub(r"^\*\*|^_", "", opener)
        if BANNED_INPUT_VERBS.match(opener):
            word = re.match(r"^(\w+)", opener).group(1)
            evidence.append(f"line {n}: step opens with '{word}', which names one "
                            f"input device, use 'select'")
    return Gate("T2", "step verbs", not evidence, evidence)


def gate_intro(prose, headings, cap) -> Gate:
    h1 = next((n for n, level, _ in headings if level == 1), None)
    if h1 is None:
        return Gate("T3", "opening length", True, [])
    nxt = next((n for n, _, _ in headings if n > h1), None)
    # Joined before counting, because a paragraph wrapped across several lines
    # is still one paragraph. Counting per line turns every wrap into a
    # sentence and fails a correct opening.
    block = []
    for n, line in prose:
        if n <= h1 or (nxt and n >= nxt):
            continue
        text = line.strip()
        if not text or LIST_LINE.match(text) or BOLD_LABEL.search(text):
            continue
        block.append(text)
    total = count_sentences(" ".join(block)) if block else 0
    passed = total <= cap
    return Gate("T3", "opening length", passed,
                [] if passed else
                [f"opening runs {total} sentences, cap {cap}, so it is "
                 f"throat-clearing before the task"])


def gate_prose_between_steps(prose, cap) -> Gate:
    step_lines = [n for n, _ in steps_of(prose)]
    if len(step_lines) < 2:
        return Gate("T4", "prose between steps", True, [])
    by_line = dict(prose)
    evidence = []
    for first, second in zip(step_lines, step_lines[1:]):
        block = []
        for n in range(first + 1, second):
            text = by_line.get(n, "").strip()
            if not text or text.startswith("#") or LIST_LINE.match(text):
                continue
            block.append(text)
        total = count_sentences(" ".join(block)) if block else 0
        if total > cap:
            evidence.append(f"line {first}: {total} sentences of prose before the "
                            f"next step, cap {cap}")
    return Gate("T4", "prose between steps", not evidence, evidence)


def gate_directional(prose) -> Gate:
    evidence = [f"line {n}: '{m.group(1)}', name the element or use "
                f"'the preceding section'"
                for n, line in prose
                for m in [DIRECTIONAL.search(visible_text(line, True))] if m]
    return Gate("T5", "no directional language", not evidence, evidence)


def gate_link_text(prose) -> Gate:
    evidence = []
    for n, line in prose:
        m = BAD_LINK_TEXT.search(line)
        if m:
            evidence.append(f"line {n}: link text '{m.group(1)}' means nothing "
                            f"read on its own")
        if BARE_URL_LINK.search(line):
            evidence.append(f"line {n}: a bare URL as link text")
    return Gate("T6", "link text", not evidence, evidence)


def gate_task_headings(headings) -> Gate:
    """Task headings, the page title included, are bare infinitives.

    The title is checked here where an argument document's is not, because a
    how-to's title names the task the reader came to do.
    """
    evidence = []
    for n, level, text in headings:
        m = GERUND_HEADING.match(text)
        if m:
            evidence.append(f"line {n}: '{text}' is not a bare infinitive, "
                            f"write 'Create a rule' rather than '{m.group(0)}...'")
    return Gate("T7", "task heading form", not evidence, evidence)


def gate_throat_clearing(prose) -> Gate:
    evidence = [f"line {n}: '{m.group(1)}' describes the document instead of "
                f"starting the task"
                for n, line in prose
                for m in [THROAT_CLEARING.search(visible_text(line))] if m]
    return Gate("T8", "no throat-clearing", not evidence, evidence)


def gate_contractions(prose) -> Gate:
    evidence = [f"line {n}: '{m.group(1)}', write it out"
                for n, line in prose
                for m in [NEGATIVE_CONTRACTION.search(visible_text(line))] if m]
    return Gate("T9", "no negative contractions", not evidence, evidence)


def gate_optional_form(prose) -> Gate:
    evidence = [f"line {n}: '(optional)' trails the step, use an 'Optional:' prefix"
                for n, line in prose if PARENTHETICAL_OPTIONAL.search(line)]
    return Gate("T10", "optional step form", not evidence, evidence)


def gate_pretend_headings(prose) -> Gate:
    evidence = [f"line {n}: a bold line standing in for a heading"
                for n, line in prose if BOLD_ONLY_LINE.match(line.strip())]
    return Gate("T11", "no bold pretend headings", not evidence, evidence)


def gate_required_sections(headings, prose) -> Gate:
    texts = [t for _, _, t in headings]
    marked = any(SOFT_MARKER.search(line) for _, line in prose)
    evidence = []
    if not any(PREREQ_HEADING.search(t) for t in texts) and not marked:
        evidence.append("no prerequisites section, and nothing marks it as a gap")
    if not any(VERIFY_HEADING.search(t) for t in texts) and not marked:
        evidence.append("nothing tells the reader how to check it worked, and "
                        "nothing marks it as a gap")
    return Gate("T12", "required sections", not evidence, evidence)


# --- advisories -------------------------------------------------------------

def advisories(sents, prose, genre, step_verbs) -> dict:
    out = {
        "sentences": len(sents),
        "passive_signals": sum(1 for _, s in sents if PASSIVE.search(s)),
        "nominalisation_signals": sum(
            len(NOMINALISATION.findall(s)) for _, s in sents),
        "open_assumptions": sum(
            1 for _, line in prose if SOFT_MARKER.search(line)),
        "note": ("advisory only, never fails the run: the prose detectors carry "
                 "false positives, and a marked assumption is a decision the "
                 "author is allowed to ship"),
    }
    if genre == "task":
        unknown = []
        for n, text in steps_of(prose):
            opener = OPTIONAL_PREFIX.sub("", text).strip()
            opener = re.sub(r"^[*_]+", "", opener)
            first = re.match(r"^([A-Za-z]+)", opener)
            if first and first.group(1).lower() not in step_verbs:
                unknown.append(f"line {n}: step opens with '{first.group(1)}'")
        # Advisory rather than a gate: no verb list is exhaustive, and a gate
        # that fires on a correct verb it has not heard of trains the author to
        # ignore it.
        out["steps_opening_with_an_unlisted_verb"] = unknown
    return out


# --- run --------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(description="Gate checks for a write-doc draft.")
    parser.add_argument("draft", help="path to the draft markdown file")
    parser.add_argument("--genre", required=True, choices=("argument", "task"),
                        help="genre settled at Step 1; selects the gate set")
    parser.add_argument("--english-variant", default="",
                        help="variant to enforce, e.g. Australian; "
                             "the check is skipped when this is absent")
    parser.add_argument("--allow-acronym", action="append", default=[],
                        help="acronym this document may use unexpanded, repeatable")
    parser.add_argument("--config", default="",
                        help="path to the skill's config.yaml "
                             "(default: beside the skill root)")
    args = parser.parse_args()

    try:
        with open(args.draft, encoding="utf-8") as handle:
            lines = handle.readlines()
    except OSError as err:
        print(json.dumps({"error": f"cannot read draft: {err}"}, indent=2))
        return 1

    cfg_path = args.config or default_config_path()
    cfg = read_config(cfg_path)

    avg_max = cfg_num(cfg, "style", "sentence_avg_max", DEFAULT_SENTENCE_AVG_MAX,
                      float)
    hard_max = cfg_num(cfg, "style", "sentence_hard_max", DEFAULT_SENTENCE_HARD_MAX)
    anchor_min = cfg_num(cfg, "style", "bullet_anchor_min_words",
                         DEFAULT_ANCHOR_MIN_WORDS)
    anchor_max = cfg_num(cfg, "style", "bullet_anchor_max_words",
                         DEFAULT_ANCHOR_MAX_WORDS)
    step_cap = cfg_num(cfg, "style", "max_words_per_step", DEFAULT_WORDS_PER_STEP)
    intro_cap = cfg_num(cfg, "style", "max_intro_sentences",
                        DEFAULT_INTRO_SENTENCES)
    between_cap = cfg_num(cfg, "style", "max_prose_sentences_between_steps",
                          DEFAULT_PROSE_BETWEEN_STEPS)
    budget = cfg_num(cfg, "gates", "bold_span_budget", DEFAULT_BOLD_BUDGET)

    bloat = cfg_map(cfg, "banned_words", "bloat", DEFAULT_BLOAT)
    slop = cfg_list(cfg, "banned_words", "slop", DEFAULT_SLOP)
    minimisers = list(cfg_list(cfg, "banned_words", "minimisers",
                               DEFAULT_MINIMISERS))
    closers = cfg_list(cfg, "banned_words", "warm_closers", DEFAULT_WARM_CLOSERS)
    step_verbs = cfg_list(cfg, "style", "step_verbs", DEFAULT_STEP_VERBS)
    if args.genre == "task":
        minimisers += list(cfg_list(cfg, "banned_words", "minimisers_task",
                                    DEFAULT_MINIMISERS_TASK))

    allow_raw = cfg.get(("gates", "acronym_allowlist"))
    allowed = ({a.upper() for a in allow_raw}
               if isinstance(allow_raw, list) and allow_raw
               else set(DEFAULT_ACRONYM_ALLOWLIST))
    allowed |= {a.upper() for a in args.allow_acronym}

    prose, fences, headings = split_document(lines)
    if not prose:
        print(json.dumps({"error": "draft has no body content"}, indent=2))
        return 1

    appendix_line = next(
        (n for n, _, text in headings if APPENDIX_HEADING.match("# " + text)), None)
    sents = sentences(prose)
    task = args.genre == "task"

    gates = [
        gate_sentences(sents, avg_max, hard_max),
        gate_banned(prose, bloat, slop, minimisers, closers),
        gate_numerals(prose),
        gate_acronyms(prose, allowed),
        gate_headings(headings),
        gate_markdown_only(prose),
        gate_spelling(prose, args.english_variant, task),
        gate_punctuation(prose),
        gate_ownership(prose),
        gate_markers(prose),
    ]
    if task:
        gates += [
            gate_step_length(prose, step_cap),
            gate_step_verbs(prose),
            gate_intro(prose, headings, intro_cap),
            gate_prose_between_steps(prose, between_cap),
            gate_directional(prose),
            gate_link_text(prose),
            gate_task_headings(headings),
            gate_throat_clearing(prose),
            gate_contractions(prose),
            gate_optional_form(prose),
            gate_pretend_headings(prose),
            gate_required_sections(headings, prose),
        ]
    else:
        gates += [
            gate_bullet_anchors(prose, appendix_line, anchor_min, anchor_max),
            gate_altitude(fences, appendix_line),
            gate_bottom_line(prose),
            gate_bold_budget(prose, appendix_line, budget),
        ]

    failures = [g for g in gates if not g.passed]
    print(json.dumps({
        "draft": args.draft,
        "genre": args.genre,
        "config": cfg_path if cfg else f"{cfg_path} (unreadable, using defaults)",
        "verdict": "pass" if not failures else "fail",
        # Named rather than silent: a check that did not run is something the
        # reply has to disclose, and it cannot disclose what it cannot see.
        "skipped": ([] if args.english_variant else
                    ["G9 english variant, because no --english-variant was named"]),
        "failed": [{"id": g.id, "name": g.name, "evidence": g.evidence}
                   for g in failures],
        "passed": [g.id for g in gates if g.passed],
        "advisories": advisories(sents, prose, args.genre, step_verbs),
    }, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
