# Pygentix TODO & Roadmap

> Living development checklist for Pygent (`pygent`).
>
> The project is currently in **alpha**. Keep the core small and stable before adding a large feature surface.

## Current milestone — Core Foundation

### CI / Quality

- [x] Add GitHub Actions test workflow
- [x] Add GitHub Actions lint/type-check workflow
- [ ] Verify CI passes on PR #2
- [ ] Fix any Ruff/mypy/test failures reported by CI
- [ ] Add Python 3.13 CI coverage

### Agent runtime

- [x] Define provider-neutral `Message`
- [x] Define provider-neutral `ModelResponse`
- [x] Define provider-neutral `ToolCall`
- [x] Define provider-neutral `ToolDefinition`
- [x] Define `ToolResult`
- [x] Define `Provider` interface
- [x] Implement basic `Agent`
- [x] Implement model/tool interaction loop
- [x] Add maximum iteration protection
- [x] Normalize tool execution failures
- [ ] Add richer `AgentContext` integration
- [ ] Preserve usage/model metadata in `AgentResponse`
- [ ] Define cancellation/timeout behavior

### Tools

- [x] Implement `Tool` abstraction
- [x] Implement `ToolRegistry`
- [x] Implement tool-call execution helper
- [ ] Support convenient function-to-tool registration
- [ ] Validate tool arguments against JSON Schema
- [ ] Improve structured tool errors
- [ ] Decide whether tool calls should execute sequentially or concurrently
- [ ] Add tests for multiple tool calls in one model response

## Providers

### Ollama

- [ ] Implement `OllamaProvider`
- [ ] Support local model selection
- [ ] Map messages to Ollama requests
- [ ] Map tool calls to Pygent types
- [ ] Map usage/finish information when available
- [ ] Add mocked provider tests
- [ ] Document local Ollama setup

### OpenAI-compatible

- [ ] Implement `OpenAICompatibleProvider`
- [ ] Support configurable base URL
- [ ] Support API key authentication
- [ ] Support model selection
- [ ] Map tool definitions/calls
- [ ] Add mocked HTTP tests

### OpenRouter

- [ ] Implement dedicated `OpenRouterProvider`
- [ ] Use the official OpenRouter Python SDK
- [ ] Support model selection
- [ ] Preserve provider-specific metadata where useful
- [ ] Add mocked provider tests

### Future providers

- [ ] OpenAI
- [ ] Anthropic
- [ ] Google Gemini

## Routing

- [ ] Define `Router` interface
- [ ] Define provider/model route configuration
- [ ] Implement explicit provider selection
- [ ] Implement fallback routing
- [ ] Implement simple strategy abstraction
- [ ] Add routing tests
- [ ] Define behavior for provider failures and retries

## Memory

- [ ] Define memory interface
- [ ] Implement in-memory conversation history
- [ ] Implement conversation/session abstraction
- [ ] Connect memory to `Agent.run()`
- [ ] Add configurable history limits
- [ ] Consider persistent memory as a separate optional feature

## Middleware

- [ ] Define middleware interface
- [ ] Implement middleware execution chain
- [ ] Add logging middleware
- [ ] Add retry middleware
- [ ] Define middleware error semantics
- [ ] Add middleware tests

## Skills

### Web search

- [ ] Define skill abstraction
- [ ] Define web-search provider interface
- [ ] Implement DuckDuckGo/`ddgs` provider
- [ ] Add search tool
- [ ] Add result normalization
- [ ] Add tests with mocked search results

### Browser

- [ ] Define browser skill
- [ ] Implement Playwright adapter
- [ ] Add navigation tool
- [ ] Add page-content extraction
- [ ] Add safe resource/time limits
- [ ] Add browser tests where practical

## Public API / Developer Experience

- [ ] Review all public exports
- [ ] Add type aliases where they improve readability
- [ ] Add clear exception hierarchy
- [ ] Improve docstrings for public classes/functions
- [ ] Add examples directory
- [ ] Keep README quick start synchronized with the real API
- [ ] Add API documentation with MkDocs
- [ ] Document optional dependencies

## Testing

- [ ] Add unit tests for all core public classes
- [ ] Add provider contract tests
- [ ] Add tool-loop edge-case tests
- [ ] Test empty model responses
- [ ] Test repeated tool calls until the iteration limit
- [ ] Test multiple tool calls in one response
- [ ] Test malformed tool arguments
- [ ] Test provider exceptions
- [ ] Test cancellation behavior
- [ ] Add coverage reporting if useful

## Security / Reliability

- [ ] Treat model-generated tool arguments as untrusted input
- [ ] Avoid executing arbitrary functions without explicit registration
- [ ] Add configurable tool execution timeouts
- [ ] Define limits for tool output size
- [ ] Define limits for conversation/context size
- [ ] Avoid leaking API keys or sensitive provider data in logs
- [ ] Document browser/tool security considerations

## Release readiness

- [ ] Finish PR #2 core foundation
- [ ] Ensure CI is green
- [ ] Review public API for breaking design mistakes
- [ ] Add a small end-to-end example
- [ ] Update README to match implementation
- [ ] Add changelog/release notes
- [ ] Decide alpha release/versioning policy
- [ ] Publish first alpha package

## Ideas / Later

- [ ] Streaming responses
- [ ] Structured output / typed model responses
- [ ] Tool-call parallelism
- [ ] Persistent memory backends
- [ ] Event hooks / observability
- [ ] OpenTelemetry integration
- [ ] Token/context budgeting
- [ ] Agent-to-agent workflows
- [ ] Plugin/extension discovery
- [ ] Evaluation/test harness for agents

## Development principles

1. **Provider-neutral core first.** Provider-specific behavior belongs behind provider adapters.
2. **Small abstractions.** Do not add an interface unless it solves a real problem.
3. **Async-first.** Agent execution and providers should remain naturally async.
4. **Tools are untrusted boundaries.** Validate model-generated input and constrain execution.
5. **Test behavior, not implementation details.** Provider tests should mock external APIs.
6. **Keep optional dependencies optional.** Installing Pygent should not require every provider or skill.
7. **README follows reality.** Experimental/future functionality must not be presented as implemented.
8. **One coherent feature per commit where practical.** Keep PR #2 reviewable while allowing additional commits.
