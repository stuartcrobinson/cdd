# XD5 (eXplicit Dependencies in Documentation- and Data-Driven Development) Reference

## Purpose

XD5 enables LLMs to generate correct, maintainable code by making all dependencies explicit at the documentation level. Before any code exists, a complete dependency graph is parseable from documentation alone.

**Core principle**: Documentation is the authoritative source of truth - a living contract that evolves during development but always leads implementation. When documentation changes, code must follow.

## Core Tenets

- **Documentation is authoritative** - Living contract that evolves but always leads code
- **Explicit dependencies only** - Every import/reference must be declared in API.md
- **Data-driven tests** - Test cases live in external files, not code
- **Linear development flow** - Design → Test → Implement phases
- **Deterministic context loading** - LLMs can predict exactly what files are needed
- **Semantic dependency declaration** - If A requires understanding C's behavior (not just B's interface), declare C explicitly

## Structure
```
<repo>/
├── [package manifest]
└── proj/                 # Root component
    ├── doc/
    │   ├── API.md        # CRITICAL: All dependencies and exports declared here
    │   ├── ABSTRACT.md   # 60-word purpose + 300-word overview
    │   └── ARCH.md       # Technical decisions, constraints, patterns
    ├── test-data/        # Test cases as data
    │   └── {path}/
    │       └── {function}.json  # or .md
    ├── test/             # Minimal harnesses that load test-data
    │   └── {path}/
    │       └── {function}.[test-ext]
    ├── test-intn/        # Integration tests for declared dependencies
    │   └── {dep-path}/   # Verify deps exist at runtime
    ├── src/
    │   └── {path}.[ext]
    └── comp/             # Sub-components (recursive structure)
```

## API.md Format (The Dependency Graph)

```markdown
# Component: {component-name}

## Component Type
standard | types-only

## Dependencies
[CRITICAL: This section defines the parseable dependency graph]
proj/comp/{other-component}: [{Import1}, {Import2}]
proj/comp/{types-component}: *  # Import all
external/{package}: [{Import1}]  # External deps must be explicit too

## Exports
### {functionName}
- **Signature**: `{functionName}(param: Type) -> ReturnType`
- **Purpose**: Single sentence.
- **Throws**: `{ErrorType}` when {condition}
- **Test-data**: `test-data/{path}/{functionName}.json`

### {TypeName}
- **Type**: `type {TypeName} = {definition}`
- **Purpose**: Single sentence.
```

## Test Data Format

Tests read cases from external files, never embed them:

**JSON format** (`test-data/utils/validateCard.json`):
```json
{
  "cases": [
    {
      "name": "valid visa",
      "input": ["4111111111111111"],
      "expected": {"valid": true}
    },
    {
      "name": "empty string",
      "input": [""],
      "throws": "ValidationError"
    }
  ]
}
```

**Test harness** (`test/utils/validateCard.test.js`):
```javascript
import testCases from '../../test-data/utils/validateCard.json';
import {validateCard} from '../../src/utils';

testCases.cases.forEach(tc => {
  test(tc.name, () => {
    if (tc.throws) {
      expect(() => validateCard(...tc.input)).toThrow(tc.throws);
    } else {
      expect(validateCard(...tc.input)).toEqual(tc.expected);
    }
  });
});
```

## Workflow


### Overview
Top-down design with bottom-up implementation. Start with component-level behavior, decompose into functions, implement functions first, then compose.

### Phases

#### 1. Documentation Phase
- Write ABSTRACT.md, ARCH.md, API.md
- Declare all dependencies and exports in API.md
- Documentation is provisional - expect updates during implementation

#### 2. E2E Test Design (Provisional)
- Write component-level test cases in `test-data/component.json`
- These are *hypothesis* - expect refinement after decomposition
- Focus on external behavior, not implementation

#### 3. Pseudocode & Decomposition
```
// Write rough implementation
// Identify pure functions
// Extract them as comments:
  // extractedFn: validateInput(x) -> bool
  // extractedFn: transformData(data) -> processed
// What remains is coordination logic
```

#### 4. Unit Test Design
- Create test cases for each extracted function
- `test-data/utils/validateInput.json`
- These tests are more stable than E2E tests

#### 5. Function Implementation (Red/Green)
- Implement each pure function
- Run tests - they must fail first
- Fix implementation until green
- **NEVER edit test data** - only fix code
- **If implementation reveals documentation errors:**
  - STOP immediately
  - Update API.md/ARCH.md to reflect reality
  - Continue implementation with correct docs

#### 6. E2E Test Revision
- Review original E2E tests against current documentation
- Update E2E test data to match documented behavior
- This revision is expected - initial E2E tests were hypotheses

#### 7. Component Implementation
- Wire together tested functions
- Implement coordination logic
- Run E2E tests (red phase)
- Debug until green
- If new documentation issues found, repeat stop/update cycle

### Critical Rules

#### Test Immutability
- Once test harness is written, it's frozen
- Test data can ONLY change with explicit human approval
- Exception: E2E test revision in step 6
- If test seems wrong: **"I believe test case X may be incorrect because Y. Should I update it?"**

#### Documentation Authority
- Documentation changes flow: Doc → Test Data → Code
- **Documentation breakage is P0**: Fix immediately upon discovery
- Never work against known-incorrect documentation
- If implementation reveals doc errors, stop and fix docs
- Frequent doc updates suggest design flaws - valuable signal

#### Debug Protocol
- Test fails? Fix code, not test
- Multiple fixes attempted? Consider test error
- Request approval before any test modification

### Example Flow

1. **Doc**: `API.md` declares `processPayment(card, amount) -> Result`
2. **E2E test data**: Happy path + edge cases
3. **Pseudocode** reveals: validate → calculate → charge
4. **Extract**: `validateCard()`, `calculateFees()`, `chargeCard()`
5. **Unit tests**: Comprehensive cases for each function
6. **Implement functions**: Red/green each
   - Discover: fees include tax not documented
   - **STOP**: Update API.md with tax behavior
7. **Revise E2E**: Update to match corrected documentation
8. **Implement component**: Compose the tested functions

---




---





## Critical Rules

- **Declared dependencies are contracts** - If it's not in API.md, it doesn't exist
- **Documentation leads implementation** - Update docs before code when discoveries occur
- **Test data is external** - No test logic/cases in code files
- **Test harnesses are immutable** - Once written, test code doesn't change
- **Each file self-contained** - Must fit in LLM context window
- **No circular runtime dependencies** - Documentation can reference circularly
- **Types-only components** - Have no test/ or src/, only doc/

### Semantic Dependencies
If component A's correct usage requires understanding transitive dependency C's behavior (not just B's interface), A must declare C explicitly. This documents abstraction leakage - when B's wrapping of C is incomplete.

## Path Conventions

- ALL paths relative to `<repo>/`
- Component paths: `proj/comp/{name}`
- Nested: `proj/comp/{parent}/comp/{child}`
- Test-intn naming: Convert slashes to hyphens

## Why This Works for LLMs

1. **Predictable context** - Given a task, the LLM knows exactly which files to request
2. **No hidden dependencies** - Everything needed is explicitly declared
3. **Documentation-first** - LLMs excel at following specifications
4. **Data-driven tests** - LLMs can generate/modify test cases without touching code
5. **Sequential development** - No complex merge resolution

The dependency graph in documentation is the architecture. Code is just the implementation detail.