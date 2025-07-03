# Purpose:

CDD aims to enable LLMs to generate, maintain, and evolve entire codebases autonomously by:

1. **Deterministic context loading**: LLMs need clear rules for what documentation/code to load when generating new code. Filesystem structure + dependency declarations provide this.

2. **Behavioral contracts (covenants)**: Specify what functions do through input/output examples. LLMs generate tests from covenants, then implementation to pass tests.

3. **Rewrite-only philosophy**: When requirements change, rewrite dependent code rather than refactor. Prevents specification drift that confuses LLMs.

4. **Self-contained files**: Each file sized for LLM context windows, comprehensible standalone. No cross-references needed.

The core insight: Traditional codebases evolved through human refactoring are illegible to LLMs. CDD creates structure where LLMs can reliably understand what exists, what's needed, and generate correct code without human intervention.

The tensions arise because this vision assumes stable specifications and known dependencies - but software development is inherently exploratory. CDD hasn't resolved how to handle the discovery phase where requirements and relationships emerge through implementation.


# CDD2: Covenant-Driven Development Specification

## Core Tenets
- **Single developer, sequential implementation**
- **Documentation-as-code**: Documentation is source of truth
- **Test-driven development**: Tests generated from behavioral contracts
- **Deterministic context selection**: Clear rules for what documentation to load
- **Rewrite-only**: No refactoring during maintenance phase

## Filesystem Structure
```
project/
├── {component}/
│   ├── doc/
│   │   ├── API.md         # Rigid format: dependencies, exports
│   │   ├── ABSTRACT.md    # Purpose (60 words) + overview (300 words)
│   │   ├── IMPL.md        # Internal algorithms, not for external context
│   │   └── STORY.md       # Usage examples, workflows
│   ├── cov/
│   │   └── {function}.cov.md  # Behavioral contracts with examples
│   ├── test/
│   │   └── {function}.test.ts # Generated from covenants
│   └── src/
│       └── {module}.ts    # Implementation
```

## API.md Format (Rigid)
```markdown
# {component}/doc/API.md

## Dependencies
fraud: [checkRisk, RiskLevel]
auth: [validateToken]

## Exports

### functionName
- **Signature**: `(param: Type) => ReturnType`
- **Purpose**: Single sentence description
- **Throws**: ErrorType when condition
```

## Development Workflow

### 1. Design Phase
- Write component ABSTRACT.md files
- Declare dependencies in API.md (may reference non-existent components)
- Tooling generates stub API.md for missing dependencies

### 2. Contract Phase
- Write covenants with input/output examples
- Generate test files from covenants
- Tests see only: covenant + imported type definitions

### 3. Implementation Phase
- Implement code to pass tests
- Extract types to component dependencies after patterns emerge
- No cross-component refactoring

## Context Loading Rules

**For implementation**: Load target component's full doc/ + declared dependencies' API.md exports (filtered to imported items only)

**For tests**: Load covenant + type definitions only

**No transitive loading**: Dependencies loaded one level deep

## Validation

Tooling validates documentation consistency:
- Declared imports exist in dependency exports
- Referenced types are imported or defined
- No circular dependencies (when detectable)
- Signature types match covenant examples

## Constraints

- Component renames out of scope
- No versioning within repository
- Accepts invalid states during development
- No concurrent development protocol
- Types organized as regular components with dependencies

## Critical Unresolved Issues

1. **Bootstrap ordering**: Which component to implement first when A needs B needs A
2. **Breaking change cascade**: When API changes propagate through dependents
3. **Stub generation ownership**: Who decides interface when generating missing dependencies

..........

i mean we still need some fs structure.  to have stardized docs files formats and test and covs and src locations.  

and we need to think about how to adapt this "concepts" idea to CDD2


    │   │   ├── concepts/            # Domain concepts
    │   │   │   └── authorization.md
Edit
Filesystem Structure Still Needed
Yes. Standardized locations within each component:

{component}/
├── doc/
│   ├── API.md
│   ├── ABSTRACT.md
│   └── concepts/        # Key addition
├── cov/
├── test/
└── src/
Concepts in CDD2
Original CDD buried concepts deep (main/core/doc/concepts/authorization.md). Should be component-level:

payment/doc/concepts/
├── transaction-lifecycle.md
├── idempotency.md
└── retry-policy.md

fraud/doc/concepts/
├── risk-scoring.md
└── ml-model.md
Purpose: Explain domain knowledge needed to understand component's behavior. Not API reference - the "why" behind the "what".

Context Loading Rules for Concepts
When loading payment context:

Always include payment/doc/concepts/*
Never include dependency concepts (fraud/doc/concepts/*)
Exception: If API.md explicitly references concept: See fraud/doc/concepts/risk-scoring.md
Unresolved: Concept Granularity
What deserves its own concept file vs. section in API.md?

Threshold: Multiple functions share same domain model
Counter: Fragments understanding across files
Reality: Subjective judgment call
Alternative: Concepts as Components
concepts/
├── transaction/
│   └── doc/API.md    # Exports: Transaction type, lifecycle states
├── risk-model/
│   └── doc/API.md    # Exports: RiskScore type, scoring algorithm docs
Payment depends on concepts/transaction. Fraud depends on concepts/risk-model.

Problem: Concepts aren't executable. No src/, no tests. Breaks component uniformity.




lets work on this "CDD2: Covenant-Driven Development Specification" as an artifact.  so its easier to edit.  regenerate it as an artifact but also update it appropriately given our latest decisions.  and keep it lean but also make sure it is comprehensive and complete for eveyrting about CDD2 an a standalone dev philosophy (like it should never reference the prior CDD etc)

Edit

CDD2: Covenant-Driven Development Specification
Document 
I've created the CDD2 specification as a comprehensive standalone document. Key updates from our discussion:

Removed "filesystem provides navigation" - Components now use explicit dependency declarations
Added component identity section - Component name declared in API.md header
Clarified concepts location - Component-level, not buried in nested structure
Specified function grouping - Optional subdirectories in cov/ and test/
Distinguished component types - Standard vs type-only components
Notable decisions embedded:

No component renames (avoiding the refactoring problem)
Single developer assumption made explicit
Validation as informational, not blocking
Concepts never auto-loaded from dependencies
Left unresolved:

Test fixture sharing strategy
Shared error type ownership
Circular dependency resolution
The spec assumes incremental development with temporary invalid states, acknowledging the reality of exploratory design while maintaining structure for LLM context loading.