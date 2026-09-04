# TODO.md

Pygent development tasks and roadmap.

## Completed

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
- [x] Conversation memory
- [x] Middleware abstraction and pipeline
- [x] Streaming API and agent events
- [x] Model usage representation
- [x] Request timeout support
- [x] Maximum tool-call limits
- [x] Concurrent tool execution
- [x] CLI configuration system
- [x] CLI localization foundation
- [x] Configuration formatting and value formatting
- [x] GitHub Actions test workflow
- [x] GitHub Actions lint/type-check workflow

## Work in Progress

### Core

- [ ] Provider contract tests
  - [ ] Common provider behavior
  - [ ] Message conversion
  - [ ] Tool-call behavior
  - [ ] Finish reasons
  - [ ] Usage handling
  - [ ] Error normalization
  - [ ] Provider lifecycle
- [ ] Improve agent context handling
- [ ] Review agent/tool loop edge cases
- [ ] Add comprehensive agent-loop tests
- [ ] Add deterministic concurrency tests
- [ ] Review public API exports
- [ ] Remove dead/accidental code

### Router

- [ ] Router abstraction
- [ ] Provider/model selection
- [ ] First-available strategy
- [ ] Fallback strategy
- [ ] Priority strategy
- [ ] Provider availability handling
- [ ] Routing errors
- [ ] Routing tests

### Memory

- [x] Memory abstraction
- [x] Conversation memory
- [x] In-memory conversation storage
- [x] Conversation IDs
- [x] Clear/reset support
- [x] `Agent` integration
- [ ] Memory tests
- [ ] Define memory lifecycle semantics
- [ ] Document memory behavior

### Middleware

- [x] Middleware abstraction
- [x] Composable middleware pipeline
- [ ] Logging middleware
- [ ] Retry middleware
- [ ] Timing middleware
- [ ] Usage tracking middleware
- [ ] Middleware tests
- [ ] Middleware ordering tests
- [ ] Middleware exception propagation tests

### Streaming

- [x] Streaming API
- [x] Agent event types
- [x] Text delta events
- [x] Iteration events
- [x] Completion events
- [ ] Tool-call delta events
- [ ] Streaming provider integration
- [ ] Streaming cancellation
- [ ] Streaming tests
- [ ] Define streaming API stability guarantees

### Structured Outputs

- [ ] Structured output API
- [ ] Pydantic model validation
- [ ] Provider integration
- [ ] Structured output errors
- [ ] Structured output tests
- [ ] Define provider fallback behavior
- [ ] Document supported response formats

### Web Search

- [ ] Web search skill
- [ ] Search tool
- [ ] DDGS provider
- [ ] Normalized search results
- [ ] Search limits
- [ ] Error handling
- [ ] Web search tests
- [ ] Result metadata normalization
- [ ] Safe query handling

### Browser

- [ ] Browser abstraction
- [ ] Open URL tool
- [ ] Page retrieval
- [ ] Link clicking
- [ ] Text finding
- [ ] Normalized browser results
- [ ] Browser errors
- [ ] Browser tests
- [ ] Request limits
- [ ] Resource cleanup

### Production Hardening

- [x] Request timeout support
- [x] Maximum tool-call limits
- [x] Basic concurrent tool execution
- [ ] Cancellation support
- [ ] Tool timeouts
- [ ] Tool cancellation
- [ ] Context-size handling
- [ ] Robust concurrent tool execution
- [ ] Retry/backoff policy
- [ ] Connection/resource lifecycle handling
- [ ] Graceful shutdown
- [ ] Exception chaining and diagnostics
- [ ] Deterministic test coverage
- [ ] Edge-case tests
- [ ] Stress/concurrency tests

### Usage and Observability

- [x] Provider usage model
- [x] Input token normalization
- [x] Output token normalization
- [x] Total token normalization
- [ ] Provider usage tests
- [ ] Usage aggregation across iterations
- [ ] Usage aggregation across tool loops
- [ ] Optional request timing metadata
- [ ] Structured execution diagnostics

### Configuration and CLI

- [x] TOML configuration loading
- [x] Environment-variable configuration
- [x] Configuration formatting
- [x] Configuration localization
- [ ] Complete CLI localization
- [ ] `config list --section`
- [ ] `config list --via`
- [ ] Configuration source filtering
- [ ] Configuration validation diagnostics
- [ ] Configuration tests
- [ ] CLI integration tests

### Testing and Quality

- [ ] Fix Ruff/isort import sorting locally
- [ ] Verify CI passes after local Ruff fixes
- [ ] Full provider test matrix
- [ ] Agent integration test suite
- [ ] Tool integration test suite
- [ ] Memory test suite
- [ ] Middleware test suite
- [ ] Streaming test suite
- [ ] Structured output test suite
- [ ] Configuration/CLI test suite
- [ ] Error-path coverage
- [ ] Cancellation tests
- [ ] Timeout tests
- [ ] Resource cleanup tests
- [ ] Python 3.12 test coverage
- [ ] Python 3.13 test coverage

## Planned

### API Stabilization

- [ ] Review all public exports
- [ ] Review naming consistency
- [ ] Review async API conventions
- [ ] Review exception hierarchy
- [ ] Review provider interface stability
- [ ] Review tool interface stability
- [ ] Review event model stability
- [ ] Define backwards-compatibility policy
- [ ] Remove experimental APIs that should not be public

### Documentation

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

### Examples

- [ ] `examples/basic_agent.py`
- [ ] `examples/ollama.py`
- [ ] `examples/openai.py`
- [ ] `examples/openrouter.py`
- [ ] `examples/custom_provider.py`
- [ ] `examples/custom_tool.py`
- [ ] `examples/web_search.py`
- [ ] `examples/browser.py`
- [ ] `examples/memory.py`
- [ ] `examples/middleware.py`
- [ ] `examples/routing.py`
- [ ] `examples/streaming.py`
- [ ] `examples/structured_output.py`

### CI and Packaging

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

### Alpha Release

- [ ] Final API review
- [ ] Final test suite pass
- [ ] Ruff/lint pass
- [ ] Type-check pass
- [ ] CI pass
- [ ] README review
- [ ] Documentation review
- [ ] Package metadata review
- [ ] Changelog/release notes
- [ ] Select final alpha version
- [ ] Create GitHub release
- [ ] Publish package
- [ ] Verify installation from published package

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
