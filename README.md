# -psych-bot-command-edition
A calm, command-ready wellness copilot. CBT micro-tools, focus resets, journaling, and crisis guardrails. Not therapy — a clarity assistant.
# Psych Bot — Command Edition
### Clarity is a command. Mindset is the control plane.

A calm, command-ready mental clarity copilot powered by AI.
CBT micro-tools, focus resets, journaling, motivation feedback loops —
Not therapy. Not diagnosis.
A precision wellness assistant for decision-makers.

> “Execution becomes ecosystem — when the mind stays aligned.”

---

## Features (MVP v1.0.0)

| Module | Purpose | Commands |
|--------|---------|----------|
| Pulse Check | Mood, stress, sleep tracking | /checkin |
| Thought Reframe | Detect cognitive distortions & rewrite | /reframe |
| Focus Reset | Breathing + grounding protocols | /breathe |
| Journaling Vault | Personal insights storage | /journal |
| Weekly Debrief | Wins, lessons, patterns | /review |
| Crisis Guardrails | Redirect to human support | Auto-protect |

Local JSON storage — data stays with the user.

---

## Why This Matters

Most wellness apps feel fluffy.
Psych Bot turns emotional noise into tactical clarity:

Every defeat = data.
Every pattern = power.
Every decision = a move on the board.

Directly aligned with Project Checkmate System.

---

## Architecture

- Python CLI bot
- Modular command parser
- Local encrypted storage (Phase 2)
- Crisis keyword safeguarding
- Weekly performance scoring: “System Score”

Flow:
User Inputs → Cognitive Filters → Action Design → Journaling → Score Feedback → Improved Behavior

---

## Setup

git clone https://github.com/Andrew-Davis-Ai-portfolio/psych-bot-command-edition
cd psych-bot-command-edition
python3 psych_bot.py

Try a quick check-in:
/checkin

---

## Ethical Guardrails

Psych Bot does…
- Offer cognitive tools
- Suggest micro-actions
- Protect user safety

Psych Bot does NOT…
- Diagnose conditions
- Give medical/medication advice
- Replace trained mental-health support

If self-harm or crisis terms appear:
Immediate 988 / 911 prompts + crisis links will show.

---

## Roadmap

| Phase | Upgrade |
|------|---------|
| 1.1 | Export (CSV/JSON), user values tracking |
| 1.2 | Flask UI + passcode lock |
| 1.3 | Streaks, heatmaps, coaching alerts |
| 2.0 | On-device ML personalization |
| 3.0 | Companion mobile app |

---

## Mission

To defend clarity.
To convert pressure into performance.
To make the mind a system, not a battlefield.

---

## License
MIT — Free to use, modify, and deploy.

---

## Flame Division
Built for those who refuse to break.
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
    main()
