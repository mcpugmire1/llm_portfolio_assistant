"""MATTGPT-275 clean PoC vs lever 2, to docs/working/MATTGPT-275_poc_protocol.md
(approved at fixture 609f903). Throwaway probe in a scratch worktree; not tracked.

Worktree: b55f9ce plus lever2_20261007_211535/green_working_tree.diff, corpus
files checked out from dacf2ff. Both arms run from this tree.

Arm "lever2": send_to_backend() with lever 2's client patch (instructions moved
to the system prompt, tool_choice "required" on the first call).

Arm "poc": nonsense + router rejections (as agy_answer) -> plan_turn (gpt-4o,
Chat Completions, temperature 0, strict schema with turn_type) -> shape-only
validation (invalid -> search on the model's query, logged) -> evidence by
action -> one forced respond call (gpt-4o, agy_answer's temperature and
max_tokens) -> closing kept only with a valid index key / quoted visitor
signal -> discussion record on the transcript entry.

Usage:
  python probes/probe_275_poc_clean.py check
  python probes/probe_275_poc_clean.py run <out_dir> <arm> [conversation numbers, comma-separated]
"""

import json
import logging
import re
import subprocess
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from dotenv import load_dotenv

REPO = Path(__file__).resolve().parents[1]
MAIN = REPO.parent / "llm_portfolio_assistant"
FIXTURE_COMMIT = "609f903"
CORPUS_COMMIT = "dacf2ff"
load_dotenv(MAIN / ".env")
logging.getLogger("streamlit").setLevel(logging.ERROR)
sys.path.insert(0, str(REPO))

from config import constants  # noqa: E402
from services import semantic_router  # noqa: E402
from ui.pages.ask_mattgpt import backend_service as bs  # noqa: E402
from ui.pages.ask_mattgpt.prompts import build_system_prompt, build_user_message  # noqa: E402
from ui.pages.ask_mattgpt.story_intelligence import build_story_context_for_rag  # noqa: E402
from utils.corpus_loader import load_stories  # noqa: E402
from config.constants import ENTITY_ALIASES  # noqa: E402
from utils.client_utils import is_generic_client  # noqa: E402

stories = load_stories(str(REPO / "echo_star_stories_nlp.jsonl"))
bs.sync_portfolio_metadata(stories)
_real_search = bs.semantic_search
_real_client = bs._openai_client


# ---------------------------------------------------------------- fixture
def git(*args, cwd=MAIN):
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True)


FIXTURE_TEXT = git("show", f"{FIXTURE_COMMIT}:tests/fixtures/evaluator_conversations.md").stdout


def parse_fixture(text):
    """Conversations 1..N: number, title, visitor turns (None for a seeded
    assistant turn), the seed (answer, offer) where present, and the
    expected-answer lines under the number."""
    head, exp = text.split("## Expected Answers", 1)
    part = head.split("## Acceptance Criteria")[0]
    convs = {}
    for num, title, line in re.findall(r"^(\d+)\. (.+)\n(.+)$", part, re.M):
        turns = []
        for t in line.split(" → "):
            t = t.strip()
            if t == "(seeded answer)":
                turns.append(None)
            else:
                assert t.startswith("“") and t.endswith("”"), (num, t)
                turns.append(t[1:-1])
        convs[int(num)] = {"num": int(num), "title": title, "turns": turns, "seed": None, "expected": []}
    for num, c in convs.items():
        if None in c["turns"]:
            block = part.split(f"{num}. {c['title']}\n", 1)[1].split(f"\n\n{num + 1}. ", 1)[0]
            quoted = [ln[2:] if ln.startswith("> ") else "" for ln in block.splitlines() if ln.startswith(">")]
            paras = "\n".join(quoted).split("\n\n")
            assert len(paras) == 2, (num, paras)
            c["seed"] = {"answer": paras[0].strip(), "offer": paras[1].strip()}
    cur = None
    for ln in exp.splitlines():
        m = re.match(r"^(\d+)\. ", ln)
        if m:
            cur = int(m.group(1))
            continue
        if ln.startswith("- ") and cur:
            convs[cur]["expected"].append(ln[2:])
    return convs


CONVS = parse_fixture(FIXTURE_TEXT)
RUNS = {n: (10 if n in {1, 7, 10, 11, *range(12, 19)} else 5) for n in CONVS}
if __import__("os").environ.get("SMOKE_RUNS"):  # smoke test only; the scored run never sets it
    RUNS = {n: int(__import__("os").environ["SMOKE_RUNS"]) for n in CONVS}

# ---------------------------------------------------------------- lever 2 client patch
_bs_src = (REPO / "ui" / "pages" / "ask_mattgpt" / "backend_service.py").read_text()
_blk = _bs_src[_bs_src.index("def _choose_opening_and_focus"):_bs_src.index("def _generate_agy_response")]
OPENER_EXAMPLES = re.findall(r'"((?:🐾|Got it)[^"]*)"', _blk)
OPENER_LINE = (
    "Begin with a short opening line in Agy's voice. Examples of how Agy opens: "
    + "; ".join(f'"{o}"' for o in OPENER_EXAMPLES) + "."
)
SPLITS = Counter()


