# Architecture: context-bundler

## Data Flow
1. Parse target filepath → extract component name, file type
2. Determine loading strategy from file type
3. Load component documentation per strategy rules
4. Extract dependency declarations from API.md
5. Load each dependency's API.md
6. Filter dependency exports to declared imports only
7. Extract and load concept file references (depth 1)
8. Assemble ordered markdown with source annotations

## Key Patterns
- **Path-based component identification**: Filesystem structure determines component boundaries
- **Declaration-driven filtering**: API.md dependencies control what's loaded
- **Type-directed loading**: File extension determines documentation subset

## Technology Decisions
- **Markdown parsing**: Required for dependency extraction and link resolution
  - Chosen for: Structured access to CDD's declaration format
  - Constraints: Must handle malformed markdown gracefully
  - Alternatives considered: Regex (brittle with nested markdown)

## Integration Points
- Filesystem: Read-only access to project documentation
- No network dependencies
- No state persistence between runs

## Constraints
- Context window limits: Output must fit LLM constraints (~100k tokens)
- No implicit imports: Cannot infer undeclared dependencies
- Unidirectional loading: No reverse dependency information

## State Management
Stateless - each invocation computes context from scratch.

## Error Handling Strategy

### FAIL (throw Error)
- Target file doesn't exist
- Target file outside any component
- Target component missing doc/API.md

### WARN (include in output) 
- Dependency component doesn't exist
- Dependency API.md malformed/unparseable
- Circular dependency detected (after first occurrence)
- Import not found in dependency's exports
- Target component missing required ARCH.md or ABSTRACT.md

### CONTINUE (silent)
- doc/adr/* files (human-only, skip)
- Empty directories
- Non-markdown files in doc/

This approach supports incremental development where dependencies may not exist yet, while failing fast on critical issues that prevent any meaningful context generation.