# Component: clada

## Component Type
standard

## Dependencies

```yaml
dependencies:
  proj/comp/sham-ast-converter:
    functions: [convertToActions]
    types: [CladaAction, ConversionError]
  
  proj/comp/fs-ops:
    functions: [executeFileOperation]
    types: [FileOpResult]
  
  proj/comp/exec:
    functions: [executeCommand]
    types: [ExecResult]
  
  proj/comp/git-tx:
    functions: [ensureCleanRepo, commitChanges]
    types: [GitError]
  
  proj/comp/context:
    functions: [addPath, removePath, listPaths, clearContext]
    types: [ContextError]
  
  external/nesl-js:
    functions: [parseSHAM]
    types: [ShamParseResult, ShamBlock, ShamError]
```

## Exports

```yaml
exports:
  classes:
    Clada:
      methods: [execute]
  types: 
    - ExecutionResult
    - ActionResult  
    - ParseError
    - CladaOptions
```

### Clada (class)
- **Purpose**: Main orchestrator executing SHAM blocks from LLM output
- **Constructor**: `new Clada(options?: CladaOptions)`
- **State**: Maintains working directory and context set across execute() calls

### execute
- **Signature**: `async execute(llmOutput: string): Promise<ExecutionResult>`
- **Purpose**: Parse and execute all SHAM blocks in LLM output, commit results
- **Process**: 
  1. Ensure clean git state
  2. Parse SHAM blocks
  3. Convert to actions
  4. Execute all valid actions
  5. Commit changes with summary
- **Throws**: Never - all errors captured in ExecutionResult
- **Test-data**: `test-data/execute/`

### ExecutionResult (type)
```typescript
interface ExecutionResult {
  success: boolean              // False if any action failed
  totalBlocks: number          // Count of SHAM blocks found
  executedActions: number      // Count of actions attempted
  results: ActionResult[]      // All execution results
  parseErrors: ParseError[]    // SHAM parsing errors
  gitCommit?: string          // Commit SHA if successful
  fatalError?: string         // Git or system failure
}
```

### ActionResult (type)
```typescript
interface ActionResult {
  seq: number                  // Execution order
  blockId: string             // SHAM block ID
  action: string              // Action type
  params: Record<string, any> // Input parameters
  success: boolean
  error?: string              // Error message if failed
  data?: any                  // Action-specific output
}
```

### ParseError (type)
```typescript
interface ParseError {
  blockId?: string            // If error is block-specific
  error: ShamError            // From parser
}
```

### CladaOptions (type)
```typescript
interface CladaOptions {
  repoPath?: string           // Default: process.cwd()
  gitCommit?: boolean         // Default: true
}
```

## Internal Architecture

### Execution Flow
```
execute(llmOutput)
  → parseSHAM(llmOutput) → ShamParseResult
  → for each valid block:
    → convertToActions(block) → CladaAction[]
    → for each action:
      → route to appropriate executor
      → capture result
  → commitChanges(results)
  → return ExecutionResult
```

### Action Routing
- file_* → fs-ops
- dir_* → fs-ops
- exec → exec
- context_* → context
- ls, grep, glob → fs-ops (read operations)

### Error Handling
- Parser errors: Skip block, record error
- Conversion errors: Skip action, record error
- Execution errors: Continue execution, record error
- Git errors: Fatal, abort with fatalError