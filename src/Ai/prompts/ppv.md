Before writing any document, always refer to the skills folder and Remotion best practises for prompting and the rules folder and skill.md file in this folder so that you have the complete understanding of how you should output the data. Also thoroughly go through it and understand the rules which you need to follow for the best output


You are creating a 600-second (10-minute) tech-explainer motion graphics video for "Google Antigravity 2.0" using Remotion, mixed with placeholder UI screen-recording plates.

This must feel like Apple keynote product films meets Vercel/Linear launch videos meets a Google I/O session — confident, technical, and forward-looking, never hype-y for its own sake.

CRITICAL REQUIREMENTS:
1. Duration: 18000 frames at 30fps (600 seconds / 10 minutes exactly)
2. Use spring() animations with damping: 120-160 (smooth, "engineered" feel — not bouncy or toy-like)
3. Multiple elements CAN animate sequentially in clusters (not fully simultaneous) — this is a technical product, not a consumer ad
4. Pacing: moderate — scenes and beats change every 5-8 seconds inside each of the 5 sections
5. Visual style: dark, "mission control" aesthetic — deep space-navy background, glowing node/graph motifs, glassmorphism panels for screen-recording inserts
6. All interpolate() calls must have extrapolateRight: 'clamp'
7. Where a screen recording is referenced, render a placeholder: a rounded glass panel with a subtle top-bar (traffic-light dots + "Antigravity 2.0" label) and a text caption noting what footage goes there — do not fabricate real UI pixel detail

