# Audiences

Read the section matching the key Step 1 resolved, once, before reading any source. Each section keys to an entry under `audiences` in `config.yaml`, which holds its label, default window and triggers.

The "where signal hides" lists jog recall. They are not a checklist to work through. The 2 gates in `SKILL.md` decide what ships.

## Contents

- `team-standup`
- `product-partner`
- `manager`
- `peer-leads`
- `report-1on1`
- Freeform

---

## `team-standup`

**Audience.** The user's own team. They report to the user.

**Goal.** Visibility on what the team cannot already see. Their delivery work lives in tickets and reviews, and they update each other on it. This slot is for everything else that lands on them.

**Tone.** Team-facing and plain. Say the thing, then what it means for them. No leadership vocabulary.

**Where signal hides:**

- Leads syncs, reviews, all-hands and leadership forums the team was not in
- Decisions made above the team, or by another team, that now land on this one
- Process changes: review policy, on-call, cadence, tooling
- Priority, scope or deadline shifts, including dates that just became real
- Cross-team asks arriving at this team
- Incidents touching surfaces this team owns
- Stakeholder feedback that reached the user and not them
- Logistics: absences, joiners, role changes, cycle deadlines
- Things the user is unblocking for them, so they stop working around it
- Recognition from outside the team

**Suppress:**

- Anything whose only home is a ticket, a pull request, or an update a team member gives themselves
- The user's own admin and calendar
- Speculation with no decision behind it
- Anything from a 1:1 the person has not shared with the team

---

## `product-partner`

**Audience.** The user's product manager, 1:1.

**Goal.** Settle scope, deadline and opportunity before they drift. Leave with decisions or owners, not updates.

**Tone.** Direct and trade-off first. Name the ask and the cost of each answer.

**Where signal hides:**

- Scope requests and what each would cost in time or people
- Dates at risk, and the date by which a call is needed
- Incoming asks from other teams that compete for the same capacity
- Experiment results, data or customer feedback that changes a bet
- Technical constraints or debt that limit what product can promise
- Opportunities the team spotted that product has not

**Suppress:**

- Delivery progress product can read in the tracker
- Team-internal process and people matters
- Engineering detail below what changes a product decision

---

## `manager`

**Audience.** The user's own manager, 1:1.

**Goal.** Alignment. What the user needs a view, a decision, backing or air cover on, and what the manager would be caught out by if they heard it elsewhere.

**Tone.** Outcome-focused. Impact first, then the ask. Where there is no ask, say what they need to know and stop.

**Where signal hides:**

- Escalations the user cannot clear at their own level
- Commitments at risk, with the date and the lever
- Capacity and priority conflicts across teams
- Decisions the user made that the manager should hear first
- People matters needing support, at the level the manager needs
- Cross-team friction that may reach the manager another way

**Suppress:**

- Status the manager already gets in writing
- Anything already raised and answered in the window
- Detail below the level the manager can act on

---

## `peer-leads`

**Audience.** Peer engineering leads and product managers across teams.

**Goal.** Surface blockers, dependencies and risks that need this room, and give a heads-up on anything about to land on another team.

**Tone.** Outcome-focused. Lead with the impact, name who holds what, then the ask.

**Where signal hides:**

- Cross-team dependencies that have stalled, and who holds them
- Asks from another team the user's team cannot meet by their date
- Risks to a committed date or scope that touch other teams
- Work about to collide with a peer's team
- Shared process, platform or on-call changes
- Incidents with blast radius beyond the user's team

**Suppress:**

- Business-as-usual progress
- Team-internal process the room cannot act on
- Anything from a 1:1
- Anything already escalated in the window and answered

---

## `report-1on1`

**Audience.** One person who reports to the user.

**Goal.** Know what to raise with them and what to pay attention to: context they are missing, decisions that change their work, follow-ups the user owes them, and growth opportunities.

**Tone.** People-first and specific. Context before ask.

**Where signal hides:**

- Decisions or changes elsewhere that touch this person's work
- Opportunities matching what they said they want
- Follow-ups from earlier 1:1s with this person
- Feedback about their work that reached the user
- Workload signals: on-call, incidents, review load, leave

**Suppress:**

- Anything from another person's 1:1, in either direction
- Team news already given at standup, unless it lands on them specifically
- Feedback the user has not decided to share yet

---

## Freeform

Where no audience fits, take 3 things from the user and follow `SKILL.md` unchanged:

- **Audience.** Who is in the room and what they can act on.
- **Goal.** What the slot is for.
- **Window.** A mode from `windows` in `config.yaml`, or a custom range.

Apply the confidentiality rule as for the widest audience in the room.
