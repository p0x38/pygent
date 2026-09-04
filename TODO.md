# TODO.md

Pygent development tasks and roadmap.

## Current Queue

### 1. Core Correctness

- [x] Provider contract tests
  - [x] Common provider behavior
  - [x] Message conversion
  - [x] Tool-call behavior
  - [x] Finish reasons
  - [x] Usage handling
  - [x] Error normalization
  - [x] Provider lifecycle
- [ ] Improve agent context handling
- [ ] Review agent/tool loop edge cases
- [ ] Add comprehensive agent-loop tests
- [ ] Add deterministic concurrency tests
- [ ] Review public API exports
- [ ] Remove dead/accidental code

### 2. Usage and Observability

- [ ] Provider usage tests
  - [ ] Verify input token counts
  - [ ] Verify output token counts
  - [ ] Verify total token counts
  - [ ] Cover providers that expose usage directly
  - [ ] Cover providers that do not expose usage
  - [ ] Cover missing/partial usage fields
- [ ] Usage aggregation across iterations
  - [ ] Aggregate usage from every provider request in one agent run
  - [ ] Preserve per-request usage for diagnostics
  - [ ] Define behavior when one request has unknown usage
  - [ ] Add regression tests for multi-iteration aggregation
- [ ] Usage aggregation across tool loops
  - [ ] Include the initial model request
  - [ ] Include follow-up requests after tool execution
  - [ ] Keep tool execution itself separate from model token usage
  - [ ] Add regression tests for multiple tool calls and loops
- [ ] Quota/budget tracking and enforcement
  - [ ] Define request-count limits
  - [ ] Define input/output/total token limits
  - [ ] Define per-run and optional global budgets
  - [ ] Track usage against configured budgets
  - [ ] Enforce limits before starting a request
  - [ ] Enforce limits after provider usage is known
  - [ ] Define behavior when usage is unavailable
  - [ ] Add quota/budget-specific exceptions
  - [ ] Add configuration and tests
- [ ] Cost calculation and estimation
  - [ ] Define a normalized pricing representation
  - [ ] Calculate input token cost
  - [ ] Calculate output token cost
  - [ ] Calculate total estimated request cost
  - [ ] Support missing/unknown pricing
  - [ ] Distinguish estimated cost from provider-reported cost
  - [ ] Add cost calculation tests
- [ ] Provider/model pricing metadata
  - [ ] Define model pricing metadata structure
  - [ ] Support input/output token prices
  - [ ] Support optional cached-input pricing
  - [ ] Associate pricing with provider/model identifiers
  - [ ] Define precedence for provider-specific pricing overrides
  - [ ] Handle unknown models without failing requests
  - [ ] Add pricing metadata tests
- [ ] Optional request timing metadata
  - [ ] Record request start/end timestamps
  - [ ] Record elapsed request duration
  - [ ] Keep timing collection optional
  - [ ] Include timing in structured execution diagnostics
  - [ ] Add tests for timing metadata
- [ ] Structured execution diagnostics
  - [ ] Define a normalized execution event/record format
  - [ ] Record provider/model information
  - [ ] Record request/response timing
  - [ ] Record usage and estimated cost
  - [ ] Record tool-call lifecycle information
  - [ ] Record retry attempts and failures
  - [ ] Make diagnostics consumable without enabling verbose logging
- [ ] Configurable artificial response delays / waiting behavior
  - [ ] Support optional delay before provider requests
  - [ ] Support optional delay before emitting streamed/final responses
  - [ ] Allow fixed and configurable delay strategies
  - [ ] Keep delays disabled by default
  - [ ] Make delays cancellation-aware
  - [ ] Avoid blocking the event loop
  - [ ] Expose delay behavior through configuration/API
  - [ ] Add deterministic tests using injected clocks/sleepers

### 3. Prompt and Agent Instructions

