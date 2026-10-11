"""MATTGPT-275 fixes rerun (Oct 11, 2026): the PoC with fixes 1 (clarify
rendered), 2 option a (gap retries with the full question; an empty gap
answers without MATT_DNA under GAP_EMPTY_RULE) and 3 (per-client search for
multi-client synthesize), against unchanged lever 2. Subset approved by Matt:
c01, c03, c04, c05, c08, c09, c11, c12 and x1, x2, x3, x5; 10 runs each,
both arms; corpus 6ec9aec. Same harness as probe_275_rerun.py. Untracked.
Usage: python probes_fix/probe_275_fixes.py <out_dir>
"""
import sys
from pathlib import Path

import probe_275_rerun as rr

pc = rr.pc
pc.CORPUS_COMMIT = "6ec9aec"
SUBSET = [1, 3, 4, 5, 8, 9, 11, 12]
rr.EXTRAS = [e for e in rr.EXTRAS if e[0] in ("x1", "x2", "x3", "x5")]
rr.EXTRA_RUNS = 10
assert hasattr(pc, "named_clients") and hasattr(pc, "GAP_EMPTY_RULE"), "fixed probe not loaded"
_all = pc.CONVS


def main(out):
    real_checks = pc.checks

    def checks():
        pc.CONVS = _all
        ok = real_checks()
        pc.CONVS = {n: _all[n] for n in SUBSET}
        pc.RUNS = {n: 10 for n in SUBSET}
        return ok

    pc.checks = checks
    rr.main(out)


if __name__ == "__main__":
    try:
        main(Path(sys.argv[1]))
    except rr.Abort as e:
        print(f"ABORT: {e}", flush=True)
        sys.exit(2)