def moved(messages, note_override=None):
    """Lever 2: the wrapped user turn split, instructions to the system prompt."""
    msgs = [dict(m) for m in messages]
    last_user = max(i for i, m in enumerate(msgs) if m.get("role") == "user")
    content = msgs[last_user]["content"]
    m = re.match(r"User Question: (.*?)\n\n## Stories from Matt's Portfolio:\n\n(.*?)\n\n---\n\n(## INSTRUCTIONS.*)", content, re.S)
    if not m:
        SPLITS["miss"] += 1
        return msgs
    SPLITS["hit"] += 1
    question, note, instructions = m.groups()
    instructions = re.sub(r"Start your response with this exact text: .*", OPENER_LINE, instructions)
    msgs[0]["content"] = msgs[0]["content"] + "\n\n**TOOLS:** " + (note_override or note) + "\n\n" + instructions
    msgs[last_user]["content"] = question
    return msgs


def lever2_client():
    real = _real_client()

    def create(**kw):
        kw = {**kw, "messages": moved(kw["messages"])}
        msgs = kw["messages"]
        last_user = max(i for i, m in enumerate(msgs) if m.get("role") == "user")
        if not any(m.get("role") == "tool" for m in msgs[last_user:]) and "tool_choice" not in kw:
            kw["tool_choice"] = "required"
        if LEVER2_MODEL != "gpt-4o":
            return lever2_sol_create(real, kw)
        return real.chat.completions.create(**kw)

    return SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=create)))


# ---------------------------------------------------------------- engagement index
def _slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


ENGAGEMENTS = defaultdict(list)
for s in stories:
    ENGAGEMENTS[(s["Client"], s["Project"])].append(s)
INDEX = {}
for (client, project), group in sorted(ENGAGEMENTS.items()):
    INDEX[f"{_slug(client)}/{_slug(project)}"] = {
        "client": client, "project": project,
        "employer": Counter(x.get("Employer") for x in group).most_common(1)[0][0],
        "start": min(x["Start_Date"] for x in group), "end": max(x["End_Date"] for x in group),
        "role": Counter(x.get("Role") for x in group).most_common(1)[0][0],
        "stories": group,
    }
KEY_OF = {(e["client"], e["project"]): k for k, e in INDEX.items()}
INDEX_TEXT = "\n".join(
    f"{k} | {e['client']} | {e['project']} | {e['employer']} | {e['start']} to {e['end']} | {e['role']} | {len(e['stories'])} stories"
    for k, e in INDEX.items()
)
PROFILE_KEYS = list(json.loads((REPO / "data" / "matt_profile.json").read_text()).keys())

_footer = (REPO / "ui" / "components" / "footer.py").read_text()
MAILTO = re.search(r'href="mailto:([^"?]+)', _footer).group(1)
LINKEDIN = re.search(r'href="(https://www\.linkedin\.com/[^"]+)"', _footer).group(1)
ENGAGE_TEXT = {
    "role_match": "Hiring for a specific role? Paste the job description into **Role Match** and it will check Matt's stories against each requirement.",
    "about_matt": "Matt's full profile is on the **About Matt** page.",
    "linkedin": f"LinkedIn: {LINKEDIN}",
    "contact": f"Email Matt: {MAILTO}",
}


def story_block(story):
    """Lever 2's block (_run_search_tool), plus the [DATES] line (difference 4)
    and the engagement key the closing names (difference 5)."""
    ctx = build_story_context_for_rag(story)
    ctx += f"\n[DATES] {story.get('Start_Date')} to {story.get('End_Date')} (Matt's time on this engagement, YYYY-MM)"
    block = f'<story title="{story.get("Title", "")}" engagement="{KEY_OF[(story["Client"], story["Project"])]}">\n{ctx}\n</story>'
    if story.get("Theme") == "Professional Narrative":
        summary = story.get("5PSummary", "") or story.get("5p_summary", "")
        block += bs.get_verbatim_requirement(summary)
    return block


# ---------------------------------------------------------------- plan
PLAN_TOOL = {
    "type": "function",
    "function": {
        "name": "plan_turn",
        "description": "Plan how Agy handles the visitor's latest message.",
        "strict": True,
        "parameters": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "turn_type": {"type": "string", "enum": ["follow_up", "new_topic"],
                              "description": "follow_up: the message continues what the latest turn discussed. new_topic: the message sets a topic of its own."},
                "action": {"type": "string", "enum": ["answer_from_referent", "search", "synthesize", "clarify", "gap", "profile"]},
                "referents": {"type": "array", "items": {"type": "string"}, "description": "Engagement keys from the index."},
                "query": {"type": "string", "description": "Standalone search query (search, gap, synthesize without referents), or what the visitor wants about the referents."},
                "clarify_question": {"type": "string", "description": "For clarify: one short question naming the candidate engagements."},
                "reason": {"type": "string", "description": "One short sentence: why this action and these referents."},
            },
            "required": ["turn_type", "action", "referents", "query", "clarify_question", "reason"],
        },
    },
}

PLAN_SYSTEM = """You plan one turn for Agy, the assistant on Matt Pugmire's portfolio site. You do not answer the visitor. First decide turn_type: follow_up when the message continues what the latest turn discussed, including accepting the open offer; new_topic when the message sets a topic of its own, even after earlier turns. Then choose one action:

- answer_from_referent: the message follows up on engagements already discussed, and the conversation identifies which. referents = those engagement keys. When the message accepts the open offer ("Sure", "yes", "go on"), referents = the offer's engagement and query = what was offered.
- search: a new question about Matt's work, or a follow-up that needs evidence the referents don't hold. query = a standalone search query naming the client, project or topic.
- synthesize: patterns or themes across engagements. If the visitor points at what was just discussed ("those", "these"), referents = the engagements the latest turn discussed; otherwise no referents and a query.
- clarify: the follow-up could refer to more than one engagement in the discussion record, and picking the wrong one would change the answer. referents = the candidates (2 or more), clarify_question names them.
- gap: the question asks about a client, industry, credential or experience that neither the index nor the profile shows. query = the nearest thing that is on record.
- profile: the facts about Matt's profile answer it (education, certifications, languages, location and availability, his summary, how to reach him, his résumé).

Referents: a follow-up's referents are the engagements the latest turn discussed. An engagement from an earlier turn is a referent only when the visitor names it. Use only keys that appear in the engagement index."""


