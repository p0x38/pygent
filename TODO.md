# TODO.md

Pygent development tasks and roadmap.

## Current Queue

### 1. Core Correctness

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

### 2. Usage and Observability

- [ ] Provider usage tests
- [ ] Usage aggregation across iterations
- [ ] Usage aggregation across tool loops
- [ ] Optional request timing metadata
- [ ] Structured execution diagnostics

### 3. Web Search and Browser Completion

- [ ] Link clicking
- [ ] Text finding
- [ ] Normalized browser results
- [ ] Browser-specific errors
- [ ] Browser tests
- [ ] Browser resource cleanup
- [ ] Search/browser agent tools

### 4. API Stabilization

- [ ] Review all public exports
- [ ] Review naming consistency
- [ ] Review async API conventions
- [ ] Review exception hierarchy
- [ ] Review provider interface stability
- [ ] Review tool interface stability
- [ ] Review event model stability
- [ ] Define backwards-compatibility policy
- [ ] Remove experimental APIs that should not be public

### 5. Documentation and Examples

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

### 6. CI and Packaging

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
- [ ] Verify CI passes after local Ruff fixes

### 7. Alpha Release

- [ ] Final API review
- [x] Final test suite pass
- [x] Ruff/lint pass
- [x] Type-check pass
- [ ] CI pass
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
