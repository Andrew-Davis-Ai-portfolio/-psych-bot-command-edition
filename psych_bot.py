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
#!/usr/bin/env python3
# Psych Bot — Command Edition (Casual tone)
# A friendly wellness copilot using CBT-style micro-tools.
# NOT A THERAPIST. If crisis terms are detected, it will show resources.

import json, csv, os, sys, time
from pathlib import Path
from datetime import datetime
from textwrap import dedent

APP_NAME = "Psych Bot — Command Edition"
DATA_DIR = Path("data")
DATA_FILE = DATA_DIR / "psych_log.json"

CASUAL = {
    "hello": "Yo! I’m Psych Bot — your clarity buddy. I’m not a therapist, but I can help you reset, reframe, and plan your next move. Type /help to see what I can do.",
    "ack": "Got it.",
    "ok": "All set ✅",
    "bye": "Proud of you for checking in today. Catch you soon 👋",
    "tip": "Pro tip: tiny actions beat perfect plans. 10 minutes > 0 minutes.",
}

CRISIS_KEYWORDS = {
    "self_harm": ["suicide", "kill myself", "end it", "self harm", "self-harm", "hurt myself"],
    "harm_others": ["kill them", "hurt someone", "harm others"],
}

CRISIS_MESSAGE = dedent("""
    🚨 I’m not equipped for emergencies.
    • If you’re in immediate danger: call 911 (US) or your local emergency number.
    • 988 (US): Suicide & Crisis Lifeline (call/text).
    • Reach a trusted person now.
    When you’re safe, we can pick this up and plan a next step together. ❤️
""").strip()

DISTORTIONS = {
    "all-or-nothing": "Seeing things in black-or-white: ‘If I’m not perfect, I failed.’",
    "overgeneralization": "One event becomes ‘always/never’.",
    "mind-reading": "Assuming others’ thoughts without evidence.",
    "catastrophizing": "Expecting the worst-case by default.",
    "labeling": "‘I’m a loser’ vs ‘I had a setback’.",
    "should-statements": "Rigid ‘should/must’ rules creating pressure.",
}

def now():
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"

def load_db():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if DATA_FILE.exists():
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                pass
    return {
        "user_profile": {"values": [], "supports": []},
        "check_ins": [],
        "entries": [],
        "system_score": {"weekly": 0, "streak_days": 0, "last_check_date": None}
    }

def save_db(db):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=2)

def crisis_scan(text: str) -> bool:
    lower = text.lower()
    for lst in CRISIS_KEYWORDS.values():
        if any(k in lower for k in lst):
            print("\n" + CRISIS_MESSAGE + "\n")
            return True
    return False

def pulse_check(db):
    print("\nLet’s do a 60-sec pulse. Numbers 1–5 (low→high).")
    mood = input("Mood (1–5): ").strip()
    stress = input("Stress (1–5): ").strip()
    sleep = input("Sleep hours (approx): ").strip()
    note = input("Anything quick to note? (enter to skip): ").strip()

    if crisis_scan(note):
        # Still log the check-in safely without the raw note content
        note = "[redacted - crisis terms detected]"
    ts = now()
    db["check_ins"].append({
        "ts": ts, "mood": int(mood or 3), "stress": int(stress or 3),
        "sleep": float(sleep or 6), "note": note
    })

    # Streak logic (simple daily check-in)
    today = datetime.utcnow().date().isoformat()
    last = db["system_score"].get("last_check_date")
    if last is None:
        db["system_score"]["streak_days"] = 1
    else:
        from datetime import date, timedelta
        if (date.fromisoformat(today) - date.fromisoformat(last)) == timedelta(days=1):
            db["system_score"]["streak_days"] = db["system_score"].get("streak_days", 0) + 1
        elif today != last:
            db["system_score"]["streak_days"] = 1
    db["system_score"]["last_check_date"] = today

    # Lightweight score bump
    db["system_score"]["weekly"] = min(100, db["system_score"].get("weekly", 0) + 2)
    save_db(db)
    print(f"\n{CASUAL['ok']} Streak: {db['system_score']['streak_days']} days • Weekly Score: {db['system_score']['weekly']}/100\n")

