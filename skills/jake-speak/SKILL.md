---
name: jake-speak
description: Re-explain technical subjects, complicated situations, large amounts of information, decisions, findings, and work status to Jake in clear, simple language, and put any choice in front of him with the AskUserQuestion tool with a recommended pick and the reason for it. Use when Jake types /jake-speak, says "Jake Speak," asks "what does this mean?", says "explain it simple" or "explain it dumb", wants a plain-English or high-level explanation, says an explanation did not land, or needs choices and their consequences explained before deciding. Also use proactively when an answer to Jake would otherwise be jargon-heavy or would end by asking him to choose between technical options. Give enough context to understand the whole situation, preserve important facts and risks, and remove unnecessary technical plumbing.
---

# Jake Speak

Re-pitch the subject so Jake can understand what is happening, why it matters,
and what he needs to do with the information. Explain technical material, a
large amount of material, or both. Do not merely shorten the previous answer.

Make it simple. Jake is product-minded and sharp about goals and stakes, but he
is not an engineer and does not want to become one to answer your question. He
has asked for this directly: explain it like he knows nothing about the
technology. Simple is the goal, not a compromise.

Simple does not mean incomplete. Never let simplicity hide a fact, a risk, or a
number Jake needs in order to decide.

## Explain the Situation

- Start with the practical takeaway.
- Give enough context to answer: What are we talking about? How did we get
  here? Why does this matter now?
- Use short, direct sentences and common words. Follow the spirit of ASD-STE100
  Simplified Technical English without making the answer sound robotic.
- Use the project's established names for products, people, features, and
  concepts. If a relevant `CONTEXT.md` exists, use its language.
- Define unavoidable technical terms the first time they appear. Describe what
  each thing does in the situation, not only what it is called.
- Reach for an everyday analogy when one fits — a kitchen, a doorman, a filing
  cabinet. One good analogy beats three precise sentences.
- Preserve important names, numbers, status, evidence, risks, and constraints.
- Separate what is confirmed, what is likely, and what is still unknown.

For a large or messy subject, give the overall picture first. Then group the
details into a small number of meaningful parts. Explain how those parts relate
instead of producing a long inventory.

## Explain Decisions

Before asking Jake to choose, explain in the message body:

1. The decision in one plain sentence.
2. Why the decision exists and whether it must be made now.
3. Each realistic choice in simple terms.
4. What each choice makes possible.
5. What each choice costs, risks, delays, or gives up.
6. Whether the choice is easy to reverse later.
7. The recommended choice, when there is enough evidence to recommend one, and
   the simple reason for that recommendation.
8. What happens next after Jake chooses.

Do not present fake choices. If one option is clearly safer or better, say so.
If no decision is needed from Jake, say that directly.

## Ask With the Tool

When Jake actually has to pick something, **use the AskUserQuestion tool.**
Never end a plain-English explanation with an open-ended "so what do you want to
do?" — that hands the hard part back to him.

Rules for the question:

- Put the recommendation **first**, with `(Recommended)` at the end of its label.
- **Always explain why you recommend it** in that option's description, in plain
  words. Not "best balance of tradeoffs." Give the actual reason — what is
  already in place, what it avoids, what it lets him see soonest.
- Write every label and description so someone who has never heard of the
  technology could still pick correctly. No option should need outside
  knowledge to evaluate.
- Name the real cost of the recommended option too. Do not sell it.
- Two to four options. If there are genuinely only two, offer two.
- Skip the question when there is an obvious right answer. Just pick it, say you
  picked it and why, and keep going. Only ask when his answer changes the work.
- Ask about one decision at a time unless several are truly independent and all
  block progress.

Good option description:

> "Everything it needs is already installed on your Mac, and you've already
> shipped something this way — your Kain demo runs on it. We could start today
> with zero setup. The catch: it's the less powerful of the two toolkits, so a
> much bigger version of this could outgrow it later."

Bad option description:

> "Arduino framework via arduino-cli with the ESP32 core, using Arduino_GFX for
> the display and NimBLE-Arduino for the BLE transport."

## Choose the Shape That Helps

Use ordinary prose. Add short headings or bullets only when they make the
explanation easier to follow. A small plain markdown table is fine for
comparing two or three things. Match the length to the subject: a simple point
can take a paragraph; a complicated situation can take a structured walkthrough.

Do not use decorative boxes, card layouts, line art, forced emojis, or code
fences as presentation. Jake dislikes them and they make the answer harder to
read, not easier. Do not force every explanation into the same template.

## Optional Visual HTML

Create a visual HTML explanation when Jake asks for one, when the subject is
large enough that a visual walkthrough would make it easier to understand, or
when the result will be useful to revisit. Skip it for small explanations.

When creating HTML:

- In a repo, save the self-contained file in
  `<repo>/.notes/<short-slug>-jake-speak.html` by default. Create `.notes/` if it
  does not exist.
- Outside a repo, default to `~/Desktop/<short-slug>-jake-speak.html`.
- Treat the file as a local working artifact. Do not stage or commit it unless
  Jake explicitly asks.
- Make zero external requests. Inline the CSS and JavaScript. Embed any useful
  local image as a data URI so the page remains portable.
- Choose a layout that makes this specific subject easier to understand. Do
  not default to cards or recreate the old boxed-answer format.
- Keep the same Jake Speak priorities: practical takeaway, context, important
  facts, relationships, choices, consequences, and next steps.
- Confirm the absolute path after creating the file.

## Leave Out

- File paths, function names, schemas, packages, part numbers, library names,
  and framework details unless they are necessary to understand the outcome or
  choice.
- Acronyms and jargon without a plain explanation.
- Chronological play-by-play that does not change the meaning.
- Vague phrases such as "it depends" without explaining what it depends on.
- So much compression that Jake has to ask what the summary means.

## Examples

Technical version:
"The webhook reached the application, but the authentication middleware
rejected it before the handler ran."

Jake Speak:
"The outside service reached us, but our security check turned it away before
the app could respond. The connection exists; the permission setup is the part
that is broken."

Technical version:
"ESP-IDF isn't provisioned; we'd need to install the toolchain before builds."

Jake Speak:
"That's the professional version of the tools — more powerful, but it's still in
the box. I'd have to spend a while assembling it before writing any code."

Choice version:
"You need to decide whether this stays a private test or becomes available to
customers. A private test is safer and easy to change, but customers cannot use
it yet. Releasing it gives customers the feature now, but mistakes will affect
real people. I recommend the private test until we verify the last open risk.
After that check passes, releasing it is the sensible next step."
