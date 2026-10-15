"""One-time MATTGPT-294 check: MATT_DNA and Ask Agy's system prompt for
c02, c05 and c16, built by whichever tree this runs in (sys.argv[1] = out).
Fixed focus angle so the only input that varies is the code."""
import json, re, sys
sys.path.insert(0, ".")
from ui.pages.ask_mattgpt import backend_service as bs
from ui.pages.ask_mattgpt.prompts import build_tool_system_prompt
from services.jd_assessor import load_matt_profile
stories = [json.loads(l) for l in open("echo_star_stories_nlp.jsonl", encoding="utf-8") if l.strip()]
bs.sync_portfolio_metadata(stories)
norm = lambda t: re.sub(r"\(Synced \d{4}-\d{2}\)", "(Synced YYYY-MM)", t)
out = {"matt_dna": norm(bs.MATT_DNA)}
for name, syn in [("standard", False), ("synthesis", True)]:
    out[name] = norm(build_tool_system_prompt(
        is_synthesis=syn, matt_dna=bs.MATT_DNA, profile_facts=load_matt_profile(),
        opener_examples=bs.SYNTHESIS_OPENERS + bs.STANDARD_OPENERS, focus_angle="ZZZ fixed focus"))
json.dump(out, open(sys.argv[1], "w", encoding="utf-8"), ensure_ascii=False)
print("written", {k: len(v) for k, v in out.items()})
