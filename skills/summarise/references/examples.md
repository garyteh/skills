<!-- Reference file for the `summarise` skill. Step and layer numbers refer to SKILL.md. -->

## Worked examples

Both briefs below show layers 1 to 4. Take the voice from them and the layer 5
shape from `intents.md`.

### Quick orient, before a meeting (layers 1 and 2 only)

~~~
## Summary: Dispatch Service design
Proposal to pull dispatch out of the monolith into its own service.
In review, and you're a named reviewer.

**Your move:** push for a circuit breaker on the Carrier API call before you LGTM.

**Owners:** Hermione drives, Platform Infra. Approvers are you and SRE. You have a vote.

**Blocked on:** SRE's fallback review.

**What to scrutinise:** the design puts a synchronous Carrier API call on the
booking path. Everything else in the split is routine.

- The win is real. It ends the 45-minute monolith regression that's caused 3
  delayed releases.
- No circuit breaker yet if the carrier is slow or down, so booking wears the latency.
- Hermione is LGTM. SRE review still open on the fallback.
~~~

### Full brief, a technical design (all 4 layers)

~~~
## Summary: triggering the retry banner when a carrier booking fails
Design for the frontend trigger that calls the Shipments Service once when a
booking fails, so the retry banner can fire. Rendering the banner is out of scope.

**Your move:** set the `RejectionReason` value, or this slice cannot start.

**The crux:** the frontend calls the Shipments Service directly on failure rather
than waiting for a backend push, which is what keeps this first slice off the
booking critical path.

- Today's failed-booking UX is hardcoded and reason-unaware, so no retry flow can
  target it.
- The trigger fires exactly once, on the booking state flip, behind 3 guards.
- It fails closed. Any error leaves today's experience unchanged.
- The `RejectionReason` enum value it depends on is still unconfirmed.

### How the trigger fires
**Diagram (AI-generated) — flowchart:**
```mermaid
flowchart TD
    rej["Carrier returns a rejection"] --> flip{"BOOKED to REJECTED?"}
    flip -->|no| idle["No call, unchanged UX"]
    flip -->|yes| guard{"Flag on, not dismissed,<br/>not already fired?"}
    guard -->|no| idle
    guard -->|yes| call["FE calls the Shipments Service"]
    call --> res{"Retry option available?"}
    res -->|yes| show["Render the retry banner"]
    res -->|"no, or error"| idle
```
The guards are the whole design. Without them the call fires per click.

### Why not the booking store or the confirm controller
The trigger lives in a dedicated installer. Putting it in the booking store would
give a shared store a network side effect. Putting it in the confirm controller
runs it per click, which can't guarantee a single call.

The backend push was rejected for scope, not correctness. It spans 3 teams, and
websocket reconnects drop subscriptions, so a near-identical frontend fallback
would be needed anyway.

### The unconfirmed enum is the only real blocker
- The `RejectionReason` value is owned by the Carrier Integrations team and still
  unset. This blocks the first slice, not just the polish. (inferred)
~~~

Both examples carry a `**Your move:**` line, including the quick orient one. The
Step 5 script only runs on full briefs, so quick orient carries that line, the
owners line and the blocked-on line by instruction rather than by gate. Nothing
mechanical checks them, so they are yours to get right.

The full brief example carries no owners line, which is correct. That shape is
quick orient only.

Where nobody owns the source at all, the line reads:

~~~
**Owners:** UNASSIGNED. No author, no reviewer table, no status field.
~~~

### When not to draw

A rollout with 3 sequential milestones has no branch, no handoff, and no system
boundary. It gets a list, not a timeline. Note the heading names the shape of the
plan rather than saying "Rollout":

~~~
### 3 milestones, roughly 4 weeks end to end
1. M1, FE trigger and guards, ~3 days.
2. M2, batch retry endpoint, ~2 weeks.
3. M3, per-reason retry options, ~1 week.
~~~