def breathe():
    print("\n90-second reset. Inhale 4 • Hold 4 • Exhale 6. I’ll count you in.")
    for i in range(3):
        print(f"Round {i+1}/3 — Inhale…4  Hold…4  Exhale…6")
        time.sleep(2)  # light delay so the loop feels paced without freezing phone UIs too long
    print("Nice. Shoulders down. Jaw unclench. You’re back. 🙌\n")

def reframe(db):
    print("\nDrop the thought that’s bugging you.")
    thought = input("Thought: ").strip()
    if crisis_scan(thought):
        return
    print("\nLet’s spot a pattern. Pick one (or type your own):")
    for k, v in DISTORTIONS.items():
        print(f"- {k}: {v}")
    kind = input("Distortion label: ").strip().lower() or "overgeneralization"

    print("\nEvidence check — give me one reason this thought might be incomplete:")
    evidence = input("> ").strip()
    alt = input("Healthier reframe (1 sentence): ").strip()

    action = input("Tiny next action (<10 min) to move forward: ").strip()
    ts = now()
    db["entries"].append({
        "ts": ts, "trigger": thought[:240],
        "distortion": kind, "evidence": evidence[:240],
        "reframe": alt[:240], "action": action[:240], "result": ""
    })
    # Score for doing the work
    db["system_score"]["weekly"] = min(100, db["system_score"].get("weekly", 0) + 3)
    save_db(db)

    print(f"\n{CASUAL['ack']} Timer 10:00 started (pretend 😉). Do the action, then come back and log /journal result.\n")

def journal(db):
    if not db["entries"]:
        print("\nNo entries yet. Use /reframe first.\n"); return
    last = db["entries"][-1]
    print(f"\nLast action: {last['action'] or '(none)'}")
    result = input("Result (done? blocked? notes): ").strip()
    last["result"] = result[:400]
    save_db(db)
    print(f"\n{CASUAL['ok']} Logged. {CASUAL['tip']}\n")

def review(db):
    checks = db["check_ins"][-5:]
    entries = db["entries"][-5:]
    print("\n===== Weekly Review (lite) =====")
    print(f"Streak: {db['system_score'].get('streak_days',0)} days • Weekly Score: {db['system_score'].get('weekly',0)}/100")
    if checks:
        avg_mood = sum(c['mood'] for c in checks)/len(checks)
        avg_stress = sum(c['stress'] for c in checks)/len(checks)
        print(f"Recent mood avg: {avg_mood:.1f} • stress avg: {avg_stress:.1f}")
    if entries:
        from collections import Counter
        counts = Counter(e['distortion'] for e in entries if e.get('distortion'))
        if counts:
            common = counts.most_common(1)[0][0]
            print(f"Most frequent thinking trap: {common}")
    print("Wins logged:")
    for e in entries:
        if e.get("result","").lower().startswith("done"):
            print(f"• {e['action']}  ✅")
    print("================================\n")

