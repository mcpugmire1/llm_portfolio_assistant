"""MATTGPT-303 gap probe: distribution of the longest silence per model call.

Splits:
  by round: tool_choice "required" (first call, must search), and the calls
    after it, by kind: "search" (no answer text) or "answer" (text streamed)
  by phase, for answer calls: the longest wait before the first text
    (headers, then each gap up to and including the first text event), and
    the longest gap after it
Percentiles are nearest-rank on the sorted values."""
import json, math, sys
from pathlib import Path
D = Path(sys.argv[1])
rows = [r for f in sorted(D.glob("rows_lane*.json")) for r in json.loads(f.read_text())]
live = [r for r in rows if not r.get("seeded")]
calls = [(r, c) for r in live for c in r.get("stream_timing", [])]


def pct(xs, p):
    xs = sorted(xs)
    return xs[max(0, math.ceil(p / 100 * len(xs)) - 1)]


def line(name, xs):
    if not xs:
        print(f"{name:<44} n=0"); return
    print(f"{name:<44} n={len(xs):>3}  median {pct(xs, 50):6.2f}  p95 {pct(xs, 95):6.2f}  p99 {pct(xs, 99):6.2f}  max {max(xs):6.2f}")


def split(c):
    """(longest wait before first text, longest gap after it) for an answer call."""
    t, pre, post = c["headers_s"], [c["headers_s"]], []
    seen = False
    for gp in c["gaps"]:
        t += gp
        (post if seen else pre).append(gp)
        if not seen and c["first_text_s"] is not None and t >= c["first_text_s"] - 0.02:
            seen = True
    return max(pre), (max(post) if post else 0.0)


print(f"turns {len(live)}, calls {len(calls)}, errors {sum(1 for _, c in calls if c.get('error'))}, "
      f"degraded {sum(1 for r in live if r.get('degraded'))}, rejected {sum(1 for r in live if r.get('rejection'))}")
print("tool_choice counts:", {k: sum(1 for _, c in calls if c['tool_choice'] == k) for k in ('required', 'auto', 'none')})
line("all calls: max_wait_s", [c["max_wait_s"] for _, c in calls])
line("round 0 (required): max_wait_s", [c["max_wait_s"] for _, c in calls if c["tool_choice"] == "required"])
line("later search calls (no text): max_wait_s", [c["max_wait_s"] for _, c in calls if c["tool_choice"] != "required" and c["first_text_s"] is None])
ans = [c for _, c in calls if c["first_text_s"] is not None]
line("answer calls: max_wait_s", [c["max_wait_s"] for c in ans])
line("answer calls: before first text", [split(c)[0] for c in ans])
line("answer calls: after first text", [split(c)[1] for c in ans])
line("answer calls: first_text_s", [c["first_text_s"] for c in ans])
line("headers_s, all calls", [c["headers_s"] for _, c in calls])
line("turn seconds", [r["seconds"] for r in live if r.get("seconds")])
# a no-text call that is not round 0 and not followed by text would be a turn that never answered
print("answer calls with tool_choice:", {k: sum(1 for c in ans if c['tool_choice'] == k) for k in ('required', 'auto', 'none')})
top = sorted(calls, key=lambda rc: -rc[1]["max_wait_s"])[:5]
print("\nlongest five:")
for r, c in top:
    pre, post = split(c) if c["first_text_s"] is not None else (c["max_wait_s"], None)
    print(f"  {r['case']} r{r['run']} t{r['turn']} {c['tool_choice']:<8} max_wait {c['max_wait_s']:.2f}s headers {c['headers_s']:.2f}s "
          f"pre-text {pre:.2f}s post-text {post} events {c.get('n_events')} total {c.get('total_s')}s err {c.get('error')}")
cost = 0.0
for r in live:
    for k in r.get("calls", []):
        u = k.get("usage")
        if u:
            cost += (u["input"] - u["cached"]) * 2e-6 + u["cached"] * 0.1e-6 + u["output"] * 10e-6
print(f"\ncost ${cost:.2f}")
