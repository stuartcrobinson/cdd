# bundleContext.cov.md

## Signature
`bundleContext(filepath: string): string`

## Examples
- `bundleContext("fraud/src/detector.ts")` → returns markdown containing fraud/doc/* + filtered dependency APIs
- `bundleContext("fraud/src/detector.ts")` with missing dependency → returns markdown with "WARNING: Component 'payment-types' not found" in output
- `bundleContext("nonexistent/file.ts")` → throws Error containing "not found"
- `bundleContext("README.md")` → throws Error containing "outside component"