# Devin Prompt: Analyze and Add Tombstones

Use this prompt to have Devin analyze a codebase and add tombstone tracking to potentially unused code.

## Prompt Template

```
Analyze the codebase at [REPO_URL] for potentially unused code and add tombstone tracking.

## Context
We want to identify and track potentially dead code in our codebase. Dead code candidates include:
- Functions with "deprecated", "legacy", "old" in their name or docstring
- Functions that appear to have no references
- Code marked with TODO/FIXME comments about removal

## Steps
1. Clone the repository and explore the codebase structure
2. Run the dead code analyzer to identify candidates:
   ```
   python scripts/analyze_and_tombstone.py --path ./[APP_DIR] --project [PROJECT_NAME] --dry-run
   ```
3. Review the candidates and confirm they look reasonable
4. Run the script without --dry-run to add tombstone decorators:
   ```
   python scripts/analyze_and_tombstone.py --path ./[APP_DIR] --project [PROJECT_NAME] --max-changes 10
   ```
5. Create a PR with the changes

## Environment Setup
Make sure these environment variables are set:
- SUPABASE_URL: Your Supabase project URL
- SUPABASE_KEY: Your Supabase anon key

## Expected Output
- A PR adding @tombstone decorators to potentially unused functions
- Each tombstone will log to Supabase when the code is executed
- After a monitoring period, we can identify which code was never called
```

## Example Usage

For the sample app in this repo:

```
Analyze the sample_app directory for potentially unused code and add tombstone tracking.

Project name: dead-code-demo
Target directory: ./sample_app

Run the analyzer first in dry-run mode, then apply the changes and create a PR.
```
