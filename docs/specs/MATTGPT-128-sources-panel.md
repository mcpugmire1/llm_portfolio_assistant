# MATTGPT-128 Sources panel: design spec

Design reference: option **8B** in `Story Detail Sidebar.dc.html` (design tool, not in repo).
This file is the implementable spec; the mock adds nothing the spec omits.

## Decision

The panel is not a citation list and stopping short of claiming to be one was the wrong
fix. Instead: Agy introduces the sources in her own voice, grouped by document kind,
with the answer's figures traced to the story sentence that contains them.

The `SOURCES` header goes away. Two prose lead-in lines replace the two uppercase labels.
The trailing "Want me to dive deeper…" question goes away too.

## Message shape

```
🐾 <answer prose>

Here is where those numbers come from:
  🔗 <ENGAGE story title>
     <extracted sentence containing the figure>
  🔗 <ENGAGE story title>
     <extracted sentence>
  🔗 <ENGAGE story title>
     <extracted sentence>

Matt's own framing on this:
  🔗 <META story title>
  🔗 <META story title>
  🔗 <META story title>
```

Rules:

1. **Group by kind, filter nothing.** Use `_kind_of()` in `backend_service.py`.
   ENGAGE under the first lead-in, META-PN / META-IND under the second. The positioning
   docs were authored to answer "why hire Matt"; removing them from the panel discards
   the most relevant material for the highest-value query.
2. **Order: project record first, framing second.** A glance lands on client work.
3. **A group renders only when populated; its lead-in renders with it.** Never fall back
   to one unlabelled list. A project-record-only panel says the answer is grounded in
   project records; a framing-only panel says there is no project record behind it. Both
   are information an unlabelled list throws away.
4. **Lead-in copy is fixed, not generated.** Two strings. Short enough that repetition
   reads as voice rather than template.
5. **No trailing question.** The lead-in is the invitation; the cards are the mechanism.
   A card click already sends `Tell me more about: <exact title>` and works because the
   title matches exactly: 41 real uses in the query log, the highest-engagement
   affordance on the page. A second invitation below the cards promises nothing new.
6. **Reason lines only on ENGAGE cards, only where a figure matches.** Framing cards
   render bare. A description of what a framing doc *is* would just be a longer title.

## Extraction rule for reason lines

Extract, never generate. The line is a substring of authored story text, so it cannot
hallucinate. (Role Match's `relevance` string is generated, and correctly so: it is the
model *arguing* that evidence satisfies a requirement. A sources reason line instead
asserts what a story *contains*, which is a factual claim about text. Argument surfaces
generate; verification surfaces extract. Worth keeping the two pages deliberately
different rather than silently inconsistent.)

Algorithm:

1. Tokenise the answer's figures (`$10M`, `$100M`, `4x`, `150`, `3%`, …).
2. **Sort longest first.** `$10M` is a substring of `$100M`; without this the HSBC line
   lands on the Innovation Ecosystem card and looks perfectly plausible.
3. Match with boundaries: reject a hit flanked by a digit, `.`/`,`, or a magnitude
   suffix (`M`/`B`/`K`).
4. On a hit, take the containing sentence from that story's Result / Use Case text.
5. **Cap near 20 words.** A 40-word sentence under a card is worse than no line.
6. No hit → no line. Visible degradation is the correct behaviour, not a gap to fill.

Soft claims ("high-trust teams") will not match. That is fine: the claims a skeptic
probes are exactly the ones with distinctive tokens.

## Layout

- **Desktop: three columns**, `SOURCES_COLS_PER_ROW` stays 3. Measured at a 1000px
  capped container: 3 cols = 311px/card, one of six titles reaches three lines; 2 cols =
  472px/card but three rows and ~90px taller. Grid stretches each row to its tallest
  card either way, so neither produces ragged heights.
- **Cap the conversation container** near 1000px. Uncapped it stretches to the monitor
  and cards reach 650px. Capped, the answer prose reaches a comfortable measure with no
  separate `max-width` on the text. Check whether the cap belongs to this page only;
  My Work wants the room for its table and detail pane.
- **Mobile: one column.** A 430px message is 386px of usable width once the 20px padding
  each side and the 4px border are removed.
- **Per-type caps** if any cap is needed, following Role Match. A cap per kind means a
  noisy retrieval cannot crowd out the framing, which no single global cap achieves.

## Values: read from source, do not re-derive

Bubble: `[data-testid="stChatMessage"]:not(:has([data-testid="chatAvatarIcon-user"]))` in `ui/pages/ask_mattgpt/styles.py`:

```
background: var(--chat-ai-bg)          /* #1E1E2E dark, #F9FAFB light */
border-radius: 16px
padding: 20px
border-left: 4px solid var(--chat-ai-border)   /* #8B5CF6, not redefined in dark */
color: var(--text-primary)             /* #E5E7EB dark, #1F2937 light */
box-sizing: border-box
```

Card: `[class*="st-key-related_proj"] button` in `_render_ask_transcript()`, `ui/pages/ask_mattgpt/conversation_helpers.py`:

```
background: var(--bg-surface)          /* #262633 dark, #F9FAFB light */
border: 1px solid var(--border-color)  /* #374151 dark, #E5E7EB light */
color: var(--accent-purple)            /* #8B5CF6 both modes */
font-size: 14px; font-weight: 500; line-height: 1.4
border-radius: 8px; min-height: 56px
```

Two **deliberate deltas** from the current card rule:

- `align-items: flex-start` and left-aligned text, not `center`. Centering is what makes
  a two-line title read as an awkward block instead of a list item.
- `padding: 12px 14px`, not `6px 12px`: a reason line needs the room.

One **fix worth taking while in this file**: card text `#8B5CF6` on `#262633` measures
**3.5:1**, under AA at 14px. The dark theme already has `--accent-purple-text` for
exactly this case and the card rule reads `--accent-purple`. One token swap.

## Vocabulary

Use `evidence_type` semantics, matching `role_match.py`: `profile` and `story`. The split
already exists there under those names; do not introduce a second pair. Display labels
stay reader-facing (the two lead-in lines); field names match Role Match exactly.

## Out of scope

- `get_cited_stories` and inline numbered markers. That is the only version that earns a
  literal `SOURCES` label back, and it is a separate build.
- Renaming either group. The lead-in lines replace labels entirely.
- Deduplicating framing against project record.
- Full conversational memory for bare-noun follow-ups (`cendian`, `banking`). Nine
  observed instances, possibly all test traffic. Cheaper alternative if it recurs: route
  a bare noun that matches a Client or Theme as a filter rather than a semantic search.

## Open

- **Thin answers.** A single-source answer, or one where every source is a framing doc,
  has no trailing line and no strong card row. Whether that reads as abrupt needs a real
  example. The Fiserv query is the test case: four sources, all one kind.
- **HSBC retrieval check** (carried from the original ticket). Confirm the HSBC stories
  are present in `ranked` for the broad revenue query. If they are absent, grouping makes
  that answer *more* misleading while making the panel look more credible: an unrelated
  engagement story with a client and a project shape looks exactly like a valid receipt.
  That needs its own ticket before this ships, and it needs an eval query, not just a
  manual DEBUG run: zero of 64 eval queries currently exercise the title-match path.

## Do not "improve" these

- Positioning docs stay in the panel. They are not noise; they are the Why.
- Reason lines are extracted, never generated.
- No expander, no horizontal scroll, no mobile-only subset. A disclosed subset is still
  a subset, and the honest set is small enough not to need one.
- No uppercase section headers. They are document furniture inside a chat message.
