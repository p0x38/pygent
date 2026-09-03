# TODO.md

## Phase 1 — Core Foundation

### Completed

- [x] Core provider-neutral types
- [x] `Provider` interface
- [x] Basic `Agent` and tool loop
- [x] Tool abstraction and registry
- [x] Tool execution error handling
- [x] Tool argument validation
- [x] Tool JSON Schema validation with Pydantic
- [x] GitHub Actions test workflow
- [x] GitHub Actions lint/type-check workflow
- [x] Ollama provider foundation
- [x] Ollama provider tests
- [x] Fix tool type variance in tests
- [x] Add multiple-tool-call tests
- [x] Improve agent context integration

### Remaining

- [ ] Fix Ruff/isort import sorting locally
- [ ] Verify CI passes after local Ruff fixes
- [ ] Add provider contract tests

---

## Phase 2 — Provider Layer

- [ ] OpenAI-compatible provider
  - [ ] Configurable base URL
  - [ ] API key support
  - [ ] Message conversion
  - [ ] Tool definitions and tool calls
  - [ ] Finish reasons
  - [ ] Usage information
  - [ ] Error handling
  - [ ] Tests
- [ ] OpenAI provider convenience wrapper
- [ ] OpenRouter provider
  - [ ] OpenRouter configuration
  - [ ] Model selection
  - [ ] Tool calls
  - [ ] Usage information
  - [ ] Error handling
  - [ ] Tests
- [ ] Normalize provider errors
  - [ ] Connection errors
  - [ ] Authentication errors
  - [ ] Rate-limit errors
  - [ ] Request errors
  - [ ] Response errors

---

## Phase 3 — Routing

- [ ] Router abstraction
- [ ] Provider/model selection
- [ ] First-available strategy
- [ ] Fallback strategy
- [ ] Priority strategy
- [ ] Provider availability handling
- [ ] Routing errors
- [ ] Routing tests

---

## Phase 4 — Memory

- [ ] Memory abstraction
- [ ] Conversation memory
- [ ] In-memory conversation storage
- [ ] Conversation IDs
- [ ] Clear/reset support
- [ ] Memory integration with `Agent`
- [ ] Memory tests

---

## Phase 5 — Middleware

- [ ] Middleware abstraction
- [ ] Composable middleware pipeline
- [ ] Logging middleware
- [ ] Retry middleware
- [ ] Timing middleware
- [ ] Usage tracking middleware
- [ ] Middleware tests

---

## Phase 6 — Skills

### Web Search

- [ ] Web search skill
- [ ] Search tool
- [ ] DDGS provider
- [ ] Normalized search results
- [ ] Search limits
- [ ] Error handling
- [ ] Web search tests

### Browser

- [ ] Browser abstraction
- [ ] Open URL tool
- [ ] Page retrieval
- [ ] Link clicking
- [ ] Text finding
- [ ] Normalized browser results
- [ ] Browser errors
- [ ] Browser tests

---

## Phase 7 — Advanced Agent Features

### Streaming

- [ ] Streaming API
- [ ] Agent event types
- [ ] Text delta events
- [ ] Tool-call events
- [ ] Iteration events
- [ ] Completion events
- [ ] Streaming tests

### Structured Outputs

- [ ] Structured output API
- [ ] Pydantic model validation
- [ ] Provider integration
- [ ] Structured output errors
- [ ] Structured output tests

### Usage

- [ ] Expose model usage through provider responses
- [ ] Normalize input/output/total token counts
- [ ] Provider usage tests

---

## Phase 8 — Production Hardening

- [ ] Request timeouts
- [ ] Cancellation support
- [ ] Tool timeouts
- [ ] Tool cancellation
- [ ] Maximum tool-call limits
- [ ] Context-size handling
- [ ] Robust concurrent tool execution
- [ ] Deterministic test coverage
- [ ] Edge-case tests
- [ ] Review public API exports
- [ ] Remove dead/accidental code

---

## Phase 9 — CI, Documentation, and Examples

- [ ] Python 3.13 CI coverage
- [ ] Installation documentation
- [ ] Quick-start documentation
- [ ] Provider documentation
- [ ] Custom provider documentation
- [ ] Tool documentation
- [ ] Skill documentation
- [ ] Memory documentation
- [ ] Middleware documentation
- [ ] Routing documentation
- [ ] Streaming documentation
- [ ] Structured output documentation
- [ ] Add `examples/basic_agent.py`
- [ ] Add `examples/ollama.py`
- [ ] Add `examples/openai.py`
- [ ] Add `examples/openrouter.py`
- [ ] Add `examples/custom_tool.py`
- [ ] Add `examples/web_search.py`
- [ ] Add `examples/memory.py`
- [ ] Add `examples/middleware.py`
- [ ] Add `examples/routing.py`

---

## Phase 10 — Alpha Release

- [ ] Final API review
- [ ] Final test suite pass
- [ ] Ruff/lint pass
- [ ] Type-check pass
- [ ] CI pass
- [ ] README review
- [ ] Documentation review
- [ ] Package metadata review
- [ ] Changelog/release notes
- [ ] Version `0.1.0`
- [ ] Create GitHub release
