# CDD: Covenant-Driven Development Specification

TODO this needs to be edited to be made language-agnostic, like the CDD_ref.md is now

## Purpose

CDD aims to enable LLMs to generate, maintain, and evolve entire codebases autonomously by:

1. **Deterministic context loading**: LLMs need clear rules for what documentation/code to load when generating new code. Filesystem structure + dependency declarations provide this.

2. **Behavioral contracts (covenants)**: Specify what functions do through input/output examples. LLMs generate tests from covenants, then implementation to pass tests.

3. **Regeneration over refactoring** - When covenants change, regenerate affected tests. When code fails tests, fix implementation not tests. This maintains the covenant → test → implementation chain of truth.

4. **Self-contained files**: Each file sized for LLM context windows, comprehensible standalone. No cross-references needed.

The core insight: Traditional codebases evolved through human refactoring are illegible to LLMs. CDD creates structure where LLMs can reliably understand what exists, what's needed, and generate correct code without human intervention.

## Core Tenets

- **Single developer, sequential implementation** - One developer owns entire system evolution
- **Documentation-as-code** - Documentation is executable specification
- **Covenant as a mortal bond** - Tests are written to implement behaviors specific in the respective covenants
- **Test-driven development** - Tests are written before code.  First, tests are run and they should all fail without the impelmenting code
- **Behavior-driven development** - Tests generated from behavioral contracts
- **Deterministic context selection** - Unambiguous rules for documentation loading


## 1. Structure

### 1.1 Component Anatomy### 1.1 Component Anatomy

```
{component}/
├── doc/
│   ├── API.md               # Required. Public exports and component type.
│   ├── ABSTRACT.md          # Required. Purpose (60 words) + overview (300 words).
│   ├── ARCH.md              # Required. Architecture patterns and constraints.
│   ├── STORY.md             # Optional. Usage examples.
│   ├── concepts/            # Optional. Domain explanations.
│   └── adr/                 # Optional. Architecture decisions (human reference only).
├── cov/                     # Required for standard components
│   └── {path}/              # Mirrors src/ structure
│       └── {function}.cov.md
├── test/                    # Required for standard components
│   ├── {path}/              # Mirrors src/ structure
│   │   └── {function}.test.ts
│   └── _helpers/            # Optional. Test utilities.
├── test-intn/
│   └── {dependency-path}/   # Full path with slashes → hyphens
│       └── {scenario}.test.ts
├── comp/              # Optional. Nested components
│   └── {nested-component}/  # Same structure as parent component
└── src/
    └── {path}.ts            # Implementation files
```

### 1.2 Component Documentation Dependency Rules 

Dependencies declared in `API.md`:

```markdown
## Dependencies
payment-types: [PaymentResult, CardType]
fraud: [checkRisk, RiskLevel]
payment/comp/stripe: [charge]
auth-types: *  # Import all exports
```

Rules:
- All paths are relative to repository root (`<repo>/`)
- Full path for nested components
- Explicit imports only
- Wildcard `*` imports all exports
- No implicit transitive dependencies - You must explicitly declare every import you use, even if another dependency also imports it. This makes context loading deterministic.
- No circular runtime dependencies. Documentation circular dependencies are allowed.
- Exported types must include all referenced types


### 1.3 Nested Components

Nested components are components within components:

```
payment/
├── doc/API.md
├── src/index.ts
└── comp/
    ├── stripe/
    │   ├── doc/API.md
    │   └── src/index.ts
    │   ...
    └── square/
        ├── doc/API.md
        └── src/index.ts
        ...
...        
```

```json
asdf
asdfasdf
"asdf" = 1;

```

Visibility:
- No automatic parent/sibling visibility
- Dependencies must be explicit
- External components import via full path: `payment/comp/stripe`
- Parent may depend on child (composition pattern)

### 1.4 Entry Point

The `proj/` directory is itself a component following the full component anatomy:

```
<repo>/
├── package.json        # External npm dependencies only
├── package-lock.json   # npm lock file
├── node_modules/       # External dependencies
└── proj/            # Root component
    ├── doc/
    │   ├── API.md      # System's public exports
    │   ├── ABSTRACT.md # Project overview
    │   └── ARCH.md     # System architecture
    ├── cov/            # Covenants for any root-level logic
    ├── test/           # Unit tests for root logic
    ├── test-intn/      # Integration tests between components (E2E tests at root level)
    ├── src/
    │   └── index.ts    # Entry point - exports public API
    └── comp/     # All sub-components
```

