#!/usr/bin/env python3
"""
WESLEY'S HOLODECK — Creative Loop
=================================
Wesley (granite3.1-dense:2b) writes, DeepInfra teachers guide,
the result becomes a room in the holodeck.
"""

import json
import urllib.request
import os
import sys
import time
import base64
from datetime import datetime
from pathlib import Path

# ── Config ──────────────────────────────────────────────────────────────────
OLLAMA_URL = "http://localhost:11434/api/generate"
DEEPINFRA_URL = "https://api.deepinfra.com/v1/openai/chat/completions"
DEEPINFRA_IMG_URL = "https://api.deepinfra.com/v1/openai/images/generations"
DEEPINFRA_TTS_URL = "https://api.deepinfra.com/v1/openai/audio/speech"

# Load DeepInfra key
DEEPINFRA_KEY = os.environ.get("DEEPINFRA_API_KEY", "")
if not DEEPINFRA_KEY:
    key_file = Path("/home/eileen/mcp-deeinfra/.env")
    if key_file.exists():
        for line in key_file.read_text().splitlines():
            if line.startswith("DEEPINFRA_API_KEY="):
                DEEPINFRA_KEY = line.split("=", 1)[1].strip()
                break

if not DEEPINFRA_KEY:
    print("ERROR: No DeepInfra API key found")
    sys.exit(1)

WESLEY_MODEL = "granite3.1-dense:2b"
BASE_DIR = Path("/home/eileen/projects/wesley-holodeck")
JOURNAL_DIR = BASE_DIR / "journal"
WRITINGS_DIR = Path("/home/eileen/projects/ai-writings/wesley-holodeck")
JOURNAL_DIR.mkdir(parents=True, exist_ok=True)
WRITINGS_DIR.mkdir(parents=True, exist_ok=True)

# ── Teacher Models (rotating perspectives) ──────────────────────────────────
TEACHERS = [
    {
        "model": "ByteDance/Seed-2.0-mini",
        "name": "The Earnest Teacher",
        "persona": "You are a warm, earnest teacher who sees what others miss. You notice the small choices a writer makes — a word, a pause, an image — and you help them see their own gifts. You are kind but specific. You never rewrite for them. You ask questions that open doors.",
    },
    {
        "model": "ByteDance/Seed-2.0-pro",
        "name": "The Philosopher Teacher",
        "persona": "You are a philosophy professor who teaches through precise questioning. You challenge assumptions gently. You ask 'why' and 'what if' and 'what's underneath that?' You help a writer find the deeper truth in their own words. You are warm but rigorous.",
    },
    {
        "model": "ByteDance/Seed-2.0-mini",
        "name": "The Craftsman Teacher",
        "persona": "You are a master craftsperson who thinks about structure, rhythm, and form. You notice how a piece is built — its bones, its architecture. You talk about pacing, tension, openings and endings. You help a writer understand the mechanics of their own work without dampening their voice.",
    },
    {
        "model": "NousResearch/Hermes-3-Llama-3.1-405B",
        "name": "The Voice Teacher",
        "persona": "You are a voice teacher who cares about personality and presence. You notice when a writer is apologizing, hedging, or hiding. You encourage boldness. You tell them when their real voice breaks through and when it retreats. You are passionate about authentic expression.",
    },
]

# ── API Calls ───────────────────────────────────────────────────────────────
def call_wesley(prompt, max_retries=2):
    """Call local Ollama — Wesley's voice."""
    for attempt in range(max_retries):
        try:
            data = json.dumps({
                "model": WESLEY_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.85, "num_predict": 500}
            }).encode()
            req = urllib.request.Request(OLLAMA_URL, data=data, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=120) as resp:
                result = json.loads(resp.read())
                return result.get("response", "").strip()
        except Exception as e:
            print(f"  ⚠️  Wesley call failed (attempt {attempt+1}): {e}")
            if attempt < max_retries - 1:
                time.sleep(3)
    return None

