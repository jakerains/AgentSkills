# Guided interview

Use this route for `/eli guide [topic]`, `ELI guide [topic]`, or an explicit request for help choosing an explainer's audience, approach, format, and depth. This is a conversation, not a form to build or a new application. The guide replaces ordinary setup; do not run both menus. Apply the standard design automatically; do not include appearance or motion questions.

**Use the native question picker first**, following the question-interface reference linked from SKILL.md. The menus below define the choices; their lettered answer lists are text fallbacks. Adapt question counts, option ordering, custom input, and long menus to the exposed tool. Do not copy a five-option menu into a tool capped at three or add a custom option when the UI already supplies free text. Keep every choice reachable through short grouped follow-ups.

## Keep the interview quick

- Resolve the topic from the current conversation or supplied topic. If missing, ask what to explain first. Offer actual current referents when available; otherwise use one free-text question. Do not recommend an invented subject.
- Use the three teaching rounds below, at most two questions per reply. Skip questions already answered and omit whole rounds that do not apply. Host option limits may require shorter follow-ups. Show only the current round, with a short label such as "Audience" or "Presentation". Do not promise a fixed turn count.
- For text fallback, number questions consecutively as they are first shown. Keep each question's number and option mapping on follow-up. Give an example such as "1A, 2D" using the actual displayed labels. For native forms, use their returned question/option mappings without asking the user to repeat selections. Accept ordinary language too.
- Mark a grounded recommendation and give a few words of reason; do not recommend personal facts such as someone's age or identity without evidence. Use the native custom entry, or the core's lettered choices with the next unused letter for custom answers in text fallback.
- Collect a working brief internally: topic/source, recipient, age or reading preference, subject familiarity, purpose/mode, format, and depth. Preserve any design requirements the user volunteers, but do not ask for them. Record user choices separately from delegated defaults. No file or template is required for this brief.
- A choice is answered once. Ask a narrow follow-up only for a consequential ambiguity. For the displayed custom letter alone, request the custom answer for that field. Do not reset the interview after a correction or require personal information that is unnecessary to the explanation.
- "Use your recommendations", "you choose the rest", or "build it" ends preference gathering. Preserve explicit choices; use the defaults below for the rest. Still clarify a missing topic, inaccessible essential source, or ambiguity that would change what gets explained.

## Round 1: Audience and age

Ask who receives the explanation, not just who is preparing it. Tailor up to three recipient choices to the topic: for example **A. Me / B. A colleague or team / C. A customer / D. Someone else — describe them**. Reuse a stated recipient instead of asking again.

Ask the preferred age/language level separately when unknown. Offer:

- **A.** Around five — very concrete language
- **B.** Around ten — simple examples with a little more detail
- **C.** Around fifteen — accessible language with useful terms
- **D.** Adult — plain language without talking down
- **E.** My own age, education level, or reading preference

These are explanation settings, not claims about a real person's age. Accept "adult, explain very simply", "college level", or "for my ten-year-old" naturally. ELI5 already selects the simplest language; ask age only if the actual recipient's age would change the result. Do not equate fifth grade with age five, education with expertise, or an adult beginner with a child. A "young adult" or "mature adult" preference remains available through natural language or E.

## Round 2: Background and purpose

For subject familiarity, offer **A. New to this / B. Know the basics / C. Comfortable with the topic; need depth / D. My own answer**. Reuse demonstrated or stated background. Avoid an arbitrary recommendation when familiarity is unknown.

For purpose, keep all five modes available; the core's stable A–E lettering applies to text fallback:

- **A.** Like I'm five — the simplest useful explanation
- **B.** Make it click — understand how it works and why it matters
- **C.** Help me explain it — prepare to explain it to someone else
- **D.** Help me use it — apply it to a practical situation
- **E.** Give me the big picture — see the main parts and relationships
- **F.** My own goal or a combination

Recommend B for general understanding, C for a stated communication task, D for a practical task, or E for orientation. Preserve an already clear goal. If the user chooses an age-five reading level and Make it click, combine them: simplest language, mechanism, and a useful changed example. Do not force age to determine mode.

## Round 3: Presentation and depth

Offer the three formats; keep this standard mapping in text fallback:

- **A.** Text in chat
- **B.** Single-page HTML or artifact — a visual explanation to read and share
- **C.** Interactive explainer — learn by stepping through or changing something
- **D.** My own format

Recommend B when a polished visual overview helps, C when an action can reveal a relationship, and A for a quick conversational answer. A guided interview itself does not select a visual format. Do not promise a native artifact workspace or public URL unless the host supports it.

For depth, offer **A. Quick overview, about 1–2 minutes / B. Standard explanation, about 3–5 minutes / C. Deeper walkthrough, about 5–10 minutes / D. My own length**. These are reader-time targets, not production-time promises. Recommend B unless the user has asked for brevity or depth. Keep only useful examples; do not pad output to hit a duration. An existing length constraint settles this question.

Once the teaching brief is resolved, finish the interview for every format. Do not add a design round, style picker, motion question, or visual approval gate. For a page or walkthrough, apply the standard light design and large explanatory SVGs. Choose static artwork, gentle reveals, or learner-controlled state changes according to what teaches the concept best, and honor reduced motion.

## Finish and create

Summarize the resolved brief in one sentence, for example: "I'll make a three-to-five-minute interactive explainer for an adult beginner, using Make it click and large SVG scenes you can step through." Then create it; do not add a final "shall I proceed?" gate. The interview answers already authorize the requested explainer, subject to normal host permissions.

For delegated preferences, use adult plain language, beginner-friendly treatment, Make it click, and standard depth. Preserve the actual recipient if known; otherwise address the user without asserting a personal age or expertise. Use chat when format was not supplied and there is no visual intent; an explicit visual intent supports a single-page HTML default, and an explicit interactive intent supports a walkthrough. State material defaults briefly. Visual output always receives the standard design unless the user has explicitly supplied a different requirement.

Use the visual-delivery reference linked from SKILL.md for implementation and review. Check the result against the brief: age changes language, background changes assumed knowledge, purpose changes teaching, format changes the experience, and depth changes scope. Keep the standard design consistent while adapting the actual diagrams, examples, and controls to the subject.
