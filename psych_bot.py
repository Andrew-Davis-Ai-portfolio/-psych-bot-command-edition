#!/usr/bin/env python3
"""
Psych Bot — Command Edition (MVP)
Calm wellness copilot. Not a therapist.
- /checkin (mood/stress/sleep)
- /reframe <thought>
- /breathe
- /journal add|list|delete
- /review (weekly)
- /export json|csv
- /help
Data stored locally in psych_data.json
Crisis guardrails: shows resources on risk keywords.
"""

import json, os, re, sys, csv, datetime as dt
from pathlib import Path

DATA_PATH = Path("psych_data.json")
EXPORT_DIR = Path("exports")
EXPORT_DIR.mkdir(exist_ok=True)

RISK_TERMS = [
    r"\bsuicide\b", r"\bkill myself\b", r"\bself[- ]?harm\b",
    r"\bhurt (myself|someone)\b", r"\bno reason to live\b"
]
DISTORTIONS = {
    "all-or-nothing": ["always", "never", "completely", "totally"],
    "overgeneralization": ["everyone", "no one", "nobody", "every time"],
    "mind reading": ["they think", "people think", "must think"],
    "catastrophizing": ["disaster", "ruined", "worst", "collapse"],
    "labeling": ["i am a failure", "i'm stupid", "i'm weak"],
}

def load():
    if DATA_PATH.exists():
        return json.loads(DATA_PATH.read_text())
    return {
        "profile": {"values": ["mastery","equity","legacy"]},
        "check_ins": [],
        "entries": [],
        "system_score": {"weekly": 0, "streak_days": 0, "last_day": None}
    }

def save(db):
    DATA_PATH.write_text(json.dumps(db, indent=2))

def now_iso():
    return dt.datetime.now().isoformat(timespec="seconds")

def risk_check(text):
    low = text.lower()
    for pat in RISK_TERMS:
        if re.search(pat, low):
            crisis_banner()
            return True
    return False

def crisis_banner():
    print("\n⚠️  CRISIS PROTOCOL")
    print("I'm not equipped for emergencies.")
    print("• US: Call 911 or text/call 988 (Suicide & Crisis Lifeline)")
    print("• If you’re outside the US: find local resources at https://findahelpline.com/")
    print("• Contact a trusted person now.\n")

def guess_distortion(text):
    low = text.lower()
    hits = []
    for name, cues in DISTORTIONS.items():
        if any(cue in low for cue in cues):
            hits.append(name)
    return hits or ["—"]

def system_score_update(db, done_action=False):
    # simple weekly score: +3 for check-in, +5 for completed action
    today = dt.date.today().isoformat()
    if db["system_score"]["last_day"] != today:
        db["system_score"]["streak_days"] += 1
        db["system_score"]["last_day"] = today
        db["system_score"]["weekly"] += 3
    if done_action:
        db["system_score"]["weekly"] += 5

def cmd_help():
    print("""
📘 Commands
  /checkin                Quick mood/stress/sleep pulse
  /reframe <thought>      Spot distortion + build next action
  /breathe                90-second box breathing guide
  /journal add            Save a note (taggable)
  /journal list           Show last 10 entries
  /journal delete <n>     Delete by index from /journal list
  /review                 Weekly snapshot
  /export json|csv        Export data
  /help                   Show this help
    """)

def cmd_checkin(db):
    print("\n— Check-in —")
    mood   = int(input("Mood 1–5: ") or "3")
    stress = int(input("Stress 1–5: ") or "3")
    sleep  = float(input("Sleep hours: ") or "6")
    note   = input("Note (optional): ").strip()
    entry = {"ts": now_iso(), "mood": mood, "stress": stress, "sleep": sleep, "note": note}
    db["check_ins"].append(entry)
    system_score_update(db)
    save(db)
    print("✓ Logged. System Score:", db["system_score"]["weekly"])

def cmd_breathe():
    print("\n🫁 Box breathing (4•4•4•4) — 6 cycles")
    print("Inhale 4 • Hold 4 • Exhale 4 • Hold 4 — repeat.\n(Count it out: 1..2..3..4)")
    print("Tip: keep shoulders down; breathe through the nose.\n")

def cmd_reframe(db, text):
    if not text:
        print("Usage: /reframe <thought>")
        return
    if risk_check(text):
        return
    hits = guess_distortion(text)
    print(f"\n🧠 Detected distortion(s): {', '.join(hits)}")
    print("Evidence check:")
    for q in [
        "• What facts support this thought?",
        "• What facts challenge it?",
        "• What would you tell a friend in the same situation?"
    ]:
        print(q)
    alt = input("\nAlternative view (one sentence): ").strip() or "This is one data point, not a pattern."
    action = input("Next controllable action (<10 min): ").strip() or "Send 1 targeted application."
    fallback = input("IF blocked, THEN (fallback): ").strip() or "Draft a 3-sentence value DM to a recruiter."
    done = input("Start now? (y/N): ").strip().lower() == "y"

    db["entries"].append({
        "ts": now_iso(),
        "trigger": text,
        "distortion": hits,
        "reframe": alt,
        "action": action,
        "fallback": fallback,
        "done": done
    })
    system_score_update(db, done_action=done)
    save(db)
    print("✓ Reframe logged. System Score:", db["system_score"]["weekly"])

