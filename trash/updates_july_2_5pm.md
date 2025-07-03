## CDD Refinements Summary

### Core Changes

1. **Eliminated mandatory orchestration layer**
   - `main/core/` → optional pattern, not requirement
   - Orchestration = just another component with many dependencies
   - Entry point: `main/entry/` for routing/config only

2. **Removed sibling isolation constraint**
   - Components can communicate directly via declared interfaces
   - Dependencies declared in each component's API.md
   - No forced routing through orchestrator

3. **Dependencies declared, not discovered**
   - Each API.md lists `Requires:` section
   - Enables deterministic context loading before code exists
   - Single source of truth per component

### Structural Changes

4. **"Shared" no longer special**
   - Just another component with zero dependencies
   - OR domain-level organization to prevent circular deps
   - Reveals true coupling instead of hiding it

5. **Test organization follows dependencies**
   - No artificial unit/integration split
   - Tests live with components
   - Build order follows dependency graph

### Context Loading

6. **Simplified algorithm**
   ```
   Load component + its declared dependencies' API.md files
   One level deep only (no transitive loading)
   ```

### Unresolved Issues

1. **Circular dependencies** - Extraction to shared/domain types doesn't eliminate coupling
2. **Test data coupling** - Real dependencies require coordinated test data
3. **Build order deadlocks** - Can't test A without B, can't build B without A's types
4. **Backward compatibility** - No mechanism to track breaking changes
5. **Performance** - Direct communication vs event-driven tradeoffs unclear

### Fundamental Tension

Documentation-driven development assumes you know dependencies before implementation. Reality: dependencies emerge during design. CDD hasn't resolved this circular knowledge problem.


.......

talk more about the LLM challenge and idea behind component registry or some way or autoamted way to ekep track of what comps use and require and are used by other comps.  focus on the unique LLM goals and this stuff

code even exists

so our tenets are:
* documentation-as-code
* test-driven development
* behavior-driven development
* deterministic context selection

....

## LLM Context Selection Challenge

LLMs need deterministic rules for loading relevant documentation. Current proposal: parse `Requires:` from API.md. But this creates maintenance burden and drift risk.

### Why Component Registry Fails for LLMs

Centralized registry = another abstraction layer between docs and code. LLMs must now:
1. Parse registry to understand relationships
2. Map registry entries to filesystem locations
3. Keep registry synchronized with reality

More indirection = more failure modes.

### The Real Problem

**Dependency relationships are temporal**. During development:
- Payment might need fraud (initial design)
- Payment might not need fraud (design change)
- Payment needs fraud.checkRisk (refinement)
- Payment needs fraud.checkRisk and fraud.auditLog (expansion)

Static registry can't capture this evolution. But LLM needs consistent context at each phase.

### Alternative: Dependency Annotations in Code

```typescript
// @requires: components/fraud
// @provides: processPayment
export function processPayment() {
  // LLM can parse these annotations
}
```

**Problem**: Violates documentation-before-code principle.

### Alternative: Versioned Dependency Graphs

```yaml
# payment/deps.v1.yaml
requires: []

# payment/deps.v2.yaml  
requires: [fraud]

# payment/deps.v3.yaml
requires: [fraud.checkRisk]
```

**Problem**: Version explosion. Which version for which task?

### The Fundamental Issue

LLMs need two incompatible things:
1. **Stable context** - Deterministic rules for what to load
2. **Evolutionary design** - Dependencies emerge/change during development

No static system captures both.

### Pragmatic Approach

Accept that context selection evolves:
1. **Early phase**: Load entire domain based on coarse dependencies
2. **Design phase**: Load specific components from API.md declarations
3. **Implementation phase**: Validate against actual imports

Different rules for different phases. LLM tooling must understand development phase, not just file structure.

### "Used By" Tracking

Bidirectional dependency tracking requires either:
- Manual maintenance (error-prone)
- Build-time scanning (merge conflicts)
- Runtime discovery (too late for LLM context)