def render_record(record):
    """The latest turn's discussed engagements (a follow-up's referents), then
    earlier turns, which are referents only when the visitor names one."""
    if not record:
        return ""
    last = record[-1]
    offer = f"\nOpen offer: {last['offer']['key']}: {last['offer']['text']}" if last.get("offer") else ""
    lines = [f"Latest turn ({len(record)}): {last['action']}; discussed: {', '.join(last['used']) or 'none'}"]
    earlier = record[:-1][-2:]
    if earlier:
        lines.append("Earlier turns (referents only if the visitor names one):")
        start = len(record) - len(earlier)
        for i, r in enumerate(earlier, start):
            lines.append(f"  Turn {i}: {r['action']}; discussed: {', '.join(r['used']) or 'none'}")
    return "\n".join(lines) + offer


# MATTGPT-282: the answering call's model is the only difference between the two
# arms. gpt-4o keeps Chat Completions exactly as before. gpt-6.1-sol rejects
# function tools on Chat Completions (needs reasoning_effort "none", which it
# doesn't accept) and rejects temperature, so it goes through the Responses API
# at its default reasoning effort (medium), with max_output_tokens raised to
# leave room for reasoning tokens. The planner stays gpt-4o in both arms.
ANSWER_MODEL = "gpt-4o"
SOL_MAX_OUTPUT = 4000
PLANNER_SEEN = {}

# MATTGPT-282 run 2: planner model, effort per call role, and lever 2's answering
# model are set per arm by probe_282b.py. Every Sol call is streamed; CALLS
# records each one (role, resolved model, effort, usage, start, time to first
# output delta, duration) and the runner clears it per turn.
PLANNER_MODEL = "gpt-4o"
PLANNER_EFFORT = "medium"
ANSWER_EFFORT = "medium"
LEVER2_MODEL = "gpt-4o"
LEVER2_EFFORT = "medium"
CALLS = []
_FIRST_DELTA = ("response.output_text.delta", "response.function_call_arguments.delta")


def sol_stream(client, role, effort, **kw):
    t_start = time.perf_counter()
    ttft, final = None, None
    for ev in client.responses.create(model="gpt-6.1-sol", stream=True, reasoning={"effort": effort},
                                      max_output_tokens=SOL_MAX_OUTPUT, **kw):
        if ttft is None and ev.type in _FIRST_DELTA:
            ttft = time.perf_counter() - t_start
        if ev.type in ("response.completed", "response.incomplete", "response.failed"):
            final = ev.response
    if final is None:
        raise RuntimeError(f"{role}: stream ended without a final response")
    u = final.usage
    CALLS.append({"role": role, "model": final.model, "effort": final.reasoning.effort if final.reasoning else None,
                  "status": final.status, "start": t_start, "ttft": round(ttft, 3) if ttft is not None else None,
                  "secs": round(time.perf_counter() - t_start, 3),
                  "usage": {"input": u.input_tokens, "cached": u.input_tokens_details.cached_tokens or 0, "output": u.output_tokens,
                            "reasoning": u.output_tokens_details.reasoning_tokens or 0, "effort": final.reasoning.effort if final.reasoning else None}})
    return final


def _chat_shaped(r):
    """A Responses result shaped like the chat.completions object agy_answer reads."""
    tcs = [SimpleNamespace(id=o.call_id, type="function", function=SimpleNamespace(name=o.name, arguments=o.arguments))
           for o in r.output if o.type == "function_call"]
    msg = SimpleNamespace(content=r.output_text or None, tool_calls=tcs or None)
    return SimpleNamespace(model=r.model, choices=[SimpleNamespace(message=msg, finish_reason=r.status)])


def lever2_sol_create(real, kw):
    """Lever 2's chat.completions call routed to gpt-6.1-sol on Responses: temperature and
    max_tokens dropped (Sol rejects both), tool_choice passed through ("required" on the
    forced round 1, "none" on the last round, auto otherwise)."""
    r = sol_stream(real, "lever2", LEVER2_EFFORT, input=_responses_input(kw["messages"]), tools=[_responses_tool(t) for t in kw.get("tools") or []],
                   tool_choice=kw.get("tool_choice") or "auto")
    return _chat_shaped(r)


class AnswerChoice:
    def __init__(self, **kw):
        self.__dict__.update(kw)


def _responses_tool(t):
    f = t["function"]
    return {"type": "function", "name": f["name"], "description": f.get("description", ""), "parameters": f["parameters"], "strict": False}


def _responses_input(msgs):
    items = []
    for m in msgs:
        if m.get("role") == "tool":
            items.append({"type": "function_call_output", "call_id": m["tool_call_id"], "output": m["content"]})
        elif m.get("tool_calls"):
            if m.get("content"):
                items.append({"role": "assistant", "content": m["content"]})
            for tc in m["tool_calls"]:
                items.append({"type": "function_call", "call_id": tc["id"], "name": tc["function"]["name"], "arguments": tc["function"]["arguments"]})
        else:
            items.append({"role": m["role"], "content": m["content"]})
    return items