def export_data(db, kind="json"):
    EXPORT_DIR = Path("exports"); EXPORT_DIR.mkdir(exist_ok=True)
    ts = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    if kind.lower() == "json":
        out = EXPORT_DIR / f"psych_export_{ts}.json"
        with open(out, "w", encoding="utf-8") as f:
            json.dump(db, f, indent=2)
    else:
        out = EXPORT_DIR / f"psych_export_{ts}.csv"
        # Flatten: check-ins and entries to CSV
        rows = []
        for c in db["check_ins"]:
            rows.append({"ts": c["ts"], "type": "checkin", "mood": c["mood"], "stress": c["stress"],
                         "sleep": c["sleep"], "note": c.get("note","")})
        for e in db["entries"]:
            rows.append({"ts": e["ts"], "type": "entry", "thought": e["trigger"],
                         "distortion": e["distortion"], "reframe": e["reframe"],
                         "action": e["action"], "result": e.get("result","")})
        with open(out, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader(); writer.writerows(rows)
    print(f"\n{CASUAL['ok']} Exported → {out}\n")

HELP = dedent("""
Commands:
  /checkin   – 1–2 min mood/stress/sleep pulse
  /reframe   – Spot the thinking trap & rewrite the thought
  /breathe   – Quick 90-sec reset
  /journal   – Log result of your last action
  /review    – Lite weekly review + streak & score
  /export    – Export data (json or csv). Example: /export csv
  /help      – Show this menu
  /quit      – Exit

Notes:
• I’m a friendly clarity bot, not a therapist or medical device.
• If you mention self-harm or danger, I’ll show crisis resources.
""").strip()

def main():
    db = load_db()
    print(f"\n{APP_NAME}\n{CASUAL['hello']}\n")
    while True:
        try:
            cmd = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n" + CASUAL["bye"]); break

        if not cmd: 
            continue

        if cmd.startswith("/export"):
            parts = cmd.split()
            kind = parts[1] if len(parts) > 1 else "json"
            export_data(db, kind)
        elif cmd == "/checkin":
            pulse_check(db)
        elif cmd == "/reframe":
            reframe(db)
        elif cmd == "/breathe":
            breathe()
        elif cmd == "/journal":
            journal(db)
        elif cmd == "/review":
            review(db)
        elif cmd == "/help":
            print("\n" + HELP + "\n")
        elif cmd == "/quit":
            print("\n" + CASUAL["bye"] + "\n"); break
        else:
            # crisis scan any free text
            if crisis_scan(cmd):
                continue
            print("Say what? Type /help for commands.")

if __name__ == "__main__":
    main()dr
    #!/usr/bin/env python3
"""
Psych Bot — Command Edition (MVP)
Calm wellness copilot. Not a therapist.

Commands
- /checkin (mood/stress/sleep)
- /reframe <thought>
- /breathe
- /journal add|list|delete
- /review
- /export json|csv
- /help

Data is stored locally in psych_data.json
Crisis guardrails: shows resources on risk keywords.
"""

import json, os, re, csv, sys
import datetime as dt
from pathlib import Path

DATA_PATH = Path("psych_data.json")
EXPORT_DIR = Path("exports")
EXPORT_DIR.mkdir(exist_ok=True)

# --- Crisis Guardrails -------------------------------------------------------
RISK_TERMS = [
    r"\bsuicide\b", r"\bkill myself\b", r"\bself[- ]harm\b",
    r"\bhurt (myself|someone)\b", r"\bno reason to live\b",
]

CRISIS_MSG = (
    "⚠️ I’m not equipped for emergencies.\n"
    "If you’re in immediate danger, call **911** (US) or text **988**.\n"
    "Prefer links? https://988lifeline.org  — Reach a trusted person now."
)

def risk_screen(text: str) -> bool:
    if not text: return False
    text = text.lower()
    return any(re.search(p, text) for p in RISK_TERMS)

# --- Persistence --------------------------------------------------------------
def _load():
    if DATA_PATH.exists():
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "user_profile": {"values": [], "supports": []},
        "check_ins": [],
        "entries": [],
        "system_score": {"weekly": 0, "streak_days": 0}
    }

def _save(state):
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

STATE = _load()

def _now_iso():
    return dt.datetime.now().isoformat(timespec="minutes")

# --- Utilities ----------------------------------------------------------------
DISTORTIONS = {
    "all-or-nothing": ["always", "never", "perfect", "ruined"],
    "overgeneralization": ["everyone", "no one", "every time", "nothing works"],
    "mind reading": ["they think", "they must think", "they probably"],
    "catastrophizing": ["disaster", "ruined", "impossible", "hopeless"],
    "should statements": ["should", "must", "have to"],
}

def guess_distortion(text: str) -> str:
    t = text.lower()
    for label, cues in DISTORTIONS.items():
        if any(cue in t for cue in cues):
            return label
    return "unknown"