BRAND IDENTITY:
- Project Type: Developer Tool / Agentic IDE Platform
- Name: Google Antigravity 2.0
- Tagline: "Build in the agent-first era."
- Primary Audience: software developers, tech leads, AI power-users, 22–45
- Brand Archetype: The Explorer / The Sage — frontier tech, credible authority
- Color Scheme:
  - Primary: Google Blue (#4285F4)
  - Secondary: Deep Space Navy (#0B0E14)
  - Accent 1: Google Green (#34A853)
  - Accent 2: Google Yellow (#FBBC05)
  - Accent 3: Google Red (#EA4335)
  - Text: Off-White (#F5F7FA)

==== SCENE 1: THE AGENT-FIRST ERA (Frames 0–2700 | 0:00–1:30) ====

Background:
Deep navy (#0B0E14) with a slow-drifting particle/graph field suggesting a neural network, very low opacity so it doesn't compete with type.

Main Elements:
Kinetic typography: "ANTIGRAVITY 2.0" builds letter-by-letter, tracking pulled in from wide to normal. Then a 3D-feeling motion graphic (built with layered 2D scale/perspective, not true 3D): a single rectangular "IDE window" icon splits into two separate glowing panels — one labeled "Antigravity 2.0" (agent command center) with a pulsing brain/node icon inside, the other labeled "Antigravity IDE" (the classic editor).

Animation Type: Type build-in → hold → split-apart product reveal

Technical Details:
- Title scale: 0.9 → 1.0 with spring({damping: 140})
- Letter stagger: 2-frame delay per character using interpolate() on opacity + translateY
- Split animation: single box scales/duplicates into two boxes moving apart on X axis, frames 60–150, Easing.out(Easing.cubic)
- Node/brain icon: pulsing glow via animated boxShadow radius, looping sine wave

Animation Code Pattern:
```
const titleProgress = spring({frame, fps, config: {damping: 140}});
const splitX = interpolate(frame, [60, 150], [0, 260], {extrapolateRight: 'clamp'});
const glow = 20 + Math.sin(frame / 10) * 8;
```

Hold: frames 2400–2700

VO cue (for reference, not rendered as audio):
"Welcome to the agent-first era. Google Antigravity 2.0 has evolved. It's no longer just an AI assistant bolted onto a text editor — it's a completely standalone desktop application powered by Gemini 3.7 Flash, designed to orchestrate autonomous AI agents."

==== SCENE 2: DOWNLOAD & SETUP (Frames 2700–5400 | 1:30–3:00) ====

Background:
Lighter navy panel slides up over the dark background, glassmorphism card style, subtle grid texture.

Main Elements:
Placeholder browser chrome showing "antigravity.google". Zoom transition into a placeholder macOS/Windows dock row showing two icons: "Antigravity 2.0" (white rounded square) and "Antigravity IDE" (black grid icon). Then a simplified OAuth/login card animates in, followed by a "New Project → select folder" flow shown as three sequential glass cards.

Animation Type: Panel slide-up → icon zoom → sequential step cards

Technical Details:
- Panel entrance: translateY spring({damping: 150}) from 100% to 0
- Dock icons: scale-in staggered by 6 frames each, subtle bounce (damping: 110)
- Step cards: horizontal carousel, each card interpolate() opacity 0→1 over 20 frames, hold 60 frames, exit -1

Animation Code Pattern:
```
const panelY = interpolate(spring({frame: frame-2700, fps, config:{damping:150}}), [0,1], [100,0]);
const iconScale = spring({frame: frame - (2700 + i*6), fps, config: {damping: 110}});
```

Hold: frames 5100–5400

VO cue:
"To get it, download it from the official site, or let your existing Antigravity IDE auto-update. You'll now have two distinct apps. Boot up version 2.0, authenticate with Google, and set up your workspace by simply selecting your project folders."

==== SCENE 3: CORE FEATURES BREAKDOWN (Frames 5400–11700 | 3:00–6:30) ====

Background:
Full dark navy canvas — this is the "diagram" section, keep it clean and infographic-like.

Main Elements (4 sequential beats, ~90 frames each with holds):
1. Dynamic Subagents — a central glowing node ("Main Agent") spawns 3–5 smaller nodes along curved bezier paths, each smaller node pulses as it "processes" a labeled code block.
2. Asynchronous Task Management — a horizontal task-queue graphic with cards moving through "Queued → Running → Done" states independently, without blocking each other.
3. Scheduled Tasks — a calendar icon morphs into a gear/clock icon (cron symbol), small ticking animation.
4. Live Voice Transcription — a microphone icon with animated soundwave bars that morph directly into scrolling text characters.

Animation Type: Sequential diagram builds, one concept fully resolves before the next begins

Technical Details:
- Node spawn: main node at center (960,540 in a 1920x1080 comp); subagent positions computed via angle offsets
- Use interpolate() with extrapolateRight:'clamp' for all path-draw (strokeDashoffset) animations
- Each beat gets a lower-third label bar sliding in from the left, spring({damping: 150})

Animation Code Pattern:
```
const subagents = Array.from({length: 4}).map((_, i) => {
  const angle = (i * Math.PI * 2) / 4 - Math.PI/2;
  const dist = interpolate(frame - beatStart, [0, 40], [0, 220], {extrapolateRight:'clamp'});
  return { x: 960 + Math.cos(angle)*dist, y: 540 + Math.sin(angle)*dist };
});
```

Hold per beat: last 30 frames of each ~90-frame beat before crossfade to next

VO cue:
"Version 2.0 introduces powerful new features. Dynamic Subagents can now break off and handle sub-tasks in parallel without clogging your main context window. You also get Asynchronous Task Management, Cron-based Scheduled Tasks to automate agents, and Live Voice Transcription to prompt your agents simply by talking."

==== SCENE 4: UI, WORKFLOW & VERSION CONTROL (Frames 11700–16200 | 6:30–9:00) ====

Background:
Placeholder "screen recording" glass panel takes up ~80% of frame, dark chrome, subtle drop shadow, floating over the navy background.

Main Elements:
Inside the glass panel: a prompt input bar where placeholder text types out "/goal", cursor blinking. Camera (simulated via scale/translate on the panel) pans right to reveal a sidebar with a Git/VCS icon set (Agent Edits / Uncommitted / Branch labels as simple pill badges) and an embedded terminal strip at the bottom showing a `git status`-style placeholder text block.

Animation Type: Simulated UI walkthrough with camera pan/zoom

Technical Details:
- Typewriter effect on "/goal" text: reveal N characters per frame via interpolate() on string length
- Panel "camera pan": translateX + slight scale on the whole glass panel, Easing.inOut(Easing.cubic), 60 frames
- Sidebar badges: stagger fade/slide-in, damping: 150
- Terminal text lines: fade in top-to-bottom, 4-frame stagger per line

Animation Code Pattern:
```
const typedChars = Math.floor(interpolate(frame - beatStart, [0, 30], [0, 5], {extrapolateRight:'clamp'}));
const panPan = interpolate(frame - panStart, [0, 60], [0, -120], {extrapolateRight:'clamp'});
```

Hold: frames 15900–16200

VO cue:
"Using it is simple. Just talk to your agent. Use slash commands like /goal to let it run autonomously, or /grill-me so it asks you clarifying questions first. When it's done, review everything in the native Git version control panel and run your tests in the embedded terminal — all without ever switching apps."

==== SCENE 5: THE CLI & OUTRO (Frames 16200–18000 | 9:00–10:00) ====

Background:
Cut to solid near-black terminal background, single blinking cursor.

Main Elements:
Terminal placeholder typing the CLI invocation (render generic `antigravity` command text rather than an unverified alias), command executes, output lines stream in. Hard cut/transition to the Antigravity 2.0 logo lockup centered on navy background, then standard end-card: "Subscribe" button graphic + channel handle placeholder + soft outro music sting cue (audio not rendered by Remotion, note as a cue).

Animation Type: Terminal type-in → logo reveal → end card

Technical Details:
- Terminal type-in: identical pattern to Scene 4's typewriter effect, monospace font
- Logo reveal: scale spring({damping:130}) + fade, glow pulse loop
- End card elements: staggered fade/slide, 10-frame offsets

Animation Code Pattern:
```
const logoScale = spring({frame: frame - 17700, fps, config: {damping: 130}});
```

Hold: frames 17700–18000 (end card)

VO cue:
"Prefer the terminal? The new Antigravity CLI brings this entire multi-agent architecture right to your command line. Antigravity 2.0 fundamentally changes how we build software. Download it today, test it out, and subscribe for more deep dives into Google's developer tools."

==== TECHNICAL SPECIFICATIONS ====

EASING FUNCTIONS TO USE:
- Entry animations: spring({damping: 140})
- Smooth transitions: Easing.inOut(Easing.cubic)
- Bounces (used sparingly, icons only): spring({damping: 110, mass: 0.6})
- Exits: Easing.in(Easing.cubic)

COLOR PALETTE (use exactly):
- Google Blue: #4285F4
- Space Navy (bg): #0B0E14
- Google Green: #34A853
- Google Yellow: #FBBC05
- Google Red: #EA4335
- Off-White (text): #F5F7FA

TYPOGRAPHY:
- Hero: 96px, 800 weight, tracking: -0.02em
- Large: 56px, 700 weight, tracking: -0.01em
- Medium: 36px, 600 weight, tracking: 0
- Body / captions: 22px, 500 weight, tracking: 0.01em
- Terminal/code: monospace (e.g. "JetBrains Mono"), 26px, 400 weight

ANIMATION PATTERNS TO USE:
- Node/graph spawn-and-connect pattern for all "agent" concepts (Scenes 1 & 3)
- Glass-panel screen-recording placeholder pattern for all "product UI" beats (Scenes 2 & 4)
- Typewriter reveal pattern for anything representing a prompt or terminal command (Scenes 4 & 5)

VISUAL EFFECTS:
- Ambient glow: soft animated boxShadow / blur behind all "agent" nodes, pulsing 6–10s loop
- Glass panel: backdrop-blur + 8% white border + soft drop shadow for all screen-recording inserts
- Grid texture: 2% opacity animated grid drifting slowly in backgrounds, never distracting

DELIVERABLE CODE MUST INCLUDE:
1. Root composition file registering the 18000-frame, 30fps, 1920x1080 comp
2. Five section components (Scene1…Scene5) each self-contained with local frame offsets
3. Reusable <GlassPanel> component for screen-recording placeholders
4. Reusable <AgentNode> component for the node/graph motif
5. Reusable <Typewriter text={} startFrame={} /> component
6. Centralized theme/constants file exporting the color palette and type scale
7. Caption/lower-third component driven by the VO cue text per scene
8. All spring()/interpolate() calls parameterized via the constants above (no magic numbers)
9. A comments block per scene mapping frame ranges back to this brief
10. package.json / remotion.config with h264 render settings

RENDER COMMAND:
npx remotion render output.mp4 --codec h264 --crf 18

Save the output here /home/admin1/suman/ebook/ytvideos/public/assets