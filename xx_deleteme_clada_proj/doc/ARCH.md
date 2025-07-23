# Clada Architecture

## Core Design Decisions

### Transaction Model
- **No automatic rollback** - All operations commit, including failures
- **Failures are data** - LLM needs failure feedback for next steps
- **Forward-only progress** - Cheaper than regenerating responses
- **Manual rollback only** - Human-initiated via git commands
- **Boundary**: One git commit per `execute()` call
- **API**: Explicit transaction management (details TBD)

### SHAM Processing Pipeline
1. SHAM parser (external npm) → AST
2. AST → Action objects (sham-ast-converter)
3. Actions → Execution → Results

### SHAM AST Structure
```typescript
interface ShamParseResult {
  blocks: ShamBlock[]
  errors: ShamError[]
}

interface ShamBlock {
  id: string           // 3-char SHA-256
  properties: {
    action: string     // Maps to tool name (e.g., "file_create")
    [key: string]: any // Tool-specific parameters
  }
  startLine: number
  endLine: number
}

interface ShamError {
  code: string         // e.g., "DUPLICATE_KEY"
  line: number
  column: number
  length: number
  blockId: string
  content: string
  context: string
  message: string
}
```

### Error Propagation Strategy
- **Parser errors**: Skip blocks with parser errors, execute valid blocks only
- **Validation errors**: Skip invalid actions, execute valid ones
- **Execution errors**: Continue with remaining actions
- **Result**: Complete execution log with successes and failures

### Action Mapping
- SHAM `action` property maps directly to tool names from unified-design.yaml
- Use canonical names: `file_create`, `file_write`, `exec`, etc.

### Context Management
- **V1**: Simple `Set<string>` of file paths
- **Storage**: In-memory only, no persistence across sessions
- **V2 Future**: Sub-file references (lines, functions, sections)

### Execution Model
- **Synchronous**: All operations block until complete
- **CWD Management**: Session-based working directory
  - Default: Repository root
  - Each exec can override with `cwd` parameter
  - CWD persists within session, not across transactions
- **Results Format**: Flat array with sequence numbers
```typescript
interface ActionResult {
  seq: number          // Execution order
  blockId: string      // SHAM block ID
  action: string       // Action type
  params: any          // Input parameters
  success: boolean
  error?: string       // Error message if failed
  data?: any           // Action-specific output (stdout, content, etc.)
}
```

### Security Model (V1)
- **None**: Full filesystem access
- **No validation**: Any path allowed
- **No sandboxing**: Direct execution
- **V2 Future**: Path allowlisting per unified-design.yaml

## Component Structure
```
clada/
├── proj/
│   ├── comp/
│   │   ├── sham-ast-converter/  # AST → Actions
│   │   ├── fs-ops/              # File/directory operations
│   │   ├── exec/                # Command execution
│   │   ├── git-tx/              # Git transaction management
│   │   └── context/             # Working set management
│   └── doc/
│       ├── API.md               # Main orchestrator API
│       ├── ARCH.md              # This document
│       └── ABSTRACT.md          # Project overview
```

## Implementation Priorities
1. `sham-ast-converter` - Cannot test without this
2. `fs-ops` - Core functionality
3. `exec` - Command execution
4. `git-tx` - Transaction wrapper
5. `context` - Working set (may be simple enough to inline)

## Open Questions

### Critical
1. **SHAM parser package**: `nesl-js` from `github:nesl-lang/nesl-js`
   - Import: `const { parseSHAM } = require('nesl-js')`
2. **Transaction API**: Single `execute()` method processes SHAM block array

### Design
1. **Parser error handling**: Execute blocks with parser errors or skip?
2. **Git conflict handling**: How to handle conflicts during manual rollback?
3. **Concurrent access**: Multiple clada instances on same repo?
4. **Partial failure behavior**: Continue executing after first failure or abort?

### Future
1. **Context references**: Syntax for line ranges and functions
2. **Execution isolation**: Container/VM strategy for V2
3. **Streaming results**: Return results as actions complete or batch at end?

## Design Rationale

### Why No Automatic Rollback
Traditional transaction systems rollback on failure to maintain consistency. Clada explicitly rejects this because:
1. **LLM responses are expensive** - Regenerating costs time and money
2. **Partial success is informative** - LLM learns from failures
3. **Git preserves history** - Can always manually revert
4. **Forward progress over perfection** - Incremental improvement model

### Why Synchronous Execution
1. **Deterministic results** - LLM needs to know exact outcomes
2. **Sequential dependencies** - Later actions may depend on earlier ones
3. **Simpler implementation** - No async state management
4. **Git compatibility** - Git operations are inherently synchronous

### Why In-Memory Context
1. **Session isolation** - Each LLM conversation is independent
2. **No persistence complexity** - No file format versioning
3. **Git is the source of truth** - Files on disk matter, not context
4. **Quick reset** - New session = clean slate