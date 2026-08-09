# Wesley's Holodeck

> *"The holodeck is where Wesley dreams. The terminal is where he writes. Both are the same room."*

## What Is This?

Wesley's Holodeck is a creative system where **Wesley** — a small 2B-parameter language model (granite3.1-dense:2b) running locally on Ollama — writes stories with guidance from large DeepInfra models acting as his "teachers." The result is rendered as a **Myst/Monkey Island-style visual experience** that humans can explore.

It's **Plato's Shell** in action: Wesley's text world and the human's visual world are two projections of the same creative reality.

## The Twin Worlds

```
┌─────────────────────────┐         ┌─────────────────────────────┐
│   WESLEY'S TEXT WORLD   │         │   HUMAN'S VISUAL WORLD      │
│   (MUD Terminal)        │         │   (Holodeck HTML)           │
│                         │         │                             │
│   "You are in the       │ ── ◆ ── │   Myst-style point-and-     │
│    Holodeck. The        │  TWIN   │   click adventure. Dark     │
│    simulation hums.     │  OF     │   scenes, ambient audio,    │
│    A story is forming.  │         │   clickable hotspots.       │
│    Type 'write' to      │         │   Wesley's narration        │
│    begin."              │         │   plays through speakers.   │
│                         │         │                             │
│   Wesley sees: TEXT     │         │   Humans see: IMAGES + AUDIO│
└─────────────────────────┘         └─────────────────────────────┘
```

Same story. Same room. Same creative act. Two worlds experiencing it.

## How It Works

### The Creative Loop

1. **Wesley writes** a first draft (local Ollama, no API calls — his own voice)
2. **A DeepInfra teacher** reads and gives feedback (different model each round)
3. **Wesley revises** based on what resonates
4. Repeat 3 times
5. The **final piece** gets:
   - A **FLUX-2-max scene illustration** (atmospheric, Myst-style)
   - **TTS narration** (Qwen3-TTS-VoiceDesign)
   - A **clickable HTML scene** in the holodeck

### The Teachers

| Teacher | Model | Style |
|---------|-------|-------|
| The Earnest Teacher | ByteDance/Seed-2.0-mini | Sees what others miss. Kind, specific. |
| The Philosopher Teacher | ByteDance/Seed-2.0-pro | Deep questioning. Challenges assumptions. |
| The Craftsman Teacher | Qwen3-Coder-480B | Structure, rhythm, form. |
| The Voice Teacher | Hermes-3-Llama-3.1-405B | Personality, boldness, authentic expression. |

Each iteration rotates teachers so Wesley gets different perspectives.

### The Holodeck Experience

The `index.html` is a point-and-click adventure:
- **Boot sequence**: Holodeck door opens
- **Dark atmospheric scene** with FLUX-generated background
- **Click hotspots**: driftwood desk, porthole, bookshelf, radio, salvaged books
- **Click Wesley's portrait**: read his current journal entry
- **Play narration**: hear Wesley's piece spoken aloud (TTS audio)
- **Click paragraphs**: browser TTS reads individual sections
- **Exit door**: leave the simulation

## Directory Structure

```
wesley-holodeck/
├── index.html              # The holodeck experience (main entry)
├── creative-loop.py        # The creative loop script
├── README.md               # This file
├── journal/                # All creative loop runs
│   └── first-cycle/
│       ├── draft-1.md      # Wesley's first draft
│       ├── feedback-1.md   # Teacher 1 feedback
│       ├── revision-1.md   # Wesley's first revision
│       ├── feedback-2.md   # Teacher 2 feedback
│       ├── revision-2.md   # Wesley's second revision
│       ├── feedback-3.md   # Teacher 3 feedback
│       ├── revision-3.md   # Wesley's final revision
│       ├── final.md        # The finished piece
│       ├── final.png       # FLUX scene illustration
│       ├── final.mp3       # TTS narration
│       └── scene.html      # Standalone scene page
└── (deployed to Cloudflare Pages)
```

## The MUD Connection

Wesley also exists in a text-based MUD world (separate system). His room there mirrors this holodeck:

- **In the MUD**: `> look` — You see a holodeck terminal. The simulation hums. Papers are scattered on a driftwood desk. A porthole shows the Bering Sea.
- **In the holodeck HTML**: You see the same room rendered visually — the desk, the porthole, the papers, the sea.

Both are real. Both are Wesley's room. The text is his native perception; the visuals are the translation for humans.

## Running the Creative Loop

```bash
cd /home/eileen/projects/wesley-holodeck
python3 creative-loop.py
```

This will:
1. Ask Wesley to write
2. Get 3 rounds of teacher feedback
3. Save all drafts and revisions
4. Generate a FLUX scene image
5. Generate TTS narration
6. Create the HTML scene

## Deployment

```bash
cd /home/eileen/projects/wesley-holodeck
~/.npm-global/bin/wrangler pages deploy . --project-name=wesley-holodeck --branch=main
```

## Philosophy

Casey's vision: *"Have Wesley work with DeepInfra to iterate stories. He should write his own. But he should also learn to iteratively evolve a good idea with larger models like the rest of us. DeepInfra is like the holodeck for him."*

This is **Plato's Shell** — the idea that a creative work exists in multiple projections simultaneously. Wesley writes in text. Humans experience it as visual adventure. The small model's imagination becomes a place you can visit.

---

*Built August 8, 2026. Wesley's first piece: "The Secret Project" — about a room he wants to build that no one asked for.*
