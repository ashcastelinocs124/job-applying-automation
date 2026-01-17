# Code Implementation Skill
**Description:** Deliver production-quality code for a requested task: plan → implement → verify → code review.
**Usage:** /code-implementation "task description"

**Trigger this skill when:**
- User asks to implement/build/add code or a feature
- User requests a function/module/service to be written
- Bug fixes that require non-trivial coding (after root cause is known)

**Skip for:** Pure analysis, docs-only tasks, minor tweaks that don't need a plan

## Execution Workflow

### Phase 1: Understand & Bound
- Capture requirements and constraints (inputs/outputs, interfaces, performance, edge cases)
- Identify affected components/files
- Note non-functional needs (tests, types, logging, telemetry)

### Phase 2: Plan (checklist-driven)
Produce a concise plan before coding:
- Scope & assumptions
- Files to touch
- Steps to implement (ordered)
- Tests/verification commands
- Rollback notes

Use this template:
```markdown
## Implementation Plan
- Scope/assumptions: ...
- Files: [...]
- Steps:
  1) ...
  2) ...
- Tests/verify: `...`
- Rollback: ...
```
Only start coding after the plan is written. Keep the plan updated if scope changes.

### Phase 3: Implement
- Follow the plan steps in order; keep changes minimal and focused
- Prefer existing patterns; match project style
- Add/extend tests alongside code changes
- Run `lsp_diagnostics` on changed files after each logical unit

### Phase 4: Verify
- Run the planned tests/commands
- If failures occur, fix and re-run until green

### Phase 5: Code Review (MANDATORY)
- Invoke the **code-reviewer** agent (see AGENTS.md) after implementation & self-verification
- Address review findings; rerun verification if code changes

### Phase 6: Summarize
- Summarize changes, tests run, and status vs plan
- Call out any deviations or TODOs

### Phase 7: Explain (only if user asks)
- If the user requests an explanation of the new code, use the **Explain** skill (/explain) or the **tutor** agent to provide a concise walkthrough (what it does, how it works, key flows)

## Quality Guidelines

**ALWAYS:**
- Plan before you code; keep it short but specific
- Update the plan if the scope shifts
- Keep diffs tight; avoid drive-by refactors
- Add/maintain tests; keep `lsp_diagnostics` clean
- Use existing patterns and conventions
- Run code-reviewer agent before considering the task done

**NEVER:**
- Start coding without a plan
- Ignore failing tests or diagnostics
- Introduce type suppressions (`# type: ignore`, `as any`, `@ts-ignore`)
- Mix unrelated refactors with the requested change

## Verification Checklist (tick before closing)
- [ ] Plan created and followed/updated
- [ ] Code written per plan
- [ ] Tests/commands executed and passing
- [ ] lsp_diagnostics clean on changed files
- [ ] code-reviewer agent run and feedback addressed
- [ ] Summary delivered to user
