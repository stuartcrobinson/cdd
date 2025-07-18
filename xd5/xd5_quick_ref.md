# XD5 LLM Quick Reference

## Core Principle
Documentation maintains dependency graphs for deterministic context assembly. Track dependencies as discovered during implementation.

## File Structure
```
<repo>/
└── proj/
    ├── doc/
    │   ├── API.md        # ⚠️ CRITICAL: All dependencies + exports
    │   ├── ABSTRACT.md   # 60-word purpose + 300-word overview
    │   └── ARCH.md       # Technical decisions, constraints
    ├── test-data/        # Test cases as JSON/MD files
    ├── test/             # Minimal harnesses loading test-data
    ├── test-intn/        # Integration tests for dependencies
    ├── src/              # Implementation
    └── comp/             # Sub-components (recursive)
```

## API.md Template
```markdown
# Component: {name}

## Component Type
standard | types-only

## Dependencies
[Update as implementation reveals needs]
proj/comp/{component}: [{Import1}, {Import2}]
external/{package}: [{Import1}]

## Exports
### {functionName}
- **Signature**: `{functionName}(param: Type) -> ReturnType`
- **Purpose**: Single sentence.
- **Throws**: `{ErrorType}` when {condition}
- **Test-data**: `test-data/{path}/{functionName}.json`
```

## Workflow

### 1. Design → 2. Test → 3. Implement

1. **Write docs**: ABSTRACT.md → ARCH.md → API.md
2. **Design tests**: Component E2E → Extract functions → Unit tests
3. **Implement**: Functions (red/green) → Update E2E → Wire component

### Critical Implementation Rules

**🛑 STOP Protocol**: If implementation reveals doc errors:
1. STOP immediately
2. Update API.md/ARCH.md
3. Continue with correct docs

**Test Immutability**: 
- Test harnesses = frozen after creation
- Test data = only change with human approval
- Fix code, not tests (unless explicitly approved)

**Dependency Updates**:
- Add to API.md as discovered
- Include transitive deps if needed for understanding
- External deps must be explicit

## Test Data Format
```json
{
  "cases": [
    {
      "name": "descriptive name",
      "input": [arg1, arg2],
      "expected": {result},
      "throws": "ErrorType"  // optional
    }
  ]
}
```

## Quick Checks

Before implementing:
- [ ] API.md declares all exports?
- [ ] Dependencies section updated?
- [ ] Test data files created?

During implementation:
- [ ] Tests fail first (red phase)?
- [ ] Docs match reality? (if not → STOP)
- [ ] All imports declared in API.md?

## Common Patterns

**Extract pure functions during pseudocode**:
```javascript
// Pseudocode reveals:
// extractedFn: validateInput(x) -> bool
// extractedFn: processData(data) -> result
```

**Types-only components**: No test/ or src/, only doc/

**Path conventions**: All relative to `<repo>/`
- Component: `proj/comp/{name}`
- Nested: `proj/comp/{parent}/comp/{child}`