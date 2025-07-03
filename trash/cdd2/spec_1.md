# CDD2: Covenant-Driven Development Specification

## Purpose

CDD aims to enable LLMs to generate, maintain, and evolve entire codebases autonomously by:

1. **Deterministic context loading**: LLMs need clear rules for what documentation/code to load when generating new code. Filesystem structure + dependency declarations provide this.

2. **Behavioral contracts (covenants)**: Specify what functions do through input/output examples. LLMs generate tests from covenants, then implementation to pass tests.

3. **Rewrite-only philosophy**: When requirements change, rewrite dependent code rather than refactor. Prevents specification drift that confuses LLMs.

4. **Self-contained files**: Each file sized for LLM context windows, comprehensible standalone. No cross-references needed.

The core insight: Traditional codebases evolved through human refactoring are illegible to LLMs. CDD creates structure where LLMs can reliably understand what exists, what's needed, and generate correct code without human intervention.

## Core Tenets

- **Single developer, sequential implementation** - One developer owns entire system evolution
- **Documentation-as-code** - Documentation is executable specification
- **Test-driven development** - Tests generated from behavioral contracts
- **Deterministic context selection** - Unambiguous rules for documentation loading
- **Rewrite-only maintenance** - Replace rather than refactor when contracts change

## Filesystem Structure

```
project/
├── {component}/
│   ├── doc/
│   │   ├── API.md         # Dependencies and exports (rigid format)
│   │   ├── ABSTRACT.md    # Purpose (60 words) + overview (300 words)
│   │   ├── IMPL.md        # Internal algorithms, excluded from external context
│   │   ├── STORY.md       # Usage examples and workflows
│   │   └── concepts/      # Domain knowledge explanations
│   │       └── {concept}.md
│   ├── cov/
│   │   └── {group}/       # Optional grouping for related functions
│   │       └── {function}.cov.md
│   ├── test/
│   │   └── {group}/
│   │       └── {function}.test.ts
│   └── src/
│       └── {module}.ts
```

## API.md Format

```markdown
# Component: {name}

## Dependencies
{component-path}: [{function1}, {function2}, {Type1}]
{component-path}: *  # Import all exports

## Exports

### functionName
- **Signature**: `(param: Type) => ReturnType`
- **Purpose**: Single sentence description
- **Throws**: `ErrorType` when condition

### TypeName
- **Type**: Interface | Enum | Type Alias
- **Purpose**: What this type represents
```

## Covenant Format

```markdown
# {functionName}.cov.md

## Signature
`functionName(param: ParamType): ReturnType`

## Examples
- `functionName(input1)` → `output1`
- `functionName(input2)` → `output2`
- `functionName(edgeCase)` → `expectedOutput`
- `functionName(errorCase)` → throws `ErrorType`
```

## Development Workflow

### Phase 1: Design
1. Create component directory structure
2. Write ABSTRACT.md defining component purpose
3. Draft initial API.md with expected dependencies (may not exist)
4. Document domain concepts in concepts/

### Phase 2: Contract Definition
1. Write behavioral covenants with concrete examples
2. Generate test files from covenants
3. Validate covenant examples are comprehensive

### Phase 3: Implementation
1. Implement functions to pass generated tests
2. Extract shared types to separate components as patterns emerge
3. Update API.md dependencies as implementation reveals needs

### Phase 4: Integration
1. Validate cross-component dependencies
2. Ensure all declared imports exist in target components
3. Update dependent components when contracts change

## Context Loading

### For Implementation
Load in order:
1. Target component's complete doc/ directory
2. Each dependency's API.md exports section (filtered to declared imports)
3. Explicit concept references from dependencies

### For Test Generation
Load only:
1. Covenant file
2. Type definitions from declared dependencies
3. No implementation details or component descriptions

### Dependency Resolution
- Dependencies reference component names, not paths
- Component identity determined by presence of doc/API.md
- No transitive loading - only direct dependencies

## Component Organization

### Standard Components
Contain behavior and types:
- Must have API.md with exports
- Should have covenants and tests
- Implementation in src/

### Type-Only Components
Pure data definitions:
- API.md exports types only
- No covenants or tests needed
- Single src/index.ts file

### Domain Concepts
- Documented in component's doc/concepts/
- Explain "why" not "what"
- Loaded only with owning component

## Validation Rules

### Static Validation
- All declared dependencies must exist
- All imported functions/types must be exported by dependency
- No circular dependencies in component graph
- Covenant examples must parse correctly

### Runtime Validation
- Implementation signatures match covenant signatures
- All covenant examples pass as tests
- No undefined types in public API

## Evolution Patterns

### Adding Functionality
1. Add examples to covenant
2. Regenerate tests
3. Extend implementation
4. Update API.md exports

### Breaking Changes
1. Create new component version
2. Rewrite dependent components
3. No in-place refactoring

### Missing Dependencies
When depending on non-existent component:
1. Continue development with assumed interface
2. Validation warnings until dependency exists
3. Manual stub creation when needed

## Constraints

- No component renames after first implementation
- All components in repository share same version
- No parallel development protocol defined
- Bootstrap order determined by developer judgment

## Unresolved Design Decisions

### Test Fixtures
Shared test data location unspecified. Options:
- Duplicate in each component's test/
- Separate test-fixtures/ component
- Embed in covenant examples

### Error Types
Shared error types ownership unclear when multiple components throw same errors.

### Documentation Examples
No specification for whether code examples in API.md require validation.

### Circular Dependencies
Permitted during development but discouraged. Resolution strategy undefined.