# Context Bundler Usage Stories

## Story 1: New Function Implementation

Developer implements fraud detection. Target: `fraud/src/detector.ts`

```javascript
import { bundleContext } from 'context-bundler'
const context = bundleContext('fraud/src/detector.ts')
```

Standard loading activates (source file). Bundler loads:
- `fraud/doc/API.md`, `ABSTRACT.md`, `ARCH.md`
- All files in `fraud/cov/detector/`
- `payment-types/doc/API.md` → extracts PaymentResult definition only
- `risk-engine/doc/API.md` → extracts checkRisk signature only

LLM receives complete behavioral specification (covenants) plus architectural context.

## Story 2: Covenant Design

Developer creates covenant for new function. Target: `analytics/cov/tracker/logEvent.cov.md`

```bash
cdd-bundle analytics/cov/tracker/logEvent.cov.md
```

Minimal loading activates (covenant file). Bundler loads:
- `analytics/doc/API.md`, `ABSTRACT.md` 
- `event-types/doc/API.md` → extracts Event type only

Focused context helps design examples using correct types without implementation distractions.

## Story 3: Missing Dependencies

Developer works on component with undefined dependency:

```bash
cdd-bundle reporting/src/generator.ts
```

Bundler encounters `dashboard: [Widget]` but `dashboard/` doesn't exist. Output includes:

```markdown
## WARNING: Missing dependency
Component 'dashboard' not found. Import 'Widget' cannot be resolved.
```

LLM sees the warning and can suggest proper dependency setup or stub implementation.