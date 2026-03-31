---
name: create-pr
argument-hint: "(optional: target branch, default: main)"
description: |
  This skill should be used when the user asks to
  "create PR", "create pull request", "submit PR", "open PR",
  or wants to create a GitHub pull request from the current branch.
---

# Create Pull Request

Target base branch: $ARGUMENTS (default: main)

## Phase 1: Branch Validation

1. Get current branch name:
   !`git branch --show-current`

2. Validate branch naming convention `{type}/{description}`:
   - Valid types: `feat`, `fix`, `refactor`, `docs`, `chore`, `test`, `i18n`, `ci`, `perf`, `style`
   - If on `main` → abort with message: "Create a feature branch first"
   - If branch name does not match convention → warn the user and ask whether to proceed

3. Verify the branch has commits ahead of base:
   ```bash
   git log main..HEAD --oneline
   ```
   If empty → abort with message: "No commits ahead of base branch"

## Phase 2: Local Verification

Run the same checks CI will run:
```bash
make check
```

- If lint fails → report errors and ask whether to proceed or fix first
- If tests fail → report failures and ask whether to proceed or fix first
- If all pass → proceed automatically

## Phase 3: Analyze Changes

1. Collect all commits since diverging from base:
   ```bash
   git log main..HEAD --format="%s%n%b" --reverse
   ```

2. Collect full diff for context:
   ```bash
   git diff main...HEAD --stat
   ```

3. From commit messages, extract:
   - **Change type**: derive from branch prefix (feat/ → feat, fix/ → fix, etc.)
   - **Related issues**: scan for patterns `#\d+`, `Fixes #`, `Closes #`
   - **Change summary**: synthesize from ALL commit messages (not just the latest)

## Phase 4: Generate PR Content

Read the PR template from `.github/pull_request_template.md` and fill in each section:

### Title
Format: `{type}: {concise description}` (under 70 characters)

### Body
Follow the exact format from `.github/pull_request_template.md`:

- **Related Issue**: fill with `Fixes #N` / `Closes #N` from extracted issues, or leave blank
- **Change Summary**: bullet points synthesized from all commits
- **Type of Change**: check `[x]` only the matching type from the full list in the template, leave others as `[ ]`
- **Checklist**: check items that were verified in Phase 2
- **How to Test**: suggest test steps based on the changes

### Labels
Map branch type to GitHub label:
| Branch prefix | Label |
|--------------|-------|
| feat/ | enhancement |
| fix/ | bug |
| docs/ | documentation |
| refactor/ | refactoring |
| chore/ | chore |
| test/ | test |
| i18n/ | i18n |

## Phase 5: Review and Create

1. Present the generated title, body, and labels to the user
2. Ask: "Create this PR? (or edit first)"
3. After user approval, push and create:
   ```bash
   git push -u origin $(git branch --show-current)
   gh pr create --base {target} --title "{title}" --body "{body}" --label "{labels}"
   ```
4. If `--label` fails (label doesn't exist in repo), retry without labels
5. Report the created PR URL to the user
