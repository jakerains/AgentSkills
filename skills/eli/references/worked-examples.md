# Worked examples

These are complete short examples and annotated choices, not required templates. All policies, prices, services, organizations, and numerical scenarios in this file are **fictional teaching fixtures**. Their rule labels are local references to the fixture text, not external citations. Never transfer their details into a real explanation as product facts.

## Contents

- [Bare invocation](#bare-invocation)
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

**Example response:**

> For the course checkpoint we're discussing, how would you like it explained?
>
> **Format:** Text in chat, visual page, or interactive walkthrough.
>
> **Approach:** Like I'm five, Make it click, Help me explain it, Help me use it, or Give me the big picture.
>
> **Audience:** You, a sales teammate, a stakeholder, engineering, or someone else. A reply like "visual, Make it click, for sales" is enough.

**Why this fits:** The referent is visible, format comes first, Like I'm five stays first among modes, and one reply settles the setup. This is not a universal menu to show before every explanation. A complete request skips it.

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

**Request:** "Help me explain fixture L to a sales teammate who doesn't know APIs. Keep it short."

**Example response:**

> **Ready-to-say version:** "This demo service accepts three requests in each ten-second window. A burst above that allowance gets rejected; it is not automatically saved for later. Finishing earlier requests doesn't restore the allowance before the next window starts." [L]
>
> For example, a customer sending four requests in the same window would have three accepted and one rejected under this rule. A request submitted in a new window can use that window's allowance. [L]
>
> Before describing a real product to a customer, verify its actual limit, how it counts requests, and what happens above the limit. This fictional example establishes none of those details for a real service.

**Why this fits:** The actual recipient is the sales teammate, not an assumed customer. The explanation supports accurate communication without creating a capacity promise, retry guarantee, or customer pitch that was not requested.

## The same topic for an engineer new to it

**Request:** "Make fixture L click for an engineer who hasn't worked on rate limiting."

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

**Request:** "Help me explain the new expense policy to my team."

**Example response:**

> **Ready-to-say version:** "Starting November 1, travel meals are reimbursable up to $35 per person per day. Keep the receipt for every claim and submit it within 14 days of the purchase." [P1-P3]
>
> Two examples: a $28 eligible meal is within the daily cap; a $42 meal would have at most $35 covered if it were the person's only travel meal that day. The policy sets a daily cap, not a separate allowance for every meal. Both claims still need a receipt and timely submission. [P1-P3]
>
> I can explain these rules, but the old policy is not supplied, so I can't say which requirements changed. The excerpt also doesn't explain exceptions or how to replace a missing receipt. [P]

**Why this fits:** It preserves the daily basis, effective date, and receipt rule without assuming those rules were newly introduced. The scenario illustrates a condition rather than substituting industry practice for the actual policy.

## A metric with a changed denominator

**Fixture M:** Period A: 80 completed applications out of 100 started. Period B: 90 completed out of 150 started. These fictional periods use the same supplied definition of completion; no information about population mix or operational changes is supplied.

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

**Request:** "Explain why this happened in plain English."

**Example response:**

> The supplied records establish that the service stopped at 14:05 and resumed at 14:20, a 15-minute interruption. They do not establish why it happened: the notice says the cause is still under investigation. [E; duration calculated from the timestamps]
>
> A deployment appears in the timeline five minutes earlier, but that timing alone doesn't prove it caused the outage. For now, it belongs in the sequence of events, not in a confirmed explanation of the cause. [E]

**Why this fits:** The answer is useful without inventing a mechanism or motive. A timeline visual should not draw a causal arrow from deployment to outage as though the investigation had established it.

## A practical explanation plus a requested draft

**Fixture Q:** A community room is reserved only after the coordinator confirms the requested date. Q1: Submit the date, start and end times, and expected attendance. Q2: A submission is a request, not a confirmed reservation. Q3: No response-time commitment is supplied.

**Request:** "Help me use this process, then draft a request for October 10, 2 to 4 PM, for 12 people."

**Example response:**

> Submit the date, start and end times, and expected attendance so the coordinator has the information required by the process. Sending that request does not reserve the room; wait for confirmation before treating the booking as final. The policy does not say how quickly confirmation arrives. [Q1-Q3]
>
> **Draft**
>
> Hi, I'd like to request the community room for October 10 from 2:00 to 4:00 PM for 12 people. Please confirm whether that slot is available and the reservation is approved. Thank you.

**Why this fits:** It explains the important action and completes the explicitly requested draft. It does not send the message or claim a booking, and it does not invent a deadline for the coordinator. Where the actual context requires a year or time zone to make a real booking, resolve that before the external action rather than silently inventing it.
