# Devin Prompt: Check and Remove Dead Code

Use this prompt to have Devin check for confirmed dead code and remove it.

## Prompt Template

```
Check for confirmed dead code in [PROJECT_NAME] and remove it from the codebase at [REPO_URL].

## Context
We've been monitoring tombstoned code for [X] days. Now we need to:
1. Query Supabase to find tombstones that were never triggered
2. Review and remove the confirmed dead code
3. Create a PR with the cleanup

## Steps
1. Clone the repository
2. Check for dead code that was never triggered:
   ```
   python scripts/check_dead_code.py --project [PROJECT_NAME] --days [MONITORING_DAYS] --output json > dead_code.json
   ```
3. Review the dead code list to ensure it's safe to remove
4. Remove the dead code:
   ```
   python scripts/remove_dead_code.py --path ./[APP_DIR] --input dead_code.json
   ```
5. Run tests to ensure nothing broke
6. Create a PR with the cleanup

## Environment Setup
- SUPABASE_URL: Your Supabase project URL
- SUPABASE_KEY: Your Supabase anon key

## Expected Output
- A PR removing confirmed dead code
- Updated tombstone status in Supabase (marked as 'removed')
- Clean codebase with less unused code
```

## Example Usage

```
Check for dead code in the 'dead-code-demo' project that hasn't been triggered in 7 days, and remove it from the sample_app.

Create a PR with the cleanup changes.
```