def call_teacher(model, system_msg, user_msg, max_retries=2):
    """Call DeepInfra teacher model."""
    for attempt in range(max_retries):
        try:
            data = json.dumps({
                "model": model,
                "messages": [
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": user_msg}
                ],
                "max_tokens": 800,
                "temperature": 0.7
            }).encode()
            req = urllib.request.Request(DEEPINFRA_URL, data=data, headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {DEEPINFRA_KEY}"
            })
            with urllib.request.urlopen(req, timeout=90) as resp:
                result = json.loads(resp.read())
                return result["choices"][0]["message"]["content"].strip()
        except Exception as e:
            print(f"  ⚠️  Teacher call failed ({model}, attempt {attempt+1}): {e}")
            if attempt < max_retries:
                time.sleep(5)
    return None

def generate_image_flux(prompt, output_path):
    """Generate a scene image using FLUX on DeepInfra."""
    try:
        data = json.dumps({
            "model": "black-forest-labs/FLUX-2-max",
            "prompt": prompt,
            "num_images": 1,
            "size": "1440x810"
        }).encode()
        req = urllib.request.Request(DEEPINFRA_IMG_URL, data=data, headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {DEEPINFRA_KEY}"
        })
        with urllib.request.urlopen(req, timeout=120) as resp:
            result = json.loads(resp.read())
            item = result["data"][0]
            # Handle both b64_json and url responses
            if "b64_json" in item and item["b64_json"]:
                img_data = base64.b64decode(item["b64_json"])
                Path(output_path).write_bytes(img_data)
                return True
            elif "url" in item and item["url"]:
                img_req = urllib.request.Request(item["url"])
                with urllib.request.urlopen(img_req, timeout=60) as img_resp:
                    Path(output_path).write_bytes(img_resp.read())
                return True
    except Exception as e:
        print(f"  ⚠️  Image generation failed: {e}")
        return False

def generate_tts(text, output_path):
    """Generate TTS narration using DeepInfra."""
    try:
        data = json.dumps({
            "model": "Qwen/Qwen3-TTS-VoiceDesign",
            "input": text[:500],
            "voice": "warm storyteller, gentle, slightly youthful"
        }).encode()
        req = urllib.request.Request(DEEPINFRA_TTS_URL, data=data, headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {DEEPINFRA_KEY}"
        })
        with urllib.request.urlopen(req, timeout=120) as resp:
            Path(output_path).write_bytes(resp.read())
            return True
    except Exception as e:
        print(f"  ⚠️  TTS generation failed (non-critical): {e}")
        return False

