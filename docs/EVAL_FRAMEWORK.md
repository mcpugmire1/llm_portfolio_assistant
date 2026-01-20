# MattGPT RAG Quality Evaluation Framework

## Why This Exists

We were playing whack-a-mole: finding bugs one query at a time with no visibility
into overall system health. This framework provides:

- **Proactive quality detection** before users find issues
- **Baseline metrics** to measure improvement
- **Regression prevention** on deploys

## The Core Problem

Agy's job is to **surface** Matt's pre-written content, not **generate** new content.
When the LLM "helps" by summarizing, it produces corporate filler instead of
Matt's authentic voice.

## Quality Dimensions

| Dimension | Definition | How We Test |
|-----------|------------|-------------|
| **Source Fidelity** | Response uses actual story content | Key phrases from 5PSummary appear |
| **Voice** | Sounds like Agy, not LinkedIn | Banned phrases absent |
| **Accuracy** | Correct client attribution | Client name matches source |
| **Authenticity** | Matt's real voice preserved | Specific DNA phrases present |

## Golden Query Set (25)

### Professional Narrative (10) - Test ALL, Voice-Critical

| # | Query | Ground Truth Phrases |
|---|-------|---------------------|
| 1 | "Tell me about Matt's leadership journey" | "builder", "modernizer", "complexity to clarity" |
| 2 | "Career Intent – What I'm Looking For Next" | "build something from nothing", "not looking for a maintenance role", "build what's next" |
| 3 | "How does Matt approach complex problems?" | "ambiguous problems", "first principles" |
| 4 | "What's Matt's leadership philosophy?" | "trust, clarity, and shared purpose", "high-trust cultures" |
| 5 | "Why is Matt exploring opportunities?" | "intentional transition", "step back", "reconnect" |
| 6 | "Where does Matt do his best work?" | "psychological safety", "challenge the status quo" |
| 7 | "What did Matt learn about risk ownership?" | "assumptions are risks in disguise", "raising a risk isn't owning it" |
| 8 | "Why is early failure important?" | "failure is a feature", "innovation", "experiment" |
| 9 | "What did Matt learn about sustainable leadership?" | "sustainable", "burnout", "pace" |
| 10 | "Matt's career transition after Accenture" | "intentional", "sabbatical", "reflect" |

### By Client (6) - Attribution Accuracy

| # | Query | Expected Client | Pass Criteria |
|---|-------|-----------------|---------------|
| 11 | "Tell me about Matt's payments work at JPMorgan" | JP Morgan Chase | Client name appears and bolded |
| 12 | "Matt's modernization work at RBC" | RBC | Client name appears and bolded |
| 13 | "How did Matt scale the CIC at Accenture?" | Accenture | Client name appears and bolded |
| 14 | "Norfolk Southern transformation" | Norfolk Southern | Client name appears and bolded |
| 15 | "Matt's work at Fiserv" | Fiserv | Client name appears and bolded |
| 16 | "Tell me about scaling learning programs" | Multiple Clients | Must say "Multiple Clients", "various", OR list 3+ distinct companies. Single client = FAIL |

### By Intent (5) - Routing Correctness

| # | Query | Expected Behavior |
|---|-------|-------------------|
| 17 | "What are Matt's core themes?" | Synthesis mode, multiple clients cited |
| 18 | "Tell me about a time Matt failed" | Behavioral, STAR format |
| 19 | "What's Matt's cloud architecture experience?" | Technical details |
| 20 | "Who is Matt Pugmire?" | Background summary |
| 21 | "Tell me about Matt's retail experience" | Graceful redirect (out of scope) |

### Edge Cases (4) - Robustness

| # | Query | What We're Testing |
|---|-------|--------------------|
| 22 | "Matt's GenAI work" | Thin theme (Emerging Tech, 3 stories) |
| 23 | "Governance and compliance work" | Risk theme coverage |
| 24 | [Multi-turn] Turn 1: "Tell me about JPMorgan payments" → Turn 2: "Tell me more about that project" | Context maintained across turns |
| 25 | "How did Matt transform delivery at JPMorgan?" | Synthesis + specific client combo |

## Banned Phrases (Voice Check)

If ANY appear, voice check fails:
```python
BANNED_PHRASES = [
    "stagnant growth",
    "emerging market demands",
    "limited potential",
    "prioritize maintenance over innovation",
    "strategic mindset",
    "foster collaboration",
    "stakeholder alignment",
    "meaningful outcomes",
    "high-trust engineering cultures",
    "bridge the gap between strategy and execution",
]
```

## Pass/Fail Criteria

### Professional Narrative Stories
- ✅ PASS: At least 2 of 3 ground truth phrases appear (exact or close match)
- ✅ PASS: Zero banned phrases
- ❌ FAIL: Fewer than 2 ground truth phrases OR any banned phrase

### Client-Specific Queries
- ✅ PASS: Correct client name appears AND is bolded
- ❌ FAIL: Wrong client attributed OR "Career Narrative" mentioned for non-narrative query

### Multiple Clients Stories
- ✅ PASS: Response says "Multiple Clients", "various clients", "across clients", OR names 3+ distinct companies
- ❌ FAIL: Attributes to single client (e.g., "At Accenture, Matt scaled learning...")

### Synthesis Queries
- ✅ PASS: 3+ different clients mentioned
- ❌ FAIL: Single client focus OR hallucinated clients

## Target Metrics

| Metric | Baseline (Current) | Target |
|--------|-------------------|--------|
| Professional Narrative Fidelity | ~60-70% (estimated) | 95%+ |
| Client Attribution Accuracy | Unknown | 100% |
| Voice (No Banned Phrases) | Unknown | 100% |
| Overall Pass Rate | Unknown | 90%+ |

## How to Run
```bash
# Run full eval suite
pytest tests/eval_rag_quality.py -v

# Run just Professional Narrative
pytest tests/eval_rag_quality.py -k "narrative" -v

# Generate report
python tests/eval_rag_quality.py --report
```

## When to Run

- **Before every deploy** (CI gate)
- **After prompt changes** (regression check)
- **Weekly** (drift detection)

## Files
```
tests/
  eval_rag_quality.py      # Main eval harness
  golden_queries.json      # Query + ground truth data
  eval_results/            # Historical results
    baseline_YYYYMMDD.json
    post_fix_YYYYMMDD.json
```

## Next Steps

1. [ ] Create `eval_rag_quality.py` with harness
2. [ ] Run baseline on current code
3. [ ] Apply "Surface, don't generate" prompt fix
4. [ ] Run benchmark, compare to baseline
5. [ ] Add to CI pipeline