def answer_call(client, msgs, is_synthesis):
    if ANSWER_MODEL == "gpt-4o":
        r = client.chat.completions.create(
            model=ANSWER_MODEL, messages=msgs, temperature=0.2 if is_synthesis else 0.4, max_tokens=700,
            tools=[bs._SEARCH_STORIES_TOOL, RESPOND_TOOL], tool_choice={"type": "function", "function": {"name": "respond"}},
        )
        ch, u = r.choices[0], r.usage
        return AnswerChoice(arguments=ch.message.tool_calls[0].function.arguments, finish_reason=ch.finish_reason,
                            requested=ANSWER_MODEL, model=r.model, api="chat.completions",
                            usage={"input": u.prompt_tokens, "cached": getattr(u.prompt_tokens_details, "cached_tokens", 0) or 0,
                                   "output": u.completion_tokens, "reasoning": 0})
    r = sol_stream(client, "answer", ANSWER_EFFORT, input=_responses_input(msgs),
                   tools=[_responses_tool(bs._SEARCH_STORIES_TOOL), _responses_tool(RESPOND_TOOL)], tool_choice={"type": "function", "name": "respond"})
    calls = [o for o in r.output if o.type == "function_call" and o.name == "respond"]
    if not calls:
        raise RuntimeError(f"no respond call (status {r.status}, {r.incomplete_details})")
    u = r.usage
    return AnswerChoice(arguments=calls[0].arguments, finish_reason=r.status if not r.incomplete_details else f"incomplete:{r.incomplete_details.reason}",
                        requested=ANSWER_MODEL, model=r.model, api="responses",
                        usage={"input": u.input_tokens, "cached": u.input_tokens_details.cached_tokens or 0,
                               "output": u.output_tokens, "reasoning": u.output_tokens_details.reasoning_tokens or 0,
                               "effort": r.reasoning.effort if r.reasoning else None})


def plan_turn(client, question, conversation_msgs, record_text, open_offer):
    user = (
        f"## ENGAGEMENT INDEX (key | client | project | employer | dates | Matt's role | stories)\n{INDEX_TEXT}\n\n"
        f"## PROFILE COVERS\n{', '.join(PROFILE_KEYS)}\n\n"
        f"## DISCUSSION RECORD\n{record_text or '(first turn)'}\n\n"
        f"## OPEN OFFER\n{json.dumps(open_offer) if open_offer else 'none'}\n\n"
        "## CONVERSATION (latest last)\n"
        + "\n".join(f"{m['role'].upper()}: {m['content']}" for m in conversation_msgs)
        + f"\n\n## VISITOR'S LATEST MESSAGE\n{question}"
    )
    if PLANNER_MODEL != "gpt-4o":
        r = sol_stream(client, "planner", PLANNER_EFFORT, input=[{"role": "system", "content": PLAN_SYSTEM}, {"role": "user", "content": user}],
                       tools=[_responses_tool(PLAN_TOOL)], tool_choice={"type": "function", "name": "plan_turn"})
        calls = [o for o in r.output if o.type == "function_call" and o.name == "plan_turn"]
        if not calls:
            raise RuntimeError(f"no plan_turn call (status {r.status}, {r.incomplete_details})")
        PLANNER_SEEN.update(model=r.model, usage=CALLS[-1]["usage"])
        return json.loads(calls[0].arguments)
    msg = client.chat.completions.create(
        model=bs.DEFAULT_CHAT_MODEL, temperature=0,
        messages=[{"role": "system", "content": PLAN_SYSTEM}, {"role": "user", "content": user}],
        tools=[PLAN_TOOL], tool_choice={"type": "function", "function": {"name": "plan_turn"}},
    )
    u = msg.usage
    PLANNER_SEEN.update(model=msg.model, usage={"input": u.prompt_tokens, "cached": getattr(u.prompt_tokens_details, "cached_tokens", 0) or 0,
                                                "output": u.completion_tokens, "reasoning": 0})
    msg = msg.choices[0].message
    return json.loads(msg.tool_calls[0].function.arguments)


# Change 2: the question refers back to an engagement, not to a concept.
# "Give me an example where that didn't work" refers to a leadership style,
# so it does not qualify; "How big was the team?" and "Which was bigger?" do.
REFERS_BACK = re.compile(
    r"\b(?:that|this|those|these) (?:project|engagement|program|one|ones|work|client|team|role)s?\b"
    r"|\bthe (?:team|project|engagement|program)\b|\bthere\b|\bwhich (?:one|was|is|were)\b|\bboth\b",
    re.I,
)


def validate(plan, question, record=None):
    """Shape, plus one rule for clarify. Returns (plan, problems); any problem
    -> search on the model's query (or the question), and the problems are logged."""
    problems = []
    if plan.get("turn_type") not in ("follow_up", "new_topic"):
        problems.append(f"turn_type {plan.get('turn_type')!r}")
    if not (plan.get("reason") or "").strip():
        problems.append("no reason")
    refs = plan.get("referents") or []
    bad = [r for r in refs if r not in INDEX]
    if bad:
        problems.append(f"unknown referents {bad}")
    act = plan.get("action")
    if act == "answer_from_referent" and not refs:
        problems.append("answer_from_referent without referents")
    if act == "clarify":
        if len([r for r in refs if r in INDEX]) < 2:
            problems.append("clarify names fewer than 2 candidates")
        if not (plan.get("clarify_question") or "").strip():
            problems.append("clarify without a question")
        # Change 2: clarify only when the latest turn used 2+ distinct
        # engagements and the question refers back to one of them; otherwise
        # answer from the latest turn's engagements (search if it used none).
        latest_used = list(dict.fromkeys(record[-1].get("used") or [])) if record else []
        disallowed = []
        if len(latest_used) < 2:
            disallowed.append(f"clarify with {len(latest_used)} engagement(s) in the latest turn")
        if not REFERS_BACK.search(question or ""):
            disallowed.append("clarify on a question that does not refer back to an engagement")
        if disallowed and not problems and latest_used:
            return {"turn_type": plan.get("turn_type"), "action": "answer_from_referent", "referents": latest_used,
                    "query": plan.get("query") or question, "clarify_question": "", "reason": "clarify disallowed"}, disallowed
        problems += disallowed
    if act in ("search", "gap") and not (plan.get("query") or "").strip():
        problems.append(f"{act} without a query")
    if act == "synthesize" and not refs and not (plan.get("query") or "").strip():
        problems.append("synthesize without referents or query")
    if problems:
        return {"turn_type": plan.get("turn_type"), "action": "search", "referents": [],
                "query": plan.get("query") or question, "clarify_question": "", "reason": "fallback"}, problems
    return plan, problems


