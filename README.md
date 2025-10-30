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




   

            
