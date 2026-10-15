"""MATTGPT-303 inside 275 (Oct 15, 2026; untracked probe): the longest
silence on Ask Agy's OpenAI stream, to size the read timeout.

httpx's read timeout bounds each wait on the socket: the wait for the
response headers after the request is sent, then each wait between body
chunks. So per model call this records, on time.perf_counter():
  headers_s   request sent -> create() returns (headers in)
  gaps        headers -> first event, then every event -> next event
  max_wait_s  max(headers_s, max gap): the longest silence the timeout sees
  first_text_s  request sent -> first response.output_text.delta (None if none)
  total_s, n_events, tool_choice, and the error with time since the last
  event, if the stream fails
Event gaps bound socket-read gaps from above (several events can share one
chunk), so the measure errs long, the safe side for a timeout.

Turns: the gate's turn set (18 conversations from fixture 609f903 and the
extras x1 to x5 and x7; 45 live turns per run), arm "new" only, the working
tree as is (COMPARISON_RULE in). Through probe_275_gate.new_run(): loggers
patched, extras bypass the nonsense rules as in the gate, raw text and usage
recorded. Lanes: LANE=i/N. RUNS from the env (default 2).
Usage: LANE=0/4 python probes/probe_275_stream_gaps.py <out_dir>
"""

import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import probe_275_gate as g  # noqa: E402  (reads sys.argv[1] as the out dir)

OUT = g.OUT
LANE, LANES = (int(x) for x in os.environ.get("LANE", "0/1").split("/"))
RUNS = int(os.environ.get("RUNS", "2"))
_record = g.stream_recording  # the gate's recorder: calls bs._stream_response, records text and usage


class _TimedResponses:
    def __init__(self, real, log):
        self._real, self._log = real, log

    def create(self, **kw):
        rec = {"tool_choice": kw.get("tool_choice"), "gaps": [], "first_text_s": None, "error": None}
        self._log.append(rec)
        t0 = time.perf_counter()
        try:
            stream = self._real.create(**kw)
        except Exception as e:  # before the headers: recorded, then raised as before
            rec["error"] = f"{type(e).__name__}: {e}"
            rec["headers_s"] = rec["max_wait_s"] = round(time.perf_counter() - t0, 3)
            raise
        last = time.perf_counter()
        rec["headers_s"] = round(last - t0, 3)

        def events():
            nonlocal last
            n = 0
            try:
                for ev in stream:
                    now = time.perf_counter()
                    rec["gaps"].append(round(now - last, 3))
                    last = now
                    n += 1
                    if rec["first_text_s"] is None and getattr(ev, "type", "") == "response.output_text.delta":
                        rec["first_text_s"] = round(now - t0, 3)
                    yield ev
            except Exception as e:
                rec["error"] = f"{type(e).__name__}: {e}"
                rec["silence_before_error_s"] = round(time.perf_counter() - last, 3)
                raise
            finally:
                rec["n_events"] = n
                rec["total_s"] = round(time.perf_counter() - t0, 3)
                rec["max_wait_s"] = max([rec["headers_s"], *rec["gaps"]])

        return events()


class _TimedClient:
    def __init__(self, real, log):
        self.responses = _TimedResponses(real.responses, log)


def timed_recording(client, *args, **kwargs):
    log = g.TURN.setdefault("stream_timing", [])
    return _record(_TimedClient(client, log), *args, **kwargs)


g.stream_recording = timed_recording  # new_turn() looks it up at call time


def main():
    jobs = [(c, r) for c in g.CASES for r in range(1, RUNS + 1)][LANE::LANES]
    print(f"lane {LANE}/{LANES}: {len(jobs)} (case, run) jobs", flush=True)
    rows, errors = [], []
    g.canary("start")
    _orig_new_turn = g.new_turn

    def new_turn_with_timing(*a, **k):
        row = _orig_new_turn(*a, **k)
        row["stream_timing"] = g.TURN.get("stream_timing", [])
        return row

    g.new_turn = new_turn_with_timing
    for case, r in jobs:
        got = g.new_run("new", case, r)
        rows += got
        errors += [(case, r, x["turn"], x["error"]) for x in got if x.get("error")]
        if len(errors) > g.MAX_ERRORS:
            raise g.Abort(f"more than {g.MAX_ERRORS} errors: {errors[-3:]}")
        (OUT / f"rows_lane{LANE}.json").write_text(json.dumps(rows, indent=1, ensure_ascii=False))
    g.canary("end")
    print(f"done | rows {len(rows)} | errors {errors}", flush=True)


if __name__ == "__main__":
    try:
        main()
    except g.Abort as e:
        print(f"ABORT: {e}", flush=True)
        sys.exit(2)