# ---------------------------------------------------------------- evidence
def search_top5(query):
    result = bs.semantic_search(query, {}, stories=stories, top_k=bs.SEARCH_TOP_K)
    return (result.get("results") or [])[:5]


def referent_stories(refs, query, cap):
    """All stories of each referent engagement; above cap, the ones the query ranks first."""
    out = []
    ranked = (bs.semantic_search(query, {}, stories=stories, top_k=bs.SEARCH_TOP_K).get("results") or []) if query else []
    for key in refs:
        group = INDEX[key]["stories"]
        if len(group) <= cap:
            out.extend(group)
            continue
        ids = {s["id"] for s in group}
        picked = [s for s in ranked if s["id"] in ids][:cap]
        seen = {s["id"] for s in picked}
        picked += [s for s in group if s["id"] not in seen][: cap - len(picked)]
        out.extend(picked)
    return out


# Fix 3: client names derived from the corpus, plus the client aliases.
_CLIENT_NAMES = {s["Client"].lower(): s["Client"] for s in stories if not is_generic_client(s["Client"])}
_CLIENT_NAMES.update({k: v[1] for k, v in ENTITY_ALIASES.items() if v[0] == "Client"})


def named_clients(text):
    """Every distinct client the text names, in corpus spelling. detect_entity()
    returns only the first, so a comparison loses the rest."""
    low = (text or "").lower()
    found = []
    for name, client in _CLIENT_NAMES.items():
        if re.search(rf"\b{re.escape(name)}\b", low) and client not in found:
            found.append(client)
    return found


def per_client_stories(query, clients, cap):
    """Fix 3: one search per named client, filtered to that client."""
    out = []
    for c in clients:
        out.extend((bs.semantic_search(query, {"clients": [c]}, stories=stories, top_k=bs.SEARCH_TOP_K).get("results") or [])[:cap])
    return out


def gather(plan, question=""):
    act, refs, q = plan["action"], plan.get("referents") or [], plan.get("query") or ""
    if act == "answer_from_referent":
        return referent_stories(refs, q, cap=6)
    if act == "synthesize":
        if refs:
            return referent_stories(refs, q, cap=3)
        clients = named_clients(f"{question} {q}")
        if len(clients) > 1:
            return per_client_stories(q or question, clients, cap=3)
        return bs.get_synthesis_stories(stories, top_per_theme=1, query=q)
    if act == "search":
        return search_top5(q)
    if act == "gap":
        # Fix 2: a planner query too short to clear the confidence floor
        # ("real estate", 0.144) retries with the visitor's full question.
        found = search_top5(q)
        if not found and question.strip() and question.strip() != q.strip():
            found = search_top5(question)
        return found
    return []


# ---------------------------------------------------------------- answer
RESPOND_TOOL = {
    "type": "function",
    "function": {
        "name": "respond",
        "description": "Agy's answer to the visitor, and the closing.",
        "parameters": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "The answer, in Agy's voice. No closing offer or links in it."},
                "closing": {"type": "string", "enum": ["none", "explore", "engage"], "description": "none is the default; an answer needs no closing."},
                "explore_key": {"type": "string", "description": "For explore: the engagement key the offered thread is in."},
                "explore_offer": {"type": "string", "description": "For explore: the visitor's most likely next question about what they asked, offered in one short sentence in Agy's voice; never 'Would you like to know more about...'."},
                "engage_options": {"type": "array", "items": {"type": "string", "enum": ["role_match", "about_matt", "linkedin", "contact"]}},
                "evaluating_quote": {"type": "string", "description": "For engage: the visitor's exact words that show they are evaluating Matt or asking to reach him."},
            },
            "required": ["text", "closing", "explore_key", "explore_offer", "engage_options", "evaluating_quote"],
        },
    },
}

TURN_RULES = """## THIS TURN
Action: {action}. Referent engagements: {referents}.
- Earlier answers in the conversation are conversation, not evidence. Take facts only from the stories in the search result and the facts about Matt above.
- Each story carries [DATES]: Matt's time on that engagement, in months. For how long, give the span from the dates, approximately (for example, about a year), with no more precision than the dates hold. A program's own length in the story text is not the same thing as Matt's time on it.
- No level labels: state organization size, programs and outcomes from the stories; never call Matt VP-level, Director-level or Senior Director. Do not judge fit; report the facts.
{action_rule}
## CLOSING
Choose the closing in the respond call; never write it into the text.
- explore: the visitor's most likely next question about what they asked, offered in one short sentence in Agy's voice, about these engagements. Never a generic "Would you like to know more about...".
- engage: only when the visitor's own words show they are evaluating Matt (a role, hiring, fit, why hire him, availability) or ask how to reach him or for his résumé. Quote their words in evaluating_quote. Options: role_match (evaluating for a role), about_matt (his profile; this is what résumé means), linkedin, contact.
- none: the default. An answer with no closing is complete; choose explore or engage only when one clearly fits."""

