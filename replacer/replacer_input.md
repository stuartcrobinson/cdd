=== PROCESSED: 2025-07-18 14:47:02 ===
SUCCESS Block 1: Updated /Users/stuart/repos/cdd/xd5_ref.md
SUCCESS Block 2: Updated /Users/stuart/repos/cdd/xd5_ref.md
SUCCESS Block 3: Updated /Users/stuart/repos/cdd/xd5_ref.md
===

Looking at the pasted xd5_ref.md, several critical pieces are missing:

1. **No explicit checkpoint after step 5** - The discovery → doc update checkpoint isn't there
2. **Pre-implementation checklist exists but is weak** - It's in "Implementation Gates" but lacks the specific checklist format
3. **No LLM behavioral directive** - Nothing tells the LLM to refuse implementation without specs
4. **Documentation Debt added** - But only to my last edit attempt, not in your pasted version

Key gaps in current docs:

<<<EXPLANATION>>>
Add explicit checkpoint after implementation discoveries

<<<FILE>>>
/Users/stuart/repos/cdd/xd5_ref.md

<<<SEARCH>>>
5. **Implement Functions** - Red/green/debug (fix code, not tests)
6. **Revise E2E Tests** - Align with discovered behavior (ask human)
<<<REPLACE>>>
5. **Implement Functions** - Red/green/debug (fix code, not tests)
   - **CHECKPOINT: Any discoveries? → Update docs before continuing**
   - New dependencies? Update API.md
   - Wrong signatures? Fix documentation
   - Missing types? Define them first
6. **Revise E2E Tests** - Align with discovered behavior (ask human)
<<<END>>>

<<<EXPLANATION>>>
Add strong pre-implementation checklist with STOP enforcement

<<<FILE>>>
/Users/stuart/repos/cdd/xd5_ref.md

<<<SEARCH>>>
## Implementation Gates

**HARD STOP if incomplete:**
1. **Specification completeness** - No undefined types, no TBD signatures
2. **Dependency accuracy** - Every import must be in API.md
3. **Test data existence** - Files must exist before code
<<<REPLACE>>>
## Pre-Implementation Checkpoint

**Before writing ANY code, verify:**
- [ ] All function signatures fully specified in API.md?
- [ ] All types defined with complete field lists?
- [ ] All dependencies declared with specific imports?
- [ ] Test data files created?
- [ ] Documentation Debt section is EMPTY?

**If ANY unchecked → STOP, complete specifications first**

## Implementation Gates

**HARD STOP if incomplete:**
1. **Specification completeness** - No undefined types, no TBD signatures
2. **Dependency accuracy** - Every import must be in API.md
3. **Test data existence** - Files must exist before code
<<<END>>>

<<<EXPLANATION>>>
Add LLM behavioral rule to refuse underspecified implementation

<<<FILE>>>
/Users/stuart/repos/cdd/xd5_ref.md

<<<SEARCH>>>
**Path conventions**: All relative to `<repo>/`
- Component: `proj/comp/{name}`
- Nested: `proj/comp/{parent}/comp/{child}`
<<<REPLACE>>>
**Path conventions**: All relative to `<repo>/`
- Component: `proj/comp/{name}`
- Nested: `proj/comp/{parent}/comp/{child}`

## CRITICAL LLM RULE
**Never suggest implementation without complete specifications**
- Missing function signatures? → Refuse to implement
- Undefined types? → Demand specification first
- "We'll figure it out during coding" → VIOLATION
- User asks to implement with gaps? → Point to Documentation Debt
<<<END>>>

The full xd5 3.md file also needs these updates but wasn't provided. These structural changes make the documentation-first principle enforceable rather than aspirational.