"""MATTGPT-275 extras rerun (Oct 11, 2026): x1 to x5 only, 5 runs each, both
arms, on corpus 6ec9aec, through probe_275_rerun.py's harness (same guards,
interleaving, nonsense filter skipped for the extras, blind packets). x6 is
dropped (Matt: a written control, not a visitor question). Untracked.
Usage: python probes/probe_275_extras.py <out_dir>
"""
import sys
from pathlib import Path

import probe_275_rerun as rr

rr.pc.CORPUS_COMMIT = "6ec9aec"
rr.EXTRAS = [e for e in rr.EXTRAS if e[0] != "x6"]
_real_convs = rr.pc.CONVS


def main(out):
    # Run the rerun's main() with the fixture conversations removed: only the extras remain.
    rr.pc.CONVS = {}
    real_checks = rr.pc.checks
    rr.pc.checks = lambda: (setattr(rr.pc, "CONVS", _real_convs), real_checks(), setattr(rr.pc, "CONVS", {}))[1]
    rr.main(out)


if __name__ == "__main__":
    try:
        main(Path(sys.argv[1]))
    except rr.Abort as e:
        print(f"ABORT: {e}", flush=True)
        sys.exit(2)
