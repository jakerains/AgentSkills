# Question interfaces across harnesses

Use the current host's native structured clarification/question picker whenever available and permitted. These mappings help recognize that capability; they do not grant tools or define a universal API. Inspect the exposed schema and host instructions before calling. A Claude model running in Cursor does not imply Claude Code's tool. Do not browse or install anything just to run the interview.

## Known surfaces

Documentation checked **2026-10-01**. Names, availability, and rendering can change; the current session wins. These are documentation/schema checks, not end-to-end tests in every product.

| Harness | Native capability to recognize | Adaptation and primary source |
|---|---|---|
| Codex | `request_user_input`; `request_user_input_async` where exposed | Current Codex Desktop session supplies both, with built-in custom text; synchronous schema allows 1–3 questions and 2–3 options, recommended first. Async returns before the answer. Availability and limits vary by host/mode: [official handler](https://github.com/openai/codex/blob/main/codex-rs/core/src/tools/handlers/request_user_input.rs). The [app-server user-input event](https://developers.openai.com/codex/app-server/) is a protocol surface, not a model-callable alias. |
| Claude Code / Agent SDK hosts | `AskUserQuestion` | 1–4 questions, 2–4 options each; `multiSelect` supports combinations. Claude's interface includes Other; custom SDK clients must implement the input UI. Option previews depend on SDK configuration and rendering support. [Official user-input documentation](https://code.claude.com/docs/en/agent-sdk/user-input). |
| Cursor | `AskQuestion` | Recognized in the [official CLI changelog](https://cursor.com/changelog/04-14-26). Use its exposed schema. The [ACP method `cursor/ask_question`](https://cursor.com/docs/cli/acp) is a client protocol with option IDs and optional multiple selection, not a tool name to invent. |
| Gemini CLI | `ask_user` | 1–4 questions; choice questions take 2–4 options. Text and yes/no questions and multi-select are also documented. [Official Ask User tool](https://geminicli.com/docs/tools/ask-user/). |
| GitHub Copilot CLI | `ask_user` | Inspect the live schema for limits and features. `/ask` is a user-initiated side question, not this tool. [Official CLI reference](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-command-reference). |
| VS Code / Copilot Chat | `vscode/askQuestions` / `askQuestions`, as exposed | The [prompt-file example](https://code.visualstudio.com/docs/agent-customization/prompt-files) uses the namespaced form; [release notes](https://code.visualstudio.com/updates/v1_109) describe single/multi-select, free text, and recommendations. Do not assume the CLI name applies. |
| OpenCode | `question` | Options and custom responses are documented. Inspect the actual schema for other capabilities. [Official tools documentation](https://opencode.ai/docs/tools/#question). |
| Cline | `ask_followup_question` | Official examples supply a question and suggested `options`; inspect the current definition. [Repository workflow example](https://github.com/cline/cline/blob/main/.clinerules/workflows/pr-review.md). |
| Roo Code | `ask_followup_question` | One question with 2–4 `follow_up` suggestions and free replies. Its parameters differ from Cline's despite sharing a name. [Official tool documentation](https://roocodeinc.github.io/Roo-Code/advanced-usage/available-tools/ask-followup-question/). |
| Other hosts | Whatever exposed tool provides structured user questions | Select by capability and current documentation. If none is available or permitted, use labeled chat choices. Do not infer support from an agent's name or an installation of this skill. |

## Adapt the interview, not the task

1. Resolve only missing information. Use the permitted question tool for that information; keep guide rounds at **at most two questions**, or one if the host requires it. Do not switch operating modes to unlock a tool.
2. Use concise, distinct option labels with short explanations where supported. Mark one grounded recommendation; obey any required ordering. Preserve semantic choices separately from display positions. Keep the native interface's own numbering/lettering without adding competing prefixes; if supplying choice labels yourself, use letters throughout. Never call an RPC event, approval tool, or guessed alias as though it were a question tool.
3. Preserve custom answers. Omit a custom/Other option when the UI already adds a text entry. Otherwise offer “My own answer” if the schema allows it, then collect the actual text through the host's supported free-text question or chat. Do not treat the literal word “Other” as the requested audience or format.
4. Fit long menus with grouped questions. Do not truncate choices, pack several selectable goals into one ambiguous option, or exceed a tool's cap. For a three-option cap with built-in custom text, ask **Understand it** versus **Explain or apply it**, then offer the corresponding modes: **Like I'm five / Make it click / Give me the big picture**, or **Help me explain it / Help me use it**. Include a custom path at each step. If custom input requires an explicit option, reserve a slot and split groups further as needed. State these are groups, not final modes.
5. Apply the same approach to age/language choices if needed: **Very simple / Teen-level / Adult plain language**, then distinguish **Around five / Around ten** when Very simple is selected. Preserve a custom age or education preference without forcing it into a preset. Grouping may add a round; skip it when the answer is already known.
6. Use multi-select only for compatible choices, such as combining teaching goals. Format and reading level ordinarily require one choice. If multi-select is unavailable, accept a combination through free text. Never invent a field to enable it.
7. Map returned question IDs, option IDs, labels, and custom text using the actual response contract. Accept an unambiguous typed reply too. After recommendations reorder a native menu, its second option is not necessarily fallback B. Do not ask for redundant confirmation.
8. Wait for answers before dependent work. For async tools, retain the pending questions, do independent work if useful, and do not issue duplicate forms. A preselected recommendation, timeout, or dismissal does not mean the user chose it. Follow the host's explicit no-answer/cancel policy; when optional defaults are allowed, state them as assumptions. Never invent a missing topic.

## Visual previews when supported

Use an option preview only if it clarifies a needed format or learning-goal question, such as a static overview versus a walkthrough with meaningful controls. Keep the same standard design across previews. Never add a style, color, typography, or motion question just because previews are available. Keep previews lightweight and use only the tool's allowed format. Without preview support, concise descriptions are enough; do not build or publish mockups just to ask an interview question.

Claude's SDK documents opt-in `toolConfig.askUserQuestion.previewFormat` with Markdown or an HTML fragment; unset configurations omit `preview`. That does not establish that every Claude CLI, desktop, or custom client exposes identical rendering. Read the current schema instead of sending `preview` unconditionally. Do not change SDK configuration merely to run ELI. [Official preview documentation](https://code.claude.com/docs/en/agent-sdk/user-input#option-previews-typescript).

## Text fallback

When a native picker is unavailable, forbidden for this question, or fails with an unavailable-capability error, use letters for all answer options and put **My own answer** last with the next unused letter: A–C plus D for three presets, A–D plus E for age/language, and A–E plus F for the five modes. Question numbers identify questions only; a reply such as **1B, 2D** means question 1 option B and question 2 option D. Never mix numeric and lettered answer options. Mark a grounded recommendation and show a short reply example. If no useful options exist, ask one free-text question. Preserve prior answers when changing interfaces and ask only what remains unresolved. Do not retry a rejected tool indefinitely or build a replacement questionnaire app.

## Review scenarios

These are expected behaviors for reviewing this skill, not claims of executed platform tests:

| Situation | Expected behavior |
|---|---|
| `ELI guide caching` in a host with a native picker | Ask the first unresolved round through that picker; do not paste the whole guide into chat. |
| Claude model in Cursor with only `AskQuestion` exposed | Use `AskQuestion`, never invent `AskUserQuestion`. |
| Three-option cap; five teaching modes | Use grouped questions; all five modes and custom answers remain reachable. |
| Native UI supplies Other | Send only real choices; no duplicate custom/Other option. |
| HTML recommended and required to appear first | Put HTML first; its returned identity selects HTML, regardless of fallback B. |
| User enters a custom audience | Record it directly; do not require a preset or repeat the form. |
| No `preview` or multi-select field in the schema | Use supported labels/descriptions and custom text; do not send unsupported fields. |
| Async question has returned but no answer has arrived | Keep it pending; no dependent explainer generation or duplicate question. |
| User dismisses an optional question | Follow host policy; distinguish stated defaults from user selections. |
| Question tool unavailable in this mode | Use labeled chat fallback, retaining prior choices; do not change modes. |
| User already supplied the full teaching brief, including guide depth if relevant | Build directly using the standard design; no style or motion questions. |
| User chooses a page or walkthrough in the last unresolved guide round | End the interview and create it; do not add a design round or approval gate. |
| User says “no questions” with a known topic | Honor the shortcut and supplied choices; do not invoke a picker merely because it exists. |
