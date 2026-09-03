# AGENTS.md

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

Update `TODO.md` whenever a commit changes the project's task status. Prefer including the TODO update in the same commit as the related implementation or test change.

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
