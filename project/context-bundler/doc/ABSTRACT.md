**Purpose (60 words):**
Context Bundler assembles documentation required for LLM code generation in CDD projects. Given a filepath, it loads the containing component's documentation and filters dependency APIs to declared imports. Implements the section 3.1 loading algorithm with file-type-specific strategies. Outputs concatenated markdown sized for LLM context windows. Enables deterministic context selection by eliminating human judgment about which documentation to include when implementing CDD components.

**Overview (300 words):**
Context Bundler operationalizes CDD's context loading algorithm to solve a specific problem: LLMs need complete, bounded documentation to generate correct code, but determining what documentation to include requires understanding implicit relationships across components. The bundler makes these decisions deterministic through explicit rules based on target file type.

The tool recognizes three context needs. Minimal loading for API design tasks loads only API.md, ABSTRACT.md, and specific covenant files. Standard loading for implementation adds ARCH.md and *all covenants. Deep loading for architectural work includes integration tests and concept files. These strategies map to CDD workflows: design contract first (minimal), implement behavior (standard), refactor architecture (deep).

Implementation centers on dependency filtering. When component A declares `payment-types: [PaymentResult]`, the bundler extracts only PaymentResult's definition from payment-types/doc/API.md, ignoring unexported types. This maintains component boundaries while providing complete type information.

The bundler handles CDD's structural requirements: path resolution for nested components, covenant-to-source mapping through directory mirroring, and concept file loading via markdown link extraction. It distinguishes between types-only and standard components, loading documentation identically but acknowledging absent covenant/test directories.

Critical design decision: no reverse dependency tracking. When working on payment-types, the bundler doesn't include components that depend on it. This follows section 3.1's unidirectional loading specification and prevents context explosion in widely-used components.

Output structure prioritizes comprehension: component documentation first, then dependencies in declaration order, with clear section boundaries. The bundler includes file-path comments indicating the source of each section, enabling LLMs to understand documentation hierarchy.

The tool assumes filesystem access to the complete project and operates statelessly - each invocation independently resolves all dependencies. This trades performance for simplicity and deterministic behavior.

---

# follow up

* Standard loading for implementation adds ARCH.md and *all covenants...

i dont think it should be all covenants... .hopefully it means all relevant covenants?  or is that just for a specific component?  

this is all several weeks old.