# How-to style

The mechanics for a task document. Read at Step 5 when the genre is task. The rules that
hold for both genres are in the skill body, not here.

## Contents

1. The shape
2. Steps
3. Verification lines
4. Recovery
5. Naming what is on screen
6. The verb set
7. Headings and titles
8. Lists
9. Links and self-containment
10. Words this genre bans outright
11. Images
12. Accessibility

## 1. The shape

A shape, not a template to fill. Drop a section the document genuinely does not need and
say why. Do not pad a section to fill the outline.

```
# <Task title, bare infinitive, sentence case>

<One sentence: the outcome the reader gets.>
<One sentence: when someone needs this.>

**How long it takes:** <realistic estimate>
**Owner:** <role> · **Last reviewed:** <date>

## Before you start

- <Specific, checkable prerequisite.>

## <First sub-task>

1. <Imperative step.>
2. <Imperative step.> <What the reader now sees.>

## Check it worked

<The observable that proves it.>

## If something goes wrong

**<Symptom>.** <Cause, then fix.>

## Related

<Links the reader may want next. Never a link they need to finish this task.>
```

**How long it takes is a decision, not decoration.** A reader who knows the task runs 20
minutes does not start it with 5 to spare, then abandon it half done.

**`## Related` never carries a link the reader needs.** Anything required to finish
belongs on this page, so a required link here is a self-containment failure wearing a
different heading. Drop the section where nothing genuinely comes next.

**The opening is capped** at `style.max_intro_sentences` sentences. Lead with the outcome,
then say when someone needs this, then stop. No background, no scope statement, no what
you will learn.

Banned openers, exactly: "This document describes", "In this guide we will", "Before we
begin", "This page is intended to", "As you may know", "It is important to understand
that". Each one describes the document instead of starting the task.

**Check it worked is the most valuable section and the one authors skip.** It is what turns
a reader who is unsure into a reader who is finished.

**If something goes wrong** holds the failures that cannot be attributed to one step, and
the answer to who to ask. Everything else goes beside its step.

## 2. Steps

The strongest rules here.

1. Every step opens with an imperative verb from `style.step_verbs` in config.
2. One action per step. Small related actions may share a step through a menu path.
3. **Location before action.** "In the left sidebar, select **Billing**" beats "Select
   **Billing** in the left sidebar".
4. **Goal before action.** "To add a second approver, select **Add**" beats "Select
   **Add** to add a second approver", because it lets a reader skip an instruction that
   does not apply to them.
5. Steps are complete sentences, capitalised, with a full stop.
6. A step runs to at most `style.max_words_per_step` words. Past that it is carrying a
   second action or an explanation.
7. Optional steps take a literal `Optional:` prefix, not a trailing "(optional)".
8. Sub-steps use lowercase letters, and there is no third level.
9. A single-step procedure is a bullet, not a numbered list of one.
10. Include the completing action. The reader does not know the form saves itself.
11. Keep a keypress in the same step as the typing it completes.
12. Give one way, the best way.
13. Never write "run the following command" without saying what the command does.
14. Do not repeat a procedure. Link to it.
15. Prerequisites go at the top, before step 1, always.
16. Past `style.max_steps_per_procedure` steps, split into sub-tasks under their own
    headings, and restate enough context under each that it stands alone.
17. At most `style.max_prose_sentences_between_steps` sentences of prose between 2 steps.
    Prose between steps breaks the reader's place in the procedure.

Inside a complex step the order is action, then command, then what the placeholders mean,
then what the reader sees. The command stays inline at its step. Pushing it to an appendix
is an argument-genre rule and it is wrong here.

## 3. Verification lines

Action first, result second, in the same paragraph.

> Select **Publish**. The status changes to **Live**.

Prefer a concrete observable. "A green **Active** badge appears in the status column"
beats "the rule is now active". Name the common failure beside the step where it happens.
Not every step needs a verification line, but everything consequential does: a save, a
publish, a send, a delete, anything that changes state.

Where the result is only the next step's context, fold it into that step's opening rather
than narrating it twice.

## 4. Recovery

Recovery sits beside the step that fails. An appendix at the bottom is where recovery goes
to be unread.

A document covering only the happy path is not finished. Find the steps where a reader
could plausibly get it wrong, and say what happens and what to do. Where a step is
irreversible or expensive, warn before it, once.

Readers skip boxes and callouts, so anything required to succeed belongs in the step flow
itself. A page with 6 warnings has none, because the reader has stopped seeing them. Four
things therefore never go in a box:

- **A prerequisite.** It goes before step 1, where the reader can still act on it.
- **A step.** A reader scanning for their next action does not read beside the flow.
- **An expected result.** It belongs in the step's own paragraph, straight after the
  action, because that is where the reader looks to check themselves.
- **A second box touching the first.** A note stacked on a warning means the section needs
  reorganising, not another box.

Collapsed content follows the same rule for the same reason: it is for what a reader
consults, such as a long output sample or a full field reference, never for a step, a
prerequisite or a verification. When unsure whether something is a box, write it as
ordinary text and see whether it needed one.

## 5. Naming what is on screen

- Bold every interface element the reader acts on. Not code font, not quotes.
- Match the on-screen capitalisation exactly. An all-caps label becomes sentence case.
- Drop the element type. "Select **Save**" beats "Select the **Save** button".
- Menu paths use a greater-than sign with a space either side, and the whole sequence is
  bolded.