GAP_OPENING = "🐾 That isn't in Matt's stories."
CLOSEST_PREFIX = "The closest work on record is"
GAP_RULE = (
    f'- The answer\'s first sentence is already written and shown to the visitor: "{GAP_OPENING[2:]}" Do not repeat or soften it.\n'
    f'- You may add, in at most two sentences: work from the stories in the search result, starting exactly "{CLOSEST_PREFIX}" and '
    "labelling it for what it is (its client and industry as the story gives them); and/or facts from the profile above, stated as facts "
    "with their category markers. Never call adjacent work the thing the visitor asked about.\n"
    "- If nothing in the stories or the profile is close, write nothing: return empty text."
)

ACTION_RULES = {
    "clarify": "- Ask this one short question in Agy's voice and nothing else: {clarify_question}",
    "gap": "- Say plainly what isn't on record, then what is.",
}


def answer_engagements(text, evidence, plan):
    """The engagements the answer used: evidence engagements whose client or
    project the answer names; all evidence engagements if it names none. A
    clarify turn has no evidence: its candidates are what it discussed."""
    if plan["action"] == "clarify":
        return list(plan.get("referents") or [])
    keys = []
    for s in evidence:
        k = KEY_OF[(s["Client"], s["Project"])]
        if k not in keys:
            keys.append(k)
    low = text.lower()
    named = [k for k in keys if INDEX[k]["client"].lower() in low or INDEX[k]["project"].lower() in low]
    return named or keys


def poc_turn(question, session):
    client = _real_client()
    obs = {"intent_family": None, "confidence": None, "entity_match": None, "rejection_reason": None}
    rejected = bs._nonsense_rejection(question, False, obs)
    if rejected:
        return {"answer_md": rejected.get("answer_md"), "rejection": obs.get("rejection_reason") or "nonsense"}
    _valid, score, _m, family = semantic_router.is_portfolio_query_semantic(question)
    rejected = bs._router_rejection(question, family, score, False, obs)
    if rejected:
        return {"answer_md": rejected.get("answer_md"), "rejection": obs.get("rejection_reason") or "router"}

    transcript = session["ask_transcript"]
    record = [e["poc_record"] for e in transcript if e.get("poc_record")]
    open_offer = record[-1].get("offer") if record else None
    history = bs._build_history_messages(transcript)
    t0 = time.time()
    raw_plan = plan_turn(client, question, history, render_record(record), open_offer)
    plan_secs = round(time.time() - t0, 2)
    plan, problems = validate(raw_plan, question, record)
    evidence = gather(plan, question)
    # Fix 1: a clarify turn is the planner's question, rendered as is; no answering
    # call, so it can't turn into an answer with no evidence (11 of 18 clarify
    # plans did in poc_rerun_20261011_084138).
    # Change 1: every gap opens with GAP_OPENING, rendered by code. The answering
    # call runs without MATT_DNA and may add only a CLOSEST_PREFIX line drawn from
    # the stories; anything else it writes is dropped (logged).
    is_gap = plan["action"] == "gap"
    rendered_text = None
    if plan["action"] == "clarify":
        rendered_text = "🐾 " + plan["clarify_question"].strip()
    if rendered_text is not None:
        rec = {"action": plan["action"], "referents": plan.get("referents") or [],
               "used": answer_engagements(rendered_text, evidence, plan), "offer": None}
        return {
            "answer_md": rendered_text, "text": rendered_text, "raw_plan": raw_plan, "plan": plan, "plan_problems": problems,
            "evidence": [], "closing": "none", "closing_raw": {}, "closing_note": "rendered without an answering call",
            "closing_rendered": "", "record": rec, "finish_reason": "rendered", "router_family": family,
            "plan_secs": plan_secs, "answer_secs": 0.0,
        }
    is_synthesis = family == "synthesis"  # router only, as agy_answer()

    profile_facts = bs.load_matt_profile()
    opening, focus = bs._choose_opening_and_focus(is_synthesis)
    base = [
        {"role": "system", "content": build_system_prompt(is_synthesis=is_synthesis, matt_dna="" if is_gap else bs.MATT_DNA, profile_facts=profile_facts)},
        *history,
        {"role": "user", "content": build_user_message(question=question, story_context="NOTE", opening=opening,
                                                       is_synthesis=is_synthesis, focus_angle=focus if not is_synthesis else "",
                                                       profile_facts=profile_facts)},
    ]
    note = "Evidence for this turn was gathered before you answer and appears as the search_stories result." if evidence else "No stories were gathered for this turn."
    msgs = moved(base, note_override=note)
    action_rule = GAP_RULE if is_gap else ACTION_RULES.get(plan["action"], "").format(clarify_question=plan.get("clarify_question", ""))
    msgs[0]["content"] += "\n\n" + TURN_RULES.format(action=plan["action"], referents=plan.get("referents") or "none", action_rule=action_rule)
    if record:
        msgs[0]["content"] += "\n\n## DISCUSSION RECORD (what earlier turns covered; not evidence)\n" + render_record(record)
    if evidence:
        msgs.append({"role": "assistant", "content": None, "tool_calls": [{"id": "call_poc", "type": "function",
                     "function": {"name": "search_stories", "arguments": json.dumps({"query": plan.get("query") or question})}}]})
        msgs.append({"role": "tool", "tool_call_id": "call_poc", "content": "\n\n".join(story_block(s) for s in evidence)})
    t1 = time.time()
    choice = answer_call(client, msgs, is_synthesis)
    answer_secs = round(time.time() - t1, 2)
    resp = json.loads(choice.arguments)
    text, _cats = bs._postprocess_agy_text(resp.get("text", ""), evidence)
    gap_note = ""
    if is_gap:
        added = (text or "").strip().lstrip("🐾").strip()
        # Kept only if it is the closest-work line (stories) or cites profile
        # facts (the [[profile:...]] markers that _postprocess_agy_text extracts).
        if added and not added.startswith(CLOSEST_PREFIX) and not _cats:
            gap_note, added = f"gap: dropped model text not starting {CLOSEST_PREFIX!r}: {added[:80]!r}", ""
        text = GAP_OPENING + (f" {added}" if added else "")
        resp["closing"] = "none"

    closing, closing_note, offer, rendered = resp.get("closing"), "", None, ""
    visitor_text = " ".join(e.get("text", "") for e in transcript if (e.get("role") or e.get("Role")) == "user").lower()
    if closing == "explore":
        if resp.get("explore_key") in INDEX and (resp.get("explore_offer") or "").strip():
            offer = {"key": resp["explore_key"], "text": resp["explore_offer"].strip()}
            rendered = offer["text"]
        else:
            closing_note, closing = f"explore dropped: key {resp.get('explore_key')!r} not in index", "none"
    elif closing == "engage":
        quote = (resp.get("evaluating_quote") or "").strip().lower()
        opts = [o for o in resp.get("engage_options") or [] if o in ENGAGE_TEXT]
        if quote and quote in visitor_text and opts:
            rendered = "\n\n".join(ENGAGE_TEXT[o] for o in opts)
        else:
            closing_note, closing = f"engage dropped: quote {resp.get('evaluating_quote')!r} not in visitor's words or no options", "none"
    answer_md = text + (f"\n\n{rendered}" if rendered else "")
    rec = {"action": plan["action"], "referents": plan.get("referents") or [],
           "used": answer_engagements(text, evidence, plan), "offer": offer}
    return {
        "answer_md": answer_md, "text": text, "raw_plan": raw_plan, "plan": plan, "plan_problems": problems,
        "evidence": [f"{s.get('Title')} [{KEY_OF[(s['Client'], s['Project'])]}]" for s in evidence],
        "closing": closing, "closing_raw": {k: resp.get(k) for k in ("closing", "explore_key", "explore_offer", "engage_options", "evaluating_quote")},
        "closing_note": closing_note or gap_note, "closing_rendered": rendered, "record": rec, "finish_reason": choice.finish_reason,
        "answer_model_requested": choice.requested, "answer_model_resolved": choice.model, "answer_api": choice.api,
        "answer_usage": choice.usage, "planner_model_resolved": PLANNER_SEEN.get("model"), "planner_usage": PLANNER_SEEN.get("usage"),
        "router_family": family, "plan_secs": plan_secs, "answer_secs": answer_secs,
    }


