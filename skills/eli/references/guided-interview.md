# Guided interview

Use this route for `/eli guide [topic]`, `ELI guide [topic]`, or an explicit request for help choosing an explainer's audience, approach, and appearance. This is a conversation, not a form to build or a new application. The guide replaces ordinary setup; do not run both menus.

**Use the native question picker first**, following the question-interface reference linked from SKILL.md. The menus below define the choices; their A–D/number layouts are text fallbacks. Adapt question counts, option ordering, custom input, and long menus to the exposed tool. Do not copy a five-option menu into a tool capped at three or add D when the UI already supplies free text. Keep every choice reachable through short grouped follow-ups.

## Keep the interview quick

- Resolve the topic from the current conversation or supplied topic. If missing, ask what to explain first. Offer actual current referents when available; otherwise use one free-text question. Do not recommend an invented subject.
- Usually use three or four small rounds, at most two questions per reply. Skip questions already answered and omit whole rounds that do not apply. Show only the current round, with a short label such as "Audience" or "Presentation". Do not promise a fixed turn count.
- For text fallback, number questions consecutively as they are first shown. Keep each question's number and option mapping on follow-up. Give an example such as "1A, 2:4" using the actual displayed labels. For native forms, use their returned question/option mappings without asking the user to repeat selections. Accept ordinary language too.
- Mark a grounded recommendation and give a few words of reason; do not recommend personal facts such as someone's age or identity without evidence. Use the native custom entry, or the core's lettered choices and D in text fallback.
- Collect a working brief internally: topic/source, recipient, age or reading preference, subject familiarity, purpose/mode, format, depth, visual direction, and motion. Record user choices separately from delegated defaults. No file or template is required for this brief.
- A choice is answered once. Ask a narrow follow-up only for a consequential ambiguity. For D alone, request the custom answer for that field. Do not reset the interview after a correction or require personal information that is unnecessary to the explanation.
- "Use your recommendations", "you choose the rest", or "build it" ends preference gathering. Preserve explicit choices; use the defaults below for the rest. Still clarify a missing topic, inaccessible essential source, or ambiguity that would change what gets explained.

## Round 1: Audience and age

Ask who receives the explanation, not just who is preparing it. Tailor up to three recipient choices to the topic: for example **A. Me / B. A colleague or team / C. A customer / D. Someone else — describe them**. Reuse a stated recipient instead of asking again.

Ask the preferred age/language level separately when unknown. Offer:

- **1.** Around five — very concrete language
- **2.** Around ten — simple examples with a little more detail
- **3.** Around fifteen — accessible language with useful terms
- **4.** Adult — plain language without talking down
- **D.** My own age, education level, or reading preference

These are explanation settings, not claims about a real person's age. Accept "adult, explain very simply", "college level", or "for my ten-year-old" naturally. ELI5 already selects the simplest language; ask age only if the actual recipient's age would change the result. Do not equate fifth grade with age five, education with expertise, or an adult beginner with a child. A "young adult" or "mature adult" preference remains available through natural language or D.

## Round 2: Background and purpose

For subject familiarity, offer **A. New to this / B. Know the basics / C. Comfortable with the topic; need depth / D. My own answer**. Reuse demonstrated or stated background. Avoid an arbitrary recommendation when familiarity is unknown.

For purpose, keep all five modes available; the core's stable numbering applies to text fallback:

- **1.** Like I'm five — the simplest useful explanation
- **2.** Make it click — understand how it works and why it matters
- **3.** Help me explain it — prepare to explain it to someone else
- **4.** Help me use it — apply it to a practical situation
- **5.** Give me the big picture — see the main parts and relationships
- **D.** My own goal or a combination

Recommend 2 for general understanding, 3 for a stated communication task, 4 for a practical task, or 5 for orientation. Preserve an already clear goal. If the user chooses an age-five reading level and Make it click, combine them: simplest language, mechanism, and a useful changed example. Do not force age to determine mode.

## Round 3: Presentation and depth

Offer the three formats; keep this standard mapping in text fallback:

- **A.** Text in chat
- **B.** Single-page HTML or artifact — a visual explanation to read and share
- **C.** Interactive explainer — learn by stepping through or changing something
- **D.** My own format

Recommend B when a polished visual overview helps, C when an action can reveal a relationship, and A for a quick conversational answer. A guided interview itself does not select a visual format. Do not promise a native artifact workspace or public URL unless the host supports it.

For depth, offer **A. Quick overview, about 1–2 minutes / B. Standard explanation, about 3–5 minutes / C. Deeper walkthrough, about 5–10 minutes / D. My own length**. These are reader-time targets, not production-time promises. Recommend B unless the user has asked for brevity or depth. Keep only useful examples; do not pad output to hit a duration. An existing length constraint settles this question.

If the user chooses text, finish after resolving the teaching brief. Do not ask about page styling, SVGs, or animation.

## Round 4: Look and motion

For visual output, offer these style choices unless already settled:

- **A.** Academy illustration **(Recommended)** — neutral light surfaces, large graphite SVG scenes, restrained cream and terracotta emphasis
- **B.** ElevenLabs editorial — light, spacious, strong typography, large visuals with selective image-based color
- **C.** Minimal light — crisp monochrome diagrams and the least decoration
- **D.** My own style, brand, or visual reference

All three presets are light. Recommend a different preset if the content or supplied brand calls for it. Treat A/B as visual directions, not permission to add official logos or claim exact brand compliance. Prefer the user's real assets and current project rules when present. A custom dark treatment is possible only when explicitly requested; do not insert a dark-mode toggle by default.

For motion, offer:

- **A.** Gentle SVG reveals — draw connections or reveal parts in the teaching order
- **B.** Learner-controlled steps — advance or change an input to see what happens
- **C.** Static SVG composition — everything readable without motion
- **D.** My own treatment

Recommend A for a sequence, B for an interactive explainer, or C when a static spatial relationship explains it better. Large SVG artwork is the baseline for all three; "static" does not mean small icons. Match the chosen format: B can be a lightweight component in one HTML page. If C follows an interactive format choice, keep useful controls with instant state changes and no animation. Honor reduced motion regardless of the preference.

## Finish and create

Summarize the resolved brief in one sentence, for example: "I'll make a three-to-five-minute interactive explainer for an adult beginner, using Make it click, a light Academy look, and large SVG scenes you can step through." Then create it; do not add a final "shall I proceed?" gate. The interview answers already authorize the requested explainer, subject to normal host permissions.

For delegated preferences, use adult plain language, beginner-friendly treatment, Make it click, standard depth, Academy illustration, and purposeful gentle reveals or a static composition. Preserve the actual recipient if known; otherwise address the user without asserting a personal age or expertise. Use chat when format was not supplied and there is no visual intent; an explicit visual intent supports a single-page HTML default, and an explicit interactive intent supports a walkthrough. State material defaults briefly.

Use the visual-delivery reference linked from SKILL.md for implementation and review. Check the result against the brief: age changes language, background changes assumed knowledge, purpose changes teaching, format changes the experience, depth changes scope, and visual choices change the composition and motion. Do not merely collect answers and deliver the same generic page every time.