- Strip trailing ellipses and colons from labels.
- Prepositions: *in* a dialog, field, list, menu or pane; *on* a page, tab or toolbar.
- Say *dialog*, not pop-up. *Page*, not window. *Field*, not text box.
- No interface slang. Name the element by its label or its accessible name.
- Never use an interface label as a verb.

## 6. The verb set

Input-neutral, because "select" covers a mouse, a touchscreen and a keyboard where "click"
covers one. Never "click", "tap", "hit" or "swipe".

| Verb | For |
|---|---|
| Select | Anything: a button, link, checkbox, menu item, value in a list, a key |
| Choose | A preference or outcome, where the reader is deciding |
| Clear | A checkbox |
| Enter | Typing a value |
| Open | Apps, panes, files, folders. Not menus |
| Close | Apps, panes, dialogs, files, tabs |
| Go to | Opening a menu, moving to a tab, visiting a page |
| Turn on, turn off | Toggles |
| Move, drag | Direct manipulation |

## 7. Headings and titles

- Sentence case, no full stop, and never an ampersand.
- Task headings are bare infinitives. "Create a rule", never "Creating a rule", "Rule
  creation" or "How to create a rule".
- Non-task headings are noun phrases and do not start with an `-ing` word.
- `Optional:` goes at the front of the heading.
- Never skip a level. Every heading is followed by content, and no heading contains a
  link.
- Do not number headings. A heading roughly every 3 to 5 paragraphs.
- Every heading is answered by the first sentence under it.
- Bold is never a substitute for a heading.
- Headings are removable. Strip them out and the content still reads correctly. Where a
  sentence only makes sense under its heading, rewrite the sentence.
- Parallel in structure at one level. All task headings or all noun phrases, never a mix.

**Restate the context under every new heading.** Readers arrive mid-page from search and
did not read the section above. Naming the thing again costs 3 words and saves a scroll.

## 8. Lists

Numbered for a sequence or a ranking, bulleted for an unordered set. Never a list of one.
The lead-in line is a complete sentence. Numbered steps end with a full stop. No trailing
conjunctions or semicolons. Parallel structure within a list, one sentence per item where
possible.

## 9. Links and self-containment

The reader arrives from search and does not follow links, so **a link is a defect wherever
the linked page holds something needed to finish**. If a fact, a value, a step or a
requirement is required, it belongs on this page. This is the exact opposite of the
argument genre's layering rule, and the difference is the reader: one is deciding and will
read the appendix, the other is mid-task and will not.

- Link text makes sense read on its own, because screen reader users jump link to link.
- Never "click here", "this page", "read more", "this document", "link", or a bare URL as
  link text.
- Front-load the meaningful words.
- The same text always points at the same target, and 2 targets never share text.
- "For more information about X, see Y". *About*, not on. *See*, not refer to.
- Punctuation sits outside the link. Do not force a new tab. Name the file type if the
  link downloads something.
- Links go inline, never into a further-reading dump.

## 10. Words this genre bans outright

**Minimisers**, from `banned_words.minimisers` and `banned_words.minimisers_task` in
config. A reader stuck on a step labelled "easy" concludes the problem is them, and that
is the moment they stop trusting the page and ask someone instead.

**Directional language.** Never "above", "below", "on the right", "the green button", "the
icon at the top". Screen readers have no right-hand side and layouts change. Name the
element by its label, or use "the preceding section" for a document position. Where an
element is genuinely hard to find, a screenshot is the sanctioned fix.

**Vague quantities.** "Several", "a few", "shortly", "may take a while". State the number
or mark it as a gap.

**Hedges and padding.** "Generally", "typically", "in most cases", "you may wish to", "it
is recommended that", "please note", "please".

**Negative contractions.** Write "do not" and "cannot". Positive contractions are fine.

**A pronoun whose referent is more than one sentence back.** Write "the API key", not "it".
Readers arrive mid-page and excerpts get quoted out of context.

Plain replacements: allows you to becomes lets you; via becomes through or by; execute
becomes run; greyed out becomes unavailable; as or since becomes because; once becomes
after. Write "for example", not an abbreviation, because a screen reader says it aloud.

Second person, present tense, active voice, imperative for steps. Passive only to
de-emphasise the reader's mistake: "over 50 conflicts were found" beats "you created over
50 conflicts".

## 11. Images

Fewer than you think. Never an image of text, a command, or terminal output. No fact
appears only in an image. Crop tightly. No personal or customer data, and blurring is
reversible, so use test data.

A screenshot is a confirmation aid and the sanctioned replacement for directional
language, never the only place something is stated. Where an image is needed and not
available, leave `style.screenshot_placeholder` from `config.yaml` at the step that needs
it, with the description filled in. Step 7 counts what is left, so the author knows how
much work is waiting instead of hunting for it.

Alt text is never omitted. Without it a screen reader reads the filename aloud. Keep it
short, do not open with "image of", and give a screenshot that merely duplicates the step
text empty alt text.

## 12. Accessibility

- Colour, size, position and shape never carry meaning alone.
- Real headings in sequence, never bold standing in for one.
- Introduce a table in the text before it. Header cells on the first row only, and never
  merge cells. Avoid tables inside a numbered procedure.
- No load-bearing content in a table or an image alone.
- Left align body text.
- Avoid all caps and camel case in prose, and no forced line breaks inside a paragraph.

The final check: does the page still convey everything with no images, no colour, and a
keyboard only?