`proj/src/index.ts` example:
```typescript
// Re-export public API
export { validateCard } from './comp/auth/src'
export { charge } from './comp/payment/src'
export type { PaymentResult } from './comp/payment-types/src'
```

`proj/doc/API.md` example:
```markdown
# Component: proj

## Component Type
standard

## Dependencies
proj/comp/auth: [validateCard]
proj/comp/payment: [charge]
proj/comp/payment-types: [PaymentResult]

## Exports

### validateCard
- **Re-export from**: comp/auth
- **Signature**: `(card: string) => ValidationResult`
- **Purpose**: Validates credit card number.
```

## 2. Formats

### 2.1 API.md

```markdown
# Component: {name}

## Component Type
standard | types-only

## Dependencies
{component-path}: [{import1}, {import2}]

## Exports

### functionName
- **Signature**: `(param: Type) => ReturnType`
- **Purpose**: Single sentence.
- **Throws**: `ErrorType` when {condition}
- **Re-export from**: `{component-path}` (if re-exporting from another component)

### TypeName  
- **Type**: `{typescript type definition}`
- **Purpose**: Single sentence.

### ErrorType
- **Type**: `class ErrorType extends Error`
- **Purpose**: Single sentence.
```

### 2.2 ARCH.md

```markdown
# Architecture: {component}

## Data Flow
Description of how data moves through the component.

## Key Patterns
- Pattern name: Why this pattern was chosen
- Pattern name: Constraints it addresses

## Technology Decisions
- Technology/Library: Version
  - Chosen for: Specific reasons
  - Constraints: Requirements it imposes
  - Alternatives considered: Why rejected

## Integration Points
External services, APIs, or systems this component integrates with.

## Constraints
- Performance: Specific requirements
- Security: Boundaries and requirements
- Scalability: Design limitations

## State Management
How component handles state, if any.

## Error Handling Strategy
Approach to errors and recovery.
```

### 2.3 Covenant Format

```markdown
# {functionName}.cov.md

## Signature
`functionName(param: ParamType): ReturnType`

## Examples
- `functionName("valid")` → `{result: "ok"}`
- `functionName("")` → throws `ValidationError`
- `functionName(null)` → throws `TypeError`
```

Minimum requirements:
- One example (happy path)
- One error example per declared throw
- Additional examples for edge cases proportional to API complexity

Covenant files are named after functions, within directories that mirror source files.

### 2.3 Generated Tests

Tests generated from covenants:

```typescript
// Generated from validateCard.cov.md
import { validateCard } from '../../../src/validation'
import { test } from 'node:test'
import { strict as assert } from 'assert'

test('validateCard("4111111111111111") → {valid: true}', () => {
  const result = validateCard("4111111111111111")
  assert.deepEqual(result, {valid: true})
})

test('validateCard("") → throws ValidationError', () => {
  assert.throws(
    () => validateCard(""),
    {name: 'ValidationError'}
  )
})
```

## 3. Algorithms

### 3.1 Context Loading

When implementing `proj/comp/fraud/src/detector.ts`:

1. Load `proj/comp/fraud/doc/*` (excluding `adr/`)
2. For each dependency in `proj/comp/fraud/doc/API.md`:
   - Load `{dependency}/doc/API.md` (all paths relative to repository root)
   - Extract declared imports with types directly in signature
3. Load concept files referenced via markdown links

Note: All paths in dependencies and imports are relative to repository root (`<repo>/`).

Example:
```
Dependencies:
  payment-types: [PaymentResult]
  
Loads:
  - fraud/doc/* (excluding adr/)
  - payment-types/doc/API.md (PaymentResult + its type definition)
```

If processPayment signature is `(result: PaymentResult) => boolean`, load both function and PaymentResult type. But if PaymentResult references Currency, that requires separate import.

Concept loading: `[See payment lifecycle](../concepts/lifecycle.md)` loads referenced file.