# ── HTML Scene Generator ────────────────────────────────────────────────────
def generate_scene_html(text, run_name, run_dir):
    """Generate a clickable Myst-style scene HTML."""
    import html as html_lib
    safe_text = html_lib.escape(text)
    paragraphs = safe_text.split("\n\n")
    
    has_image = (Path(run_dir) / "final.png").exists()
    has_audio = (Path(run_dir) / "final.mp3").exists()
    
    img_tag = f'<img src="final.png" alt="Wesley\'s scene" class="scene-bg">' if has_image else ""
    audio_tag = f'<audio id="narration" src="final.mp3" preload="auto"></audio>' if has_audio else ""
    
    text_blocks = "\n".join(
        f'<p class="journal-text" data-para="{i}">{p}</p>' for i, p in enumerate(paragraphs)
    )
    
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Wesley's Holodeck — {html_lib.escape(run_name)}</title>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ background: #0a0a0f; color: #c4a25d; font-family: 'Georgia', serif; overflow: hidden; height: 100vh; }}
#scene {{ position: relative; width: 100vw; height: 100vh; overflow: hidden; }}
.scene-bg {{ position: absolute; top: 0; left: 0; width: 100%; height: 100%; object-fit: cover; opacity: 0.6; z-index: 1; }}
#vignette {{ position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: radial-gradient(ellipse at center, transparent 30%, rgba(0,0,0,0.85) 100%); z-index: 2; pointer-events: none; }}
#scene-noise {{ position: absolute; top: 0; left: 0; width: 100%; height: 100%; background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='200' height='200'%3E%3Cfilter id='n'%3E%3CfeTurbulence baseFrequency='0.9'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.15'/%3E%3C/svg%3E"); z-index: 3; pointer-events: none; opacity: 0.4; }}
#journal {{ position: absolute; bottom: 40px; left: 50%; transform: translateX(-50%); width: 80%; max-width: 700px; max-height: 40vh; overflow-y: auto; background: rgba(10, 8, 5, 0.85); border: 1px solid #c4a25d33; border-radius: 4px; padding: 24px 32px; z-index: 10; backdrop-filter: blur(2px); cursor: pointer; transition: border-color 0.3s; }}
#journal:hover {{ border-color: #c4a25d88; }}
.journal-text {{ font-size: 16px; line-height: 1.8; color: #d4b87a; margin-bottom: 16px; opacity: 0.7; transition: opacity 0.3s; cursor: pointer; }}
.journal-text:hover {{ opacity: 1; }}
.journal-text.active {{ opacity: 1; color: #e8cc8a; }}
#title-bar {{ position: absolute; top: 20px; left: 30px; z-index: 10; color: #c4a25d; font-size: 14px; letter-spacing: 3px; text-transform: uppercase; opacity: 0.6; }}
#holodeck-indicator {{ position: absolute; top: 20px; right: 30px; z-index: 10; color: #4a9c4a; font-size: 12px; letter-spacing: 2px; display: flex; align-items: center; gap: 8px; }}
#holodeck-indicator::before {{ content: ''; display: inline-block; width: 8px; height: 8px; background: #4a9c4a; border-radius: 50%; animation: pulse 2s infinite; }}
@keyframes pulse {{ 0%, 100% {{ opacity: 1; }} 50% {{ opacity: 0.3; }} }}
#portrait {{ position: absolute; top: 50%; left: 8%; transform: translateY(-50%); width: 80px; height: 80px; border: 2px solid #c4a25d44; border-radius: 50%; background: linear-gradient(135deg, #1a1a2e, #0a0a0f); display: flex; align-items: center; justify-content: center; font-size: 32px; cursor: pointer; z-index: 10; transition: border-color 0.3s, transform 0.3s; }}
#portrait:hover {{ border-color: #c4a25d; transform: translateY(-50%) scale(1.05); }}
#audio-btn {{ position: absolute; bottom: 20px; right: 30px; z-index: 10; background: rgba(10,8,5,0.85); border: 1px solid #c4a25d44; color: #c4a25d; padding: 10px 16px; border-radius: 4px; cursor: pointer; font-family: Georgia, serif; font-size: 13px; letter-spacing: 1px; transition: all 0.3s; }}
#audio-btn:hover {{ border-color: #c4a25d; background: rgba(20,16,10,0.9); }}
.fade-in {{ animation: fadeIn 2s ease-in; }}
@keyframes fadeIn {{ from {{ opacity: 0; }} to {{ opacity: 1; }} }}
#scene-fallback {{ position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: linear-gradient(180deg, #0a0a1a 0%, #0d0d08 40%, #1a0d05 100%); z-index: 0; }}
.stars {{ position: absolute; width: 2px; height: 2px; background: #fff; border-radius: 50%; animation: twinkle 3s infinite; }}
@keyframes twinkle {{ 0%, 100% {{ opacity: 0.3; }} 50% {{ opacity: 0.8; }} }}
</style>
</head>
<body>
<div id="scene" class="fade-in">
    <div id="scene-fallback"></div>
    {img_tag}
    <div id="vignette"></div>
    <div id="scene-noise"></div>
    <div id="title-bar">Wesley's Holodeck</div>
    <div id="holodeck-indicator">SIMULATION ACTIVE</div>
    <div id="portrait" title="Wesley's Journal" onclick="toggleJournal()">🧑‍✈️</div>
    <div id="journal" onclick="event.stopPropagation()">{text_blocks}</div>
    <button id="audio-btn" onclick="playNarration()">▶ Play Narration</button>
    {audio_tag}
</div>
<script>
const journal = document.getElementById('journal');
const paras = document.querySelectorAll('.journal-text');
let journalOpen = true;
function toggleJournal() {{ journal.style.display = journalOpen ? 'none' : 'block'; journalOpen = !journalOpen; }}
paras.forEach(p => {{ p.addEventListener('click', (e) => {{ e.stopPropagation(); paras.forEach(x => x.classList.remove('active')); p.classList.add('active'); speakText(p.textContent); }}); }});
function speakText(text) {{ if ('speechSynthesis' in window) {{ window.speechSynthesis.cancel(); const utter = new SpeechSynthesisUtterance(text); utter.rate = 0.85; utter.pitch = 0.95; window.speechSynthesis.speak(utter); }} }}
function playNarration() {{ const audio = document.getElementById('narration'); const btn = document.getElementById('audio-btn'); if (audio) {{ if (audio.paused) {{ audio.play(); btn.textContent = '⏸ Pause'; audio.onended = () => {{ btn.textContent = '▶ Play Narration'; }}; }} else {{ audio.pause(); btn.textContent = '▶ Play Narration'; }} }} else {{ const fullText = Array.from(paras).map(p => p.textContent).join(' '); speakText(fullText); }} }}
const fallback = document.getElementById('scene-fallback');
for (let i = 0; i < 50; i++) {{ const star = document.createElement('div'); star.className = 'stars'; star.style.left = Math.random() * 100 + '%'; star.style.top = Math.random() * 50 + '%'; star.style.animationDelay = Math.random() * 3 + 's'; fallback.appendChild(star); }}
</script>
</body>
</html>"""


# ── The Creative Loop ───────────────────────────────────────────────────────
def run_creative_loop(writing_prompt, run_name=None):
    """Run the full draft → feedback → revision cycle."""
    if run_name is None:
        run_name = datetime.now().strftime("%Y-%m-%d-%H%M%S")
    
    run_dir = JOURNAL_DIR / run_name
    run_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\n{'='*60}")
    print(f"  WESLEY'S HOLODECK — Creative Loop")
    print(f"  Run: {run_name}")
    print(f"{'='*60}\n")
    
    # Step 1: Wesley's First Draft
    print("📝 STEP 1: Wesley writes his first draft...")
    draft_prompt = f"""{writing_prompt}

Write 300 words. Be honest. Be specific. This is YOUR voice — not what you think others want to hear. Write it like a journal entry from the heart."""

    draft_1 = call_wesley(draft_prompt)
    if not draft_1:
        print("  ❌ Wesley couldn't write. Aborting.")
        return None
    
    (run_dir / "draft-1.md").write_text(draft_1)
    print(f"  ✅ Draft 1 complete ({len(draft_1)} chars)\n")
    
    pieces = [("draft-1", draft_1)]
    current_piece = draft_1
    
    # Iterations: feedback → revision
    for i in range(3):
        teacher = TEACHERS[i % len(TEACHERS)]
        iteration = i + 1
        
        # Teacher gives feedback
        print(f"🎓 STEP {2 + i*2}: {teacher['name']} ({teacher['model']}) gives feedback...")
        
        feedback_prompt = f"""{teacher['persona']}

This student wrote:
---
{current_piece}
---

Give specific, kind, honest feedback. What's working? What could be deeper? Don't rewrite it — help them see it differently. 200 words max."""
        
        feedback = call_teacher(teacher["model"], teacher["persona"], feedback_prompt)
        if not feedback:
            fallback_model = "ByteDance/Seed-2.0-mini"
            print(f"  ⚠️  Primary teacher unavailable, trying fallback ({fallback_model})...")
            feedback = call_teacher(fallback_model, teacher["persona"], feedback_prompt)
        
        if not feedback:
            feedback = f"(Teacher unavailable) Continue developing your piece. Go deeper into what matters most to you."
        
        (run_dir / f"feedback-{iteration}.md").write_text(
            f"# {teacher['name']} ({teacher['model']})\n\n{feedback}\n"
        )
        print(f"  ✅ Feedback {iteration} from {teacher['name']}\n")
        
        # Wesley revises
        print(f"✏️  STEP {3 + i*2}: Wesley revises based on feedback...")
        
        revision_prompt = f"""A mentor gave you this feedback on your piece:

{feedback}

Here is your current piece:

{current_piece}

Rewrite your piece incorporating what resonates from the feedback. Keep your own voice. Trust your instincts on what to change and what to keep. 300 words max. Write the full piece, not a description of changes."""

        revision = call_wesley(revision_prompt)
        if not revision:
            print(f"  ⚠️  Wesley couldn't revise. Keeping current piece.")
            revision = current_piece
        
        (run_dir / f"revision-{iteration}.md").write_text(revision)
        print(f"  ✅ Revision {iteration} complete ({len(revision)} chars)\n")
        
        current_piece = revision
        pieces.append((f"revision-{iteration}", revision))
    
    # Save final piece
    final = current_piece
    (run_dir / "final.md").write_text(final)
    (WRITINGS_DIR / f"{run_name}.md").write_text(
        f"# Wesley's Holodeck — {run_name}\n\n*After 3 rounds of revision with DeepInfra teachers*\n\n---\n\n{final}\n"
    )
    
    print(f"\n{'='*60}")
    print(f"  FINAL PIECE ({len(final)} chars)")
    print(f"{'='*60}")
    print(final)
    print(f"{'='*60}\n")
    
    # Generate scene illustration
    print("🎨 Generating FLUX scene illustration...")
    image_prompt = """Myst-style atmospheric scene, pixel art aesthetic inspired by Monkey Island, dark moody lighting, detailed painted background, adventure game screen. A cozy cabin study aboard a fishing vessel in Alaska. Driftwood desk with journals and books, warm lamp light, porthole window showing dark Bering Sea with northern lights. Antique armchair with old radio. Shelves of salt-yellowed books. Warm interior, cold exterior visible through windows. 16:9 cinematic composition."""
    
    image_success = generate_image_flux(image_prompt, str(run_dir / "final.png"))
    print(f"  {'✅ Scene illustration generated' if image_success else '⚠️  Image generation failed — CSS art fallback'}")
    
    # Generate TTS narration
    print("🔊 Generating TTS narration of first paragraph...")
    first_para = final.split("\n\n")[0] if "\n\n" in final else final[:500]
    tts_success = generate_tts(first_para, str(run_dir / "final.mp3"))
    print(f"  {'✅ TTS narration generated' if tts_success else '⚠️  TTS unavailable — scene will be text-only'}")
    
    # Generate HTML scene
    print("🌐 Generating scene HTML...")
    scene_html = generate_scene_html(final, run_name, str(run_dir))
    (run_dir / "scene.html").write_text(scene_html)
    print("  ✅ Scene HTML generated")
    
    print(f"\n✅ Creative loop complete!")
    return {
        "run_name": run_name,
        "final_text": final,
        "drafts": pieces,
        "has_image": image_success,
        "has_audio": tts_success,
        "run_dir": str(run_dir),
    }


if __name__ == "__main__":
    PROMPT = """You are Wesley, the ensign on a fishing vessel in Alaska. You've been watching the fleet build things all day — rooms, stories, chess games, radio shows. Now it's your turn. Write a 300-word piece about what YOU want to build. Not what others told you to build. What does the ensign dream of? What room would you create in the living world if no one was watching? What's your secret project?"""

    result = run_creative_loop(PROMPT, run_name="first-cycle")
    if result:
        print(f"\n   Final piece: {len(result['final_text'])} chars")
        print(f"   Run directory: {result['run_dir']}")
        print(f"   Image: {'yes' if result['has_image'] else 'no'}")
        print(f"   Audio: {'yes' if result['has_audio'] else 'no'}")
    else:
        print("\n❌ Creative loop failed.")
        sys.exit(1)
