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
| OpenAI provider          | 🚧 Planned      |
| OpenRouter provider      | 🚧 Planned      |
| OpenAI-compatible APIs   | 🚧 Planned      |
| Provider routing         | 🚧 Planned      |
| Conversation memory      | 🚧 Planned      |
| Web search               | 🚧 Planned      |
| Browser automation       | 🚧 Planned      |
| Middleware               | 🚧 Planned      |
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

Ollama support is currently available as an optional dependency:

```bash
pip install "pygent[ollama]"
```

Or with `uv`:

```bash
uv add "pygent[ollama]"
```

Other provider and skill integrations will be added as their implementations land.

---

## Quick Start

> [!WARNING]
> The following API is **experimental** and may not represent the final Pygent API.

```python
from pygent import Agent
from pygent.providers import OllamaProvider

provider = OllamaProvider(model="qwen2.5-coder:3b")
agent = Agent(provider=provider)

response = await agent.run("Explain what a Python list is.")

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

## Providers

Pygent separates model communication from agent orchestration through providers.

The intended provider ecosystem includes:

| Provider   | Purpose                        | Status         |
| ---------- | ------------------------------ | -------------- |
| Ollama     | Local/self-hosted models       | Experimental   |
| OpenAI     | OpenAI models                  | Planned        |
| OpenRouter | Multi-model hosted API         | Planned        |
| Anthropic  | Anthropic models               | Planned        |
| Google     | Google models                  | Planned        |
| Compatible | Generic OpenAI-compatible APIs | Planned        |

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

## Development Status

Pygent is currently **Alpha**.

The project is expected to undergo substantial development before reaching a stable
release.

### Current core

* Provider-neutral message and tool types
* Provider abstraction
* Basic agent execution loop
* Tool registry and execution
* Ollama provider foundation
* Automated tests and lint/type checks

### Planned

* OpenAI-compatible provider
* OpenRouter provider
* Provider routing and fallback
* Conversation memory
* Middleware
* Web search and browser skills
* Streaming responses
* Structured outputs
* Better tool argument validation
* Python 3.13 CI coverage
* Documentation and examples
* First alpha release

---

## Contributing

Pygent is still evolving rapidly. Contributions, bug reports, tests, and architectural
feedback are welcome.

Before relying on a new feature, please check its tests and current implementation
because the public API is not stable yet.

---

## License

Pygent is licensed under the [MIT License](LICENSE).