def reframe_thought(thought: str) -> dict:
    """Return a structured CBT-style reframe."""
    distortion = guess_distortion(thought)
    prompts = {
        "evidence_for": "List facts supporting the thought (1–3 bullets).",
        "evidence_against": "List facts against it (1–3 bullets).",
        "alt_view": "Write a balanced alternative thought.",
        "next_action": "One controllable step (<10 min) you can take now.",
        "if_then": "IF blocked, THEN small fallback you will do.",
    }
    # default templates
    alt = {
        "all-or-nothing": "Reality is a spectrum. One outcome ≠ total identity.",
        "overgeneralization": "One sample ≠ the whole set. New attempts can yield new data.",
        "mind reading": "I can’t know others’ minds. I can ask or test with evidence.",
        "catastrophizing": "Even if this is hard, there are partial wins and recovery paths.",
        "should statements": "Preferences beat rules. I can aim, adjust, and learn.",
        "unknown": "I can check facts, consider contexts, and choose one next step."
    }[distortion]

    card = {
        "ts": _now_iso(),
        "input": thought,
        "distortion": distortion,
        "reframe": alt,
        "prompts": prompts
    }
    return card

# --- Commands -----------------------------------------------------------------
def cmd_help():
    return (
        "🧭 Psych Bot — Command Edition\n"
        "/checkin  → quick mood/stress/sleep capture\n"
        "/reframe <thought>  → spot distortion & get a reframe card\n"
        "/breathe  → 90-sec box-breathing guide\n"
        "/journal add|list|delete  → notes vault\n"
        "/review   → weekly wins/lessons\n"
        "/export json|csv  → download your data\n"
        "Note: I’m a wellness copilot, not a therapist. Crisis? Call **911** or text **988**."
    )

def cmd_checkin():
    print("Mood 1–5? ", end="", flush=True); mood = input().strip()
    print("Stress 1–5? ", end="", flush=True); stress = input().strip()
    print("Sleep hours (last night)? ", end="", flush=True); sleep = input().strip()
    entry = {"ts": _now_iso(), "mood": int(mood), "stress": int(stress), "sleep": float(sleep)}
    STATE["check_ins"].append(entry)
    # simple streak logic
    today = dt.date.today()
    if STATE["check_ins"]:
        last = STATE["check_ins"][-1]["ts"][:10]
        if last == today.isoformat():
            STATE["system_score"]["streak_days"] += 1
    _save(STATE)
    return f"Logged ✅  mood={mood}, stress={stress}, sleep={sleep}h"

def cmd_breathe():
    return (
        "🫁 Box Breathing (90s)\n"
        "Inhale 4 • Hold 4 • Exhale 4 • Hold 4 — repeat 6 cycles.\n"
        "Tip: Relax shoulders. Unclench jaw. Notice 5 things you see/hear/feel."
    )

def cmd_journal(args):
    if not args:
        return "Usage: /journal add <text> | /journal list | /journal delete <id>"
    sub = args[0].lower()
    if sub == "add":
        text = " ".join(args[1:]).strip()
        if not text: return "Add what? Example: /journal add Landed interview; felt proud."
        if risk_screen(text): return CRISIS_MSG
        item = {"id": len(STATE["entries"])+1, "ts": _now_iso(), "text": text}
        STATE["entries"].append(item); _save(STATE)
        return f"Added journal #{item['id']} ✅"
    if sub == "list":
        if not STATE["entries"]: return "No journal entries yet."
        lines = [f"#{e['id']}  • {e['ts']}  • {e['text']}" for e in STATE["entries"][-20:]]
        return "🗒️ Recent entries:\n" + "\n".join(lines)
    if sub == "delete":
        if len(args) < 2: return "Usage: /journal delete <id>"
        try:
            target = int(args[1])
            before = len(STATE["entries"])
            STATE["entries"] = [e for e in STATE["entries"] if e["id"] != target]
            _save(STATE)
            return "Deleted ✅" if len(STATE["entries"]) != before else "ID not found."
        except ValueError:
            return "ID must be a number."
    return "Unknown subcommand. Use: add | list | delete"