def cmd_journal(db, subcmd):
    if subcmd == "add":
        text = input("\nEntry: ")
        tags = [t.strip() for t in input("Tags (space or comma): ").replace(",", " ").split() if t.strip()]
        if risk_check(text):  # still log, but show resources
            pass
        db["entries"].append({"ts": now_iso(), "journal": text, "tags": tags})
        save(db)
        print("✓ Saved.")
    elif subcmd == "list":
        last = db["entries"][-10:]
        if not last:
            print("No entries yet.")
            return
        for i, e in enumerate(last, start=max(0, len(db["entries"]) - len(last))):
            kind = "journal" if "journal" in e else "reframe"
            print(f"[{i}] ({kind}) {e.get('ts')} :: {e.get('journal', e.get('trigger',''))}")
    elif subcmd.startswith("delete"):
        try:
            idx = int(subcmd.split()[-1])
            _ = db["entries"].pop(idx)
            save(db)
            print("✓ Deleted.")
        except Exception:
            print("Usage: /journal delete <index>  (use /journal list first)")
    else:
        print("Usage: /journal add | list | delete <index>")

def cmd_review(db):
    week = db["system_score"]["weekly"]
    streak = db["system_score"]["streak_days"]
    checks = db["check_ins"][-7:]
    if checks:
        avg_mood = sum(c["mood"] for c in checks)/len(checks)
        avg_stress = sum(c["stress"] for c in checks)/len(checks)
    else:
        avg_mood = avg_stress = 0
    print("\n📊 Weekly Review")
    print(f"System Score: {week} | Streak days: {streak}")
    print(f"Avg mood: {avg_mood:.1f} | Avg stress: {avg_stress:.1f}")
    # top triggers
    trig = {}
    for e in db["entries"]:
        t = e.get("trigger")
        if t:
            key = t.lower()[:40]
            trig[key] = trig.get(key, 0) + 1
    top = sorted(trig.items(), key=lambda x: x[1], reverse=True)[:3]
    if top:
        print("Top triggers:")
        for k,v in top:
            print(f" • {k} ×{v}")
    print("Next week focus: 1) Sleep 2) Movement 3) One proof-of-work per day")

def cmd_export(db, kind):
    ts = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    if kind == "json":
        out = EXPORT_DIR / f"psych_export_{ts}.json"
        out.write_text(json.dumps(db, indent=2))
        print("✓ Exported:", out)
    elif kind == "csv":
        out = EXPORT_DIR / f"psych_entries_{ts}.csv"
        with out.open("w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["ts","type","text","distortion","action","done","tags"])
            for e in db["entries"]:
                if "journal" in e:
                    w.writerow([e["ts"], "journal", e["journal"], "", "", "", " ".join(e.get("tags",[]))])
                else:
                    w.writerow([e["ts"], "reframe", e["trigger"], ",".join(e.get("distortion",[])), e.get("action",""), e.get("done",""), ""])
        print("✓ Exported:", out)
    else:
        print("Usage: /export json|csv")

def banner():
    print("Psych Bot — Command Edition  |  Calm • Ethical • Effective")
    print("Type /help to see commands. Ctrl+C to exit.\n")

def main():
    db = load()
    banner()
    if len(sys.argv) > 1 and sys.argv[1].startswith("/"):
        # allow quick one-shot CLI
        line = " ".join(sys.argv[1:])
    else:
        line = ""
    try:
        while True:
            if not line:
                line = input("> ").strip()
            if not line:
                line = ""
                continue
            if line == "/help": cmd_help()
            elif line == "/checkin": cmd_checkin(db)
            elif line.startswith("/reframe"):
                cmd_reframe(db, line.replace("/reframe","",1).strip())
            elif line == "/breathe": cmd_breathe()
            elif line.startswith("/journal"):
                cmd_journal(db, line.replace("/journal","",1).strip() or "list")
            elif line == "/review": cmd_review(db)
            elif line.startswith("/export"):
                cmd_export(db, line.split(maxsplit=1)[1] if len(line.split())>1 else "")
            elif line in ("/quit","/exit"): break
            else: print("Unknown. Try /help")
            line = ""  # loop
    except KeyboardInterrupt:
        print("\nBye.")

if __name__ == "__main__":
    main()