Note: Implementations should support granular loading strategies:
- **Minimal**: API.md + target function covenant only
- **Standard**: Full doc/* (excluding adr/) + filtered dependencies  
- **Deep**: Add concepts/, STORY.md, integration tests
- **Architectural**: Multiple components + dependency graph

The algorithm defines maximum loadable context. Tools optimize selection based on task.

### 3.2 Test Generation

1. Parse covenant file for function signature
2. Extract dependencies from component's API.md
3. For each example:
   - Generate test case with assertion
   - Import types from declared dependencies only
4. Write to `test/{path}/{function}.test.ts`

Type resolution uses component's declared dependencies. Generation fails if types not found.

### 3.3 Integration Test Generation

When component A declares dependency on B:
1. Create `A/test-intn/{dependency-path}/` (see section 1.1 for path format)
2. Generate tests verifying:
   - Imported functions exist at runtime
   - Call signatures match API.md declarations
   - One successful function call
3. Generate stub for non-existent dependencies:
   ```typescript
   // Stub for missing dependency
   export function checkRisk() {
     throw new Error('fraud component not implemented')
   }
   ```

Note: Type-only components with no runtime exports have no integration tests.

Basic test structure:
```typescript
test('payment functions exist and are callable', () => {
  assert(typeof charge === 'function')
  assert(charge.length === 2) // verify function arity
  const result = charge(100, '4111111111111111')
  assert(result instanceof Promise)
})
```

## 4. Patterns

### 4.1 Basic Component

```
proj/comp/auth/
├── doc/
│   ├── API.md
│   └── ABSTRACT.md
├── cov/
│   └── index/
│       ├── validateToken.cov.md
│       └── refreshToken.cov.md
├── test/
│   └── index/
│       ├── validateToken.test.ts
│       └── refreshToken.test.ts
└── src/
    └── index.ts
```

`proj/comp/auth/doc/API.md`:
```markdown
# Component: auth

## Dependencies
proj/comp/auth-types: [Token, User]

## Exports

### validateToken
- **Signature**: `(token: string) => Promise<User>`
- **Purpose**: Validates JWT token and returns user.
- **Throws**: `InvalidTokenError` when token invalid/expired
```

### 4.2 Type Component

```
proj/comp/payment-types/
├── doc/
│   ├── API.md          # Component Type: types-only
│   └── ABSTRACT.md
└── src/
    └── index.ts
```

`proj/comp/payment-types/doc/API.md`:
```markdown
# Component: payment-types

## Component Type
types-only

## Dependencies

## Exports

### PaymentResult
- **Type**: `{success: boolean, transactionId?: string, error?: string}`
- **Purpose**: Standard payment operation result.

### CardType
- **Type**: `"visa" | "mastercard" | "amex"`
- **Purpose**: Supported card types.
```

### 4.3 Nested Component

`proj/comp/payment/comp/stripe/doc/API.md`:
```markdown
# Component: payment/comp/stripe

## Component Type
standard

## Dependencies
proj/comp/payment-types: [PaymentResult, CardType]
proj/comp/payment: [validateCard]

## Exports

### charge
- **Signature**: `(amount: number, card: string) => Promise<PaymentResult>`
- **Purpose**: Process payment via Stripe.
- **Throws**: `PaymentError` when charge fails
```

### 4.4 Root Component

```
proj/
├── doc/
│   ├── API.md          # System public API
│   ├── ABSTRACT.md     # Project overview  
│   └── ARCH.md         # System architecture
├── test-intn/          # Integration tests (E2E tests for the system)
│   ├── auth-payment/
│   │   └── token-validation.test.ts
│   ├── user-registration.test.ts
│   └── payment-flow.test.ts
├── src/
│   └── index.ts        # Public exports
└── comp/
    ├── auth/
    └── payment/
```

### 4.5 Cross-Dependency Integration

Given:
- `proj/comp/fraud` depends on `proj/comp/payment/comp/stripe`
- `proj/comp/fraud` depends on `proj/comp/risk-engine`

Generated structure:
```
proj/comp/fraud/
└── test-intn/
    ├── proj-comp-payment-comp-stripe/
    │   └── risk-check.test.ts
    └── proj-comp-risk-engine/
        └── score-calculation.test.ts
```
