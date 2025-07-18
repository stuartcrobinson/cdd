# Covenant-Driven Development (CDD) Reference for LLMs

## Purpose

This reference enables LLMs to generate correct CDD-structured code. CDD creates codebases that LLMs can reliably understand and evolve autonomously.

**Core insight**: Traditional codebases evolved through human refactoring are illegible to LLMs. CDD provides structure for deterministic, autonomous code generation.

**How CDD works**:

1. **Behavioral contracts (covenants)**: Specify what functions do through input/output examples
2. **Generated tests**: LLMs generate tests from covenants, which then drive implementation
3. **Deterministic dependencies**: Explicit imports enable predictable context loading
4. **Regeneration over refactoring**: When covenants change, regenerate tests. When tests fail, fix implementation. This maintains the covenant → test → implementation chain of truth

Each file is self-contained for LLM context windows, with no implicit cross-references.


## Core Tenets

- **Single developer, sequential implementation** - One developer owns entire system evolution
- **Documentation-as-code** - Documentation is executable specification
- **Covenant as sacred bond** - Covenants are inviolable contracts. Tests must exactly implement covenant behaviors, and code must pass these tests
- **Test-driven development** - Tests are written before code. Tests must fail first, then implementation makes them pass
- **Behavior-driven development** - Tests generated from behavioral contracts
- **Deterministic context selection** - Unambiguous rules for documentation loading

## Workflow
1. Write component docs (API.md, ABSTRACT.md, ARCH.md)
2. Write covenants (.cov.md) - behavioral contracts as examples
3. Generate tests from covenants (will fail initially - TDD)
4. Implement code to pass tests
5. Generate integration tests for declared dependencies
6. Never modify generated tests - fix covenants or implementation

## Structure
```
<repo>/
├── package.json         # External npm deps only
└── proj/                # Root component
    ├── doc/
    │   ├── API.md       # Exports & dependencies
    │   ├── ABSTRACT.md  # 60-word purpose + 300-word overview
    │   └── ARCH.md      # Tech decisions, constraints, patterns
    ├── cov/             # Behavioral contracts
    │   └── {path}/
    │       └── {function}.cov.md
    ├── test/            # Generated from covenants
    │   └── {path}/
    │       └── {function}.test.ts
    ├── test-intn/       # Verify dependencies exist at runtime
    │   └── {dep-path}/  # Full path, slashes → hyphens
    ├── src/
    │   └── {path}.ts
    └── comp/            # Sub-components (same structure)
```

## Path Rules
- **ALL paths relative to `<repo>/`**
- Example deps: `proj/comp/{your-component}`
- Example nested: `proj/comp/{parent}/comp/{child}`
- Test-intn naming: `proj-comp-payment` (slashes→hyphens)

## API.md Format
```markdown
# Component: {component-name}

## Component Type
standard | types-only

## Dependencies
proj/comp/{other-component}: [{Import1}, {Import2}]
proj/comp/{types-component}: *  # Import all

## Exports
### {functionName}
- **Signature**: `(param: Type) => ReturnType`
- **Purpose**: Single sentence.
- **Throws**: `{ErrorType}` when {condition}
- **Re-export from**: `proj/comp/{source}` (if re-exporting)

### {TypeName}
- **Type**: `{typescript definition}`
- **Purpose**: Single sentence.
```

## Covenant Format (Example)
**Purpose**: Hand-written behavioral contracts that generate tests
```markdown
## Signature
`validateCard(card: string): ValidationResult`

## Examples
- `validateCard("4111111111111111")` → `{valid: true}`
- `validateCard("")` → throws `ValidationError`
```
Min: 1 happy + 1 per throw

## Key Rules
- No transitive dependencies - declare all direct imports
- No circular runtime deps (but docs can be circular)
- Types-only components: no cov/ or test/
- Covenants are truth - never edit generated tests
- Change covenant → regenerate test → fix implementation
- Integration tests verify dependency contracts at runtime
- Each file self-contained for context window
- Tests must fail first before implementation (TDD)