- [ ] Custom system-prompt support
  - [ ] Accept a custom system prompt from the Python API
  - [ ] Allow replacing or extending the built-in system prompt
  - [ ] Define precedence between built-in and user-provided prompts
  - [ ] Preserve system prompts correctly during context truncation
  - [ ] Add prompt composition tests
- [ ] CLI prompt customization
  - [ ] Add a CLI option for a one-off system/custom prompt
  - [ ] Add a CLI option for loading a prompt from a file
  - [ ] Support stdin-based prompt input where practical
  - [ ] Define precedence between CLI prompt, config, and context files
  - [ ] Add CLI tests
- [ ] `SOUL.md` support
  - [ ] Support an instance/global `SOUL.md` for durable agent identity
  - [ ] Allow configurable location for the global soul file
  - [ ] Provide a safe default location using the existing Pygent data directory
  - [ ] Fall back to the built-in identity when the file is missing or empty
  - [ ] Define size limits and truncation behavior
  - [ ] Add loading and fallback tests
- [ ] `AGENTS.md` support
  - [ ] Discover `AGENTS.md` from the working directory
  - [ ] Walk toward the repository root when appropriate
  - [ ] Support nested directory-specific instruction files
  - [ ] Define ordering and precedence for multiple instruction files
  - [ ] Keep project instructions separate from global identity
  - [ ] Define size limits and truncation behavior
  - [ ] Add discovery and merge tests
- [ ] Additional coding-agent instruction file compatibility
  - [ ] Consider `.hermes.md` / `HERMES.md` compatibility
  - [ ] Consider `CLAUDE.md` compatibility
  - [ ] Consider `.cursorrules` / `.cursor/rules/*.mdc` compatibility
  - [ ] Define which formats are supported officially versus best-effort
  - [ ] Avoid loading conflicting instruction sources twice
- [ ] Prompt source resolution and security
  - [ ] Define deterministic prompt-source precedence
  - [ ] Distinguish identity, project instructions, and per-invocation prompts
  - [ ] Prevent accidental prompt duplication
  - [ ] Apply bounded file-size limits before prompt injection
  - [ ] Handle unreadable/invalid prompt files without crashing the agent
  - [ ] Add regression tests for conflicting prompt sources
- [ ] Prompt presets / session-level instruction overlays
  - [ ] Support named prompt/personality presets
  - [ ] Allow temporary session-level overlays without modifying persistent files
  - [ ] Define replace versus append behavior
  - [ ] Add CLI commands/options for selecting presets
  - [ ] Add persistence and precedence tests

### 4. Web Search and Browser Completion

- [ ] Link clicking
- [ ] Text finding
- [ ] Normalized browser results
- [ ] Browser-specific errors
- [ ] Browser tests
- [ ] Browser resource cleanup
- [ ] Search/browser agent tools

### 5. API Stabilization

- [ ] Review all public exports
- [ ] Review naming consistency
- [ ] Review async API conventions
- [ ] Review exception hierarchy
- [ ] Review provider interface stability
- [ ] Review tool interface stability
- [ ] Review event model stability
- [ ] Define backwards-compatibility policy
- [ ] Remove experimental APIs that should not be public

### 6. Documentation and Examples

- [ ] Installation documentation
- [ ] Quick-start documentation
- [ ] Architecture documentation
- [ ] Provider documentation
- [ ] OpenAI-compatible provider documentation
- [ ] OpenRouter documentation
- [ ] Custom provider documentation
- [ ] Tool documentation
- [ ] Skill documentation
- [ ] Memory documentation
- [ ] Middleware documentation
- [ ] Routing documentation
- [ ] Streaming documentation
- [ ] Structured output documentation
- [ ] Configuration documentation
- [ ] CLI documentation
- [ ] Error handling documentation
- [ ] Cancellation/timeout documentation
- [ ] API reference
- [ ] Keep README feature/status tables synchronized with implementation
- [ ] Prompt customization and context-file documentation

### 7. CI and Packaging

