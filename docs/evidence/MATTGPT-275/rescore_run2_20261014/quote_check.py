"""Deterministic check for the locked brief's quotation rule (rule 8): every
double-quoted span in an answer must appear verbatim in a story, the profile,
the visitor's question or a story title, apart from curly vs straight quotes,
letter case and whitespace. The profile is checked as stored and as rendered
by load_matt_profile() (the sentences the model receives). Markdown bold markers and the \\$ escape are
display formatting and are removed before comparing."""
import json, re, sys
from pathlib import Path
R = Path(sys.argv[1]); rows = json.load(open(sys.argv[2], encoding="utf-8"))
def norm(t):
    t = t.replace("“", '"').replace("”", '"').replace("‘", "'").replace("’", "'")
    t = t.replace("**", "").replace("\\$", "$")
    return re.sub(r"\s+", " ", t).strip().lower()
stories = [json.loads(l) for l in (R / "corpus_6ec9aec.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
hay = norm(" \n ".join(json.dumps(s, ensure_ascii=False) for s in stories) + " \n " + (R / "matt_profile.json").read_text(encoding="utf-8"))
hay_plain = norm(" \n ".join(" ".join(str(v) if not isinstance(v, list) else " ".join(map(str, v)) for v in s.values()) for s in stories)
                 + " " + (R / "matt_profile.json").read_text(encoding="utf-8")
                 + " " + (R / "profile_rendered.txt").read_text(encoding="utf-8"))
QUOTE = re.compile(r'["“]([^"“”\n]{2,300})["”]')
out = []
for r in rows:
    spans = [m.group(1) for m in QUOTE.finditer(r["answer_md"])]
    if not spans: continue
    res = []
    for s in spans:
        ns = norm(s).strip(" .,;:")
        ok = ns in hay or ns in hay_plain or ns in norm(r["question"])
        res.append({"quote": s, "verbatim": ok})
    out.append({"case": r["case"], "run": r["run"], "turn": r["turn"], "quotes": res})
(R / "quote_check.json").write_text(json.dumps(out, indent=1, ensure_ascii=False))
n_ans = len(out); n_q = sum(len(o["quotes"]) for o in out); bad = [o for o in out if not all(q["verbatim"] for q in o["quotes"])]
print(f"answers with quotes: {n_ans} of {len(rows)}; quoted spans: {n_q}; answers with a non-verbatim quote: {len(bad)}")
for o in bad:
    for q in o["quotes"]:
        if not q["verbatim"]: print(f"  {o['case']} r{o['run']} t{o['turn']}: \"{q['quote'][:110]}\"")
