# Synthesis Mode Prompt Audit

**Source:** `ui/pages/ask_mattgpt/backend_service.py` lines 1091-1320
**Total lines:** 230 lines of prompt text
**Audit date:** January 26, 2026

---

## Structure Overview

| Section | Lines | Content |
|---------|-------|---------|
| System Prompt | 1097-1288 | ~190 lines |
| User Message | 1290-1320 | ~30 lines |
| **Total** | **~220 lines** | Sent to LLM |

---

## NEVER/DO NOT Rules (Flagged)

### Location 1: Lines 1099-1103 (Top of system_prompt)
```
## NEVER DO THESE (violating these is a failure)
- NEVER write meta-commentary about Matt (phrases starting with "This reflects...", "In essence...", "Matt's ability to...", "This demonstrates...")
- NEVER end with a reflection paragraph summarizing Matt's skills or patterns
- NEVER write "His approach shows..." or "This experience demonstrates..." — that's LinkedIn garbage
- Your response ENDS with the closing line. No summary paragraph after it.
```
**Flag:** Contains quoted examples of banned phrases - LLM may learn patterns FROM examples

### Location 2: Lines 1111 (PRIMARY DIRECTIVE)
```
2. DO NOT GENERALIZE: When themes appear across stories, reference them while keeping specific vocabulary...
```

### Location 3: Lines 1148-1153 (DUPLICATE - same rules repeated)
```
## NEVER DO THESE (violating these is a failure)
- NEVER use sycophantic openers ("Great question!", "That's a great topic!")
- NEVER use these words: "impactful", "holistic", "synergy", "showcasing"
- NEVER write meta-commentary about Matt (phrases starting with "This reflects...", "In essence...", "Matt's ability to...", "This demonstrates...")
- NEVER end with a reflection paragraph summarizing Matt's skills or patterns — your response ends with the closing line, period
- NEVER write "His approach shows..." or "This experience demonstrates..." — that's LinkedIn garbage
```
**Flag:** DUPLICATE of lines 1099-1103 with minor variations

### Location 4: Lines 1157-1163 (BANNED STARTERS)
```
**BANNED STARTERS - Never use these phrases:**
- "In my journey"
- "I've encountered"
- "I've learned"
- "In my experience"
- "What I found"
- "I was responsible"
```

### Location 5: Lines 1185-1186
```
- Do NOT reorganize responses by pattern unless the user explicitly asks about "patterns" or "themes"
```

### Location 6: Lines 1205
```
**DO NOT PARAPHRASE.** If the source says "I'm a builder," you write "Matt is a builder" - NOT "Matt builds things."
```

### Location 7: Lines 1213-1217
```
- Do NOT use a client/employer name from a supporting story to label the primary story
- Do NOT pull metrics from supporting stories into your primary narrative
- NEVER invent additional client examples to "show breadth"
```

### Location 8: Lines 1255-1264 (BANNED PHRASES - third location)
```
**BANNED PHRASES — Never use these (UNLESS the user's question explicitly asks about that topic):**
- "In essence..." or "Overall..." as sentence starters — state the point directly
- "This reflects Matt's..." — state the principle without meta-commentary
- "bridge the gap between strategy and execution"
- "foster collaboration"
- "high-trust engineering cultures"
- "meaningful outcomes"
- "stakeholder alignment"
- "strategic mindset"
- "execution excellence"
```

### Location 9: Lines 1280-1283
```
**DO NOT use "people were struggling" framing.** Frame as Matt's own goals:
- BANNED: "Job seekers were struggling...", "Engineers needed...", "Teams lacked..."
- **NEVER invent fictional stakeholders for personal projects.**
```

---

## Quoted Examples (Potential Learning Source)

| Line | Example Given | Risk |
|------|---------------|------|
| 1100 | "This reflects...", "In essence...", "Matt's ability to...", "This demonstrates..." | LLM may learn pattern from negative example |
| 1102 | "His approach shows..." or "This experience demonstrates..." | Same risk |
| 1151 | Same as 1100 (DUPLICATE) | Reinforces pattern |
| 1153 | Same as 1102 (DUPLICATE) | Reinforces pattern |
| 1169 | "Matt learned / Matt has demonstrated" | "demonstrated" appears as GOOD example |
| 1242 | "He ships." not "Execution & Delivery theme" | Good - shows replacement |
| 1251 | "Builder's mindset, coach's heart..." | Good - shows direct statement |
| 1281-1282 | "Job seekers were struggling...", "Matt wanted to..." | Good/Bad examples |

---

## Repeated/Redundant Concepts

### Meta-commentary ban
- **Line 1100:** "NEVER write meta-commentary about Matt..."
- **Line 1151:** Same rule repeated verbatim
- **Line 1257:** "This reflects Matt's..." banned again
- **Count:** 3 locations saying essentially the same thing

### "In essence" ban
- **Line 1100:** Listed in parenthetical examples
- **Line 1151:** Listed again (duplicate section)
- **Line 1251:** "NO wrappers like 'In essence...'"
- **Line 1256:** "'In essence...' as sentence starters"
- **Count:** 4 locations, but still being violated

### Reflection paragraph ban
- **Line 1101:** "NEVER end with a reflection paragraph..."
- **Line 1103:** "No summary paragraph after it."
- **Line 1152:** "NEVER end with a reflection paragraph..." (duplicate)
- **Count:** 3 locations

### Corporate filler bans
- **Lines 1117-1130:** 13 specific banned phrases with alternatives
- **Lines 1255-1264:** 9 more banned phrases (some overlap)
- **Count:** 2 separate lists, ~18 unique phrases

---

## Distance from Generation Point

```
Line 1097: System prompt starts
Line 1100: FIRST "In essence" ban                    ← 220 lines from generation
Line 1151: SECOND "In essence" ban (duplicate)       ← 170 lines from generation
Line 1251: THIRD "In essence" ban                    ← 70 lines from generation
Line 1256: FOURTH "In essence" ban                   ← 65 lines from generation
Line 1308: "Generate a SYNTHESIS response that:"     ← GENERATION POINT
Line 1320: End of prompt                             ← NO final reminder
```

**Problem:** The NEVER rules appear 4 times but all are 65+ lines before generation. The final instruction block (1316-1320) contains NO reminder of banned phrases.

---

## Conflicting Instructions

| Line | Instruction | Potential Conflict |
|------|-------------|-------------------|
| 1169 | "Matt has demonstrated" as GOOD output | Uses "demonstrated" which is banned elsewhere |
| 1270 | "First person ('I see seven patterns...')" | Conflicts with "convert I to Matt" rules |
| 1133 | "draw explicit connections between them" | May encourage synthesis language |
| 1313 | "Connect to a broader principle" | May encourage "In essence" type statements |

---

## Recommendations

1. **Consolidate NEVER rules** - Currently spread across 4 locations (1099, 1148, 1255, 1280). Merge into ONE authoritative section.

2. **Remove quoted negative examples** - Instead of "NEVER say 'This reflects...'" try "State principles directly without meta-commentary wrappers"

3. **Add final reminder** - The REMEMBER block (1316-1320) should include the critical bans:
   ```
   REMEMBER:
   - NO "In essence...", "This reflects...", "Overall..." wrappers
   - The 🐾 is already in your opening...
   ```

4. **Fix conflicting instructions** - Line 1270 says use first person but other rules say convert to third person

5. **Reduce prompt length** - 220 lines is excessive. LLMs lose focus. Target 100-120 lines.