# ---------------------------------------------------------------- run
def patches(session, search_log, arm):
    mock_st = MagicMock()
    mock_st.session_state = session

    def search_wrap(query, *a, **k):
        search_log.append(query)
        return _real_search(query, *a, **k)

    ps = [
        patch("streamlit.session_state", session),
        patch.object(bs, "st", mock_st),
        patch.object(bs, "log_query", lambda *a, **k: None),
        patch.object(bs, "log_offdomain", lambda *a, **k: None),
        patch.object(semantic_router, "_log_borderline", lambda *a, **k: None),
        patch.object(semantic_router, "_log_router_low_confidence", lambda *a, **k: None),
        patch.object(bs, "semantic_search", search_wrap),
    ]
    if arm == "lever2":
        ps.append(patch.object(bs, "_openai_client", lever2_client))
    return ps


def seed_entry(conv, arm):
    seed = conv["seed"]
    entry = {"type": "conversational", "Role": "assistant", "text": seed["answer"] + "\n\n" + seed["offer"]}
    if arm == "poc":
        fiserv = KEY_OF[("Fiserv", "White-Label Card Portal")]
        entry["poc_record"] = {"action": "search", "referents": [fiserv], "used": [fiserv],
                               "offer": {"key": fiserv, "text": seed["offer"]}}
    return entry


