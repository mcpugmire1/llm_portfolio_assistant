# Skill Evidence Corpus Work — Working Document (MATTGPT-080)

> **What this file is.** The single working source of truth for closing the Role Match
> "missing evidence" gaps and the architecture that makes it stick. It holds the *reasoning*
> (principles/findings), the *tracker* (per-skill dispositions + the imported skill map + pending
> corrections), the *log* (what changed, when), the *queue* (what's still open), the *active
> drafts* (story augments ready to enter), and the *architecture* (convergence + build approach).
> It absorbs `Skill_Evidence_Map.xlsx`, the 01JUL26 session recap, and the parked architecture
> notes, all of which retire into this file.
>
> **How agents use it.** Read §1 for current state. Do work against §5 (open items), §6
> (corrections), and §7 (active augments). When something changes, update the relevant row/entry
> **and** add a dated line to §4. Keep §2 (principles) and §11 (architecture) stable — they are
> the "why," not the worklist.
>
> **Two standing rules (see §8):** (1) never write to Matt's device without asking first, every
> time; (2) reference every story by its **title**, never a row number — row numbers shift on
> every master edit and are always stale.

**Last touched:** 2026-07-26 · **Owner:** Matt · **Status: ARCHIVED (26JUL26) — historical reference only**

> **✅ CLOSED / ARCHIVED (26JUL26).** This doc did its job: it carried the evidence-population work to
> its conclusion (corpus proven, ready to drop the skills array), and its durable decisions are now in
> BACKLOG (commit 6bc39c2: -080, -088, -155, -156, -157). **It is no longer maintained.** For anything
> live — the array drop (-080), scorer honesty (-088), the sell-side story (-155), the vendor-spend gap
> (-156), the keyword question (-157) — go to BACKLOG, not here. This file survives only as the
> historical record of how the corpus was made honest. Do not act on its worklist sections; they are a
> frozen snapshot.
>
> **⚠ Document status (26JUL26): this doc did its job as a worklist and is retired.** It
> was the consolidation of 5–6 scattered 080 docs into one source of truth, and it carried the
> evidence-population work from "skills scattered" to "corpus proven, ready to drop the array." That
> job is essentially complete. The **worklist sections (§3 tracker, §5 open items, §6 corrections, §7
> active draft) trail the live corpus.** The 26JUL sync folded the key corrections in (P&L now
> dedicated-story Resolved, exit criterion logged with two JD runs, the Use-Case-first retrieval rule
> and the retrieval-latency distinction added), but the worklist still trails the full live corpus
> (the Dynamics revision, the database Use Case batch, the retrieval-gap detector are not all reflected
> row-by-row). **Do not re-litigate closed items from the stale worklist; the live corpus is the
> source of truth.**
>
> **Durable bits MIGRATED to BACKLOG (commit 6bc39c2, 26JUL) — migration done, not pending:** -080
> (pre-drop worklist: retrieval-latency audit, database fix batch, re-embed, A/B re-run; exit
> criterion; all six do-not-re-open dispositions; §11 architectural rationale), -088 (gating note
> pointing at the -080 exit criterion), -155 (sell-side commercial story, HSBC anchor, do-not-bundle),
> -156 (vendor spend gap, distinct from Vendor Management coordination). **This doc is now ready to
> archive** — it survives only as historical reference until -080 actually drops.

---

## 1. Status at a glance

| Area | State | Where |
|---|---|---|
| Principles & findings | Stable, corpus-verified (30JUN26 master) | §2 |
| Skill-evidence tracker | 73 skill rows (from `Skill_Evidence_Map.xlsx`). Status column maintained; Hits column regenerated from corpus | §3 |
| Row corrections | All 5 applied to §3 (Prompt Engineering, SQL, Oracle, Java, Azure) | §6 |
| Active story augment | "Delivering Working Prototypes in Days, Not Months" — full draft ready to enter | §7 |
| Pass 1 (augment existing) | Complete 25JUL26 (AWS/Prompt Eng/SQL/ops; AI-workflows fluency; Delivering Working Prototypes draft entered) | §4, §5 |
| Prune (Set C / vendor D) | Both closed. Set D vendor cluster 24JUL26; Set C 25JUL26 (nothing to execute — 4 risk stories live-verified clean, no self-credit tagged) | §5 |
| Pass 2 (new stories, Set E) | Fully resolved. Multi-home: SQL Server/Oracle. Single-home ceiling (correct, don't re-open): Aurora/ElastiCache/Azure. Dropped: PostgreSQL/TypeScript/ECMAScript | §5, §3.E |
| Stories to write / recover | 8 queued (incl. deferred sell-side HSBC story → BACKLOG) + purged-story recovery not yet triaged. NOTE: worklist trails live corpus — see doc status banner | §5 |
| Convergence architecture | Decided in principle, parked (the MATTGPT-080 spine) | §11 |

---

## 2. Guiding principles & findings

Context: closing the Role Match "missing evidence" gaps (MATTGPT-080 family). The profile
(matt_profile.json) asserts 73 skills; the corpus demonstrates a subset. Role Match reads the
profile + corpus; Ask Agy reads only the corpus. That asymmetry let Role Match affirm skills Agy
couldn't substantiate — which is what exposed the json as a quick fix that satisfied the checker
without making the claim true. End-state architecture removes the profile as an evidence source,
so every claimable skill must have a corpus home. (The full architecture is in §11.)

### Root cause (the one idea everything follows from)

**The gap isn't missing experience. It's experience described above the altitude where skills live.**

Stories were written at architecture/leadership altitude (the accomplishment), correct for human
readers. Technical skills live one level below (the tools). Last year's readability pass abstracted
the tools out of the prose. The matcher searches at the lower altitude, finds no skill keyword, and
reports "missing evidence" even though the work happened.

Example: "Led resolution of cross-domain data issues..." names the achievement, not the SQL
underneath it. The skill is below the sentence, not in it.

### Governing rule (from the corpus-as-evidence architecture)

A skill is honestly claimable only where a story demonstrates **you doing it** — not leading others
who did it, and not the technology merely appearing as context.

- Surfacing true-but-undescribed work = **augmentation** (legitimate).
- Adding a skill a story doesn't describe = **padding** (not allowed).

The profile is not an evidence source in the end state, so there is no "list-only" resting place.
A skill either gets demonstrated in the corpus or it is not claimed.

**Demonstration vs. assertion is the spine of every decision.** "I have the experience, why not
claim it" and "no reason not to include all" are both the assertion model — the exact thing the
redesign exists to refuse. Touching a tool isn't the bar; demonstrating it is.

### Principles

1. **Honesty is per-era, not per-skill.** The career is a U: hands-on early, leadership middle,
   hands-on again (Liquid Studio/CIC, then sabbatical). The same skill name can be yours, the
   team's, or yours-again depending on era. The unit of decision is the **skill-era pair**.

2. **Augmentation can only lower altitude, not invent it.** Where you personally did the lower-level
   work, an existing story can honestly surface the abstracted-out tool. Where you directed it,
   lowering altitude becomes self-credit. The practitioner/leader line is a hard ceiling.
   *Not strictly binary:* a single story can surface only the specific lines your hands were on at
   a middle altitude, while the rest stays at leadership altitude.

3. **The architecture raised your own bar.** Corpus-as-evidence converts "skills I have" into
   "skills I can demonstrate." Honest, harder, correct.

4. **Era is a free variable.** A skill need not be claimed where you *first* did it. Claim it where
   you *most recently and relevantly* did it, demonstrably. This dissolves the false binary of
   "augment the old story or drop the skill" — a third path is a new story in the on-target era.

5. **Demonstration presentation controls the seniority signal.** A vendor-name list reads as junior
   padding. A real build story with those tools reads as a senior leader who's stayed hands-on and
   relevant. Same skills, opposite read; the variable is demonstration vs. enumeration.

### The master filter: practitioner vs. leader, by era (a thinking aid, not a spec)

| Era | Span | Relationship | Skills | Augmentability |
|---|---|---|---|---|
| Early hands-on | 2000–2014 | Practitioner → architect | Oracle, Java, SQL, SQL Server, PostgreSQL (on-prem), relational design | Per-story altitude test: claimed where the story shows your hands on the work (e.g. AT&T Mobility), non-claim where directing. |
| Leadership middle | ~2014–2018 | Led teams who used it | SQL/RDBMS (Norfolk Southern, Railroad) | Non-claim where you directed (self-credit); claim only where a specific line shows your hands on it. |
| Liquid Studio / CIC | ~2018–2023 | Re-skilled, hands-on | AWS, Azure, GCP, Aurora, ElastiCache, PostgreSQL/SQL Server (managed), TypeScript, IaC, serverless, DynamoDB | Strongest augment targets; some already named. |
| Sabbatical | 2024–present | Fully hands-on | RAG, vector DBs, semantic search, embeddings, Pinecone, data engineering, prompt eng, Python, BDD, eval-driven dev | Largely ALREADY demonstrated in the MattGPT stories. |

Era locates the work; **altitude decides the claim** (hands-on vs. directing), per story — see the
Key finding below. The corpus **already extends past Accenture** — the sabbatical/MattGPT stories are
in it and are the most technically dense in the corpus. (Corpus-scope is settled; it was wrongly
treated as open in v1.)

### Key finding: the non-claim test is altitude, not era

SQL is the clean example, and the one that corrected this finding. The original framing (established
2JUL26) treated 2000–2014 as a blanket non-claim era. That was wrong: SQL was load-bearing across
nearly every project until the platform era (Dynamics, SFDC, cloud), and the real test was never the
year — it was whether you were hands-on or directing.

- **Norfolk Southern (Railroad)** — director-era self-credit. Your team wrote the queries, not you.
  Non-claim, regardless of era.
- **Building the Payment Engine Behind JP Morgan ACCESS** — hands-on, current-era integration work
  (AML monitoring, sanctions/PEP screening). Claimed.
- **Building AT&T Mobility's Service Delivery Platform (2006–2007)** — Technical Design & Development
  Lead, explicit hands-on language ("hands-on schema design and SQL development for platform data
  integration"). Claimed, despite being the earliest of the four — proof the date was never the real
  filter.
- **Resolving Cross-Domain Data Issues for AT&T's Order Management (2005)** — Data & Functional
  Architect, governance/architecture language, not hands-on query. Resolved: carries Relational
  Database Design, NOT SQL, and the corpus already reflects this. Contrast with AT&T Mobility, which
  is dual-tagged (SQL + Relational Database Design) because you built the schema *and* wrote the
  queries there. The altitude test, answered: architecture, not hands-on SQL.

The "don't reach back more than 5–10 years" guidance applies to *authoring new claims* that far back,
not to suppressing real, already-written corpus content. These stories are already there; the
question was never whether to dig them up, it's whether the story's own language shows your hands on
the work.

So: early-era SQL is not a blanket non-claim. Test each story on whether you personally did the work,
same as any other era. Java and on-prem relational work get the same per-story test, not a date
cutoff. Director/architect-altitude self-credit stays dropped (Norfolk Southern). Genuine hands-on
work is claimed (JPM ACCESS, AT&T Mobility), regardless of how early it sits in the corpus.

### Per-story field map (where evidence and retrieval actually live)

- **Use Case(s)** — **the strongest retrieval signal.** `build_embedding_text` front-loads Use Case(s)
  as the first content block (explicit "strongest retrieval signal" comment in code). This is where
  retrieval-critical evidence must land.
- **5P Summary** — a secondary retrieval signal. It sits *after* the 2000-char Situation block in the
  embedding text, so it is positionally weaker than Use Case(s). Not the anchor; earlier docs said so,
  the code says otherwise.
- **Competencies** — explicit skill evidence for tagging / skill matching (does NOT drive retrieval).
- **Action** — where capability is demonstrated (most capability evidence; does NOT drive retrieval).
- **Result** — business-impact outcome (STAR surface).
- **Performance** — metrics/outcomes (5P surface); intentional overlap with Result, by design.
- **Process** — methodology / how (5P surface).

To make a skill "score correctly," the skill-match lever is Competencies and the **retrieval lever is
Use Case(s) first, 5P Summary second** — not Action prose, not Performance. This is load-bearing: the
database and P&L fixes target **Use Case(s)** specifically because that is the front-loaded field.

---

## 3. Skill-evidence tracker

Two layers: the **disposition sets** (A–E, the reasoning) and the **full per-skill map** (73 rows
imported from the xlsx). Classification legend: **Content-there** = ≥2 narrative (S/T/A/R) stories
demonstrate it; **Partial** = 1 narrative hit or tag-only; **Content-needed** = no evidence in any
narrative or tag.

> **Two different columns, two different rules.** **Class/status is maintained** — keep it current
> when a disposition changes, because a stale status (e.g. a homed skill still reading "Content-needed")
> makes agents re-litigate closed work. When you home, drop, or reclassify a skill, update its status
> row here in the same pass. **Hits is the regenerable one** — the exact count is derived from the
> corpus and not worth hand-chasing; refresh it from `echo_star_stories_nlp.jsonl` when a number
> actually matters (a "—" means "recompute from corpus," it is not zero). Skill, Home Story, status,
> and Action Required are the decision columns and are kept current; the raw Hits integer is not.

### Disposition sets

**A. Demonstrated — verify surfacing (low effort).**
AWS (expanded 23JUL26 to 6 more stories — "Building Tangible Cloud Tech Skills for HBCU Students,"
"Creating and Leading a Self-Directed Capability Development Program," "Driving Cloud-Native
Innovation through TICARA Framework," "Launching a Self-Paced Learning Program for Emerging
Technologies," "Mentoring Underserved High School Students into Technology Careers," "Eliminating
Idle Server Costs with Serverless Architecture" — verified, closed), RAG (confirm the 2005 hit isn't
a false match), IaC, DynamoDB, OpenAI API, plus the sabbatical cluster below. Confirm each appears in
Competencies + retrieval fields (Use Case(s), 5P Summary) on its demonstrating stories. Java and
Prompt Engineering removed from this set 23JUL26 — both had been mis-tallied here. See Set C and Set B.

**B. Already demonstrated in the MattGPT/sabbatical stories (recent, on-target, hands-on).**
RAG Architecture, Vector Databases, Semantic Search, LLM Integration, OpenAI Embeddings, Pinecone,
Data Engineering, Prompt Engineering, Python, JSONL, Eval-Driven Development, BDD, Playwright,
pytest. "MattGPT: RAG Architecture & Semantic Search Implementation" already carries the data-layer
validation. A net-new "MattGPT data story" is largely redundant. Prompt Engineering closed 23JUL26:
pulled from "Simplifying MattGPT's RAG Pipeline Through Entity Gate Removal" and "Implementing
Eval-Driven Development for RAG Systems" (Competencies-only, no Action/retrieval grounding), given a
real home via a new dedicated story ("My Chatbot Kept Flattering Me Instead of Answering the
Question. Here's How I Fixed It.") built from code-level evidence (prompts.py diagnosis, Jan 25–Feb 2
2026 arc), plus a grounding pass on "MattGPT: RAG Architecture & Semantic Search Implementation"
(system-prompt-design line added to Use Case(s)).

**C. Non-claims by altitude, not era (drop only the director/architect-altitude self-credit).**
The test is per-story: does the story's own language show your hands on the work? See §2 Key finding
for the full logic. There is no blanket early-era non-claim.
- **SQL:** claimed where hands-on ("Building the Payment Engine Behind JP Morgan ACCESS," current-era
  AML/sanctions/PEP integration; "Building AT&T Mobility's Service Delivery Platform," 2006–2007,
  explicit hands-on schema design + SQL development). Non-claim where directing (Norfolk Southern).
  "Modernizing Railroad Revenue: Transitioning from Legacy to Cloud" carries Relational Database
  Design, not SQL (architecture-level). "Resolving Cross-Domain Data Issues for AT&T's Order
  Management" is resolved: Relational Database Design plus Oracle / CASE Method (added 24JUL26, OCP
  credential + named design methodology at architect altitude), NOT SQL (governance, not hands-on
  query) — live in the corpus. See §6 SQL. Note: the SQL claims are "SQL" the language, distinct from
  "SQL Server" the named product (now homed separately — see §3.E, 24JUL26).
- **Java:** the "(5)" count in Set A conflated two things. Early hands-on Java as a build stack —
  "Lowering Barriers to Adoption for American Express's Virtual Payments Platform" (AmEx),
  "Recovering Fiserv's $8.5M White-Label Card Portal" (Fiserv), "Transitioning to Microservices with
  Domain-Driven Design (DDD)" — is a non-claim by the directing/hands-on test as applied. Curriculum
  Java, where you taught or enabled it ("Creating and Leading a Self-Directed Capability Development
  Program," "Launching a Self-Paced Learning Program for Emerging Technologies," "Mentoring
  Underserved High School Students into Technology Careers"), is a separate legitimate claim under
  Principle 1. Corrected 23JUL26.
- **On-prem relational work:** the early hands-on database build gets the same per-story test;
  architecture-altitude Relational Database Design is separately claimed (Content-there in the map).

**D. Vendor-tool cluster — collapse, don't enumerate. (Closed 24JUL26.)**
Claude Code, Claude Skills, Anthropic Claude, plus ChatGPT and Gemini — all confirmed **generic
references, not the named product features**, and marked "covered, not separately claimed" in the §3
map. You used MULTIPLE frontier tools to build MattGPT, so the honest claim is **AI-assisted
development fluency across frontier models**, already carried by the Claude Code Fluency competency on
"Building Effective AI-Assisted Development Workflows" (tool-agnostic — naming one vendor overstates it).
- Do NOT add vendor names as individual competency strings (assertion/padding; junior signal).
- The product runs on **OpenAI** (gpt-4o, text-embedding-3-small) — the honest integration claim
  that's *in* the artifact. Anthropic/Claude was a **build tool**, a different claim.
- Exception: a vendor earns a named claim only with a real build story showing depth in *that one*
  tool ("built X using its specific capabilities, with situation/result"), not mere use.
- **-077 self-reference risk**: MattGPT citing its own construction as the work sample. Keep visible.

**E. No existing home, on-target (candidate new stories, Pass 2).**
Worked 24JUL26 by a toolkit-connector / data-store tagging pass (see §4). **Resolved, multi-home
(career-relevant):** **SQL Server** (AT&T Network Engineering Platform + TICARA), **Oracle** (TICARA +
AT&T Mobility RAC + AT&T Cross-Domain CASE Method). **Resolved at the honest ceiling, single home
(project-specific — do NOT re-open):** **Amazon Aurora** (TICARA), **ElastiCache** (Octane/Summit),
**Microsoft Azure** (Delivering Working Prototypes, range-altitude). These are specific technical
choices on specific projects, not recurring themes — one real home is the truthful weight; a second
would manufacture breadth that isn't there. AWS is the real, deep, multi-story cloud claim; Azure was
project-specific/incidental (AWS-funded Launchpad predominated). **Dropped (deliberate non-claims):**
PostgreSQL
(no honest home), TypeScript (React-only), ECMAScript (folded into JavaScript). **Set E is fully
resolved** — nothing left to chase.

### Full per-skill map (73 rows, imported from `Skill_Evidence_Map.xlsx` 23JUL26)

Skill is the key. **Disposition** tracks whether a skill is **represented at its true weight**, not
its raw hit count.
**Resolved** = represented correctly, decision final. That's ≥2 homes for a career-long theme, OR a
single home for a project-specific choice where one home is the honest ceiling (more would manufacture
breadth that isn't real). **Open** = under-represented relative to true weight — a career-long theme
with too few homes (e.g. Enterprise Digital Transformation was one home → needed more), or
Content-needed with no home yet. **Dropped** = deliberate non-claim, out of the scored set.
**Covered** = subsumed by another claim.

The test is not "find more homes for everything," it's "represent each skill at its true weight." Some
skills are broad and under-homed (multi-home them); some are narrow and correctly single-homed
(leave them). Forcing either into the other's pattern is the error.

**Resolved requires retrievability, not just a tag.** A Competencies tag does NOT retrieve (proven: P&L
was marked Resolved on a Competencies/Action tag yet gapped at probe #12). A skill is **fully
Resolved** only if its evidence reaches the retrieval-critical field, **Use Case(s)** (see §2 field
map). A skill demonstrated only in Competencies/Action is **"tag-resolved but retrieval-latent"** — it
scores on skill-match but will **gap the moment the profile array drops**. Retrieval-latent skills are
not surprises to discover at array-drop time; they must be flagged now. Clearest example: **Vendor
Management** (Content-there, 10 hits, but zero occurrences in any retrieval field). There are others —
see the §5 retrieval-latency audit; do not mark any skill "Resolved" unqualified until its Use Case(s)
evidence is confirmed.

| Skill | Class (snapshot) | Hits (snapshot) | Home Story (Primary) | Home Story (Secondary) | Evidence Snippet | Action Required | Disposition |
|---|---|---|---|---|---|---|---|
| Engineering Leadership | Content-there | 23 | About Matt – My Leadership Journey | The CIC's First Engagement: Coaching Modern Engineering at Norfolk Southern | ...s, designers, and product teams could thrive. Whether I was leading a 150-person Cloud Innovation Center, redesigning payments systems across 12 countries, or guiding an executive through a transformation decision, my approach stayed consistent: l... |  | Resolved |
| Platform Modernization | Content-there | 31 | About Matt – My Leadership Journey | Consolidating Legacy Payment Systems into JP Morgan's Unified ACCESS Platform | ...lems, building high-trust engineering cultures, modernizing platforms, and helping organizations shift how they think about technology. My task throughout my career has been to translate complex technology challenges into clear, people-centered st... |  | Resolved |
| Payments & Financial Services | Content-there | 28 | About Matt – My Leadership Journey | Navigating Multi-Jurisdictional Compliance for JP Morgan's Global Payments Platform Rollout | ...s-functional teams, led major modernization programs across banking, healthcare, retail, and telecommunications, and created environments where engineers, designers, a... | Spot-checked 25JUL26 — thematically demonstrated in a delivery story, holds. No action. | Resolved |
| Generative AI | Content-there | 5 | Delivering AI-Powered Chronic Disease Management for Healthcare | Implementing Eval-Driven Development for RAG Systems | ...pabilities — starting with diabetes management — leveraging generative AI, machine learning, and health-tracking devices to deliver personalized care, identify risks early, ... |  | Resolved |
| P&L Management | Content-there | 3 | Owning the P&L: From Engagement Margin to Center Cost Base | Building Cloud Innovation Centers (CIC) - Bringing Silicon Valley Product Culture to Fortune 500 | dedicated buy-side story: engagement margin → recovery engagements → center cost base; Use Case(s) carries the P&L thesis (retrieves rank 1 @ 0.534) | Homed in the dedicated story **"Owning the P&L: From Engagement Margin to Center Cost Base"** (buy-side; P&L is the thesis, not a clause in an innovation story). "Building Cloud Innovation Centers (CIC)" retains its P&L bullet (no longer carries the claim alone); Fiserv ("Recovering Fiserv's $8.5M White-Label Card Portal") getting financial framing added as a client-specific proof point. **Exit-criterion A/B confirmed it holds strong in the array-blanked condition** (cites the story, not the profile). Retrievability confirmed — not retrieval-latent. | Resolved |
| People Management | Content-there | 59 | Building Cloud Innovation Centers (CIC) - Bringing Silicon Valley Product Culture to Fortune 500 | Accelerating Modernization with Reusable Solution Patterns | grew from 10-person pilot to 150+ trained practitioners; career progression frameworks that retained talent | Tag added 25JUL26 on "Building Cloud Innovation Centers (CIC)"; Action already carried the evidence. | Resolved |
| Tech-Enabled Business Transformation | Content-there | 24 | About Matt – My Leadership Journey | Building JP Morgan's Global Payments Gateway Across 12 Countries | ...forms, and helping organizations shift how they think about technology. My task throughout my career has been to translate complex technology challenges into clear, people-centered strategies — and to help teams deliver real outcomes, not just art... | Spot-checked 25JUL26 — thematically demonstrated in a delivery story, holds. No action. | Resolved |
| Enterprise Digital Transformation | Content-there | 3 | Shifting Client Focus from What They Build to How They Work | Building Cloud Innovation Centers (CIC) - Bringing Silicon Valley Product Culture to Fortune 500 | tag added 25JUL26 to 3 distinct homes: Fortune 500 general pattern ("the operating model was the problem"), CIC (internal), Norfolk Southern (client-specific) | Spot-checked 25JUL26 — the 14th capability skill. Enterprise Digital Transformation tag added to "Shifting Client Focus...", CIC, and "The CIC's First Engagement (Norfolk Southern)." Three distinct, real homes. Verified live. | Resolved |
| Agile & DevOps Leadership | Content-there | 32 | Accelerating Delivery at Norfolk Southern Through Agile Transformation | Accelerating Modernization with Reusable Solution Patterns | ...ity, and accelerate delivery. Implement agile workflows and continuous integration to streamline development, enhance efficiency, and support transformation goals. - Introduced pair programming to foster knowledge-sharing, accountability, and impr... | Spot-checked 25JUL26 — thematically demonstrated in a delivery story, holds. No action. | Resolved |
| Behavior-Driven Development (BDD) | Content-there | 4 | Building Cloud Innovation Centers (CIC) - Bringing Silicon Valley Product Culture to Fortune 500 | Building Effective AI-Assisted Development Workflows | ... testing), agile fundamentals (balanced team collaboration, BDD, discovery and framing), and XP engineering practices (pair programming, test-driven development, C... |  | Resolved |
| Eval-Driven Development | Content-there | 5 | Building Effective AI-Assisted Development Workflows | Implementing Eval-Driven Development for RAG Systems | ...o support AI reasoning over multi-file changes - Integrated eval-driven development as a verification layer, using golden queries to catch regressions introduced by AI-ass... |  | Resolved |
| LLM Integration | Content-there | 5 | Building Effective AI-Assisted Development Workflows | Defining System Interfaces for AT&T's Order Management Platform | ...Building MattGPT as a solo developer, I used AI coding assistants as a true development partner — not just for code generation, but for architecture decisions, debugging, test writing, and refactoring. I quickly ran into the same systemic limits m... |  | Resolved |
| Semantic Search | Content-there | 6 | MattGPT: Product Vision, Roadmap, Scope, and MVP Delivery | MattGPT: RAG Architecture & Semantic Search Implementation | ...xperience with modern AI/ML, specifically RAG architecture, semantic search, Pinecone, and Python. I chose a project I'd actually use rather than a tutorial exercise: an AI-po... |  | Resolved |
| Claude Skills | Covered — not separately claimed | — |  |  |  | Generic reference, not the product feature. Covered by AI-assisted development fluency (Claude Code Fluency on "Building Effective AI-Assisted Development Workflows"). Do not tag separately (§3.D). | Covered |
| Claude Code | Covered — not separately claimed | — |  |  |  | Covered by AI-assisted development fluency (Claude Code Fluency on "Building Effective AI-Assisted Development Workflows"). Do not tag as a standalone vendor (§3.D). | Covered |
| Anthropic Claude | Covered — not separately claimed | — |  |  |  | Build tool, not a product-integration claim. Covered by AI-assisted development fluency (§3.D); the product itself runs on OpenAI. Do not tag separately. | Covered |
| OpenAI API | Content-there | 2 | MattGPT: Product Vision, Roadmap, Scope, and MVP Delivery | MattGPT: RAG Architecture & Semantic Search Implementation | ...mlit frontend, Python backend, Pinecone for vector storage, OpenAI text-embedding-3-small for embeddings, GPT-4o for response generation. I named the assistant "Agy" ... |  | Resolved |
| Vector Databases | Content-there | 3 | MattGPT: Product Vision, Roadmap, Scope, and MVP Delivery | MattGPT: RAG Architecture & Semantic Search Implementation | ...dern AI/ML, specifically RAG architecture, semantic search, Pinecone, and Python. I chose a project I'd actually use rather than a tutorial exercise: an AI-powered assi... |  | Resolved |
| Embedding Models | Content-there | 15 | Building JP Morgan's Global Payments Gateway Across 12 Countries | Building Cloud Innovation Centers (CIC) - Bringing Silicon Valley Product Culture to Fortune 500 | ... and regulatory requirements. As the bank built ACCESS Next Generation on Bottomline Technologies' WebSeries Global Cash Management platform, it needed a centralized payments gateway to handle message transformation, protocol translation, and rout... |  | Resolved |
| AI for Business | Non-claim (dropped 25JUL26) | — |  |  |  | Dropped as redundant — real AI work already carried by Generative AI, LLM Integration, RAG, Semantic Search, AI-Enabled Product Innovation, Responsible AI. Adds no claim those don't. Do not re-open. | Dropped |
| Responsible AI | Content-there | 3 | Fast-Tracking Client Innovation with Emerging Technologies | Implementing Responsible AI Governance for Patient Data Privacy and Compliance at Fortune 500 healthcare company | ...nterested in understanding how disruptive technologies like AI, blockchain, and the metaverse could reshape their business models but lacked clear strategies for adoption and execution. Accenture's Liquid Studio was tasked with helping clients exp... |  | Resolved |
| Retrieval-Augmented Generation (RAG) | Content-there | 6 | Building Effective AI-Assisted Development Workflows | Implementing BDD for System Behavior Specification | ...afe AI leverage - Shipped a complete product (100+ stories, RAG architecture, polished UI) as a solo developer operating at team-level velocity - Eliminated the "r... |  | Resolved |
| Cloud Infrastructure | Content-there | 11 | Balancing Execution Speed with Security and Compliance | Building an Innovation Ecosystem to Connect Clients with Emerging Technology | ... than treated as separate governance checkpoints. - Defined cloud-native security best practices as standard for CIC engagements at financial services clients including encryption at rest and in transit, role-based access control (RBAC), automated... |  | Resolved |
| Prompt Engineering | Content-there | 2 | MattGPT: RAG Architecture & Semantic Search Implementation | My Chatbot Kept Flattering Me Instead of Answering the Question. Here's How I Fixed It. | ...system prompt design (MattGPT RAG); root-cause diagnosis of eval failures via prompts.py (new dedicated story)... | Resolved 23JUL26 — two demonstrating stories. | Resolved |
| Operational Efficiency | Content-there | 23 | Accelerating Delivery at Norfolk Southern Through Agile Transformation | Accelerating Modernization with Reusable Solution Patterns | ... was maintained through manual processes, resulting in high operational costs and delayed release cycles. A transformation was needed to improve efficiency, enhance code quality, and accelerate delivery. Implement agile workflows and continuous in... |  | Resolved |
| Cloud Security & Compliance | Content-there | 11 | Consolidating Legacy Payment Systems into JP Morgan's Unified ACCESS Platform | Balancing Execution Speed with Security and Compliance | ... platform while preserving regulatory traceability (AML/KYC/PCI-DSS), client configurations, and operational continuity across live payment processing for 135,000+... | Spot-checked 25JUL26 — thematically demonstrated in a delivery story, holds. No action. | Resolved |
| Microsoft Azure | Partial | 1 | Delivering Working Prototypes in Days, Not Months |  | Azure in the story's Competencies; §7 homes it at range altitude (fit-for-purpose across AWS/GCP/Azure, defaulting to AWS) | **Single home is the honest ceiling — do NOT re-open.** AWS was the predominant, AWS-funded (Launchpad) platform; Azure usage was project-specific/incidental, not a career-spanning theme. Corpus-confirmed: no second delivery home exists. Range-altitude framing is the truthful representation. | Resolved (ceiling) |
| Budget Management | Content-there | 2 | Recovering Fiserv's $8.5M White-Label Card Portal | Stabilizing and Delivering AT&T's Southeast CRM Replacement | second home added: AT&T SE CRM ("$1M in delivery scope," "eliminated operational overspend") | Added second real home 25JUL26 (AT&T Southeast CRM) alongside existing Fiserv. | Resolved |
| Microsoft 365 | Non-claim (dropped 25JUL26) | — |  |  |  | Dropped — zero real corpus hits (searched directly). The map's Dynamics CRM citation was a token-overlap false match (Dynamics CRM is not M365). Do not re-open. | Dropped |
| Program Management | Content-there | 40 | About Matt – My Leadership Journey | Accelerating Delivery at Norfolk Southern Through Agile Transformation | ... and scaled cross-functional teams, led major modernization programs across banking, healthcare, retail, and telecommunications, and created environments where engineers, designers, and product teams could thrive. Whether I was leading a 150-perso... |  | Resolved |
| Organizational Design | Content-there | 77 | About Matt – My Leadership Journey | Accelerating Modernization with Reusable Solution Patterns | ...lenges into clear, people-centered strategies — and to help teams deliver real outcomes, not just artifacts. I built and scaled cross-functional teams, led major modernization programs across banking, healthcare, retail, and telecommunications, an... |  | Resolved |
| Executive-level Communication | Content-there | 13 | Balancing Execution Speed with Security and Compliance | Building Cloud Innovation Centers (CIC) - Bringing Silicon Valley Product Culture to Fortune 500 | "Executive Stakeholder Communication" tagged in "Balancing Execution Speed with Security and Compliance" | Re-anchored 25JUL26: map cited the wrong story (AT&T Mobility, no such content); real evidence lives in "Balancing Execution Speed with Security and Compliance." Citation fixed. | Resolved |
| Platform Strategy | Content-there | 31 | About Matt – My Leadership Journey | Building JP Morgan's Global Payments Gateway Across 12 Countries | ...lems, building high-trust engineering cultures, modernizing platforms, and helping organizations shift how they think about technology. My task throughout my career has been to translate complex technology challenges into clear, people-centered st... | Spot-checked 25JUL26 — thematically demonstrated in a delivery story, holds. No action. | Resolved |
| Cloud-Native Architecture | Content-there | 26 | Accelerating Modernization with Reusable Solution Patterns | Accelerating Product Delivery Through Lean Innovation at Capital One | ... modernization scenarios such as transitioning monoliths to microservices, managing dependencies, and implementing CI/CD pipelines - Organized weekly collaborative workshop... |  | Resolved |
| AI-Enabled Product Innovation | Content-there | 3 | Career Intent – What I’m Looking For Next | Fast-Tracking Client Innovation with Emerging Technologies | ...neering - Technology transformation - Cloud modernization - AI-enabled product innovation... |  | Resolved |
| Product Development & Prototyping | Content-there | 14 | Accelerating Product Delivery Through Lean Innovation at Capital One | The CIC's First Engagement: Coaching Modern Engineering at Norfolk Southern | ...s faster - Improved customer satisfaction through iterative MVP releases and defect-free production code - Empowered teams to sustain high-quality output and agile... | Spot-checked 25JUL26 — thematically demonstrated in a delivery story, holds. No action. | Resolved |
| DevOps | Content-there | 34 | Accelerating Delivery at Norfolk Southern Through Agile Transformation | Accelerating Modernization with Reusable Solution Patterns | ...ity, and accelerate delivery. Implement agile workflows and continuous integration to streamline development, enhance efficiency, and support transformation goals. - Introduced pair programming to foster knowledge-sharing, accountability, and impr... |  | Resolved |
| Agile Transformation | Content-there | 20 | Accelerating Delivery at Norfolk Southern Through Agile Transformation | Accelerating Product Delivery Through Lean Innovation at Capital One | ...y, enhance code quality, and accelerate delivery. Implement agile workflows and continuous integration to streamline development, enhance efficiency, and support transformation goals. - Introduced pair programming to foster knowledge-sharing, acco... |  | Resolved |
| Innovation Strategy | Content-there | 33 | About Matt – My Leadership Journey | Accelerating Modernization with Reusable Solution Patterns | ...e complex technology challenges into clear, people-centered strategies — and to help teams deliver real outcomes, not just artifacts. I built and scaled cross-functional teams, led major modernization programs across banking, healthcare, retail, a... |  | Resolved |
| Infrastructure as Code (IaC) | Content-there | 7 | Building Cloud Innovation Centers (CIC) - Bringing Silicon Valley Product Culture to Fortune 500 | Accelerating Enterprise Delivery Through Cloud-Native Architecture and CI/CD | ...0 transformation. Specifically: 1) Establish facilities and infrastructure in both locations creating collaborative environments that embodied modern product culture, 2) Build talent pipeline by recruiting, training, and developing 150+ practition... |  | Resolved |
| Amazon Web Services (AWS) | Content-there | 9 | Building Cloud Innovation Centers (CIC) - Bringing Silicon Valley Product Culture to Fortune 500 | Building Tangible Cloud Tech Skills for HBCU Students | ...rsion with external training resources and platforms (e.g., AWS, Pluralsight, Spring, code katas) tailored to technology needs. Training covered the full balanced ... |  | Resolved |
| Technical Solution Design | Non-claim (dropped 25JUL26) | — |  |  |  | Dropped as redundant — same two home stories as Solution Architecture (35 hits, well-evidenced); the design work is consistently tagged Solution Architecture, never as a separate claim. Do not re-open. | Dropped |
| Strategic Planning | Content-there | 17 | Keeping Roadmaps Alive When Priorities Keep Shifting | Architecting AT&T's Scalable Order Management Platform | ...enges in aligning product development efforts with evolving strategic objectives. Misaligned priorities, shifting market demands, and a lack of transparency in product planning resulted in resource inefficiencies, delays, and stakeholder frustrati... |  | Resolved |
| IT Strategy | Content-there | 21 | Keeping Roadmaps Alive When Priorities Keep Shifting | Architecting AT&T's Scalable Order Management Platform | ...ct initiatives. - Introduced OKRs and KPIs for each roadmap item, ensuring every deliverable had clear, measurable objectives - Conducted workshops with product owners, stakeholders, and team leads to prioritize high-impact features aligned with b... |  | Resolved |
| Solution Architecture | Content-there | 35 | Accelerating Modernization with Reusable Solution Patterns | Accelerating Product Delivery Through Lean Innovation at Capital One | ...ation projects. Teams often spent valuable time reinventing solutions or implementing unique patterns for problems that had already been solved by others. This fragmented approach led to misaligned architectures, slowed delivery timelines, and inc... |  | Resolved |
| Cloud-Native Application Development | Content-there | 24 | Accelerating Product Delivery Through Lean Innovation at Capital One | Balancing Execution Speed with Security and Compliance | ...oduce a new product development paradigm integrating modern cloud-native engineering, lean product management, and user-centered design to enable rapid, validated iterations. - Adopted modern engineering practices, implementing Extreme Programming... |  | Resolved |
| API Development | Content-there | 28 | Accelerating Product Delivery Through Lean Innovation at Capital One | Keeping Roadmaps Alive When Priorities Keep Shifting | ... from user needs. They needed a scalable framework to align development with business goals while improving delivery speed. Introduce a new product development paradigm integrating modern cloud-native engineering, lean product management, and user... |  | Resolved |
| Cross-functional Team Leadership | Content-there | 41 | About Matt – My Leadership Journey | Accelerating Modernization with Reusable Solution Patterns | ...liver real outcomes, not just artifacts. I built and scaled cross-functional teams, led major modernization programs across banking, healthcare, retail, and telecommunications,... |  | Resolved |
| Enterprise Architecture | Content-there | 13 | Architecting Enhancements for AT&T's Network Engineering Platform | Building Cloud Innovation Centers (CIC) - Bringing Silicon Valley Product Culture to Fortune 500 | ...hnical requirements gathering, and interface design. Design enterprise-grade enhancements aligned with AT&T's IT roadmap. Manage Accenture, Avanade, and third-party developers and coordinate offshore transitions to Hyderabad teams. - Defined and d... |  | Resolved |
| Stakeholder Management | Content-there | 40 | Keeping Roadmaps Alive When Priorities Keep Shifting | Building JP Morgan's Global Payments Gateway Across 12 Countries | ...t planning resulted in resource inefficiencies, delays, and stakeholder frustration. A robust and adaptable Roadmapping process was needed to integrate stakeholder input, adjust dynamically to change, and provide measurable outcomes aligned with b... |  | Resolved |
| Product Management | Content-there | 43 | Accelerating Product Delivery Through Lean Innovation at Capital One | Keeping Roadmaps Alive When Priorities Keep Shifting | ...Capital One faced slow, misaligned product iterations that extended time-to-market and disconnected solutions from user needs. They needed a scalable framework to align development with business goals while improving delivery speed. Introduce a ne... |  | Resolved |
| Practice Development (was "Organizational Development") | Content-there | 6 | Breaking Silos Between Engineering, Design, and Product | Scaling Talent and Practices for Agile Product Innovation | anchored thematically across six delivery stories | Renamed 25JUL26 (OD reads HR-adjacent; wrong signal for Dir/VP Eng/AI targeting). Had zero corpus hits — existed only in matt_profile.json (likely LinkedIn carryover). Anchored across 6 stories: Breaking Silos, Scaling Talent and Practices, Enabling New Ways of Working (Immersive Coaching/Transformation Labs), Creating and Leading a Self-Directed Capability Development Program, Empowering Teams through Decentralized Decision-Making, Establishing Team Rhythm — all 6 confirmed live 25JUL26. | Resolved |
| Talent Development | Content-there | 21 | The CIC's First Engagement: Coaching Modern Engineering at Norfolk Southern | Building Cloud Innovation Centers (CIC) - Bringing Silicon Valley Product Culture to Fortune 500 | ...h evolving business needs - Delivered targeted training and coaching to break through legacy, mainframe-centric mindsets and promote modern product-oriented thinking - Introduced OKRs to reinforce accountability and align delivery with business ou... |  | Resolved |
| Skills Transformation | Content-there | 15 | Architecting AT&T's Scalable Order Management Platform | Replacing Velocity Metrics with Lead Time, Cycle Time, and Throughput | ...grated Order Management (IOM) domain within the Big Picture Transformation (BBT) program required solution architecture for a scalable, high-performance order management platform. The architecture had to align with both business and IT strategies ... |  | Resolved |
| Capability Development | Content-there | 25 | Navigating Multi-Jurisdictional Compliance for JP Morgan's Global Payments Platform Rollout | Building an Innovation Ecosystem to Connect Clients with Emerging Technology | ...e the WebSeries platform's native multi-tenant/multi-region capabilities handled jurisdictional segmentation vs. where JPM-specific configuration or custom development was required - Enabled ongoing alignment between JPM's regional compliance offi... |  | Resolved |
| Integration | Content-there | 36 | Keeping Roadmaps Alive When Priorities Keep Shifting | Building JP Morgan's Global Payments Gateway Across 12 Countries | ...d implement a product Roadmapping framework that integrates data-driven metrics, drives stakeholder alignment, and adapts to rapidly shifting priorities. The roadmap needed to enable transparency, continuous improvement, and timely delivery of hig... |  | Resolved |
| Design Thinking | Content-there | 10 | About Matt – My Leadership Journey | Building Mentorship Programs for Long-Term Growth and Retention | ...rnizing platforms, and helping organizations shift how they think about technology. My task throughout my career has been to translate complex technology challenges into clear, people-centered strategies — and to help teams deliver real outcomes, ... |  | Resolved |
| Change Management | Content-there | 24 | Building Cloud Innovation Centers (CIC) - Bringing Silicon Valley Product Culture to Fortune 500 | Building Effective AI-Assisted Development Workflows | ...legacy systems, compliance requirements, and organizational change management. Building on this proof point, I was tasked with scaling the practice by creating new Cloud Innovation Centers in Atlanta and Tampa from the ground up, establishing repe... |  | Resolved |
| Vendor Management | Content-there | 10 | Architecting Enhancements for AT&T's Network Engineering Platform | Building Effective AI-Assisted Development Workflows | ... deliverable reviews with Accenture, Telcordia, third-party vendors, and AT&T teams - Developed work plans, scope inventory, cost estimates, variance reports, and risk mitigation strategies - Led Accenture, Avanade, and third-party developers in d... | **RETRIEVAL-LATENT** — 10 hits but ZERO occurrences in any retrieval field (Use Case(s)). Tag-resolved only; will gap when the profile array drops. Clearest instance of the retrieval-latency problem (see §5 audit). Covers vendor *coordination*, a different claim from vendor commercial/spend control (§5 gap / -156). **Two flags (26JUL):** (1) the secondary home "Building Effective AI-Assisted Development Workflows" is odd for vendor management — verify it's a real home against the live corpus, likely a stale/weak citation. (2) An invoice bullet was added 26JUL to "Building the Payment Engine Behind JP Morgan ACCESS" — new evidence, but at Action/Competencies only, so still retrieval-latent by the rule (and it leans toward spend-control / -156, not coordination). | Tag-resolved, retrieval-latent |
| SQL | Content-there | 2 | Building the Payment Engine Behind JP Morgan ACCESS | Building AT&T Mobility's Service Delivery Platform | hands-on schema design + SQL development (AT&T Mobility); AML/sanctions/PEP integration (JPM ACCESS) | Resolved by altitude test. Railroad + Cross-Domain carry Relational Database Design, not SQL. Claim is "SQL" the language, not SQL Server. | Resolved |
| PostgreSQL | Non-claim (dropped 24JUL26) | — |  |  |  | Decided drop — no honest home; out of the scored set. Do not re-open. | Dropped |
| Oracle | Content-there | 3 | Driving Cloud-Native Innovation through TICARA Framework | Building AT&T Mobility's Service Delivery Platform | Oracle RAC hands-on (AT&T Mobility); Oracle/CASE Method at architect altitude (AT&T Cross-Domain); toolkit-connector (TICARA). Southeast CRM = non-claim (legacy replaced). | Homed 24JUL26. | Resolved |
| Relational Database Design | Content-there | 9 | Navigating Multi-Jurisdictional Compliance for JP Morgan's Global Payments Platform Rollout | Consolidating Legacy Payment Systems into JP Morgan's Unified ACCESS Platform | ...icas created a patchwork of conflicting requirements around data visibility, access controls, and cross-border data handling. Singapore's Monetary Authority (MAS) imposed strict banking secrecy obligations under the Banking Act and cross-border da... |  | Resolved |
| SQL Server | Content-there | 2 | Architecting Enhancements for AT&T's Network Engineering Platform | Driving Cloud-Native Innovation through TICARA Framework | added to the .NET/C#/ESRI leadership bullet (Network Eng); toolkit-connector option (TICARA) | Homed 24JUL26. | Resolved |
| Amazon Aurora | Partial | 1 | Driving Cloud-Native Innovation through TICARA Framework |  | added to Action, Competencies, Process, 5PSummary (TICARA) | **Single home is the honest ceiling — do NOT re-open.** A specific technical choice on one project (TICARA), not a recurring theme. One real home is correct. | Resolved (ceiling) |
| DynamoDB | Content-there | 2 | Launchpad: Empowering Clients and Teams with AWS Enablement and Cloud Certifications | Spearheading IoT Solutions with Serverless Frameworks | ...cusing on AWS core services, including Lambda, API Gateway, DynamoDB, and cloud-native application development - Delivered interactive workshops and labs, immersing eng... |  | Resolved |
| ElastiCache | Partial | 1 | Driving Modern Software Engineering with Project Octane |  | tied to the Summit reference app (AWS AppSync, GraphQL, ElastiCache) | **Single home is the honest ceiling — do NOT re-open.** A specific technical choice on one project (Octane/Summit), not a recurring theme. One real home is correct. | Resolved (ceiling) |
| Java | Content-there | 7 | Creating and Leading a Self-Directed Capability Development Program | Launching a Self-Paced Learning Program for Emerging Technologies | ...a practical, engaging way to adopt modern technologies like Spring Boot, AWS, Docker, and Microservices — but existing programs weren't driving adoption or improving deliv... | This is curriculum/enablement Java (taught it). Distinct from early hands-on build-stack Java (AmEx, Fiserv, DDD) which is a deliberate non-claim (§2, §3.C) — do not conflate. | Resolved |
| JavaScript | Content-there | 2 | Driving Modern Software Engineering with Project Octane | Mentoring Underserved High School Students into Technology Careers | ...osting interactive workshops on modern frameworks (Angular, React.js, Kubernetes, AWS ECS/Fargate) - Embedded security best practices, ensuring compliance with OWASP... |  | Resolved |
| TypeScript | Non-claim (dropped 24JUL26) | — |  |  |  | Decided drop — only React exposure, no substantial hands-on TypeScript. Out of scored set; do not re-open. | Dropped |
| Python | Content-there | 4 | Enabling New Ways of Working Through Immersive Coaching and Transformation Labs | Fast-Tracking Client Innovation with Emerging Technologies | ... be varied widely across product management, agile, DevOps, Python, and modern engineering. Without a structured way to assess readiness, map gaps, and prescribe the ... |  | Resolved |
| ECMAScript | Non-claim (folded into JavaScript) | — |  |  |  | Decided drop — ECMAScript is just JavaScript; folded into the JavaScript claim (Content-there). Do not re-open. | Dropped |
| Mobile Application Development | Content-there | 4 | Accelerating Enterprise Delivery Through Cloud-Native Architecture and CI/CD | Delivering AI-Powered Chronic Disease Management for Healthcare | ...ode quickly but waited days or weeks for builds, tests, and approvals—creating frustration and slowing innovation. The cost of this friction was massive: missed market opportunities, accumulated technical debt, and demoralized engineers who wanted... |  | Resolved |

---

## 4. Change log

### 2026-07-26 — Sync pass: corrections to reflect decisions already made (no new judgment)

- **P&L Management** — reclassified from "Partial / Resolved (ceiling), single home, retrieval gap
  open" to **Content-there / Resolved**. Homed in the dedicated story "Owning the P&L: From Engagement
  Margin to Center Cost Base" (buy-side; P&L is the thesis). CIC keeps its P&L bullet; Fiserv getting
  financial framing as a proof point. Exit-criterion A/B confirmed strong array-blanked (cites the
  story, not the profile). The "do not re-open / single-home ceiling" language was the opposite of what
  happened — removed.
- **§5 P&L retrieval fix — closed.** The "add a P&L clause to CIC's Use Case(s)/5P" plan was rejected
  (one clause couldn't move CIC's innovation-dominated embedding, ranked 37). Resolved instead via the
  dedicated P&L story — retrieves rank 1 @ 0.534, A/B strong both conditions.
- **Embedding-anchor correction (§2, §8, §7).** Code's `build_embedding_text` front-loads **Use Case(s)**
  as the first content block ("strongest retrieval signal"); 5P Summary sits after the 2000-char
  Situation block and is positionally weaker. Corrected the field map, the score-levers rule, and the
  §7 leftover: Use Case(s) is the strongest retrieval signal, 5P is secondary. Load-bearing — it's why
  retrieval fixes target Use Case(s).
- **"Resolved" split to account for retrievability (§3 legend, §8).** A Competencies tag doesn't
  retrieve (proven: P&L gapped at #12 while marked Resolved). New qualifier: a skill is fully Resolved
  only if evidence reaches Use Case(s); Competencies/Action-only = **retrieval-latent** (will gap at
  array drop). Flagged **Vendor Management** as the clearest instance (10 hits, zero retrieval-field
  occurrences). Added a §5 retrieval-latency audit for the rest.
- **Vendor commercial / spend management — gap recorded (§5).** Corpus-wide zero on invoice / rate-card
  / third-party-spend / procurement / vendor-governance. Distinct from the existing "Vendor Management"
  (coordination). Recorded as a decide-later gap, not resolved.
- **Exit criterion (§5) — recorded as RUN, two data points.** Demo JD passed (P&L resolved;
  product-company experience is the deliberate honest gap). Structured JD surfaced the database
  requirement (SQL Server/PostgreSQL/Redis-family) as a new gap, being fixed via Use Case edits (Network
  Eng / Octane / TICARA) + the detector batch. Not fully passed until the database fix re-run confirms.

### 2026-07-25 — Capability spot-check + AI-workflows / prototypes augments (verified live in the 24JUL26 corpus)

- **"Building Effective AI-Assisted Development Workflows"** — added one Competency, **Claude Code
  Fluency** (not three vendor tags, per §3.D), and named Claude / Claude Code in 5PSummary matching
  Situation. ChatGPT/OpenAI deliberately excluded (redundant with existing OpenAI API homes; the
  narrative frames ChatGPT as outgrown, not where the depth is). Pass 1 vendor item entered.
- **"Delivering Working Prototypes in Days, Not Months"** — §7 draft was entered
  (Situation/5P/Theme/most of Action). Fixed a gap: Competencies had Alexa Skills / Conversational AI
  / MQTT with zero Action support; added an Action bullet for the Alexa-Skills voice-interface /
  serverless-backend (software half), removed MQTT (hardware-side, owned by "Building Smart, Connected
  Devices at Accenture's Liquid Studio"). Story-boundary logic: that story owns the device half of the
  robotic bartender, this one owns the software half.
- **Capability tag-onto spot-check (14 of 14):** 6 hold (Payments & Financial Services, Tech-Enabled
  Business Transformation, Agile & DevOps Leadership, Platform Strategy, Product Development &
  Prototyping, Cloud Security & Compliance); 3 dropped (Microsoft 365, AI for Business, Technical
  Solution Design — see §3 for reasons); 2 augmented on "Building Cloud Innovation Centers (CIC)" (P&L
  Management, People Management); Executive-level Communication re-anchored to "Balancing Execution
  Speed with Security and Compliance"; Organizational Development renamed to **Practice Development**
  and anchored across 6 stories (all 6 confirmed live). Enterprise Digital Transformation (the 14th)
  closed via 3 distinct homes — "Shifting Client Focus from What They Build to How They Work" (Fortune
  500 general pattern), CIC (internal), Norfolk Southern (client-specific); Capital One checked and
  excluded (execution, not operating-model change). **Full 14-skill spot-check complete.**
- **Budget Management** — added a second real home, "Stabilizing and Delivering AT&T's Southeast CRM
  Replacement" ($1M delivery scope, eliminated operational overspend), alongside existing Fiserv.
- **Method confirmed:** capability skills are semantic, not string-matchable (all 14 returned zero
  string hits despite real hit-counts); and Category/Theme classifier fit gates where content belongs
  (see §8). Sequencing status (array/ingestion deferred) recorded in §11.
- **Set C prune closed:** live-verified the four director/architect-altitude risk stories (Norfolk
  Southern Railroad, AmEx, Fiserv $8.5M, DDD microservices) — none carries SQL or Java in Competencies,
  so there was never any self-credit to drop. The re-homing had already happened. Checkbox was stale,
  now closed (§5).
- **Set E disposition corrected:** Azure/Aurora/ElastiCache moved from "Open (thin)" to Resolved
  (ceiling) — single home is the honest weight for project-specific choices; do not re-open. Rule
  refined (§3 legend, §8): disposition tracks true weight, not raw count.

### 2026-07-24 — Toolkit-connector / data-store tagging pass (confirmed live in the 24JUL26 corpus)

Closed most of Set E by surfacing data stores already present in existing builds, at the right altitude:
- **"Driving Cloud-Native Innovation through TICARA Framework"** — added Amazon Aurora (Action,
  Competencies, Process, 5PSummary; fixed "Arurora" typo), then Oracle and SQL Server as
  toolkit-connector options (Action data-store bullet, Competencies, 5PSummary).
- **"Driving Modern Software Engineering with Project Octane"** — added AWS AppSync, GraphQL, and
  ElastiCache tied specifically to the Summit reference app (Action, 5PSummary, Process, Competencies).
  Result left generic by design, matching the TICARA precedent.
- **"Architecting Enhancements for AT&T's Network Engineering Platform"** — added SQL Server to Action
  (the .NET/C#/ESRI leadership bullet), Competencies, 5PSummary.
- **"Building AT&T Mobility's Service Delivery Platform"** — added Oracle RAC to the Service Broker
  database bullet (Action), Competencies, 5PSummary. Hands-on altitude, not directing.
- **"Resolving Cross-Domain Data Issues for AT&T's Order Management"** — added Oracle + CASE Method
  (OCP credential, named design methodology at architect altitude), including the 5PSummary line
  ("data architecture leadership using Oracle's CASE method"). SQL deliberately NOT added: a "probably
  wrote some SQL in 2006" plausibility guess is inference, not evidence, and would blur the
  Mobility-vs-Cross-Domain contrast the doc is calibrated on. Stays Relational Database Design + Oracle.
- **PostgreSQL** — decided drop, no honest home; deliberate non-claim, out of the scored set.
- **TypeScript** — decided drop; only React exposure, no substantial hands-on TypeScript. Non-claim.
- **ECMAScript** — decided drop; it is just JavaScript, folded into the existing JavaScript claim
  (already Content-there). Non-claim.
- **Vendor cluster (Claude Code / Claude Skills / Anthropic Claude)** — confirmed generic references,
  not the named product features; not separately trackable. Covered by the Claude Code Fluency
  competency on "Building Effective AI-Assisted Development Workflows." Marked "covered, not separately
  claimed" in §3; Set D collapse closed.
- **Backlog audits** — JavaScript, Mobile App Dev, IaC, DynamoDB, OpenAI API audited and hold as-is.
- Consequences reconciled into §3 (status column), §3.D, §3.E, §5, §6 Oracle, §7; §9 decision 1
  unaffected (Cross-Domain SQL verdict unchanged — Oracle/CASE Method is not a SQL claim).
- **Remaining open (as of 24JUL):** the §7 draft entry and the 14-skill spot-check — both resolved
  25JUL (see the entry above). Azure was recorded "closed" here, later corrected to Open (thin, single
  tag) once the Disposition logic landed — see §3.E.
- **Validated §5 against `MATTGPT-080_skill_triage_v2.xlsx`:** all 73 triage skills are in the §3 map;
  triage's 8 AI-build / 22 tag-onto / 43 anchored buckets reconcile. Triage is a superseded 28JUN
  input; enumerated the 14 genuinely-remaining capability skills into §5 with a spot-check-not-skip caveat.

### 2026-07-23 — Altitude reconciliation of the non-claim finding

The Key finding (§2) was reframed from era-based ("early practitioner era is a deliberate non-claim")
to altitude-based (the test is hands-on vs. directing, per story; the date was never the filter),
correcting the 02JUL26 framing. Consequences: SQL is a multi-era hands-on claim, not a blanket
non-claim — "Building the Payment Engine Behind JP Morgan ACCESS" and "Building AT&T Mobility's
Service Delivery Platform" are the two hands-on citations (the AT&T Mobility SQL tag was verified
already present in the live corpus — Competencies: SQL, Relational Database Design, Schema Design,
Database Design & Optimization; Use Case(s): "hands-on schema design and SQL development for platform
data integration"); Norfolk Southern stays the director-altitude non-claim; "Resolving Cross-Domain
Data Issues for AT&T's Order Management" (Oct 2005, Data & Functional Architect) is resolved as
Relational Database Design, not SQL — already reflected in the corpus (§9 decision 1 closed; it had
been briefly mis-marked "open"). Also recorded: the SQL claims are "SQL" the language; "SQL Server"
the named product still has no home (JPM ACCESS is tagged literally "SQL"). Oracle stays a non-claim,
correction identified but not yet written to the map (§6). PostgreSQL, Aurora, ElastiCache, and SQL
Server were open as of 23JUL (closed 24JUL — see the entry above). The master-filter table cells,
§3.C, §5, §6 SQL, and §9 decision 1 were all reconciled to this.

### 2026-07-23 — STAR corpus ingestion batch (confirmed via ingestion diff, in Pinecone)

Stories referenced by title (see §8 rule):
- **"Simplifying MattGPT's RAG Pipeline Through Entity Gate Removal"** and **"Implementing
  Eval-Driven Development for RAG Systems"** — Prompt Engineering pulled from Competencies
  (ungrounded); the latter also got "Regression Testing for LLM Systems" + a new Action bullet on
  retrieval verification.
- **"Building the Payment Engine Behind JP Morgan ACCESS"** — added SQL, AML Transaction Monitoring
  Integration, Sanctions & PEP Screening, Risk-Based Entitlements Design, Sev-1 Incident Response,
  On-Call Ownership + 4 new Action bullets.
- **MATTGPT-154 operational-ownership tags** (Production Support / Sev Defect Management / Release
  Planning / Sev-1) added to "Consolidating Legacy Payment Systems into JP Morgan's Unified ACCESS
  Platform," "Building AT&T Mobility's Service Delivery Platform," "Driving Salesforce Adoption
  Across 12 Countries for JP Morgan," "Leading Global Delivery of JP Morgan's Asset Management
  Salesforce Solution," "Overhauling Entitlement Management for JP Morgan ACCESS," and "Recovering
  Fiserv's $8.5M White-Label Card Portal." Action-level grounding on all but the two Salesforce/
  data-migration rows ("Leading Global Delivery..." and "Overhauling Entitlement Management...") were
  accepted as tag-only per explicit call.
- **AWS (and related toolkit tags)** added/expanded on "Building Tangible Cloud Tech Skills for HBCU
  Students," "Creating and Leading a Self-Directed Capability Development Program," "Driving
  Cloud-Native Innovation through TICARA Framework," "Launching a Self-Paced Learning Program for
  Emerging Technologies," "Mentoring Underserved High School Students into Technology Careers," and
  "Eliminating Idle Server Costs with Serverless Architecture," grounded in existing Result/
  Performance text.
- **"Modernizing Railroad Revenue: Transitioning from Legacy to Cloud"** — tagged Relational Database
  Design (not SQL, per architecture-vs-hands-on distinction); removed an unconfirmed 20% cost claim
  from Interview Questions.
- **"MattGPT: RAG Architecture & Semantic Search Implementation"** — Python added; 5PSummary and Use
  Case(s) grounded.
- **"Building JP Morgan's Global Payments Gateway Across 12 Countries," "Implementing BDD for System
  Behavior Specification," "Stabilizing and Delivering AT&T's Southeast CRM Replacement"** — verified
  already correct, no changes.
- **New story: "My Chatbot Kept Flattering Me Instead of Answering the Question. Here's How I Fixed
  It."** (Prompt Engineering, root-cause diagnosis arc, Jan 25–Feb 2 2026).
- AT&T Southeast CRM and "Building JP Morgan's Global Payments Gateway Across 12 Countries" verified
  already grounded, no change. Confirmed via `generate_jsonl_from_excel.py` that edits landed in
  `echo_star_stories.jsonl`.

### Earlier — "Stabilizing and Delivering AT&T's Southeast CRM Replacement"

Action reordered: 3 scope/headcount lines pulled out of the lead (they live in Task), 12 action
lines kept intact, none merged. Process trimmed 10→9 (dropped the "served as manager-level leader"
role line + fixed its bare-dash formula risk). Performance correct as-is. Oracle honest as
legacy-migration context — no Oracle competency claim (migrated off it, didn't build on it). Tag
case-duplication left alone (separate known ticket).

### Surfaced by ingestion, not this session's work (noted, not owned here)

- "Launching a Self-Paced Learning Program for Emerging Technologies" has an "and Splunk"
  Oxford-comma parsing artifact, still unfixed.
- Two Capital One stories carry Monday's edits (not this session's) — not a concern.

---

## 5. Open items & backlog

### Pass 1 — augment existing stories

- [x] "Building Effective AI-Assisted Development Workflows" — vendor cluster closed 24JUL26. The
      AI-assisted-fluency competency (Claude Code Fluency) is already on the story; Claude Code /
      Claude Skills / Anthropic are generic references, not separately tagged (§3.D). No further action.
- [x] "Delivering Working Prototypes in Days, Not Months" — §7 draft entered (Situation/5P/Theme/most
      of Action). Fixed a real gap: Competencies carried Alexa Skills / Conversational AI / MQTT with
      zero Action support — added an Action bullet for the Alexa-Skills voice-interface / serverless-
      backend work (software half), and removed MQTT (hardware-side, owned by "Building Smart, Connected
      Devices at Accenture's Liquid Studio"). Pass 1 complete.

### Pass 2 — new stories (Set E)

- [x] Set E — **fully resolved.** Multi-home: SQL Server, Oracle. Single-home at the honest ceiling
      (project-specific, do NOT re-open hunting for breadth): Amazon Aurora, ElastiCache, Microsoft
      Azure. Dropped: PostgreSQL, TypeScript, ECMAScript. Nothing left to chase — one real home is the
      truthful weight for the three single-home skills.

### Prune

- [x] Set C (director/architect-altitude self-credit) — **closed 25JUL26, nothing to execute.**
      Live-verified the four risk stories: "Modernizing Railroad Revenue" (Norfolk Southern), "Lowering
      Barriers to Adoption for American Express's Virtual Payments Platform," "Recovering Fiserv's $8.5M
      White-Label Card Portal," and the DDD microservices story. **None carries SQL or Java in
      Competencies** — Railroad has Relational Database Design, the other three have neither. The
      re-homing already happened (SQL → JPM ACCESS + AT&T Mobility; Java → the 3 curriculum stories),
      and the directing-altitude stories were never tagged in the first place. No self-credit to drop.
      Do not re-open.
- [x] SQL tag on "Building AT&T Mobility's Service Delivery Platform" — confirmed already present in
      the live corpus (Competencies include SQL, Relational Database Design, Schema Design, Database
      Design & Optimization; Use Case(s) grounds "hands-on schema design and SQL development for
      platform data integration"). Closed, no action.
- [x] AT&T Cross-Domain SQL-vs-architecture question — closed. Answer: architecture, so Relational
      Database Design, not SQL; corpus already tagged correctly. No action.
- [x] Collapse Set D vendor enumeration — done 24JUL26. Claude Skills / Claude Code / Anthropic Claude
      marked "covered, not separately claimed" in §3; the tool-agnostic fluency claim stands.
- [ ] Sequencing constraint: corpus carries evidence **first**; matcher change (stop scoring
      profile-only skills) lands **last**, after re-embedding. Order matters or Role Match briefly
      loses skills it was crediting.
- [~] **EXIT CRITERION — RUN, two data points (26JUL26).** The gate before dropping the skills array
      (and the -088 matcher change): run a representative JD (–097 taxonomy) through Role Match twice,
      array intact vs blanked, 2–3× per condition. **Results so far:**
      - **Demo JD — passed.** P&L resolved (cites the dedicated story, not the profile); product-company
        experience surfaced as the deliberate honest gap (not a corpus failure).
      - **Structured JD — surfaced a new gap:** the database requirement (SQL Server / PostgreSQL /
        Redis-family) flipped. Being fixed via Use Case edits on "Architecting Enhancements for AT&T's
        Network Engineering Platform," "Driving Modern Software Engineering with Project Octane," and
        "Driving Cloud-Native Innovation through TICARA Framework," plus the detector-driven batch.
      - **Not fully passed** until the database fix re-embeds and the structured-JD A/B re-run confirms
        the flip resolves. The flip did its job — it named the remaining work.
- [x] **Retrieval fix — P&L: resolved via a dedicated story, not a Use Case clause.** The original plan
      (add a P&L clause to "Building Cloud Innovation Centers (CIC)" Use Case(s)/5PSummary) was rejected:
      one clause couldn't move CIC's innovation-dominated embedding (ranked 37). Instead, P&L got a
      dedicated story where P&L is the thesis, "Owning the P&L: From Engagement Margin to Center Cost
      Base" — confirmed retrieving **rank 1 @ 0.534**, A/B strong in both conditions. Closed.
- [ ] **Retrieval-latency audit (before the array drops).** "Resolved" now requires Use Case(s)
      evidence (§3 legend). Audit every skill marked Resolved on Competencies/Action tags only for
      retrieval-field presence; any without Use Case(s) evidence is **retrieval-latent** and will gap at
      array-drop. Confirmed retrieval-latent: **Vendor Management** (10 hits, zero retrieval-field
      occurrences). Others expected — sweep the Resolved rows. Not a fix-all-now item; the point is no
      surprises at drop time.

### Backlog audits

- [x] JavaScript, Mobile App Dev, IaC, DynamoDB, OpenAI API — audited, hold as-is.
- [x] **Triage "tag-onto-story" spot-check — all 14 resolved 25JUL26** (§3 statuses updated):
      - **6 hold, no action:** Payments & Financial Services, Tech-Enabled Business Transformation,
        Agile & DevOps Leadership, Platform Strategy, Product Development & Prototyping, Cloud Security
        & Compliance.
      - **3 dropped:** Microsoft 365 (zero real hits; Dynamics-CRM citation was a token-overlap false
        match), AI for Business (redundant with Generative AI / LLM Integration / RAG / Semantic Search
        / AI-Enabled Product Innovation / Responsible AI), Technical Solution Design (redundant with
        Solution Architecture, same homes).
      - **2 augmented (both on "Building Cloud Innovation Centers (CIC)"):** P&L Management (tag + Action
        bullet, full P&L accountability), People Management (tag; Action already carried it).
      - **1 re-anchored:** Executive-level Communication → "Balancing Execution Speed with Security and
        Compliance" (map cited the wrong story).
      - **1 renamed + anchored:** Organizational Development → **Practice Development**, anchored across
        6 stories (all confirmed live).
      - **Enterprise Digital Transformation (the 14th):** tag added to 3 distinct homes — "Shifting
        Client Focus from What They Build to How They Work" (Fortune 500, the general repeatable
        pattern), CIC (internal), "The CIC's First Engagement" (Norfolk Southern, client-specific). Row
        89 (Capital One) checked and excluded — execution/velocity work, not operating-model change.
- **Methodology (now a §8 rule):** literal string matching is the wrong instrument for capability/
  leadership skills — all 14 returned zero string hits despite real map hit-counts, because retrieval
  is semantic, not string-based. The correct test: does a *delivery* story (not "About Matt")
  demonstrate the capability thematically.
- `MATTGPT-080_skill_triage_v2.xlsx` remains a superseded 28JUN input, not a live worklist.

### Stories to write / recover (the story-side worklist)

Story equivalent of the §3 skill tracker. Status is the decision state; several are gated (blocked,
audit-first, or needs-decision) and should not be written until the gate clears.

> **Cross-check:** the "Skills it closes" column predates the 24–25JUL drops/reframes. Re-validate
> against §3 before using skill-closure as justification — **AI for Business** and **Technical
> Solution Design** are now Dropped, **Anthropic Claude** is Covered, and **Organizational Development**
> is renamed **Practice Development**. The story may still be worth writing on its own merits; just
> don't cite a retired skill as the reason.

| Story | Type | Source | Priority | Effort mode | Draft exists? | Skills it closes | Status | Notes |
|---|---|---|---|---|---|---|---|---|
| AI Enablement Before It Had a Name | Net-new | BACKLOG MATTGPT-078 | Medium | Write from draft | YES — full draft in BACKLOG.md | Anthropic Claude (indirect); AI for Business; Capability Development; Change Management; Skills Transformation | Ready — needs 5P + STAR field mapping before corpus add | CloudFirst + CIC enablement as retrieval anchor for AI Enablement / AI Transformation role queries; VP-level AI CoE positioning. |
| Data Quality Cleanup Journey Story | Net-new | BACKLOG MATTGPT-022 | Medium | Write from scratch | No — topic described | Eval-Driven Development; Relational Database Design; Python; AI for Business | **Blocked** — hold until MATTGPT-061 (retrieval overweighting) resolved | March 2026 data-quality pass across 85+ stories. Adding a 5th MattGPT-meta story may worsen CIC over-ranking; that's why it's held. |
| Failure / Hard-Call Story (TBD) | Net-new | BACKLOG MATTGPT-091 | Medium | Audit first, write if needed | No — subject TBD | (depends on topic chosen) | **Audit-gated** — Phase 1 audit corpus for failure content; Phase 2 probe failure-shaped queries; write only if gap confirmed | Candidates: a hire that didn't work, a wrong architecture call, a program killed, a performance conversation held too late. |
| Anti-Consulting Bias Reframe (corpus-wide) | Corpus reframe | BACKLOG MATTGPT-095 | Medium | Audit + targeted rewrites | N/A — edits to existing stories | (affects all leadership/engineering stories) | Not started — ~4–6h across 20+ stories | Surface org built / code shipped / people hired as the lead; consulting deployment as context. NOT erasing consulting history — changing what leads. |
| Broke a stalled diagnosis by treating a symptom as a hard constraint (ghost-avatar) | Net-new | Chat history (external session) | **High** | Write from draft | YES — full STAR draft in chat | Eval-Driven Development; BDD; Engineering Leadership; Technical Solution Design; Cloud-Native Application Development | Ready — highest priority | MattGPT ghost-avatar defect; root cause in <1h after 1.5 weeks closed it unfixable. Lead with method (falsify competing theories, read the framework's own bundle); let the time delta land as support, not headline. Dir/VP AI Transformation intent. |
| D18 — Strategic Partnerships | Net-new | Chat history (flagged Feb 24) | Medium | Write from scratch | No | Stakeholder Management; Executive-level Communication; Cross-functional Team Leadership; Platform Strategy | **Blocked** — confirmed corpus gap, but verify the resume claim it sources before writing | June 30 corpus check confirms no equivalent story in the 113-story corpus; adjacent stories touch partnership themes only indirectly. |
| Norfolk Southern — Conway's Law / product mindset | Net-new | Chat history (Jan 16, no decision) | Medium | Needs decision before writing | PARTIAL — "The CIC's First Engagement" is adjacent, not the story | Agile Transformation; Organizational Design; Tech-Enabled Business Transformation; Change Management | **Needs decision** — explicit go/no-go pending | Conway's Law angle: mainframe org structures recreated in cloud; rethinking how clients work, not just what they build. "CIC's First Engagement" mentions org structure/incentives but doesn't own the Conway's Law frame as primary thesis. |
| Sell-side commercial / deal-shaping (HSBC-anchored) | Net-new | Chat 26JUL26 (deferred decision) → **BACKLOG ticket (permanent home)** | Medium | Write from scratch | No | Commercial/deal-shaping; pricing & costing (CFM); LCR/UCR resourcing; estimating; CRs & SOW expansion; outcome-based contracting | **Deferred** — gated on nothing; write after evidence-population + array drop, when energy allows | **Distinct from the buy-side "Owning the P&L…" story — do NOT bundle.** Buy-side = owning the number on work you deliver; sell-side = winning work commercially. Covers pricing/costing with CFM, LCR/UCR resourcing, estimating, CRs and SOW expansions, and the hours×rate → outcome-based contracting shift. Anchor: HSBC ($10M SOW via ROM / pricing model / staffing plan). Currently nowhere in the corpus. Migrating to a BACKLOG ticket; this row is the interim capture so the decision survives the doc's retirement. |
| Vendor commercial / spend management | Gap — decide later | Corpus sweep 26JUL26 | Undecided | Decide first, then write-or-drop | No — undemonstrated | vendor commercial/spend control (invoice, rate-card, third-party spend, procurement, vendor governance) | **Gap recorded, not resolved.** Corpus-wide zero on invoice / rate-card / third-party-spend / procurement / vendor-governance. Distinct from the existing "Vendor Management" skill (coordination, not controlling third-party money). | Same shape P&L had (real capability, no retrieval home) — decide later whether it's a claim worth surfacing or an honest gap. Recorded here so it's not invisible; do not resolve now. |

### Recover-first (purged stories, before authoring net-new)

- [ ] Read `STAR_Story_Triage_Mar25_vs_Jun26.xlsx` (131 rows, only headers read so far) and enumerate
      purged stories worth resurrecting — named so far: the Takeda healthcare + cloud-native + genAI
      16-week story (GONE/HIGH, "resurrect as standalone"). Not yet triaged.

### Housekeeping

- [ ] "Launching a Self-Paced Learning Program for Emerging Technologies" — fix the "and Splunk"
      Oxford-comma parsing artifact.

---

## 6. Corrections queue — skill-keyed

> §3 is now the source of truth and its **status column is kept current**, so status corrections get
> applied there directly and marked Applied here. What remains "Open" in this queue is work not yet
> reflected in §3. Keyed by skill name; stories referenced by title.

| Skill | Current (stale) | Direction | Status |
|---|---|---|---|
| Prompt Engineering | "Partial," 1 hit, cites "MattGPT: RAG Architecture & Semantic Search Implementation," Action "single hit; extend or add second story." | Count now wrong — **two** stories demonstrate it: the MattGPT RAG story plus the new "My Chatbot Kept Flattering Me..." story. Reclassify off Partial/1-hit. | **Applied to §3** (Content-there, 2 stories) |
| SQL | "Partial," 1 hit, cites "Modernizing Railroad Revenue: Transitioning from Legacy to Cloud" as sole hit. | Wrong on both count and citation (see §2 Key finding). SQL is a multi-era hands-on claim by the altitude test. Two hands-on citations: "Building the Payment Engine Behind JP Morgan ACCESS" and "Building AT&T Mobility's Service Delivery Platform." Railroad is a non-claim (carries Relational Database Design). "Resolving Cross-Domain Data Issues for AT&T's Order Management" is resolved (Relational Database Design, not SQL; already in the corpus). AT&T Mobility's SQL tag is confirmed already present. Reclassify off Partial/1-hit. Note: claim is "SQL" the language, not "SQL Server." | **Applied to §3** (Content-there; homes re-cited) |
| Oracle | "Partial," 1 hit, cites "Stabilizing and Delivering AT&T's Southeast CRM Replacement." | Two changes. (1) The Southeast CRM citation is wrong: Oracle there is the legacy system replaced, not built in — that instance is a non-claim. (2) But Oracle is now genuinely homed as of 24JUL26 — re-cite to "Driving Cloud-Native Innovation through TICARA Framework," "Building AT&T Mobility's Service Delivery Platform" (Oracle RAC, hands-on), and "Resolving Cross-Domain Data Issues for AT&T's Order Management" (Oracle / CASE Method). Reclassify to Content-there against those homes, not Content-needed. | **Applied to §3** (Content-there; Southeast CRM dropped, 3 homes cited) |
| Java | "Content-there," 7 hits (training/curriculum context). | Content-there part is fine, **don't touch it**. Missing: a note distinguishing it from the separate resolved non-claim of hands-on early Java (AmEx, Fiserv, DDD stories) so a future read doesn't conflate them. | **Applied to §3** (note added to Java row) |
| Microsoft Azure | "Content-needed," 0 hits. | Azure is tagged in "Delivering Working Prototypes in Days, Not Months" Competencies (pre-session). One home, project-specific — the honest ceiling, not a gap. | **Applied to §3** (Partial / Resolved (ceiling); single home is correct, do not re-open) |

---

## 7. Active story augment — "Delivering Working Prototypes in Days, Not Months"

> From the 01JUL26 session (Liquid Studio client-delivery work). A full draft, **ready for you to
> enter into the master** (nothing was written to the master for you). Target story: **"Delivering
> Working Prototypes in Days, Not Months"** in `MPugmire - STAR Stories - [DATE].xlsx`, sheet "STAR
> Stories - Interview Ready." Find it by title, not row.

### The decision (settled)

Gap skills (Azure, cloud breadth, IoT/serverless) belong on this **existing** story as ONE capability
story with clients as evidence inside it. NOT a new story; NOT one-story-per-client (re-creates the
sprawl consolidated away a year ago); NOT bolted onto the internal/enablement stories ("Driving
Cloud-Native Innovation through TICARA Framework," "Driving Modern Software Engineering with Project
Octane," "Launchpad: Empowering Clients and Teams with AWS Enablement and Cloud Certifications,"
"Building Smart, Connected Devices at Accenture's Liquid Studio"). Oracle is EXCLUDED here — doesn't
fit the modern/innovative theme; lands elsewhere or stays a non-claim.

### The unlock: the missing WHY

The story had HOW (design thinking, co-creation, CI/CD) and WHAT (prototypes in days) but no WHY. The
why = **clients came to us with a problem or an idea they brought**, sometimes a transformation-or-die
pressure to stay relevant in their market. Feeds both surfaces: the scorer gets demonstrated evidence
for the stack tags; Ask Agy gets the "so what" its WHY→HOW→WHAT voice needs.

### Structure: constant SPINE + three WORKSTREAMS

The arc is constant; the build varied by client (variety is the point, not a gap).
- **Spine (constant):** client brings problem/idea → design thinking, journey maps, UX/CX
  pain-point interviews, whiteboarding → co-create with full cross-functional team (client +
  Accenture) → validated prototype in hours/days.
- **Workstream 1 — UX/CX:** journey maps → crude mocks → validate → wireframe → prototype → validate.
- **Workstream 2 — Physical/IoT:** design thinking on the physical object → cardboard / 3D-printed /
  laser-cut iterations → smart-thing prototyping (gauges, actuators, sensors). ANCHOR EXAMPLE = the
  robotic bartender (do NOT call it "Mixy"): an Alexa skill takes a drink order + tells a joke →
  serverless backend stores/retrieves recipes → recipe sent over MQTT to a Raspberry Pi orchestrating
  liquid actuators in millisecond timing. Stack: AWS, Alexa Skills, serverless, MQTT, Raspberry Pi,
  IoT/edge.
- **Workstream 3 — Software:** iPhone/web apps and services to prove art-of-the-possible; JS
  frameworks (MEAN, Node, Angular, React) + Python on cloud-hosted architectures.

### Altitude / honesty rules (don't lose these)

- **Co-creation is the altitude.** Full cross-functional team, client + Accenture, building together
  in hours/days. NOT solo "I built it," NOT watered-down "I facilitated." Phrase technical lines as
  the team delivering, not a carved-out solo build.
- **Specific where remembered, categorical where not.** The robotic bartender names its exact stack
  (remembered concretely); software/UX workstreams described as the RANGE worked across — accurate,
  not a hedge, because the work genuinely varied.
- **Cloud = fit-for-purpose across AWS/GCP/Azure, defaulting to AWS as an AWS Launchpad** (you were
  AWS-funded). Makes Azure + GCP honest at RANGE altitude and explains the AWS lean. Keep the
  Launchpad mention to ONE clause — don't poach "Launchpad: Empowering Clients and Teams with AWS
  Enablement and Cloud Certifications."
- **Tag only what the Action demonstrates.** No bare competency tags; every tag traces to Action
  evidence. Write Action first, Competencies follow.

### The four fields a full skill-restoration touches

Competencies (skill-match tag) · Action (STAR evidence/demonstration) · Use Case(s) + 5P Summary
(retrieval-critical; **Use Case(s) is the front-loaded, strongest retrieval signal — 5P is secondary**, corrected per §2) · Interview Questions (question-to-story routing).
Leave Hierarchy and the 5P Narrative group (Person/Place/Purpose/Performance/Process) untouched — not
skill-restoration targets.

### DRAFT TO ENTER

**Situation (why-first)**
> Clients came to Accenture's Liquid Studio with a real business problem or an unproven idea,
> sometimes a transformation-or-die pressure to stay relevant in their market, and no fast way to
> test whether a solution was viable. Traditional development would take months to answer a question
> the market was asking now. The studio's job was to compress that: start from the client's actual
> problem and, working side by side with their team, turn it into something working in hours and days.

**5P Summary (why → how → what; embedding anchor)**
> Clients arrived with a business problem or an unproven idea, often under pressure to stay relevant,
> and no fast way to validate a path forward. At Accenture's Liquid Studio, I led cross-functional
> teams — client and Accenture together — through a repeatable model: design thinking to find the real
> pain, then rapid co-creation into a working prototype. The build varied by problem across three
> workstreams — UX/CX, physical/IoT, and software — delivering validated prototypes in days instead of
> months and giving clients evidence to decide.

**Action (spine + three workstreams + robotic bartender anchor)**
Spine (constant):
- Started every engagement from the client's problem or idea, using design thinking, journey mapping,
  and UX/CX pain-point interviews to define what actually needed solving
- Co-created with the full cross-functional team (client + Accenture) in tight, iterative feedback
  loops, moving from whiteboard to validated prototype in hours and days
- Delivered working proofs-of-concept that proved feasibility and business value fast enough to drive
  a decision

UX/CX workstream:
- Turned journey maps and friction points into crude visual mocks, validated with users, then
  wireframed and prototyped through successive validation loops

Physical / IoT workstream:
- Prototyped physical smart things through fast material iterations (cardboard, 3D-printed,
  laser-cut) into working devices with gauges, actuators, and sensors
- Example — a robotic bartender: an Alexa skill took a guest's drink order and told a joke, a
  serverless backend stored and retrieved recipes [specific: AWS, Alexa Skills, serverless], and the
  recipe was sent over MQTT to a Raspberry Pi that orchestrated liquid actuators in millisecond
  timing to pour the drink [specific: MQTT, Raspberry Pi, IoT/edge]

Software workstream:
- Prototyped iPhone apps, web apps, and services to prove the art of the possible; cloud-native builds
  were fit-for-purpose per engagement across AWS, GCP, and Azure, defaulting to AWS as an AWS
  Launchpad, working across JS frameworks (MEAN, Node, Angular, React) and Python on cloud-hosted
  architectures [range: describes the toolkit the work spanned, not a single build]

**Competencies (each tag traces to evidence above)**
- KEEP: Cloud & Innovation Adoption, Agile & Lean Delivery, Design Thinking Facilitation, Rapid
  Prototyping, DevOps Implementation, Cloud-Native Development
- ADD (specific-evidence, robotic bartender): Serverless Architecture, IoT / Edge, AWS, MQTT
- ADD (range-evidence, workstreams): Microsoft Azure, Google Cloud Platform, Multicloud Architecture,
  JavaScript Frameworks, Python
- DO NOT ADD: Oracle (theme-fit excluded); individual framework names as separate tags beyond the
  JS-frameworks capability

**Interview Questions (add these question-shapes)**
- How have you rapidly validated a business idea or turned a client problem into a working prototype
  in days?
- Tell me about building an IoT or connected-hardware prototype — how did the software and physical
  pieces come together?
- How do you run a discovery-to-delivery process when the client's team is co-creating alongside you?

**Also fix on this story**
- Theme currently "Org & Working-Model Transformation" — likely a copy-down error given the content
  (rapid prototyping / cloud-native / design thinking). Pick a better enum value (Emerging Tech or a
  delivery/innovation theme fits).

### Next steps

**Entered 25JUL26** — draft is in the corpus (Situation/5P/Theme/most of Action), Theme fixed, and the
Competencies/Action gap resolved (Alexa-Skills Action bullet added, MQTT removed to the device story;
see §4). Remaining: re-run ingestion when ready (`python generate_jsonl_from_excel.py` → `python
build_custom_embeddings.py`) — user runs end of day.

### Still open in the corpus (reconciled to 23JUL26 state)

- **"Building Effective AI-Assisted Development Workflows"** augment — name Claude Code / Claude Skills
  / Anthropic in Situation + add ONE AI-assisted-fluency competency (not 3 vendor tags). Scoped, not
  entered. This is the Set D vendor cluster (§3.D) — coordinate there.
- **"MattGPT: RAG Architecture & Semantic Search Implementation"** — confirmed COMPLETE as of 01JUL26,
  no edits. (The map's "Prompt Engineering Partial" was a stale/false signal; the 23JUL26 work
  confirms this — see §6 Prompt Engineering.)
- **Broader Liquid Studio under-telling:** many named client engagements (Travelsify [cannot name],
  Coca-Cola, Marriott, National Wildlife Federation, Carnival, etc.) not in corpus. If ever addressed:
  capability-with-clients-as-evidence, NOT one record per client. This story is the vehicle; don't
  sprawl.
- **Oracle, SQL Server, Aurora, ElastiCache:** RESOLVED 24JUL26 — all homed via the toolkit-connector
  / data-store tagging pass (TICARA, Octane, AT&T Network Engineering, AT&T Mobility; see §3.E, §4).
  PostgreSQL was the one dropped as a non-claim.

---

## 8. Ground rules for agents working this doc

- **Ask before any write to Matt's device — every time, no exceptions.** Not just the main Excel
  file. Draft in the cloud workspace and deliver for review; commit to disk only on an explicit
  go-ahead. (Origin: an unauthorized write to this file in a prior session, no git history to restore
  from since it was untracked.)
- **Reference stories by TITLE, never row number.** Row numbers (Excel or pandas) shift on every
  master edit and are always stale — the 01JUL26 recap's numbers were already wrong by 23JUL26. The
  master is `MPugmire - STAR Stories - [DATE].xlsx`, sheet "STAR Stories - Interview Ready"; find
  stories by their Title column. Same for skills: key by skill name, not map row.
  - **If any task spec, hand-off, or agent (Code included) says "row N," treat it as stale spreadsheet
    coordinates.** Do not act on it. Re-anchor to the story's Title against the live corpus first, then
    proceed. "Row N" is the signal that someone is working from coordinates that may no longer point at
    the story they think they do (e.g. "row 21" = "Building Cloud Innovation Centers (CIC) - Bringing
    Silicon Valley Product Culture to Fortune 500").
- **Keep §3 status current; treat only counts as regenerable.** When a skill is homed, dropped, or
  reclassified, update its status in §3 in the same pass — a stale status makes agents re-litigate
  closed work. The Hits integer is the only regenerable column; recompute it from
  `echo_star_stories_nlp.jsonl` when a number matters, don't hand-chase it.
- **Disposition = represented at true weight, not raw hit count.** A Partial (one home) is **Open**
  only if the skill is a career-long theme that's under-represented (needs more homes); it's **Resolved
  (ceiling)** if it's a project-specific technical choice where one home is the honest maximum. Don't
  reflexively mark every Partial "Open" — and don't hunt for a second home on a single-project skill;
  manufacturing breadth is the exact failure §2 refuses. Multi-home the broad themes, single-home the
  narrow ones. (Content-there = Resolved; Content-needed = Open; non-claim = Dropped; folded = Covered.)
- **Resolved requires retrievability, not just a tag.** A Competencies/Action tag does NOT retrieve; a
  skill is fully Resolved only if its evidence reaches **Use Case(s)** (the front-loaded retrieval
  field, §2). A skill demonstrated only in Competencies/Action is **retrieval-latent** — mark it as
  such, not "Resolved," because it will gap the moment the profile array drops (proven: P&L, Vendor
  Management). Don't hand a retrieval-latent skill an unqualified Resolved.
- **Update in place:** when a skill's state changes, edit its row in §3 or §6 **and** append a dated
  line to §4. Don't let §2 (principles) or §11 (architecture) drift — they're stable reasoning, not
  worklists.
- **Score levers: Competencies (skill-match) + Use Case(s) FIRST, 5P Summary second (retrieval)** —
  not Action prose, not Performance. Use Case(s) is the front-loaded, strongest retrieval signal;
  5P Summary is positionally weaker (sits after the Situation block). Target Use Case(s) for any
  retrieval fix (see §2 field map). This is why the database and P&L fixes go to Use Case(s), not 5P.
- **Don't audit capability/leadership skills by literal string match — retrieval is semantic.** All
  14 tag-onto capability skills returned zero string hits despite real map hit-counts. The correct
  test: does a *delivery* story (not "About Matt") demonstrate the capability thematically?
- **Check the Category / Sub-category / Theme classifier fit before adding content to a story, not
  just literal evidence.** Taxonomy is a real signal: "Building Cloud Innovation Centers (CIC)" is the
  corpus's only story with Category "Leadership & Organizational Transformation" — use that when
  deciding where leadership/practice content belongs.

---

## 9. Open decisions

1. **AT&T Cross-Domain Data (2005) — RESOLVED:** were your hands on the SQL, or on the architecture
   above it? Answer: architecture. The story ("Resolving Cross-Domain Data Issues for AT&T's Order
   Management") reads Data & Functional Architect with governance/architecture language, no hands-on
   query, so it carries Relational Database Design, NOT SQL — and the corpus already reflects exactly
   that. Contrast with AT&T Mobility, dual-tagged (SQL + Relational Database Design) because you built
   the schema *and* wrote the queries. Kept here because it's the altitude test in miniature and the
   template for verifying every "augmentable" verdict.
2. **Single vendor tools (Claude Code / etc.):** a real build story with depth in *that one* tool, or
   genuine multi-tool fluency? (Decides whether any vendor name earns its own claim.)
3. **Index question — resolved:** this doc leads; `Skill_Evidence_Map.xlsx` retires as source of
   truth (the 73 rows are in §3). Tradeoff accepted: no spreadsheet sort/filter on the rows. Optional
   future: a script that regenerates §3's Hits column from the corpus (counts only; status stays a
   maintained decision column).

---

## 10. Corpus pipeline & key files

- **Master Excel (source of truth for stories):** `MPugmire - STAR Stories - [DATE].xlsx`, sheet
  "STAR Stories - Interview Ready" (also under `.../Career Hub/Content Vault/Storytelling &
  Anecdotes/`). Reference stories by Title.
- **Repo:** `/Users/matthewpugmire/Projects/portfolio/llm_portfolio_assistant/`.
- **Pipeline (one-directional):** Excel → `generate_jsonl_from_excel.py` → `echo_star_stories_nlp.jsonl`
  (prod corpus) → `build_custom_embeddings.py` → Pinecone index `matt-portfolio-v2`. No manual JSONL
  surgery (ARCHITECTURE.md rule).
- **Other:** `ARCHITECTURE.md`, `services/jd_assessor.py`, `data/matt_profile.json`.

---

## 11. Architecture approach (MATTGPT-080 spine — decided in principle, parked)

> Pertinent context, not a worklist. This is the "why" the profile is retiring and the shape of the
> convergence fix. Grounded in ARCHITECTURE.md, which was reviewed.

### The real problem: divergent sources

Role Match and Ask Agy can give different answers because they read DIFFERENT sources: Role Match
reads `matt_profile.json` (an ungoverned island); Ask Agy reads the corpus. The profile can assert a
skill the corpus can't back → a contradiction a CTO would catch. Convergence is the requirement.

### The fix (smaller than a store migration)

- ARCHITECTURE.md ALREADY declares Excel the canonical source of truth, JSONL derived, one-directional
  Excel→JSONL→Pinecone flow, "No Manual JSONL Surgery" rule.
- The Hybrid Sovereignty model + MATT_DNA ALREADY implement "one source, derived projection so it
  can't drift" — for CLIENT NAMES (via `generate_dynamic_dna()`). Skills are the identical unsolved
  problem.
- `matt_profile.json` is the anomaly: outside the governed flow, read only by Role Match. THAT is the
  divergence.
- **The fix:** derive the claimable-skills set from the corpus's own per-story **Competencies** arrays
  (already in Excel→JSONL), kill the profile's skills array, point Role Match at the derived set —
  same pattern MATT_DNA already uses for clients. The skill↔story relationship is ALREADY encoded as
  the Competencies field. Only degree/certs/identity (by-nature-unstorytellable facts) need structured
  attestation, as fact-type records inside the governed source.
- **One shared claim set, two renderings, neither surface asserts past it.** Same facts, two voices
  (structured for the matcher, human for Agy). Two backing types: skills backed by demonstration in
  the corpus; facts (degree/certs/identity) backed by attestation. Nothing claimable without one.
- **Scope of "retire":** retirement means the profile's **skills array** stops being an independent
  source of truth — NOT deleting `matt_profile.json`. Certifications and other fields stay.

### Sequencing status (25JUL26): evidence landed, array/matcher changes deliberately deferred

Corpus evidence for every disposition is in the 24JUL26 corpus. The following are **confirmed not yet
acted on by design**, per the sequencing rule (evidence first, array/matcher changes last, after
re-embedding), not oversight:
- `matt_profile.json`'s skills array still lists every drop-decided skill (PostgreSQL, TypeScript,
  ECMAScript, Claude Skills, Claude Code, Anthropic Claude, Microsoft 365, AI for Business, Technical
  Solution Design, Organizational Development). Intentional — the array change lands last.
- Ingestion (`generate_jsonl_from_excel.py` → `build_custom_embeddings.py`) not re-run since 24JUL;
  user runs it end of day.

### Two corrections to earlier thinking

- The earlier SQLite/store-migration proposal was OVERBUILT. Excel-as-SSOT is a documented,
  load-bearing decision. The bullet-hack / no-relationships pain is real but a SEPARATE
  quality-of-life question, decided on its own merits later — NOT bundled into the convergence fix.
- The Competencies-field cleanup (picklist / normalization) is PARKED. Already cleaned, no known
  drift, so no picklist on spec. If drift appears later, a picklist is the fix.

### Cert routing decision (Ask Agy)

Fact records (certs/degree) should be ANSWERABLE by Agy as short factual statements (in-voice, not
deflected to My Profile) — deflection creates a soft seam that undercuts convergence. Needs a
record-type flag the connector and prompt both key on (fact vs story). Explicit routing rule, not
emergent behavior.

### JD-assessor refactor (`services/jd_assessor.py`) — designed, parked, build sequence set

Verbatim code read confirmed four issues:
1. **Sequential fan-out** (`run_assessment`): 23–24 reqs × (Pinecone + gpt-4o) serial ≈ 336s.
2. **Repeated work:** `build_assessment_prompt()` re-reads `matt_profile.json` ~24×/run for an
   invariant prompt.
3. **Zero instrumentation** inside the loop.
4. **pc_score** returned per hit but never read programmatically (the cheap clear-vs-hard signal
   already flows through, unused).

Build order (parked):
1. Mechanical wins: hoist invariant prompt/profile build out of loop; add instrumentation (per-req
   timing, total, pc_score distribution capture).
2. Parallelize via **ThreadPoolExecutor** (explicit over asyncio — avoids async propagation into
   Streamlit; OpenAI + Pinecone clients are thread-safe). Add a max_workers cap.
3. Labeled-profile restructure: emit sub-typed FACT records (education/certs/identity). NOTE:
   post-convergence there is NO skills section in the profile — skills EXIT to the corpus. Write
   against the end state, not today's profile shape.
4. Targeted reasoning loop: route on pc_score — strong/story-backed → single-pass; weak → self-check.
   Post-convergence: facts short-circuit to deterministic lookup; skills route by pc_score.

Two empirical gates — measure before coding (UNRESOLVED):
- **pc_score threshold** (gates step 4): run real assessment scores, check distribution. If strong/weak
  separate cleanly (e.g. strong >0.82, weak <0.65) the threshold falls out of the data. If mushed, need
  a second signal. Don't hardcode.
- **max_workers cap** (gates step 2): 23–24 concurrent gpt-4o may hit OpenAI TPM/RPM. Start ~8–10,
  confirm against throttling via step-1 instrumentation. Don't fan out all 24 unbounded.

### Ticket map

- **-080** = matt_profile.json restructure (blocker for -088). Convergence fix proper. Dropping the
  profile's skills array is gated by the §5 Prune **exit criterion** (blank-the-array A/B test).
- **-088** = Role Match scorer honesty, on top of -080. Also gated by that exit criterion passing.
- **-094 probes** = CIC over-concentration + operational under-surfacing; run BEFORE -080, findings
  shape the restructure.
- **-077** = strip "Matt" from embedded queries on technical-noun shapes (query-side, independent).
- **-097** = career-intent refresh (independent, live-flow value now).
- **-129** = AT&T SE CRM + Fiserv expand-from-logged (operational depth, pairs with -094 sub-hyp B).
- **Critical path:** -094 → -080 → -088 → gates -012. -077 and -097 are parallel/independent.
