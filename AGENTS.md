# AGENTS.md

## TODO.md Format

AI agents writing or editing any `TODO.md` file in this repository **must** follow the project's custom TODO specification: see [`custom-todo-specification.md`](custom-todo-specification.md) for the full grammar.

Key rules agents must apply:

- The first non-whitespace line of any `TODO.md` must be `# TODO` or `# TODO.md`. Never start a TODO file with a different top-level heading (for example, `# TODO.md for pygent`).
- Tasks are unordered-list items whose content begins with exactly one of `[ ]`, `[x]`, or `[-]`. Plain `- Task` bullets are **not** valid tasks.
- Sections are Markdown subheaders (`##`, `###`, …) below the top-level header. Use them to group related tasks.
- Subtasks use standard Markdown indentation (two spaces is the convention here).
- Use `@username` to assign a task and `#tag` to categorise one. Metadata may appear anywhere in the task text; the rest is the task description.
- Anything that is not a recognised task or section heading is informational content and is allowed (and expected) for context, notes, or descriptions.
- Multiple `TODO.md` files may exist at different levels of the repository; the same rules apply to each one.
- When a commit changes a task's status, update the corresponding `TODO.md` in the same commit (see `## Commits and Pull Requests` below).

## Project

Pygentix (`pygent`) is a modular, provider-agnostic AI agent framework for Python 3.12+.

Keep the core independent from application-specific integrations such as Discord bots.

## Architecture

- `agent/` orchestrates model and tool interaction.
- `providers/` contains LLM provider implementations behind `Provider`.
- `tools/` contains callable tool abstractions, validation, execution, and registry logic.
- `types/` contains provider-neutral Pydantic models and shared types.
- `memory/` stores conversation state.
- `middleware/` wraps agent operations such as logging and retries.
- `routing/` selects providers/models and handles fallback strategies.
- `skills/` packages related tools into reusable capabilities.

## Development

- Target Python 3.12 and support Python 3.13 where practical.
- Use `uv` for dependency and environment management.
- Use Ruff for formatting and linting.
- Use mypy in strict mode for type checking.
- Use pytest and pytest-asyncio for tests.
- Prefer async-native APIs for I/O-bound operations.
- Keep public APIs small, explicit, and provider-neutral.
- Add tests for behavior changes, especially provider/tool interactions.

## Commits and Pull Requests

Use Conventional Commits:

```text
<type>[scope]: <summary>

[optional body]

[optional footer]
```

Keep the summary focused on the largest change in the commit. Use a scope when it improves clarity.

Work should normally be developed on a feature branch and submitted through a pull request rather than committed directly to `main`.

Update `TODO.md` whenever a commit changes the project's task status. Prefer including the TODO update in the same commit as the related implementation or test change. Edits to `TODO.md` must follow the format defined in `## TODO.md Format` above.

## Verification

Before considering a change complete, run:

```bash
uv run pytest
uv run ruff format --check .
uv run ruff check .
uv run mypy src
```

When dependency lock state changes, also verify the lockfile with `uv lock` and use `uv sync --locked --group dev` where appropriate.

## Design Guidelines

- Avoid adding provider-specific behavior to core abstractions when it can live in a provider implementation.
- Preserve tool-call ordering when returning multiple concurrent tool results.
- Convert provider-specific errors and responses into stable Pygent types at the boundary.
- Do not swallow unexpected errors silently; expose useful normalized tool/model failures to the agent loop.
- Avoid speculative abstractions until a concrete feature needs them.

## Project-Specific Gotchas

These are non-obvious facts that an agent cannot easily infer from the directory layout or the README:

- **Public API surface is intentionally narrow at the top level.** Only `Agent`, `AgentContext`, `AgentResponse`, `Message`, `ModelResponse`, `ToolCall`, `ToolDefinition`, `Usage`, `getenv`, and `load_dotenv` are re-exported from `pygent`. Everything else (`AgentLoop`, `AgentEvent`, `parse_structured_output`, `Tool`, `ToolRegistry`, `Provider`, providers, middleware, routing, skills) must be imported from its submodule. Don't add re-exports here without a deliberate API decision.
- **`Tool.execute_with_timeout` is what the agent loop actually calls**, not `Tool.execute`. Subclasses should override `execute`; `execute_with_timeout` honours the class attribute `timeout: float | None` and converts `asyncio.TimeoutError` into `pygent.exceptions.ToolTimeoutError`.
- **`OllamaProvider` is the only vendor-SDK-based provider.** All other providers use raw `httpx.AsyncClient.post("/chat/completions", …)`. New providers should follow the httpx pattern unless a vendor SDK offers a clear benefit.
- **`OpenAICompatibleProvider` does not auto-inject `Authorization` headers when a caller passes their own `httpx.AsyncClient`.** Tests that stub a transport must put the `Authorization` header on the `AsyncClient` themselves. The provider also does **not** call `aclose()` on a user-supplied client (it checks `getattr(client, "_is_pygent_default", True)`).
- **Use `pygent.config.getenv`, not `os.environ.get`, in providers.** It auto-loads a `.env` file from the current working directory (or parents) when the `python-dotenv` extra is installed, and silently falls back to `os.environ` otherwise. Existing `OPENAI_API_KEY` and `OPENROUTER_API_KEY` reads go through it.
- **Provider exceptions are normalized in `pygent.exceptions`**: `ProviderConnectionError`, `ProviderAuthenticationError`, `ProviderRateLimitError`, `ProviderRequestError`, `ProviderResponseError`. The `OpenAICompatibleProvider` raises these on HTTP 401/403, 429, ≥400, and transport failures respectively.
- **The agent loop runs in `AgentLoop` and is wrapped by `Agent`.** The `Agent` class adds memory integration and a typed `AgentResponse`; new orchestration features (streaming, structured output) live on `AgentLoop` first, then surface through `Agent` only when needed.
- **`TODO.md` is significantly out of date.** Phases 1–7 and most of Phase 9 are largely implemented despite the checklist still showing them as pending. Don't trust the TODO as a source of truth for "is this done" — check the codebase. Update `TODO.md` in the same commit that changes a task's status.

## Examples and Smoke Tests

- `examples/` contains runnable snippets for each major feature (`basic_agent`, `cli`, `custom_tool`, `env_file`, `memory`, `middleware`, `ollama`, `openai`, `openrouter`, `routing`, `web_search`).
- `scripts/smoke_cli.py` is a scripted-input smoke test for `examples/cli.py`; it monkey-patches `builtins.input` and runs the REPL with a fixed list of commands.
- New public features should ship with an example under `examples/` that uses a stub provider (no network) so CI / local reviewers can copy-paste it.
