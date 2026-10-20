"""Write tests/fixtures/agy_voice_answers.json from a live acceptance run.

agy_voice.feature checks Agy's voice rules on answers a live run recorded,
so a BDD run makes no model call. A prompt ticket's acceptance run refreshes
the fixture:

    python scripts/build_agy_voice_fixture.py <run dir> <commit> [--arm N]

<run dir> holds the probe's rows*.json; each row needs question, turn,
intent_family, answer_md and rejection (arm, when the run has arms). Rows
the router redirected (rejection set) and rows seeded from an earlier
turn are left out: the fixture holds answers the model wrote in that run.
"""

import argparse
import json
from pathlib import Path

FIXTURE = (
    Path(__file__).resolve().parent.parent / "tests/fixtures/agy_voice_answers.json"
)
KEEP = ("case", "turn", "run", "question", "intent_family", "answer_md")


def build(run_dir: Path, commit: str, arm: str | None) -> dict:
    rows = [
        r for f in sorted(run_dir.glob("rows*.json")) for r in json.loads(f.read_text())
    ]
    answers = [
        {k: r.get(k) for k in KEEP}
        for r in rows
        if (arm is None or r.get("arm") == arm)
        and not r.get("rejection")
        and not r.get("seeded")
    ]
    if not answers:
        raise SystemExit(f"no answered rows in {run_dir} (arm {arm})")
    return {
        "source": run_dir.as_posix(),
        "arm": arm,
        "commit": commit,
        "answers": answers,
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("run_dir", type=Path)
    p.add_argument("commit")
    p.add_argument("--arm")
    a = p.parse_args()
    data = build(a.run_dir, a.commit, a.arm)
    FIXTURE.write_text(
        json.dumps(data, indent=1, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(f"{len(data['answers'])} answers -> {FIXTURE}")


if __name__ == "__main__":
    main()
