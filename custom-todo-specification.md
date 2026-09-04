# TODO.md Specification

This document defines the specification for the custom `TODO.md` format.

## Origin

The format is inspired by [todo-md/todo-md](https://github.com/todo-md/todo-md).

The format is intentionally minimal and builds on standard Markdown syntax.

## File Placement

A `TODO.md` file may be placed in any folder within a project repository.

Multiple `TODO.md` files may therefore exist at different levels of the repository.

## Header

The first non-whitespace line of a `TODO.md` file must be one of:

```md
# TODO
```

or:

```md
# TODO.md
```

The top-level TODO header identifies the document as a `TODO.md` file.

## Content After the Header

Paragraphs and other non-task content appearing after the top-level TODO header are informational content.

They are not tasks.

They may be used for descriptions, notes, explanations, or other contextual information.

Informational content does not have a task status.

## Sections

Each Markdown subheader below the top-level TODO header defines a TODO section.

Sections group related tasks together.

Example:

```md
# TODO

## Parser

- [ ] Implement the parser

## Tests

- [ ] Add parser tests
```

Heading hierarchy is preserved. For example, a `###` heading may be used as a subsection of a `##` section.

## Tasks

A TODO task is a Markdown unordered-list item whose content begins with one of the supported checkbox states:

```md
- [ ] Task
- [x] Task
- [-] Task
```

Tasks may appear inside sections or directly after the top-level TODO header.

A task may contain additional text after its checkbox.

## Task Status

The checkbox value determines the task status.

| Status | Meaning |
| --- | --- |
| `[ ]` | The task is not yet done or is currently a work in progress |
| `[x]` | The task is completed |
| `[-]` | The task was cancelled or declined |

No other checkbox values are valid TODO task statuses.

## Nested Tasks

Tasks may be nested using standard Markdown indentation.

A nested task is treated as a subtask of its nearest parent task.

Example:

```md
# TODO

## Parser

- [ ] Implement parser
  - [ ] Parse headers
  - [ ] Parse task metadata
- [ ] Add parser tests
```

The two indented tasks are subtasks of `Implement parser`.

## Metadata

Tasks may contain metadata.

Two metadata forms are currently supported:

```text
@USERNAME
#TAG
```

`@USERNAME` assigns a task to a person.

`#TAG` associates a task with a topic or category.

Example:

```md
- [ ] Implement parser @alice #parser
```

A task may contain zero or more metadata entries of either type.

Example:

```md
- [ ] Review parser design @alice @bob #parser #architecture
```

Metadata belongs to the task on which it appears.

## Task Text and Metadata

Metadata may appear anywhere in a task's textual content where it can be recognized as a metadata token.

The remaining text is the task description.

Example:

```md
- [ ] Implement the parser @alice #parser
```

Task description:

```text
Implement the parser
```

Assignee:

```text
@alice
```

Tag:

```text
#parser
```

## Non-task Content

Any content that is not a recognized task or section heading is treated as informational content.

Example:

```md
# TODO

This project needs better test coverage.

## Testing

Before release, all new features should have tests.

- [ ] Add missing tests
```

The first two paragraphs are notes, while only the checkbox line is a task.

## Whitespace and Markdown

The format uses Markdown as its base syntax.

Leading whitespace and indentation may be used for nested tasks and ordinary Markdown formatting.

Task checkboxes must use one of the three supported status values exactly:

```text
[ ]
[x]
[-]
```

## Parsing Rules

A TODO parser should:

1. Read the document as Markdown-oriented text.
2. Require the first non-whitespace line to be `# TODO` or `# TODO.md`.
3. Recognize Markdown headings below the top-level header as sections.
4. Recognize unordered-list items beginning with `[ ]`, `[x]`, or `[-]` as tasks.
5. Preserve task nesting based on Markdown indentation.
6. Recognize `@USERNAME` metadata as an assignee.
7. Recognize `#TAG` metadata as a tag.
8. Treat all other content as informational text.
9. Preserve the original section and task hierarchy.

Unknown or unsupported checkbox values do not represent valid TODO tasks.

## Minimal Example

```md
# TODO

A small project task list.

## Development

- [ ] Implement parser @alice #parser
  - [ ] Parse sections
  - [ ] Parse metadata
- [x] Set up repository
- [-] Investigate deprecated approach

## Documentation

- [ ] Write specification #docs
```

## Design Goals

The format is intended to remain:

- minimal
- human-readable
- Markdown-compatible
- easy to parse
- easy to edit manually
- suitable for both humans and developer tooling

Future extensions should preserve these properties whenever practical.