- [ ] Python 3.13 CI coverage
- [ ] Test multiple operating systems where practical
- [ ] Package build verification
- [ ] Package installation smoke test
- [ ] Verify wheel contents
- [ ] Verify source distribution contents
- [ ] Verify package metadata
- [ ] Verify optional dependencies
- [ ] Automated release validation
- [ ] Changelog/release notes workflow
- [x] Fix Ruff/isort import sorting locally
- [x] Verify CI passes after local Ruff fixes

### 8. Alpha Release

- [ ] Final API review
- [x] Final test suite pass
- [x] Ruff/lint pass
- [x] Type-check pass
- [x] CI pass
- [ ] README review
- [ ] Documentation review
- [ ] Package metadata review
- [ ] Changelog/release notes
- [ ] Select final alpha version
- [ ] Create GitHub release
- [ ] Publish package
- [ ] Verify installation from published package

## Completed

### Core

- [x] Core provider-neutral types
- [x] `Provider` interface
- [x] Agent execution loop
- [x] Tool abstraction and registry
- [x] Tool execution and argument validation
- [x] Pydantic JSON Schema validation
- [x] Ollama provider
- [x] OpenAI-compatible provider
- [x] OpenAI provider convenience wrapper
- [x] OpenRouter provider
- [x] Provider error normalization
- [x] Router abstraction
- [x] Provider/model selection
- [x] First-available strategy
- [x] Fallback strategy
- [x] Priority strategy
- [x] Provider availability handling
- [x] Routing errors
- [x] Routing tests
- [x] Conversation memory
- [x] Middleware abstraction and pipeline
- [x] Logging middleware
- [x] Retry middleware
- [x] Timing middleware
- [x] Usage tracking middleware
- [x] Streaming API and agent events
- [x] Model usage representation

### Production Hardening

- [x] Request timeout support
- [x] Maximum tool-call limits
- [x] Concurrent tool execution
- [x] Cancellation support
- [x] Tool timeouts
- [x] Tool cancellation
- [x] Robust concurrent tool execution
- [x] Context-size handling
- [x] Retry/backoff policy
- [x] Connection/resource lifecycle handling
- [x] Graceful shutdown
- [x] Exception chaining and diagnostics
- [x] Deterministic test coverage
- [x] Edge-case tests
- [x] Stress/concurrency tests

### Structured Output

- [x] Structured output API
- [x] Pydantic model validation
- [x] Structured output errors
- [x] Structured output tests

### Web Search / Browser

- [x] Web search abstraction
- [x] DuckDuckGo provider
- [x] Normalized search results
- [x] Page retrieval
- [x] Request limits
- [x] Redirect handling

### Other

- [x] Username configuration
- [x] Persistent conversation memory
- [x] CLI memory management
- [x] GitHub Actions test workflow
- [x] GitHub Actions lint/type-check workflow

## Work in Progress

- [ ] Core correctness
- [ ] Usage and observability
- [ ] Prompt and agent instructions
- [ ] Web search / browser completion
- [ ] API stabilization
- [ ] Documentation and examples
- [ ] CI and packaging
- [ ] Alpha release

## Planned

### Future Providers

- [ ] Anthropic provider
- [ ] Google provider
- [ ] Additional OpenAI-compatible providers
- [ ] Provider capability discovery
- [ ] Provider-specific feature negotiation

### Future Features

- [ ] Persistent memory backends
- [ ] External memory/vector-store integration
- [ ] Tool result caching
- [ ] Response caching
- [ ] Advanced context management
- [ ] Token budgeting
- [ ] Model capability metadata
- [ ] Tool dependency management
- [ ] Agent hooks/lifecycle events
- [ ] Better tracing/observability integration
- [ ] Plugin/extension system
- [ ] MCP server support
- [ ] ACP server support
- [ ] Node.js integration where it provides a clear capability or ecosystem benefit
- [ ] Rust integration where it provides a clear performance or systems-level benefit
