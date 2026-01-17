# Bug Fix Skill
**Description:** Systematic bug fixing through planning and delegated execution. Main agent identifies the issue, creates a fix plan, and delegates execution to subagents.
**Usage:** /bug-fix [bug description or error message]

**Trigger this skill when:**
- User reports a specific bug or error
- User shares an error message or stack trace
- User says "fix this bug", "debug this", "why is this failing"
- User describes unexpected behavior in their code
- Test failures that need investigation

**Skip for:** General refactoring, feature requests, code review, performance optimization

## Core Philosophy

**Main Agent = Architect** → Analyzes, identifies issue, plans, defines success criteria
**Subagent = Builder** → Executes the plan, makes changes, verifies

This separation ensures:
1. Thorough analysis before any code changes
2. Clear success criteria defined upfront
3. Focused execution without scope creep
4. Verification against the original plan

---

## Phase 1: Bug Identification (Main Agent)

### Step 1.1: Gather Context

Run in parallel:
- Read the error message/stack trace carefully
- Identify the failing file(s) and line numbers
- Fire `explore` agent to search for related code
- Check recent changes that might have caused it

### Step 1.2: Reproduce Understanding

| Question | Purpose |
|----------|---------|
| What is the expected behavior? | Define success |
| What is the actual behavior? | Understand the symptom |
| When does it occur? | Identify triggers |
| What changed recently? | Find root cause candidates |

### Step 1.3: Root Cause Analysis

1. Read the failing code section
2. Trace the data flow to the failure point
3. Check dependencies and imports
4. Look for similar patterns elsewhere that work
5. Identify the ACTUAL root cause (not just symptoms)

**For common bug patterns, see:** `examples.md` in this folder

---

## Phase 2: Create Fix Plan (Main Agent)

### Plan Template

```markdown
## Bug Fix Plan

### Bug Summary
[One sentence describing the bug]

### Root Cause
[Specific reason why the bug occurs]

### Subagents Involved
- `explore` - [what to search for]
- `general` - [execution tasks]
- `oracle` - [if architectural guidance needed]

### Files to Modify
- `path/to/file1.py` - [what changes needed]
- `path/to/file2.py` - [what changes needed]

### Fix Steps (Ordered)
1. [First change to make]
2. [Second change to make]
3. [Third change to make]

### Success Criteria
- [ ] [Specific testable outcome 1]
- [ ] [Specific testable outcome 2]
- [ ] [No regressions in related functionality]

### Verification Commands
```bash
[command to verify fix works]
```
```

### Validation Checklist

Before delegating:
- [ ] Root cause is clearly identified (not guessing)
- [ ] Fix addresses root cause, not just symptoms
- [ ] All affected files are listed
- [ ] Steps are specific and actionable
- [ ] Success criteria are testable
- [ ] No unnecessary refactoring included

---

## Phase 3: Execute Fix (Delegate to Subagent)

Use Task tool with `subagent_type: "general"`:

```
TASK: Execute bug fix plan for [bug summary]

CONTEXT:
[Paste the full bug fix plan]

EXPECTED OUTCOME:
- All fix steps completed
- All success criteria verified
- lsp_diagnostics clean on changed files
- Verification commands pass

REQUIRED TOOLS:
- Read, Edit, lsp_diagnostics, Bash

MUST DO:
- Follow fix steps IN ORDER
- Make MINIMAL changes (no refactoring)
- Run lsp_diagnostics after each file change
- Execute verification commands at the end

MUST NOT DO:
- Deviate from plan without explicit reasoning
- Add unrelated improvements
- Suppress errors with type ignores
- Change files not in the plan

REPORT BACK:
1. Changes made (file:line for each edit)
2. Verification results (pass/fail)
3. Any issues encountered
```

---

## Phase 4: Verify & Close (Main Agent)

### Review Results

| Check | Action if Failed |
|-------|------------------|
| All steps completed? | Ask subagent to complete missing steps |
| Success criteria met? | Investigate why, create new plan if needed |
| No new errors? | Fix introduced regressions |
| Verification passed? | Debug verification failure |

### Final Verification

1. Run lsp_diagnostics on all changed files
2. Run the original failing scenario
3. Run related tests if they exist
4. Check for regressions

---

## Quality Guidelines

**ALWAYS:**
- Identify root cause before planning fix
- Create specific, actionable fix steps
- Define testable success criteria
- Make minimal changes (fix only what's broken)
- Verify fix doesn't introduce regressions

**NEVER:**
- Guess at the root cause
- Mix bug fixes with refactoring
- Skip verification steps
- Deploy subagent without a clear plan
- Suppress errors instead of fixing them

---

## Escalation Triggers

**Consult Oracle if:**
- Root cause unclear after investigation
- Fix requires architectural changes
- Multiple possible solutions with trade-offs
- Two fix attempts have already failed

**Ask User if:**
- Bug is in business logic (intended behavior unclear)
- Fix would change public API
- Multiple valid interpretations of expected behavior
