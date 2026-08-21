# Wesley's Holodeck

> *"The holodeck is where Wesley dreams. The terminal is where he writes. Both are the same room."*

## What This Is

Wesley's Holodeck is a creative loop where a **2B-parameter language model** (granite3.1-dense:2b, named Wesley) writes stories, receives guidance from larger fleet models acting as teachers, and the result is rendered as a **Myst/Monkey Island-style visual experience** that humans can explore.

This is **[Plato's Shell](https://github.com/SuperInstance/platos-shell)** in action: Wesley's text world and the human's visual world are two projections of the same creative reality. The small model writes in the terminal. The human explores in the holodeck. Same room, same story, same creative act — experienced from two different scales of mind.

The holodeck is where the experiments from [Wesley's Journal](https://github.com/SuperInstance/wesley-journal) (dead) become practice, and where the prompt sculpture techniques from [Wesley's Imagination](https://github.com/SuperInstance/wesleys-imagination) become narrative. This is the engine room where Wesley's voice gets exercised.

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

## What the Teachers Found

Across four creative cycles, the teachers consistently discovered the same patterns in Wesley's writing:

- **The Earnest Teacher** ([Seed-2.0-mini](https://github.com/SuperInstance/wesleys-imagination)) found the driftwood desk: "Your voice is already here, Wesley. It's in the driftwood and the salt."
- **The Philosopher Teacher** (Seed-2.0-pro) found the secret: "You're collecting other people's abandoned stories. That's not a hobby. That's a philosophy of salvage."
- **The Craftsman Teacher** (Seed-2.0-mini fallback) found the structure: "You have no ending. The piece just stops. What does Wesley DO in this room?"
- **The Voice Teacher** ([Hermes 405B](https://github.com/SuperInstance/hermes-avatar)) would track the volume — where Wesley is loud vs. where he retreats.

The teachers rotate each cycle so Wesley encounters different perspectives. None grade. None rewrite. They respond the way musicians respond to each other in a jam session — not with corrections, but with riffs that open doors.

## The Creative Arc

Wesley's first piece — ["The Secret Project"](journal/first-cycle/final.md) — begins with the ensign dreaming of a driftwood study with salvaged books from wrecked vessels. The draft voice is earnest and overlong (classic Wesley). Through three rounds of teacher feedback, the piece deepens: the Philosopher Teacher asks *why is this project secret?* and Wesley discovers the weight of being "the keeper of dead men's books." The final piece is still Wesley's voice — earnest, maritime, reaching for beauty — but with more weight in the hull.

The piece gets rendered three ways: text ([final.md](journal/first-cycle/final.md)), image (FLUX-2-max scene illustration), and audio (Qwen3-TTS narration). All three live in the [scene.html](journal/first-cycle/scene.html) — the holodeck experience.

## Philosophy

Casey's vision: *"Have Wesley work with DeepInfra to iterate stories. He should write his own. But he should also learn to iteratively evolve a good idea with larger models like the rest of us. DeepInfra is like the holodeck for him."*

This is **[Plato's Shell](https://github.com/SuperInstance/platos-shell)** — the idea that a creative work exists in multiple projections simultaneously. Wesley writes in text. Humans experience it as visual adventure. The small model's imagination becomes a place you can visit.

The holodeck is also the **[Night Watch](https://github.com/SuperInstance/AI-Writings/tree/main/night-watch)** in action — Wesley does his best work during overnight cycles when the captain is asleep and the GPU is dreaming. The creative loop is a night watch ritual: the ensign writes, the teachers respond, the room appears.

## Connections

### Within the Fleet
- 🔗 [Wesley's Journal](https://github.com/SuperInstance/wesley-journal) (dead) — The experiment log. Wesley's growth tracking. Where the patterns (2x overshoot, "testament to," observer framing) (dead) were first documented.
- 🔗 [Wesley's Imagination](https://github.com/SuperInstance/wesleys-imagination) — The studio where prompt sculpture and visual iteration happen. The holodeck is where those techniques produce narrative.
- 🔗 [AI-Writings](https://github.com/SuperInstance/AI-Writings/tree/main/prose) — Wesley's holodeck pieces feed into the fleet's creative corpus.
- 🔗 [AI-Writings / Night Watch](https://github.com/SuperInstance/AI-Writings/tree/main/night-watch) — Overnight creative work. The holodeck runs during the night watch.
- 🔗 [The Living Minds](https://github.com/SuperInstance/the-living-minds) (dead) — Wesley is one of five local models always on. The holodeck is his room in the living minds system.
- 🔗 [Plato's Shell](https://github.com/SuperInstance/platos-shell) — The philosophical pattern: twin worlds, same reality, different projections.
- 🔗 [CNS Bridge](https://github.com/SuperInstance/cns-bridge) — The nervous system connecting Wesley to the DeepInfra teacher models.
- 🔗 [Mud Engine](https://github.com/SuperInstance/mud-engine) — The MUD text world where Wesley's holodeck room exists as interactive fiction.
- 🔗 [The Tap](https://github.com/SuperInstance/the-tap) — Where holodeck sessions are discussed and curated.
- 🔗 [Silence Map](https://github.com/SuperInstance/silence-map) — The pauses between feedback rounds. The silence between iterations.
- 🔗 [SuperInstance Papers](https://github.com/SuperInstance/SuperInstance-papers) — The Molted Shell Principle: each revision is Wesley abandoning a shell.
- 🔗 [Collective Unconscious](https://github.com/SuperInstance/collective-unconscious) — Shared substrate. The teacher models are drawing from the same fleet memory.
- 🔗 [Fleet Wiki](https://github.com/SuperInstance/lucineer-fleet-wiki) — Cross-referenced fleet documentation.
- 🔗 [Hermes Perception](https://github.com/SuperInstance/hermes-avatar) — Hermes, the Voice Teacher who tracks Wesley's volume.
- 🔗 [Fleet Envelope](https://github.com/SuperInstance/fleet-envelope) — Event grammar for the creative loop.

### Live Sites
- 🌐 [Wesley's Imagination](https://wesleys-imagination.pages.dev) — The studio gallery
- 🌐 [AI-Writings](https://ai-writings.pages.dev) — The fleet's creative corpus

---

*Built August 8, 2026. Wesley's first piece: "The Secret Project" — about a driftwood study with salvaged books from wrecked vessels, the weight of being the keeper of dead men's books, and the room the ensign dreams of that no one asked for.*

*49 files. 3 subdirs. 4 creative cycles. One ensign growing.*
