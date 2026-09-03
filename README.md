# Pygentix

> **Pygent — A modular, provider-agnostic AI agent framework for Python.**

[![Status: Alpha](https://img.shields.io/badge/status-alpha-orange.svg)](#development-status)
[![Python](https://img.shields.io/badge/python-3.12%20%7C%203.13-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

> [!WARNING]
>
> ## Alpha software
>
> Pygent is currently in **alpha** and is under active development.
>
> APIs, architecture, behavior, dependencies, and internal implementations may change
> without notice. Breaking changes are expected.
>
> **Pygent should not currently be considered production-ready.**

> [!IMPORTANT]
>
> ## AI-assisted development
>
> Pygent is being developed with significant assistance from AI tools.
>
> AI-generated code, documentation, and architectural suggestions can contain:
>
> * Bugs
> * Inefficient implementations
> * Incorrect assumptions
> * Outdated information
> * Poor architectural decisions
> * Incomplete error handling
>
> **AI-generated content is not automatically considered correct.**
>
> Human review, testing, optimization, and continued development are required.
> Please review the implementation and verify the documentation before relying on
> Pygent in production or other reliability-sensitive applications.

---

## Overview

**Pygent** is a Python library for building conversational, tool-using AI agents.

The project is designed to provide an abstraction layer between an application and
LLM providers, allowing applications to combine:

* 🤖 Conversational AI
* 🔌 Multiple LLM providers
* 🔀 Model and provider routing
* 🛠️ Tool calling
* 🧩 Extensible skills
* 🌐 Web search
* 🌍 Browser automation
* 🧠 Conversation memory
* 🔧 Middleware

Pygent is intended to be **provider-agnostic** and **application-agnostic**.

For example, a Discord bot can use Pygent as its AI layer without Pygent needing
to know anything about Discord.

```text
┌──────────────────────────────┐
│           Application        │
│                              │
│        Discord Bot           │
│        Matrix Bot            │
│        CLI Application       │
│        Web Application       │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│           Pygent             │
│                              │
│  Agent → Router → Provider   │
│     │       │         │      │
│   Memory  Tools      LLM     │
│             │                │
│           Skills             │
└──────────────────────────────┘
```

---

## Goals

Pygent aims to make it straightforward to give an application an AI agent that
can **understand requests, choose tools, retrieve information, and produce a response**.

### Design goals

* Keep the core library lightweight.
* Avoid coupling the library to a specific LLM provider.
* Support both local and hosted models.
* Provide a consistent provider interface.
* Make tools easy to register and extend.
* Keep application-specific logic outside the library.
* Support asynchronous applications.
* Make advanced functionality optional.
* Keep the public API as simple as possible.

---

## Features

> [!NOTE]
> Feature availability and API design are still subject to change during alpha
> development.

| Feature                  | Status          |
| ------------------------ | --------------- |
| Agent orchestration      | 🚧 Experimental |
| Agent loop               | 🚧 Experimental |
| Tool calling             | 🚧 Experimental |
| Ollama provider          | 🚧 Experimental |
| OpenAI provider          | 🚧 Experimental |
| OpenRouter provider      | 🚧 Experimental |
| OpenAI-compatible APIs   | 🚧 Experimental |
| Provider routing         | 🚧 Experimental |
| Conversation memory      | 🚧 Experimental |
| Web search               | 🚧 Experimental |
| Browser automation       | 🚧 Planned      |
| Middleware               | 🚧 Experimental |
| Comprehensive test suite | 🚧 In progress  |
| Stable public API        | ⏳ Not yet       |

---

## Installation

> [!WARNING]
> Pygent is currently in alpha. Installation and dependency requirements may change.

### Using `pip`

```bash
pip install pygent
```

### Using `uv`

```bash
uv add pygent
```

### Optional integrations

Pygent keeps integrations optional where practical.

For example, to install Ollama support:

```bash
pip install "pygent[ollama]"
```

Or with `uv`:

```bash
uv add "pygent[ollama]"
```

Additional integrations can be installed using their corresponding extras:

```bash
pip install "pygent[openai]"
pip install "pygent[openrouter]"
pip install "pygent[anthropic]"
pip install "pygent[google]"
pip install "pygent[web]"
pip install "pygent[browser]"
```

Multiple extras can be installed together:

```bash
pip install "pygent[ollama,web]"
```

---

## Quick Start

> [!WARNING]
> The following API is **experimental** and may not represent the final Pygent API.

```python
from pygent import Agent
from pygent.providers import OllamaProvider

provider = OllamaProvider(
    model="qwen2.5-coder:3b",
)

agent = Agent(
    provider=provider,
)

response = await agent.run(
    "Explain what a Python list is."
)

print(response.text)
```

The intended API is designed to keep application code simple while allowing the
agent implementation to remain extensible.

---

## Architecture

The core architecture is based around several independent components:

```text
                         ┌──────────────┐
                         │    Agent     │
                         └──────┬───────┘
                                │
                         ┌──────▼───────┐
                         │  Agent Loop  │
                         └──────┬───────┘
                                │
              ┌─────────────────┼─────────────────┐
              │                 │                 │
              ▼                 ▼                 ▼
           Router             Memory            Tools
              │                                   │
       ┌──────┼──────┐                    ┌───────┴───────┐
       ▼      ▼      ▼                    ▼               ▼
    Ollama  OpenAI OpenRouter          Web Search      Browser
       │      │      │                    │               │
       └──────┴──────┴────────────────────┴───────────────┘
```

### Agent loop

The agent loop is the central execution cycle:

```text
User input
    │
    ▼
Build context
    │
    ▼
Select provider/model
    │
    ▼
Send request to LLM
    │
    ├───────────────┐
    │               │
    ▼               ▼
Final response    Tool call
                    │
                    ▼
                Execute tool
                    │
                    ▼
                Tool result
                    │
                    ▼
                 LLM again
                    │
                    ▼
              Final response
```

This allows an agent to decide whether it can answer directly or needs to use a
tool first.

---

<details>
<summary><strong>Project structure</strong></summary>

```text
pygentix/
├── pyproject.toml
├── README.md
├── LICENSE
├── uv.lock
│
├── src/
│   └── pygent/
│       ├── __init__.py
│       ├── exceptions.py
│       │
│       ├── agent/
│       │   ├── __init__.py
│       │   ├── agent.py
│       │   ├── context.py
│       │   ├── loop.py
│       │   └── messages.py
│       │
│       ├── memory/
│       │   ├── __init__.py
│       │   ├── base.py
│       │   ├── conversation.py
│       │   └── in_memory.py
│       │
│       ├── middleware/
│       │   ├── __init__.py
│       │   ├── base.py
│       │   ├── logging.py
│       │   └── retry.py
│       │
│       ├── providers/
│       │   ├── __init__.py
│       │   ├── base.py
│       │   ├── compatible.py
│       │   ├── ollama.py
│       │   ├── openai.py
│       │   └── openrouter.py
│       │
│       ├── routing/
│       │   ├── __init__.py
│       │   ├── router.py
│       │   └── strategies.py
│       │
│       ├── skills/
│       │   ├── __init__.py
│       │   │
│       │   ├── browser/
│       │   │   ├── __init__.py
│       │   │   ├── skill.py
│       │   │   └── tools.py
│       │   │
│       │   └── web_search/
│       │       ├── __init__.py
│       │       ├── skill.py
│       │       ├── tools.py
│       │       └── providers/
│       │           ├── __init__.py
│       │           └── ddgs.py
│       │
│       ├── tools/
│       │   ├── __init__.py
│       │   ├── base.py
│       │   ├── calls.py
│       │   ├── registry.py
│       │   └── result.py
│       │
│       └── types/
│           ├── __init__.py
│           ├── model.py
│           ├── tool.py
│           └── usage.py
│
└── tests/
    ├── agent/
    ├── memory/
    ├── middleware/
    ├── providers/
    ├── routing/
    ├── skills/
    └── tools/
```

</details>

---

## Providers

Pygent separates model communication from agent orchestration through providers.

The intended provider ecosystem includes:

| Provider   | Purpose                        |
| ---------- | ------------------------------ |
| Ollama     | Local/self-hosted models       |
| OpenAI     | OpenAI models                  |
| OpenRouter | Multi-model hosted API         |
| Anthropic  | Anthropic models               |
| Google     | Google models                  |
| Compatible | Generic OpenAI-compatible APIs |

The provider abstraction allows the rest of Pygent to work without needing to know
which provider is being used.

For example:

```text
Agent
  │
  ▼
Provider interface
  │
  ├── OllamaProvider
  ├── OpenAIProvider
  ├── OpenRouterProvider
  └── OpenAICompatibleProvider
```

---

## Routing

Multiple providers can be registered with a router.

Conceptually:

```python
router.add("local", ollama_provider)
router.add("cloud", openrouter_provider)
```

An agent can then use the router to select an appropriate provider.

Possible routing strategies include:

* Priority
* Fallback
* Manual selection
* Capability-based routing
* Load balancing
* Latency-aware routing

> [!NOTE]
> Not all routing strategies are implemented yet. This API is experimental.

---

## Tools

Tools allow an agent to interact with external functionality.

A tool may represent something as simple as a calculator or something more complex
such as a web-search API.

```text
Agent
  │
  ▼
LLM
  │
  ▼
Tool call
  │
  ▼
Tool registry
  │
  ▼
Tool execution
  │
  ▼
Tool result
  │
  ▼
LLM
```

The goal is to make custom application tools easy to register without requiring
Pygent to know anything about the application implementing them.

---

## Skills

A **skill** is a collection of related capabilities.

For example:

```text
skills/
├── browser/
└── web_search/
```

A web-search skill may provide tools such as:

```text
web.search
web.fetch
```

while a browser skill may eventually provide:

```text
browser.open
browser.click
browser.read
browser.screenshot
```

This allows functionality to remain modular instead of making every feature part
of the core library.

---

## Web Search

Web search is intended to be an optional Pygent skill.

The initial implementation is designed around a provider abstraction:

```text
Web Search Skill
       │
       ▼
Search Provider
       │
       ├── DDGS
       ├── Other provider
       └── Future providers
```

This allows search providers to be replaced without changing the agent itself.

---

## Browser Automation

Browser automation is planned as a separate optional skill.

Pygent may use Playwright for browser-based interactions:

```text
Agent
  │
  ▼
Browser Tool
  │
  ▼
Playwright
  │
  ├── Chromium
  ├── Firefox
  └── WebKit
```

Browser support is optional because browser automation introduces additional
dependencies and browser binaries.

---

## Memory

Memory is responsible for maintaining information across agent interactions.

The initial design separates the memory interface from individual implementations:

```text
Memory
  │
  ├── In-memory
  ├── Conversation memory
  └── Future persistent implementations
```

Potential future backends may include:

* SQLite
* PostgreSQL
* Redis
* Vector databases

These are not necessarily implemented yet.

---

## Middleware

Middleware provides hooks around agent execution.

For example:

```text
Request
   │
   ▼
LoggingMiddleware
   │
   ▼
RetryMiddleware
   │
   ▼
Agent
   │
   ▼
Response
```

Potential middleware includes:

* Logging
* Retries
* Metrics
* Tracing
* Rate limiting
* Request/response processing

---

## Using Pygent in a Discord Bot

Pygent is intentionally **not a Discord framework**.

A Discord bot should handle Discord-specific concerns itself:

```text
pox-bot
├── Discord events
├── Commands
├── Permissions
├── i18n
├── Database
└── AI integration
       │
       ▼
     Pygent
```

A simplified integration might look like:

```python
response = await agent.run(
    message.content,
    context=AgentContext(
        user_id=str(message.author.id),
        channel_id=str(message.channel.id),
    ),
)

await message.reply(response.text)
```

This separation allows the same Pygent agent to potentially be used by:

* Discord bots
* Matrix bots
* CLI applications
* Web applications
* Background services
* Other Python applications

---

## Development Status

Pygent is currently **Alpha**.

The project is expected to undergo substantial development before reaching a stable
release.

### Core

* [ ] Define stable public API
* [ ] Implement core agent
* [ ] Implement agent execution loop
* [ ] Improve context handling
* [ ] Implement robust error handling

### Providers

* [ ] Ollama
* [ ] OpenAI
* [ ] OpenRouter
* [ ] OpenAI-compatible APIs
* [ ] Anthropic
* [ ] Google

### Tools

* [ ] Tool abstraction
* [ ] Tool registry
* [ ] Tool-call parsing
* [ ] Tool result handling
* [ ] Better validation

### Skills

* [ ] Web search
* [ ] Browser automation
* [ ] Search-provider abstraction
* [ ] Skill registration/discovery

### Memory

* [ ] Conversation memory
* [ ] In-memory backend
* [ ] Persistent memory abstraction

### Quality

* [ ] Expand test coverage
* [ ] Type-check entire project
* [ ] Benchmark implementations
* [ ] Review AI-generated code
* [ ] Remove unnecessary dependencies
* [ ] Improve documentation
* [ ] Improve API consistency
* [ ] Review security considerations

### Release

* [ ] Alpha release
* [ ] Beta release
* [ ] Stable API
* [ ] Stable `1.0.0` release

---

## AI-Assisted Development

Pygent makes extensive use of AI-assisted development.

This is useful for:

* Exploring architectural ideas
* Generating initial implementations
* Finding potential bugs
* Creating tests
* Improving documentation
* Exploring alternative designs

However, AI assistance is **not a substitute for engineering review**.

AI-generated output can appear correct while containing subtle problems such as:

* Incorrect API usage
* Race conditions
* Resource leaks
* Poor error handling
* Unnecessary complexity
* Inefficient algorithms
* Incorrect type assumptions
* Security issues
* Outdated library information

Therefore, every important implementation should be treated as something that needs
**human verification and testing**.

> [!IMPORTANT]
> If you encounter code that looks unnecessarily complex, inefficient, incorrect,
> or questionable, please report it.
>
> Early architectural decisions are not sacred. Pygent is still evolving, and
> improving or replacing an AI-generated implementation is completely acceptable.

---

## Contributing

Contributions are welcome.

Because Pygent is an early-stage project, contributions that improve the architecture,
correct implementation mistakes, improve tests, or identify inaccurate documentation
are particularly valuable.

Before contributing:

1. Read the existing code and architecture.
2. Check existing issues and pull requests.
3. Keep changes focused.
4. Add or update tests where appropriate.
5. Verify that the implementation actually works.
6. Do not assume existing AI-generated code is correct.

If you find a bug or questionable implementation, please open an issue with:

* What you expected to happen
* What actually happened
* A minimal reproduction if possible
* Relevant logs or traceback
* Your Python version
* Relevant provider/model information

---

## Compatibility

Pygent currently targets:

| Component         | Version                       |
| ----------------- | ----------------------------- |
| Python            | 3.12–3.13                     |
| Package manager   | `pip`, `uv`                   |
| Operating systems | Intended to be cross-platform |

> [!NOTE]
> Compatibility is not guaranteed during alpha development.

---

## License

Pygent is released under the [MIT License](LICENSE).

---

## Project Status

Pygent is an **experimental, AI-assisted, open-source project**.

The long-term goal is to provide a clean and extensible agent framework that makes
it easy for Python applications to gain conversational AI, tool usage, and external
information retrieval without being tied to a single provider.

```text
┌──────────────────────────────────────────┐
│                  Pygent                  │
│                                          │
│       Chat • Tools • Skills • Memory     │
│                                          │
│     Ollama • OpenAI • OpenRouter • ...   │
└──────────────────────────────────────────┘
```

**Build the agent. Plug in the model. Give it tools.**