def run(out_dir, arm, nums):
    out_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    out = out_dir / f"{arm}_{'-'.join(map(str, nums))}.json"
    for n in nums:
        conv = CONVS[n]
        for r in range(1, RUNS[n] + 1):
            session = {"ask_transcript": []}
            for turn, q in enumerate(conv["turns"], 1):
                if q is None:
                    entry = seed_entry(conv, arm)
                    session["ask_transcript"].append(entry)
                    rows.append({"arm": arm, "conversation": n, "run": r, "turn": turn, "question": None,
                                 "answer_md": entry["text"], "seeded": True})
                    continue
                session["ask_transcript"].append({"role": "user", "text": q})
                search_log = []
                ps = patches(session, search_log, arm)
                for p in ps:
                    p.start()
                t0 = time.time()
                try:
                    if arm == "lever2":
                        res = bs.send_to_backend(q, {}, None, stories)
                        row = {"answer_md": res.get("answer_md") or "", "rejection": res.get("rejection_reason"),
                               "sources": [f"{s.get('title')} ({s.get('client')})" for s in res.get("sources") or []]}
                    else:
                        row = poc_turn(q, session)
                except Exception as e:  # recorded, scored as a fail; the run goes on
                    row = {"answer_md": "", "error": f"{type(e).__name__}: {e}"}
                finally:
                    for p in reversed(ps):
                        p.stop()
                row.update({"arm": arm, "conversation": n, "run": r, "turn": turn, "question": q,
                            "search_queries": search_log, "seconds": round(time.time() - t0, 2)})
                entry = {"type": "conversational", "Role": "assistant", "text": row["answer_md"] or ""}
                if arm == "poc" and row.get("record"):
                    entry["poc_record"] = row["record"]
                session["ask_transcript"].append(entry)
                rows.append(row)
                tag = f"{row['raw_plan']['turn_type']} {row['plan']['action']}" if row.get("plan") else row.get("error", "")
                print(f"[{arm} c{n} r{r} t{turn}] {row['seconds']}s {tag} | {(row['answer_md'] or '')[:60]!r}", flush=True)
            out.write_text(json.dumps(rows, indent=2, ensure_ascii=False))
    print(arm, nums, "done", len(rows), "splits", dict(SPLITS), flush=True)


# ---------------------------------------------------------------- pre-run checks
def checks():
    fails = []

    def check(ok, label):
        print(("PASS " if ok else "FAIL ") + label)
        if not ok:
            fails.append(label)

    d = git("diff", "--quiet", FIXTURE_COMMIT, "--", "tests/fixtures/evaluator_conversations.md")
    check(d.returncode == 0, f"fixture file matches {FIXTURE_COMMIT}")
    check(sorted(CONVS) == list(range(1, 19)), f"parser reads conversations 1 to 18 (got {sorted(CONVS)})")
    fx_turn_lines = re.findall(r"^\d+\. .+\n(.+)$", FIXTURE_TEXT.split("## Acceptance Criteria")[0], re.M)
    for n in sorted(CONVS):
        c = CONVS[n]
        rebuilt = " → ".join("(seeded answer)" if t is None else f"“{t}”" for t in c["turns"])
        n_exp = len(re.findall(r"^- ", FIXTURE_TEXT.split("## Expected Answers")[1].split(f"\n{n}. ", 1)[1].split(f"\n\n{n + 1}. ", 1)[0], re.M))
        check(rebuilt == fx_turn_lines[n - 1] and len(c["expected"]) == n_exp,
              f"conv {n} '{c['title']}': {len(c['turns'])} turns, {len(c['expected'])} expected lines, runs {RUNS[n]} | {rebuilt}")
    c17 = CONVS[17]
    fx_seed = FIXTURE_TEXT[FIXTURE_TEXT.index("> 🐾"):].split("\n\n18.")[0]
    check(c17["turns"][0] is None and c17["seed"] is not None, "conv 17: first turn is the seeded answer")
    check(f"> {c17['seed']['answer']}\n>\n> {c17['seed']['offer']}" == fx_seed, "conv 17: parsed seed (answer, offer) equals the fixture's text")
    check(seed_entry(c17, "lever2")["text"] == seed_entry(c17, "poc")["text"], "conv 17: seeded text identical in both arms")
    check(c17["seed"]["offer"] == "Want to hear how he moved that team from 6-month waterfall releases to 2-week sprints?", "conv 17: offer text")

    for f in ("echo_star_stories.jsonl", "echo_star_stories_nlp.jsonl"):
        check(git("diff", "--quiet", CORPUS_COMMIT, "--", f, cwd=REPO).returncode == 0, f"{f} matches {CORPUS_COMMIT}")
    check(len(stories) == 124 and len(INDEX) == 46, f"corpus {len(stories)} stories, {len(INDEX)} engagements (want 124, 46)")
    check(bs.DEFAULT_CHAT_MODEL == "gpt-4o", f"answering and planner model {bs.DEFAULT_CHAT_MODEL}")
    print(f"     SEARCH_TOP_K={bs.SEARCH_TOP_K}; confidence: " + ", ".join(
        f"{k}={getattr(constants, k)}" for k in dir(constants) if "CONFIDENCE" in k and not k.startswith("_")))
    check(git("rev-parse", "--short", "HEAD", cwd=REPO).stdout.strip() == "b55f9ce", "worktree base b55f9ce")
    check(bool(OPENER_EXAMPLES), f"lever 2 opener examples found ({len(OPENER_EXAMPLES)})")

    rbc = [s for s in stories if s["Client"] == "RBC"]
    check(bool(rbc) and all("2012-06" in story_block(s) and "2013-06" in story_block(s) for s in rbc),
          f"every RBC story block the PoC builds has 2012-06 and 2013-06 ({len(rbc)} stories)")
    with patch.object(bs, "semantic_search", lambda *a, **k: {"results": rbc, "top_score": 1.0}):
        content, _f, _s = bs._run_search_tool(json.dumps({"query": "RBC"}), stories)
    check("2012-06" not in content and "2013-06" not in content, "no lever 2 RBC block (_run_search_tool) carries the dates")
    print("\n" + ("ALL CHECKS PASS" if not fails else f"{len(fails)} CHECK(S) FAILED"))
    return not fails


if __name__ == "__main__":
    if sys.argv[1] == "check":
        sys.exit(0 if checks() else 1)
    if sys.argv[1] == "run":
        assert checks(), "pre-run checks failed"
        nums = [int(x) for x in sys.argv[4].split(",")] if len(sys.argv) > 4 else sorted(CONVS)
        run(Path(sys.argv[2]), sys.argv[3], nums)