**Critical insight**: LLMs don't need "used by" for code generation. They need it for impact analysis. Different use case = different solution. Perhaps "used by" is a query, not stored data.

.....

RetrySCanyting else? imporatnt from this chat re new CDD approaches /overhaulsEditCritical Unaddressed Issues
1. Frozen Covenants vs Evolving Dependencies
Document claims covenants freeze after implementation, but dependencies declared in API.md must evolve during design. This contradicts the "frozen behavioral contracts" principle. Which freezes when?
2. Single File Context Windows
Modern LLMs handle 128K+ tokens. "One file, one thought" may be outdated constraint. Should file boundaries match human cognitive limits or LLM context windows?
3. Rewrite-Only Philosophy
Never addressed your response to the rewrite cascade problem. If shared/validation changes, rewriting all consumers seems absurd. What's your position?
4. Test Generation from Covenants
markdownparseEdit(xmlNode) → {path: string, search: string, replace: string}
How do you generate meaningful test cases from this? Behavior isn't specified, just signature. Property-based testing? Example expansion?
5. Types Emerge from Implementation
Contradicts documentation-first. If payment needs fraud.RiskScore, must define before implementing either. Document handwaves this.
6. No Versioning Strategy
How do components evolve? If payment 2.0 breaks compatibility, how do dependencies update? Rewrite everything per the philosophy?
7. LLM vs Human Optimized
Is CDD optimizing for LLM context windows at expense of human comprehension? Filesystem hierarchy that makes sense to humans might not be optimal for LLM context loading.
Most Critical Missing Piece
No feedback loop from code to documentation. Once implementation reveals documentation was wrong, what updates? Manual process? This breaks LLM automation promise.RetrySCthis is not really true: "Modern LLMs handle 128K+ tokens", they supposedly handle but actually are really bad at comprehending that much infoEditYou're right. LLMs exhibit severe degradation with large contexts.
adding relevant context at the beginning or the end of a prompt improves the performance of LLMs, compared to including the relevant context in the middle of the prompt ArXivArXiv
The "lost in the middle" problem means 128K context ≠ 128K comprehension. Effective context is much smaller.
Implications for CDD

File boundaries matter more, not less. Each file must be comprehensible standalone.
Dependency loading order critical. Most important dependencies first/last, not alphabetical.
Context budget real constraint. Loading payment + 5 dependencies' API.md might already strain comprehension.
"One thought" per file validated. Not outdated constraint - necessary for LLM comprehension.

Unresolved Context Management
How to prioritize which dependencies to load when context budget exceeded?

Static priority in API.md?
Task-specific loading rules?
Dependency "importance" scores?

No clear answer. Context window size isn't the binding constraint - comprehension is.

https://claude.ai/chat/40bd9a81-643f-4387-a856-0e787d6680c0

........

Do you understand the main purpose of CDD? Explain it briefly.EditCDD aims to enable LLMs to generate, maintain, and evolve entire codebases autonomously by:

CDD aims to enable LLMs to generate, maintain, and evolve entire codebases autonomously by:

1. **Deterministic context loading**: LLMs need clear rules for what documentation/code to load when generating new code. Filesystem structure + dependency declarations provide this.

2. **Behavioral contracts (covenants)**: Specify what functions do through input/output examples. LLMs generate tests from covenants, then implementation to pass tests.

3. **Rewrite-only philosophy**: When requirements change, rewrite dependent code rather than refactor. Prevents specification drift that confuses LLMs.

4. **Self-contained files**: Each file sized for LLM context windows, comprehensible standalone. No cross-references needed.

The core insight: Traditional codebases evolved through human refactoring are illegible to LLMs. CDD creates structure where LLMs can reliably understand what exists, what's needed, and generate correct code without human intervention.

The tensions arise because this vision assumes stable specifications and known dependencies - but software development is inherently exploratory. CDD hasn't resolved how to handle the discovery phase where requirements and relationships emerge through implementation.