# Dead Code Detection Demo

A complete demonstration of using Devin for automated dead code detection and removal, with Supabase integration for tracking.

## Overview

This demo showcases a full workflow where Devin:
1. **Analyzes** a codebase to identify potentially unused code
2. **Adds tombstones** (tracking decorators) to flag suspicious code
3. **Monitors** code execution via Supabase to confirm what's actually dead
4. **Removes** confirmed dead code automatically

## Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Devin         │     │   Your App      │     │   Supabase      │
│   (Analyzer)    │────▶│   (Running)     │────▶│   (Tracking)    │
└─────────────────┘     └─────────────────┘     └─────────────────┘
        │                                               │
        │                                               │
        ▼                                               ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   PR: Add       │     │   Slack Alert   │◀────│   Dead Code     │
│   Tombstones    │     │   (Optional)    │     │   Query         │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │
                               ▼
                        ┌─────────────────┐
                        │   Devin         │
                        │   (Cleanup)     │
                        └─────────────────┘
                               │
                               ▼
                        ┌─────────────────┐
                        │   PR: Remove    │
                        │   Dead Code     │
                        └─────────────────┘
```

## Quick Start

### 1. Set Up Supabase

Create a new Supabase project (or use an existing one) and run the schema:

```sql
-- Run the contents of supabase/schema.sql in your Supabase SQL Editor
```

### 2. Configure Environment

```bash
export SUPABASE_URL="https://your-project.supabase.co"
export SUPABASE_KEY="your-anon-key"
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Demo

**Step 1: Analyze and add tombstones**
```bash
# Dry run first to see what would be changed
python scripts/analyze_and_tombstone.py --path ./sample_app --project demo --dry-run

# Apply the changes
python scripts/analyze_and_tombstone.py --path ./sample_app --project demo
```

**Step 2: Run your application** (tombstones will log to Supabase when executed)
```bash
python -m sample_app.main
```

**Step 3: Check for dead code** (after monitoring period)
```bash
python scripts/check_dead_code.py --project demo --days 7
```

**Step 4: Remove confirmed dead code**
```bash
python scripts/remove_dead_code.py --path ./sample_app --input dead_code.json
```

## Workshop Demo Flow

For a live workshop demonstration, follow this sequence:

### Part 1: Setup (5 minutes)
1. Show the sample application with intentionally unused code
2. Explain the tombstone concept
3. Set up Supabase schema (can be pre-done)

### Part 2: Devin Analyzes Code (10 minutes)
1. Give Devin the prompt from `devin_prompts/01_analyze_and_tombstone.md`
2. Watch Devin analyze the codebase
3. Review the PR with tombstone decorators

### Part 3: Simulate Monitoring (5 minutes)
1. Run the sample app to trigger some tombstones
2. Show the Supabase dashboard with events
3. Note which functions were never called

### Part 4: Devin Removes Dead Code (10 minutes)
1. Give Devin the prompt from `devin_prompts/02_check_and_remove_dead_code.md`
2. Watch Devin query Supabase and identify dead code
3. Review the cleanup PR

### Part 5: Full Automation Discussion (5 minutes)
1. Show the Slack integration architecture
2. Discuss how this could run continuously
3. Q&A

## Project Structure

```
dead-code-detection-demo/
├── sample_app/              # Sample Python app with unused code
│   ├── __init__.py
│   ├── main.py              # Entry point (uses some functions)
│   ├── utils.py             # Utilities (some unused)
│   └── processors.py        # Processors (some unused)
├── tombstone/               # Tombstone tracking library
│   ├── __init__.py
│   ├── tracker.py           # @tombstone decorator and tracker
│   └── analyzer.py          # Static analysis for dead code
├── scripts/                 # Automation scripts
│   ├── analyze_and_tombstone.py   # Add tombstones to code
│   ├── check_dead_code.py         # Query Supabase for dead code
│   └── remove_dead_code.py        # Remove confirmed dead code
├── supabase/                # Database schema
│   └── schema.sql           # Tombstone tracking tables
├── devin_prompts/           # Ready-to-use Devin prompts
│   ├── 01_analyze_and_tombstone.md
│   ├── 02_check_and_remove_dead_code.md
│   └── 03_slack_triggered_cleanup.md
├── requirements.txt
└── README.md
```

## How Tombstones Work

The `@tombstone` decorator wraps functions and logs to Supabase when they're called:

```python
from tombstone import tombstone

@tombstone(reason="Deprecated in v2.0")
def legacy_function():
    # This function is suspected to be unused
    # If it gets called, we'll know via Supabase
    pass
```

When `legacy_function()` is called:
1. The decorator logs the event to Supabase
2. The original function executes normally
3. After the monitoring period, we can query which tombstones were never triggered

## Supabase Tables

### `tombstones`
Stores registered tombstone locations:
- `tombstone_id`: Unique identifier
- `function_name`: Name of the function
- `file_path`: File location
- `line_number`: Line number
- `reason`: Why it's suspected dead
- `status`: active/triggered/removed/kept

### `tombstone_events`
Stores execution events:
- `tombstone_id`: Reference to tombstone
- `triggered_at`: When the code was executed
- `context`: Additional context (JSON)

### `dead_code_candidates` (View)
Shows tombstones with no events - confirmed dead code.

## Slack Integration

For fully automated workflows, you can:

1. **Schedule checks**: Use Supabase Edge Functions or GCP Cloud Scheduler
2. **Alert on dead code**: Send Slack notifications when dead code is found
3. **Trigger Devin**: Use Slack commands or webhooks to trigger cleanup

See `devin_prompts/03_slack_triggered_cleanup.md` for detailed setup instructions.

## Customization

### Adjusting Detection Sensitivity

Edit `tombstone/analyzer.py` to customize:
- `DEAD_CODE_KEYWORDS`: Words that suggest dead code
- `min_confidence`: Threshold for flagging code
- `exclude_patterns`: Files/directories to skip

### Custom Tombstone Behavior

The `TombstoneTracker` class can be customized:
- Different storage backends (not just Supabase)
- Custom event context
- Sampling for high-traffic code

## Best Practices

1. **Start with dry-run**: Always preview changes before applying
2. **Set appropriate monitoring periods**: 7-30 days depending on code usage patterns
3. **Review before removing**: Devin should create PRs for human review
4. **Keep tests passing**: Run tests after each change
5. **Track metrics**: Monitor how much dead code is found over time

## Troubleshooting

### Supabase Connection Issues
- Verify `SUPABASE_URL` and `SUPABASE_KEY` are set
- Check that the schema has been applied
- Ensure RLS policies allow access

### No Dead Code Found
- Verify tombstones were registered (check `tombstones` table)
- Ensure monitoring period has passed
- Check that the app was actually running

### False Positives
- Increase `min_confidence` threshold
- Add patterns to `exclude_patterns`
- Review and mark as "kept" in Supabase

## License

MIT License - Feel free to use and modify for your own projects.