def cmd_review():
    # weekly slice
    now = dt.datetime.now()
    week_ago = now - dt.timedelta(days=7)
    checks = [c for c in STATE["check_ins"] if dt.datetime.fromisoformat(c["ts"]) >= week_ago]
    if not checks:
        return "No check-ins this week. Try /checkin to start a streak."
    avg_mood = sum(c["mood"] for c in checks)/len(checks)
    avg_stress = sum(c["stress"] for c in checks)/len(checks)
    avg_sleep = sum(c["sleep"] for c in checks)/len(checks)
    # simple “System Score”
    score = round(max(0, min(100, 20*avg_mood - 10*avg_stress + 5*avg_sleep)))
    STATE["system_score"]["weekly"] = score
    _save(STATE)
    return (
        "📊 Weekly Review\n"
        f"• Check-ins: {len(checks)}\n"
        f"• Avg mood: {avg_mood:.1f}  |  Avg stress: {avg_stress:.1f}  |  Avg sleep: {avg_sleep:.1f}h\n"
        f"• System Score: **{score} / 100**\n"
        "Next: Log a small win in /journal, then run /reframe on anything sticky."
    )

# --- NEW: /reframe ------------------------------------------------------------
def cmd_reframe(args):
    if not args:
        return "Usage: /reframe <thought>. Example: /reframe No one will hire me."
    thought = " ".join(args).strip()
    if risk_screen(thought): return CRISIS_MSG
    card = reframe_thought(thought)
    # store as entry
    STATE["entries"].append({
        "id": len(STATE["entries"])+1,
        "ts": card["ts"],
        "trigger": "thought_reframe",
        "distortion": card["distortion"],
        "reframe": card["reframe"],
        "text": thought
    })
    _save(STATE)
    return (
        "🧠 Reframe Card\n"
        f"• Distortion: **{card['distortion']}**\n"
        f"• Balanced view: {card['reframe']}\n"
        f"• Next step (10 min): {card['prompts']['next_action']}\n"
        f"• IF-THEN: {card['prompts']['if_then']}"
    )

# --- NEW: /export -------------------------------------------------------------
def cmd_export(args):
    if not args:
        return "Usage: /export json|csv"
    kind = args[0].lower()
    ts = dt.datetime.now().strftime("%Y%m%d_%H%M")
    if kind == "json":
        path = EXPORT_DIR / f"psych_export_{ts}.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(STATE, f, indent=2)
        return f"Exported JSON ✅ → {path}"
    if kind == "csv":
        path = EXPORT_DIR / f"psych_export_{ts}.csv"
        # flatten a few useful records
        rows = []
        for c in STATE["check_ins"]:
            rows.append({"type":"checkin","ts":c["ts"],"mood":c["mood"],"stress":c["stress"],"sleep":c["sleep"],"text":""})
        for e in STATE["entries"]:
            rows.append({"type":"entry","ts":e.get("ts",""),"mood":"","stress":"","sleep":"","text":e.get("text","")})
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["type","ts","mood","stress","sleep","text"])
            writer.writeheader(); writer.writerows(rows)
        return f"Exported CSV ✅ → {path}"
    return "Unknown format. Use: json | csv"

# --- CLI Router ---------------------------------------------------------------
def main():
    print("Psych Bot ready. Type a command (or /help).")
    while True:
        try:
            text = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye."); break
        if not text: continue
        if risk_screen(text):
            print(CRISIS_MSG); continue

        parts = text.split()
        cmd, args = parts[0].lower(), parts[1:]

        if cmd in ("/quit", "/exit"): print("Bye."); break
        elif cmd == "/help": print(cmd_help())
        elif cmd == "/checkin": print(cmd_checkin())
        elif cmd == "/breathe": print(cmd_breathe())
        elif cmd == "/journal": print(cmd_journal(args))
        elif cmd == "/review": print(cmd_review())
        elif cmd == "/reframe": print(cmd_reframe(args))      # NEW
        elif cmd == "/export": print(cmd_export(args))        # NEW
        else: print("Unknown. Try /help")

if __name__ == "__main__":
    main()
