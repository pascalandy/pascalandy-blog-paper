---
title: "Delegating tool calls cut my audit cost by 81 percent"
tags:
  - technologie
date_created: 2026-11-23
author: Pascal Andy
lang: en
description: "Two Astra agents audited the same codebase. Giving one a Luna terminal cut the estimated API cost from $40.91 to $7.71 and added 34 minutes."
---

**My lead agent used 92.4% fewer tokens on a codebase audit.** I gave two GPT-6.2 Astra agents the same prompt about Mixtape, my desktop app for keeping Spotify playlists on disk. Both ran at high reasoning effort.

> mixtape ;
>
> First read ALL of the AGENTS.md file and README.md file super carefully and understand ALL of both! Then use your code investigation agent mode to fully understand the code and technical architecture and purpose of the project. THEN apply `$reality-check-for-project` here in an exhaustive way.

**1 · Astra alone.** Astra read the code, ran the tests, and wrote the report.

**2 · Astra with Luna.** I added one instruction block. Astra sent every task-related tool call to one persistent GPT-6 Luna agent at medium effort. Astra could batch independent calls and kept the final say. [Jump to the prompt](#copy-the-tool-call-delegation-prompt).

Follow the orange. Astra went from 37.1M tokens to 2.8M. Including Luna, the audit used 28.0M, down 24.4%.

![Astra used 92.4% fewer cumulative tokens. The bars compare both runs. The table separates cached input, uncached input, and output for each agent.](../../assets/images/tool-call-delegation/tokens-by-agent.png)

The call count barely moved. What changed was whose conversation filled up with code and test logs.

![163 tool calls alone versus 162 with delegation. Astra coordinated Luna in 31 calls. Luna made 131.](../../assets/images/tool-call-delegation/tool-calls.png)

## What was that worth in dollars and minutes?

A test log can reappear in the model’s input on every later request. Even at the cache discount, Astra alone spent an estimated **$32.28 rereading context**. With Luna, Astra’s cache reads cost **$2.03**. Its uncached input fell only 11.5%. The pair used more uncached input and generated more output, yet Luna’s entire share came to **58 cents**.

![Estimated API cost fell from $40.91 to $7.71. The table breaks each agent’s cost into uncached input, cached input, and output.](../../assets/images/tool-call-delegation/api-cost.png)

![Astra alone finished in 45m 30s. With delegation, the report took 1h 19m 21s, an extra 33m 51s.](../../assets/images/tool-call-delegation/elapsed-time.png)

I matched the three T3 sessions and priced each request in ClickHouse at November 23, 2026 API rates, outside my Codex plan. I used Astra’s configured Fast tier, assumed Standard for Luna, and included long-context pricing above 272,000 input tokens. At all-Standard rates, the same usage costs **$20.45 versus $4.15**. All figures are USD. [OpenAI API pricing](https://developers.openai.com/api/docs/pricing) · [Fast pricing](https://openai.com/api-fast-mode/)

## Two reports landed on my desk

Both runs downloaded 15 playable songs and passed 511 Rust and 192 Python tests. Yet my installed Linux app couldn’t find Deno. Astra alone reproduced the failure and got the engine check to pass by adding Deno to the audit process’s path.

The delegated run reproduced a Python 3.13 diagnostic failure. It also found that an interrupted replacement could leave a music player reading a stale playlist after the audio and index recovered. Each method ran once from the same starting revision. The second inspected a later commit too. I’d use this trial to budget another audit, not to rank bug-finding ability.

## Was tool call delegation worth it?

**For the way I work in T3 Code? Absolutely.** I can leave an audit running in one thread and get on with something else. Whether the report is ready in half an hour or an hour and a quarter makes little difference to my day.

On this run, delegation added **33 minutes and 51 seconds** and saved an estimated **$33.20** at API rates. If I needed the answer before I could do anything else, getting it sooner would be worth about $59 an hour. For a background audit, I’d give Luna the terminal again.

I’d also give it the working directory. Luna ran `just e2e` from the wrong directory and had to retry. Elsewhere, when a shallow Git repository refused a fetch, Luna found a way to reuse the existing objects. That’s why I’d keep medium effort. I haven’t tested low.

## Copy the tool call delegation prompt

Append this block to your task. Your agent needs to be able to start a second agent and send it follow-up messages.

```text
Use one persistent GPT-6 Luna agent at medium reasoning effort.
Delegate all task-related tool calls to Luna. Make direct calls only
to start Luna or communicate with it. You choose the operations,
interpret the results, and write the final answer.

Send an ID, the exact tool and arguments, and the output you need.
For shell commands, include the absolute working directory.
Batch independent calls when safe. Read each prerequisite result
before choosing a dependent call.

Give Luna these rules at startup:
- Execute the specified calls. Run marked parallel calls together.
- Follow running commands to completion. Return the ID, status,
  and requested output. Quote errors exactly. Flag truncated output.
- Use a fallback only if I specify the trigger and the exact action.
- When you need a decision, ask me. Continue independent calls.
```

I keep the full instructions in my `tool-call-delegation` skill. Once it’s configured, I can append `$tool-call-delegation` to a task and specify Luna at medium effort to use the same setup.

<https://github.com/pascalandy/skills/tree/main/authoring/andy/tool-call-delegation>
