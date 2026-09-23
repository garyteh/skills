<!-- Reference file for the `summarise` skill. Step and layer numbers refer to SKILL.md. -->

## Appendix — Mermaid syntax by diagram type

Match the type to the content (Step 3). All render in Confluence, most markdown
viewers, and chat.

**Contents**

- [C4 Container](#c4-container) — architecture, what a system is made of
- [Flowchart / decision tree](#flowchart--decision-tree) — process, branching logic
- [Swimlane](#swimlane) — who owns which step
- [State](#state) — lifecycle or status machine
- [Timeline](#timeline) — phases, dependencies, parallel tracks
- [Sequence](#sequence) — ordered call flow between deployed services
- [Class](#class) — on request only, and the form for a requested C4 level 4
- [General rules](#general-rules)

### C4 Container

Architecture — what a system is made of:
```
C4Container
    Person(user, "Merchant")
    System_Boundary(ship, "Planet Express") {
        Container(api, "Booking API", "Kotlin/Spring")
        ContainerDb(db, "Shipments DB", "Postgres")
    }
    System_Ext(carrier, "Pony Express API")
    Rel(user, api, "Books a shipment via")
    Rel(api, db, "Reads/writes")
    Rel(api, carrier, "Books a pickup", "sync")
```
`C4Component` (one service's internals) and `C4Context` (cross-system boundaries)
use the same building blocks — `Component(...)` inside `Container_Boundary`, or
`System`/`System_Ext` with no internals. `Rel(from, to, "label", "tech")`; the
tech arg is optional, good for flagging sync/async.

### Flowchart / decision tree

Process, workflow, branching logic:
```
flowchart TD
    req["Rebook request"] --> cls{"Under or over the limit?"}
    cls -->|"under: self-serve"| a["Support: approve in the console"]
    cls -->|"over: needs review"| asmt{"Justified?<br/>owner: TBD"}
    asmt -->|yes| b["Pony Express integration team: manual rebook"]
    asmt -->|no| stop["Align on the trade-off"]
```
`<br/>` for line breaks; quote any label with spaces/punctuation. Put ordering in
the edge labels (`-->|"1. validate"|`) when a flow is ordered.

### Swimlane

Who owns which step — a flowchart with `subgraph` lanes:
```
flowchart LR
    subgraph SUP["Support agent"]
        r["Confirm the shipment and the address"]
    end
    subgraph CAR["Pony Express integration team"]
        cfg["Rebook with the fallback carrier"]
    end
    r --> cfg
```

### State

Lifecycle:
```
stateDiagram-v2
    [*] --> WithinLimit
    WithinLimit --> LimitHit: usage hits 100%
    LimitHit --> WithinLimit: window resets
```

### Timeline

Phases with dependencies or parallel tracks; a straight list of dates gets a
numbered list instead:
```
timeline
    title Delivery, 2 tracks
    section Platform
        Idempotency keys : blocks M2
        Batch retry endpoint : after keys
    section Surfaces
        Hardcoded banner : parallel, no dependency
        Generic CMS surface : after end-to-end testing
```

### Sequence

An ordered call flow between deployed services, the C4 Dynamic view. Every
participant must be independently deployable, so a service, gateway, frontend,
queue or datastore. Never a class, method or handler:
```
sequenceDiagram
    participant FE as Booking page (frontend)
    participant SS as Planet Express API
    participant CA as Pony Express API
    participant DB as Shipments store
    FE->>SS: submitBooking
    SS->>CA: book the pickup
    CA-->>SS: booking result
    SS->>DB: write the shipment
    DB-->>SS: shipment id
    SS-->>FE: confirmation or failure
```
`->>` solid call, `-->>` dashed reply; `Note over FE: ...` for annotations. Name
participants after the deployable, not the code inside it.

### Class

Draw this only when the reader names it, per `diagrams.on_request_only` in
config. It is also the form to use for a requested C4 level 4, scoped to a single
component:
```
classDiagram
    class RebookResolver {
        +resolve(shipmentId, reason) Rebooking
        -filterEligible(list) List
    }
    class RebookRule {
        <<interface>>
        +matches(shipment) boolean
    }
    RebookResolver --> RebookRule : applies
```
`<|--` inheritance, `-->` association, `..>` dependency; `<<interface>>` and
`<<enumeration>>` for stereotypes.

### General rules

One diagram answers one question. If it needs a legend it's too big, so split it
or raise the altitude. Don't invent nodes the source doesn't support.
