# Semantic Router: Analysis & Post-Mortem

**Date:** 2025-12-23 (Updated: 2026-01-05)
**Status:** ✅ RESOLVED - Root cause was nonsense filter, not semantic router

---

## ⚠️ POST-MORTEM: What Actually Happened

**The root cause was the word "solve" in the homework regex pattern, not the semantic router.**

### What actually happened:

1. **"What problems does Matt solve?"** → triggered `homework` category in nonsense filter → **blocked**
2. **Removed "solve" from pattern** → synthesis questions pass
3. **Semantic router was a red herring** - it returns `valid=False` but doesn't block (Pinecone overrides)

### Current state (as of Jan 5, 2026):

- ✅ **Nonsense filter**: Fixed (removed "solve" from homework pattern in commit `2dab2dc`, Dec 23, 2025)
- ⚠️ **Semantic router**: Still runs, returns `valid=False` for synthesis questions, but doesn't block them
- ✅ **Pinecone**: Returns high confidence (0.38-0.51) → queries pass

### All synthesis questions are now passing:

| Query | Semantic Router | Pinecone Score | Result |
|-------|----------------|----------------|--------|
| "What kinds of transformation problems does Matt consistently solve" | valid=False, score=0.569 | 0.382 → high | ✅ PASSED |
| "Where has Matt repeated success across different clients" | valid=False, score=0.627 | 0.460 → high | ✅ PASSED |
| "What distinguishes Matt from other cloud or transformation leaders" | valid=False, score=0.707 | 0.507 → high | ✅ PASSED |
| "What roles is Matt best suited for" | valid=False, score=0.631 | 0.441 → high | ✅ PASSED |
| "What evidence shows Matt can operate at Director / VP level" | valid=False, score=0.651 | 0.411 → high | ✅ PASSED |
| "What patterns show up across Matt's most successful transformations" | valid=False, score=0.645 | 0.415 → high | ✅ PASSED |

**Key finding:** The semantic router says `valid=False` for all of these, but they still pass because Pinecone returns high confidence scores (0.38-0.58).

### The router is NOT blocking these queries. The flow is:

1. Router runs → `valid=False` (but doesn't block)
2. Pinecone runs → returns high confidence
3. Query passes, Agy responds

### So the semantic router:

- ✅ Isn't blocking anything
- ❌ Costs an extra API call per query (~$0.00002 per request)
- ❌ Returns data nobody uses (intent_family logged to borderline_queries.csv but not consumed)
- ✅ But also isn't breaking anything

**Updated decision:** The router removal is now **low priority optimization, not urgent fix**. It's dead weight, not a blocker.

---

## What the Router Does

The semantic router provides **one specific function** in the current architecture:

```python
# Line 958-960 in backend_service.py
is_trusted_behavioral = (
    semantic_valid and semantic_score >= 0.8 and intent_family == "behavioral"
)

# Line 962-966: Bypass Pinecone confidence gate for trusted behavioral questions
if confidence in ("none", "low") and not is_trusted_behavioral:
    return reject
```

**Translation:** If Pinecone returns low confidence (< 0.15) BUT the semantic router identifies the question as behavioral with high confidence (>= 0.8), allow it through anyway.

---

## Test Results: Does This Bypass Matter?

### Behavioral Questions - Router Scores
```
✓ PASS 1.000 [behavioral] | Tell me about a time you failed
✓ PASS 0.848 [behavioral] | Describe a situation where you had to influence stakeholders
✓ PASS 1.000 [behavioral] | How do you handle conflict?
✓ PASS 1.000 [behavioral] | Give me an example of leadership
✓ PASS 0.856 [behavioral] | Tell me about a time you disagreed with your manager
✓ PASS 1.000 [behavioral] | Describe a failure and what you learned
```

**Result:** Router correctly identifies all behavioral questions with scores 0.848-1.000 (well above 0.8 threshold)

### Same Questions - Pinecone Direct Scores
```
✓ PASS 0.530 | Tell me about a time you failed
  → "What I Learned About Assumptions and Risk Ownership"

✓ PASS 0.496 | Describe a situation where you had to influence stakeholders
  → "Managing Global Stakeholder Engagement and Multi-T..."

✓ PASS 0.354 | How do you handle conflict?
  → "How I Approach Complex, Ambiguous Problems"

✓ PASS 0.436 | Give me an example of leadership
  → "Leadership Philosophy – How I Lead"
```

**Result:** Pinecone scores behavioral questions **0.354-0.530**, well above the 0.15 threshold

---

## Key Insight: The Bypass Is Unused

**The behavioral bypass only triggers when:**
1. Pinecone score < 0.15 (low confidence)
2. AND router score >= 0.8 (high behavioral confidence)

**But in reality:**
- Behavioral questions score **0.35-0.53 in Pinecone** (far above 0.15)
- The bypass never triggers because Pinecone already passes them

**Conclusion:** The router's only implemented advantage (behavioral bypass) **provides zero actual value** because Pinecone naturally scores behavioral questions high enough to pass.

---

## Theoretical Advantages (Not Implemented)

### 1. Intent Family Classification
**What it could do:** Tag queries with intent family (behavioral, technical, leadership, etc.)

**Current status:**
- Router returns `intent_family` variable
- BUT it's only used for the behavioral bypass check
- NOT used for result ranking, filtering, or UI display

**Value if removed:** None - we don't use this classification anywhere

---

### 2. Telemetry / Analytics
**What it could do:** Track which types of questions users ask (behavioral vs technical vs background)

**Current status:**
- Borderline queries (0.72-0.80) logged to `data/borderline_queries.csv`
- But this data isn't consumed by any analytics pipeline
- No dashboard, no insights, just accumulating CSV rows

**Value if removed:** Minimal - we're not acting on this data

---

### 3. Early Rejection (Before Pinecone)
**What it could do:** Reject garbage queries before hitting Pinecone, saving API costs

**Current status:**
- Router runs AFTER nonsense filter (which catches obvious garbage)
- Router runs BEFORE Pinecone search
- BUT router still calls OpenAI embeddings API ($0.00002 per request)
- AND if router passes, we still call Pinecone anyway

**Cost analysis:**
- Router embed call: $0.00002
- Pinecone query: $0.00001
- **Net savings: $0** (we're calling both APIs)

**Value if removed:** Actually saves money - one less embedding call per query

---

## What Gaps Would Removing the Router Create?

### Gap 1: No Behavioral Question Safety Net
**Description:** If Pinecone somehow scored a behavioral question < 0.15, the router bypass wouldn't be there to save it

**Risk:** LOW
- Test data shows behavioral questions score 0.35-0.53 (2-3x above threshold)
- Would require Pinecone to catastrophically fail (return wrong embeddings)
- Hasn't happened in production

**Mitigation:** None needed - if Pinecone is that broken, the router won't help

---

### Gap 2: No Intent Family Telemetry
**Description:** We'd lose visibility into which intent families users are querying

**Risk:** MINIMAL
- We're not using this data currently
- Can get same insights from Pinecone results (which stories matched)
- Can add query classification later if needed

**Mitigation:** Log matched story themes instead (e.g., "Leadership", "Delivery", "Team Scaling")

---

### Gap 3: No "Second Opinion" on Borderline Queries
**Description:** Router provides independent validation of query relevance

**Risk:** LOW
- Router blocks synthesis questions (false negatives)
- Pinecone passes synthesis questions (correct classification)
- The "second opinion" is wrong more often than right

**Mitigation:** Trust Pinecone - it's trained on actual story content, router is trained on 59 hardcoded examples

---

## Alternative Architectures (If We Need Behavioral Detection)

If we truly need to ensure behavioral questions never get rejected, we have better options than the semantic router:

### Option 1: Regex-Based Behavioral Detection
```python
# In nonsense filter or backend_service.py
BEHAVIORAL_PATTERNS = [
    r"tell me about a time",
    r"describe a situation",
    r"give me an example",
    r"how do you handle",
    r"walk me through",
]

def is_behavioral_query(query: str) -> bool:
    query_lower = query.lower()
    return any(re.search(pattern, query_lower) for pattern in BEHAVIORAL_PATTERNS)

# Bypass confidence gating for behavioral questions
if confidence in ("none", "low") and not is_behavioral_query(query):
    return reject
```

**Advantages:**
- Free (no API calls)
- Fast (regex matching)
- Explicit patterns (maintainable)
- Same safety net as router

**Disadvantages:**
- Doesn't catch paraphrased behavioral questions
- But neither does the router (synthesis questions prove this)

---

### Option 2: Lower Confidence Threshold for Behavioral Matches
```python
# Detect behavioral questions by checking if top Pinecone result is behavioral
top_result_theme = pool[0].get('Theme') if pool else None

if top_result_theme in ['Behavioral', 'Leadership', 'Conflict Resolution']:
    effective_threshold = 0.10  # More lenient for behavioral
else:
    effective_threshold = 0.15  # Standard threshold

if top_score < effective_threshold:
    return reject
```

**Advantages:**
- Uses actual Pinecone results (data-driven)
- No additional API calls
- Adaptive per-query

**Disadvantages:**
- Requires 'Theme' metadata in Pinecone
- Slightly more complex logic

---

## Recommendation

**Remove the semantic router** because:

1. **The bypass doesn't trigger** - Behavioral questions score 0.35-0.53 in Pinecone (far above 0.15 threshold)
2. **The telemetry isn't used** - No analytics pipeline consuming intent family data
3. **It costs money** - Extra embedding API call with no benefit
4. **It doesn't block anything** - Synthesis questions that score low in router still pass via Pinecone

**If behavioral safety net is required** (which test data suggests it isn't):
- Use regex-based detection (free, fast, explicit)
- OR lower threshold for behavioral themes (data-driven, no extra API calls)

**Risk of removal:** Near zero - the feature exists in code but provides no actual protection because Pinecone naturally handles behavioral questions correctly.

**Priority:** Low - it's dead weight (extra API cost, unused telemetry), but not breaking anything.

---

## Appendix: Full Test Data

### Behavioral Questions - Router vs Pinecone

| Question | Router | Pinecone | Gap? |
|----------|--------|----------|------|
| Tell me about a time you failed | 1.000 (behavioral) | **0.530** | No - Pinecone passes |
| Describe influencing stakeholders | 0.848 (behavioral) | **0.496** | No - Pinecone passes |
| How do you handle conflict? | 1.000 (behavioral) | **0.354** | No - Pinecone passes |
| Give me an example of leadership | 1.000 (behavioral) | **0.436** | No - Pinecone passes |

**Conclusion:** Router bypass would only help if Pinecone scored < 0.15. Reality: Pinecone scores 0.35-0.53 (2-3x safety margin).

### Synthesis Questions - Router vs Pinecone

| Question | Router | Pinecone | Problem? |
|----------|--------|----------|----------|
| What transformation problems does Matt solve? | **0.602** ✗ | 0.382 ✓ | Router says invalid, but Pinecone passes |
| What are common themes across Matt's work? | **0.572** ✗ | 0.333 ✓ | Router says invalid, but Pinecone passes |
| What kind of teams does Matt build? | 0.732 ✓ | 0.411 ✓ | Both pass |
| How does Matt approach technical leadership? | 0.800 ✓ | 0.498 ✓ | Both pass |

**Conclusion:** Router returns `valid=False` for some synthesis questions, but they pass anyway because Pinecone scores are high. The router's opinion is ignored.

### Garbage Query Scores (Pinecone Direct)
```
0.075 | How much did Madonna bras cost?
0.124 | What is the weather today?
0.125 | Explain quantum physics
0.129 | Who won the Super Bowl?
```

**Threshold:** CONFIDENCE_LOW = 0.15

**Result:** Clear separation between garbage (< 0.15) and valid (> 0.15) without router.
