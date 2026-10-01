# Worked examples

These are complete short examples and annotated choices, not required templates. All policies, prices, services, organizations, and numerical scenarios in this file are **fictional teaching fixtures**. Their rule labels are local references to the fixture text, not external citations. Never transfer their details into a real explanation as product facts.

**The chat menus below illustrate text fallback.** When the host exposes a permitted native question picker, ask the same unresolved choices through it, adapting option counts, grouping, recommendations, and custom input. Do not copy these menus into chat instead of using an available picker. See the question-interface reference linked directly from SKILL.md for platform mappings and review scenarios. Native selected IDs/labels settle choices without requiring the user to repeat these reply codes.

## Contents

- [Bare invocation](#bare-invocation)
- [A named topic still needs setup](#a-named-topic-still-needs-setup)
- [ELI5 with an audience still needs a format](#eli5-with-an-audience-still-needs-a-format)
- [A partial answer preserves earlier choices](#a-partial-answer-preserves-earlier-choices)
- [Custom and ambiguous selections](#custom-and-ambiguous-selections)
- [A later clarification uses the same convention](#a-later-clarification-uses-the-same-convention)
- [A guided start becomes a visual brief](#a-guided-start-becomes-a-visual-brief)
- [Guide shortcuts and completed choices](#guide-shortcuts-and-completed-choices)
- [Explicit delegation skips setup](#explicit-delegation-skips-setup)
- [A short answer stays short](#a-short-answer-stays-short)
- [Make it click for a nontechnical adult](#make-it-click-for-a-nontechnical-adult)
- [The same topic for a sales teammate](#the-same-topic-for-a-sales-teammate)
- [The same topic for an engineer new to it](#the-same-topic-for-an-engineer-new-to-it)
- [A proposal without a historical baseline](#a-proposal-without-a-historical-baseline)
- [A new policy without an old policy](#a-new-policy-without-an-old-policy)
- [A metric with a changed denominator](#a-metric-with-a-changed-denominator)
- [An event without an established cause](#an-event-without-an-established-cause)
- [A practical explanation plus a requested draft](#a-practical-explanation-plus-a-requested-draft)

## Bare invocation

**Context:** The conversation is about a learner checkpoint in a course. No format, audience, or mode has been selected. The user says: "ELI."

**First response:** Use the labeled three-question example in section 1 of SKILL.md: format A–C plus D, all five approaches lettered A–E plus F, and audience A–C plus D. Recommend the visual page and Make it click for the checkpoint's role in the learner route; leave audience to the user because it is unknown.

**User reply:** "b, b, a"

**Next action:** Create a single-page visual explanation using Make it click for the user. The equivalent reply "1B, 2B, 3A" resolves the same choices. Do not ask for confirmation. The number identifies the question; the letter selects its answer.

**Why this fits:** The referent is visible, format comes first, and all choices can be supplied in one short reply. Wait after presenting the menu; do not append the explanation. If no current topic exists, ask what to explain without inventing a topic or a recommendation about it.

## A named topic still needs setup

**Request:** "ELI caching quickly."

**Example first response:**

> For caching, I'll keep it brief:
>
> **1. Format**
>
> - **A.** Text in chat **(Recommended)** — quickest way to get the core idea
> - **B.** Single-page HTML/artifact
> - **C.** Interactive explainer
> - **D.** My own answer
>
> **2. Approach**
>
> - **A.** Like I'm five
> - **B.** Make it click **(Recommended)** — explain what caching does and why
> - **C.** Help me explain it
> - **D.** Help me use it
> - **E.** Give me the big picture
> - **F.** My own answer
>
> **3. Audience** — I need your choice here.
>
> - **A.** You
> - **B.** A nontechnical teammate
> - **C.** An engineer new to caching
> - **D.** Someone else — describe them
>
> Reply like **"A, B, A"** or **"1A, 2B, 3D: my manager"**.

**Why this fits:** The topic and pace are known, but format, approach, and recipient are not. "Quickly" keeps setup concise; it does not select chat. Wait for the reply rather than supplying a brief explanation followed by an offer to make a page.

## ELI5 with an audience still needs a format

**Request:** "ELI5 caching for sales."

**Example first response:**

> I'll use Like I'm five with adult-appropriate language for sales. Choose a format:
>
> - **A.** Text in chat **(Recommended)** — an easy version to use in conversation
> - **B.** Single-page HTML/artifact
> - **C.** Interactive explainer
> - **D.** My own answer
>
> Reply **A**, **B**, **C**, or **D: your answer**.

**User reply:** "b"

**Next action:** Create the visual explanation using the visual-delivery reference. Use an available native artifact workspace or a self-contained HTML file. Do not ask for the mode or audience again, and do not substitute a chat-only explanation for the selected artifact.

**Why this fits:** ELI5 settles the approach and sales settles the audience. The first response asks only for the missing format; the reply completes setup without another confirmation.

## A partial answer preserves earlier choices

**Context:** The topic is caching. The first response used the three numbered questions above.

**User reply:** "1C, 3A"

**Example next response:**

> An interactive explainer of caching for you. Just **2. Approach** remains:
>
> - **A.** Like I'm five
> - **B.** Make it click **(Recommended)** — connect the controls to how caching works
> - **C.** Help me explain it
> - **D.** Help me use it
> - **E.** Give me the big picture
> - **F.** My own answer
>
> Reply with a letter or **F: your answer**.

**User reply:** "B"

**Next action:** Build the walkthrough. Use general examples unless relevant background is known; do not require another audience form. Keep the chosen topic, audience, and format for follow-up edits.

**Why this fits:** Only the unresolved approach is requested. A recommendation is visible and the user can accept it naturally; it does not become a silent default before they reply.

## Custom and ambiguous selections

**Context:** The three-question caching setup above is awaiting a reply.

| Reply | Next action |
|---|---|
| "1B, 2D, 3D: my spouse, who is new to this" | Build the HTML page in Help me use it mode for the stated recipient. D means Help me use it in question 2 and a custom recipient in question 3; use each displayed mapping. |
| "1B, 2B, 3D" | Preserve HTML and Make it click. Ask only who the custom audience is; a free-text answer is now necessary. |
| "B" | Ask whether B means format B (HTML), approach B (Make it click), or audience B (nontechnical teammate), with labeled choices and D for a different answer. Do not choose either silently. |
| "Use your recommendations, for me" | Use chat and Make it click from this menu's recommendations, and the user as audience. Do not ask again. |
| "HTML, help me use it, for my team" | Accept the natural-language choices without requiring codes. |

**Why this fits:** Labels make replies shorter without becoming a rigid command syntax. Unambiguous choices stand; only unresolved meaning prompts a follow-up. Preserve the original mappings when referring back to them.

## A later clarification uses the same convention

**Context:** The user chose chat and received a conceptual explanation of a rule. They now ask, "Help me choose a better way to understand it."

**Example response:**

> Which route would help most?
>
> - **A.** A worked example **(Recommended)** — follow one case through the rule
> - **B.** An analogy — connect it to something familiar
> - **C.** A shorter overview — focus on the main idea
> - **D.** My own answer
>
> Reply with a letter, or tell me what you have in mind.

**User reply:** "A"

**Next action:** Give the worked example in the already-selected chat format. Do not restart topic, audience, or format setup.

**Why this fits:** Later clarification uses the same labels, grounded recommendation, and custom-answer route. It does not add a questionnaire to an already clear revision request.

## A guided start becomes a visual brief

**Request:** "/eli guide caching"

**Example first response:**

> Let's set up your caching explainer, starting with the audience.
>
> **1. Who is it for?**
>
> - **A.** You
> - **B.** A colleague or team
> - **C.** A customer
> - **D.** Someone else — describe them
>
> **2. What age/language level should I aim for?**
>
> - **A.** Around five
> - **B.** Around ten
> - **C.** Around fifteen
> - **D.** Adult plain language
> - **E.** My own age or reading preference
>
> I need your choices for these. You can reply **"1A, 2D"**.

**Continuation:** Present only the current round's options, using the guided-interview reference linked from SKILL.md. The following is a trace of the exchange, not one large menu to show upfront.

| User reply | Next action |
|---|---|
| "1A, 2D" | Keep recipient = user and language = adult. Ask question 3 about familiarity and question 4 about purpose; recommend Make it click for general understanding. |
| "3A, 4B" | Keep beginner-friendly treatment and Make it click. Ask question 5 about format and question 6 about depth. Recommend an interactive explanation if the planned cache example gives the learner a meaningful input to change, and standard depth. |
| "5C, 6B" | The teaching brief is complete. Summarize it in one sentence and build with the standard light design, a large SVG scene explaining cache hits/misses, and useful step controls. Ground the actual caching model or label it as a simplified teaching example. Do not ask about style or motion or request another confirmation. |

**Why this fits:** The user makes short selections through three small rounds. Each teaching choice changes the eventual explainer; the standard design applies automatically. Age affects wording, familiarity affects prerequisites, and the large SVG shows the relationship rather than acting as decoration. The request does not create a native slash command or authorize publishing.

## Guide shortcuts and completed choices

| Request or reply | Expected behavior |
|---|---|
| "ELI guide" with no current topic | Ask what to explain first. Do not invent topical choices or assume the subject is the ELI skill. |
| "ELI guide caching for sales, adult beginners, Make it click, HTML, three minutes" | The complete teaching brief is supplied. Build immediately with the standard light design; do not ask any style or motion questions. |
| "ELI guide the supplied rule, for adult beginners, text in chat, Make it click, two paragraphs" | The brief is complete. Explain in chat without further setup. |
| "E: for a ten-year-old who already codes" in the age menu | Preserve both age ten and coding experience; ask only for background relevant to the actual topic if still unknown. Do not infer they are an absolute beginner. |
| "Use your recommendations, for adult beginners" during an interview for visual output | Fill remaining preferences with the relevant recommendations/defaults, state the resulting brief, and create the visual. Preserve earlier source, format, and audience choices. |
| "Build it, no more questions, HTML" | Resolve remaining preferences with the standard light design, standard depth, and Make it click unless already chosen; build once the topic is clear. |
| "Make it interactive, but no animation" | Honor the volunteered requirement: keep useful controls and instant state changes without motion. Do not ask the user to select a motion preset. |
| "Use the dark theme from my supplied project guidelines" | Honor the explicit requirement without a design questionnaire. The standard light design does not override a direct user instruction. |
| "Make it click for adult beginners in HTML, no interview" | Use the ordinary complete-request route and light visual defaults. Do not force guide mode or add style questions. |

**Why this fits:** Guide mode clarifies the teaching brief while applying the standard design automatically. Short requests and explicit delegation still work. No companion skill, logo package, proprietary font, or external animation library is required to produce the default standalone result.

## Explicit delegation skips setup

**Request:** "ELI the reservation rule below. Choose the approach and format for me; no questions."

**Next action:** Explain the supplied rule directly using Make it click, text, and a nontechnical adult audience. Preserve any explicit choice if supplied, such as "no questions, make an HTML page."

**Why this fits:** The user explicitly delegates the unresolved choices. A missing topic would still need clarification; delegation does not supply the subject.

## A short answer stays short

**Fixture R:** A room rule says: "A reservation holds one named seat until 7:00; if the guest has not arrived by then, the seat is available to others."

**Request:** "ELI5 that reservation rule in two sentences."

**Example response:**

> Booking the seat keeps it for you until 7:00. If you have not arrived by then, someone else can have it.

**Why this fits:** Two sentences, no baby talk, no menu, no extra analogy, and the condition is preserved. The skill does not need its other references for this request.

## Make it click for a nontechnical adult

**Fixture L:** A toy service accepts at most three requests in each fixed ten-second window starting at time zero. Extra requests in the same window are rejected, not queued. Finishing a request does not restore the allowance. The demo does not automatically retry rejected requests.

**Request:** "Make this click for me. I'm not technical. Text please."

**Example response:**

> A rate limit is a rule about how many requests a service will accept during a particular period. In this fictional service, the rule is three requests per ten-second window. [L]
>
> Imagine a counter with three admission tickets available for each ten-second round. Each accepted request takes a ticket. Once all three are used, another request is turned away until a new round starts. It is not placed in a waiting line. [L]
>
> In the actual rule, the tickets represent the allowance and the round represents a fixed time window. The service is counting accepted requests in that window, not how many are still being worked on. Finishing one does not give a ticket back. [L]
>
> Suppose three requests have already been accepted in the current window. Even if they all finish immediately, a fourth request in that same window is rejected. When the next window begins, three requests are available again. The rejected request is not automatically sent again. [L]
>
> **The idea to keep:** a limit on starts during a period is different from a limit on jobs running at once.

**Why this fits:** The analogy maps to the actual rule, avoids a false queue model, and transfers to a case where work finishes quickly. Claims apply to the fixture, not to all API services. A user who knows the topic well would not need the entire analogy.

**Misleading alternative:** "A rate limit is a queue that slows requests down until the system can handle them."

**Problem:** That invents both queuing and a reason for the rule. Neither follows from this fixture.

## The same topic for a sales teammate

**Request:** "Help me explain fixture L to a sales teammate who doesn't know APIs. In chat, and keep it short."

**Example response:**

> **Ready-to-say version:** "This demo service accepts three requests in each ten-second window. A burst above that allowance gets rejected; it is not automatically saved for later. Finishing earlier requests doesn't restore the allowance before the next window starts." [L]
>
> For example, a customer sending four requests in the same window would have three accepted and one rejected under this rule. A request submitted in a new window can use that window's allowance. [L]
>
> Before describing a real product to a customer, verify its actual limit, how it counts requests, and what happens above the limit. This fictional example establishes none of those details for a real service.

**Why this fits:** The actual recipient is the sales teammate, not an assumed customer. The explanation supports accurate communication without creating a capacity promise, retry guarantee, or customer pitch that was not requested.

## The same topic for an engineer new to it

**Request:** "Make fixture L click for an engineer who hasn't worked on rate limiting. Text please."

**Example response:**

> This fixture uses a **fixed-window admission limit**. Divide time into windows [0, 10), [10, 20), and so on. Each window has an accepted-request counter capped at three; another request in that same window is rejected. Completion does not decrement this counter because it tracks admissions, not active work. [L]
>
> The boundary matters. Three requests just before a window ends and three just after the next begins can all be accepted under this rule, even though the six starts are close together. That is a consequence of counting separate fixed windows, not an extra allowance within either window. [L]
>
> **Keep separate:** an admission counter answers "how many starts in this window?"; an active-work count answers "how many are running now?" A limit on the first does not define a limit on the second.

**Why this fits:** Useful terminology stays in place and a boundary example supplies depth. It does not invent an implementation, a distributed-store guarantee, or actual product behavior. The explanation is technical without assuming previous topic expertise.

## A proposal without a historical baseline

**Fixture D:** The supplied proposed order form states: 12-month term; $1,200 per month; 10,000 events included per month; $0.05 for each event above that monthly allowance. No current agreement, usage forecast, tax terms, or unused-allowance rule is supplied.

**Request:** "Make this renewal deal click for my manager. Text only."

**Example response:**

> The proposal is a 12-month agreement at $1,200 per month, with 10,000 events included each month. Events above that monthly allowance cost another $0.05 each. Those are the proposed terms in the supplied order form. [D]
>
> As a **hypothetical illustration, not a usage forecast**, a month with 12,500 events would have 2,500 events above the allowance. The listed charges would be $1,200 + (2,500 x $0.05) = **$1,325**, before any other charges not established by this excerpt. [Calculated from D]
>
> I don't have the current agreement, so I can't establish whether this changes the price, allowance, or overage terms. The excerpt also does not establish taxes or whether unused allowance carries over. [D]
>
> **What matters for the manager:** understand the monthly commitment and the variable charge above the allowance; obtain the current terms before describing this as an increase, saving, or better deal.

**Why this fits:** It explains the available proposal without blocking on missing history, labels arithmetic and hypothetical usage, and identifies unknown terms rather than inventing them. It does not turn the explanation into a full commercial recommendation.

## A new policy without an old policy

**Fixture P:** The supplied policy is effective November 1. P1: Travel meals are reimbursable up to $35 per person per day. P2: A receipt is required for every claim. P3: Claims must be submitted within 14 days of the purchase. No prior policy or exception process is supplied.

**Request:** "Help me explain the new expense policy to my team. Text in chat."

**Example response:**

> **Ready-to-say version:** "Starting November 1, travel meals are reimbursable up to $35 per person per day. Keep the receipt for every claim and submit it within 14 days of the purchase." [P1-P3]
>
> Two examples: a $28 eligible meal is within the daily cap; a $42 meal would have at most $35 covered if it were the person's only travel meal that day. The policy sets a daily cap, not a separate allowance for every meal. Both claims still need a receipt and timely submission. [P1-P3]
>
> I can explain these rules, but the old policy is not supplied, so I can't say which requirements changed. The excerpt also doesn't explain exceptions or how to replace a missing receipt. [P]

**Why this fits:** It preserves the daily basis, effective date, and receipt rule without assuming those rules were newly introduced. The scenario illustrates a condition rather than substituting industry practice for the actual policy.

## A metric with a changed denominator

**Fixture M:** Period A: 80 completed applications out of 100 started. Period B: 90 completed out of 150 started. These fictional periods use the same supplied definition of completion; no information about population mix or operational changes is supplied.

**Setup already resolved:** The user chose Make it click, text in chat, for themselves as a nontechnical reader.

**Request:** "What does this actually mean? More people completed, but the rate went down."

**Example response:**

> Both statements can be true because they answer different questions. Completions count finished applications; the completion rate compares finished applications with all starts. [M]
>
> Period A's rate is 80 / 100 = **80%**. Period B's rate is 90 / 150 = **60%**. So there were **10 more completions**, but the rate was **20 percentage points lower**, because the larger completion count was measured against a much larger number of starts. [Calculated from M]
>
> Think of 80 marked boxes among 100, then 90 marked boxes among 150: the marked count grows, but its share of the whole shrinks. These numbers do not establish why the share changed or whether a particular intervention caused it. [M]
>
> **Takeaway:** compare both the count and what it is being compared against before deciding what a rate means.

**Why this fits:** The arithmetic is transparent, the unit of change is correct, and the explanation stops short of a causal claim. A visual version could use equally sized unit marks, not two full-width bars that hide the different totals.

## An event without an established cause

**Fixture E:** A notice says service stopped at 14:05 and resumed at 14:20. It says the cause is under investigation. A separate supplied timeline records a deployment at 14:00, without connecting it to the outage.

**Request:** "Explain why this happened for me in plain English, here in chat."

**Example response:**

> The supplied records establish that the service stopped at 14:05 and resumed at 14:20, a 15-minute interruption. They do not establish why it happened: the notice says the cause is still under investigation. [E; duration calculated from the timestamps]
>
> A deployment appears in the timeline five minutes earlier, but that timing alone doesn't prove it caused the outage. For now, it belongs in the sequence of events, not in a confirmed explanation of the cause. [E]

**Why this fits:** The answer is useful without inventing a mechanism or motive. A timeline visual should not draw a causal arrow from deployment to outage as though the investigation had established it.

## A practical explanation plus a requested draft

**Fixture Q:** A community room is reserved only after the coordinator confirms the requested date. Q1: Submit the date, start and end times, and expected attendance. Q2: A submission is a request, not a confirmed reservation. Q3: No response-time commitment is supplied.

**Request:** "Here in chat, help me use this process, then draft a request for October 10, 2 to 4 PM, for 12 people."

**Example response:**

> Submit the date, start and end times, and expected attendance so the coordinator has the information required by the process. Sending that request does not reserve the room; wait for confirmation before treating the booking as final. The policy does not say how quickly confirmation arrives. [Q1-Q3]
>
> **Draft**
>
> Hi, I'd like to request the community room for October 10 from 2:00 to 4:00 PM for 12 people. Please confirm whether that slot is available and the reservation is approved. Thank you.

**Why this fits:** It explains the important action and completes the explicitly requested draft. It does not send the message or claim a booking, and it does not invent a deadline for the coordinator. Where the actual context requires a year or time zone to make a real booking, resolve that before the external action rather than silently inventing it.
