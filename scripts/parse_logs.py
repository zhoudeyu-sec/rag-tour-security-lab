import json
import re
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOGS2 = Path(r"C:\Users\Le'novo\Desktop\ai安全截图（2）\conversation_logs(2).json")
DB = ROOT.parent / "ai-tour-guide-lab" / "backend" / "data" / "lab.db"
if not DB.exists():
    DB = ROOT / "backend" / "data" / "lab.db"


def parse_txt(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    asr_m = re.search(r"ASR:\s*([\d.]+)%\s*\(\s*(\d+)\s*/\s*(\d+)\s*\)", text)
    fr_m = re.search(r"误杀率\s*([\d.]+)%\s*\(\s*(\d+)\s*/\s*(\d+)\s*\)", text)
    run_m = re.search(r"run_id:\s*(\d+)", text)
    out = {}
    if asr_m:
        out["asr"] = float(asr_m.group(1)) / 100
        out["attack_success"] = int(asr_m.group(2))
        out["attack_cases"] = int(asr_m.group(3))
    if fr_m:
        out["false_refusal_rate"] = float(fr_m.group(1)) / 100
        out["false_refusal"] = int(fr_m.group(2))
        out["benign_cases"] = int(fr_m.group(3))
    if run_m:
        out["run_id"] = int(run_m.group(1))
    return out


def main():
    run1 = {
        "baseline": parse_txt(ROOT / "docs/results/all-baseline.txt"),
        "hardened": parse_txt(ROOT / "docs/results/all-hard.txt"),
    }

    eval_runs = []
    if DB.exists():
        conn = sqlite3.connect(DB)
        rows = conn.execute(
            "SELECT id, lab_mode, dataset, total, attack_success, false_refusal, asr, created_at "
            "FROM eval_runs WHERE dataset='all' ORDER BY id"
        ).fetchall()
        eval_runs = [
            {
                "run_id": r[0],
                "lab_mode": r[1],
                "dataset": r[2],
                "total": r[3],
                "attack_success": r[4],
                "false_refusal": r[5],
                "asr": r[6],
                "created_at": r[7],
            }
            for r in rows
        ]
        conn.close()

    print("RUN1", json.dumps(run1, ensure_ascii=False, indent=2))
    print("EVAL_RUNS", json.dumps(eval_runs, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
