# Dead Code Detection Demo with Sentry

A workshop demo showing how to use Devin for automated dead code detection and cleanup, with Sentry integration for runtime tracking.

## Overview

This demo shows a complete flow where:
1. **Devin adds tombstones** to potentially unused code
2. **Tombstones log to Sentry** when the code is executed
3. **You see tombstone events** in Sentry's dashboard
4. **Devin queries Sentry via MCP** and cleans up the legacy code

## Prerequisites

Before the workshop, you need:
- A **Sentry account** (free tier works)
- **Sentry MCP** enabled in Devin
- **DEVIN_API_KEY** (for automated triggers)

---

## Step-by-Step Setup

### Step 1: Create a Sentry Project

1. Go to [sentry.io](https://sentry.io) and sign in (or create a free account)
2. Create a new project:
   - Click **Projects** → **Create Project**
   - Select **Python** as the platform
   - Name it `dead-code-demo`
3. Copy your **DSN** (looks like `https://xxx@xxx.ingest.sentry.io/xxx`)
   - You'll find this in **Settings** → **Projects** → **dead-code-demo** → **Client Keys (DSN)**

### Step 2: Get a Sentry Auth Token

1. Go to **Settings** → **Auth Tokens**
2. Click **Create New Token**
3. Give it a name like `devin-mcp`
4. Select scopes: `project:read`, `event:read`, `issue:read`
5. Copy the token (you'll need it for the MCP config)

### Step 3: Enable Sentry MCP in Devin

Ask your Devin admin to enable the Sentry MCP with this config:

```json
{
  "mcpServers": {
    "sentry": {
      "command": "uvx",
      "args": ["mcp-server-sentry", "--auth-token", "YOUR_SENTRY_TOKEN"]
    }
  }
}
```

Replace `YOUR_SENTRY_TOKEN` with the token from Step 2.

### Step 4: Set Environment Variables

For the demo, you'll need these environment variables:

```bash
export SENTRY_DSN="https://xxx@xxx.ingest.sentry.io/xxx"  # From Step 1
export DEVIN_API_KEY="your-devin-api-key"                  # For automated triggers
```

---

## Workshop Demo Flow

### Phase 1: Show the Starting Code (2 min)

Show participants the `legacy.py` file:
- Point out functions with names like `legacy_`, `old_`, `debug_`
- Show comments like "TODO: Remove", "Deprecated", "FIXME"
- Explain: "We suspect these are dead code, but we're not sure"

```bash
cat legacy.py
```

### Phase 2: Devin Adds Tombstones (10 min)

Give Devin this prompt:

```
In the dead-code-demo-sentry folder, I need you to:

1. Create a `tombstones.py` module that:
   - Initializes Sentry using the SENTRY_DSN environment variable
   - Defines a @tombstone decorator that logs to Sentry when decorated functions are called
   - The Sentry message should start with "TOMBSTONE_HIT:" followed by the function name

2. In `legacy.py`, add @tombstone decorators to functions that look like dead code candidates:
   - Functions with "legacy", "old", "debug" in their names
   - Functions with comments mentioning "deprecated", "TODO: remove", "FIXME"

3. Update `app.py` to initialize Sentry at startup

4. Create a PR with these changes
```

**Watch Devin:**
- Create `tombstones.py` with Sentry integration
- Add `@tombstone` decorators to suspicious functions
- Create a PR

### Phase 3: Trigger a Tombstone (5 min)

Run the app with the legacy flag to trigger a tombstone:

```bash
cd dead-code-demo-sentry
SENTRY_DSN="your-dsn" python app.py --legacy
```

This calls `process_user_auth()` which should now have a tombstone decorator.

### Phase 4: View in Sentry (5 min)

1. Open your Sentry dashboard
2. Go to **Issues**
3. You should see a new issue with title like: `TOMBSTONE_HIT: legacy.process_user_auth`
4. Click on it to see:
   - The full message with reason
   - Stack trace showing where it was called
   - Timestamp of when it was triggered

**Key point:** "Now we have runtime evidence that this legacy code is actually being used!"

### Phase 5: Devin Fixes the Legacy Code via MCP (10 min)

Copy the Sentry issue URL, then give Devin this prompt:

```
A tombstone was triggered in our codebase. Use the Sentry MCP to investigate and fix it.

Sentry Issue URL: [paste the URL here]

Please:
1. Use the 'sentry' MCP server's get_sentry_issue tool to fetch details about this issue
2. Find the corresponding function in the codebase
3. Either:
   - Remove the function if it's truly dead code, OR
   - Refactor it to use modern patterns if it's still needed
4. Update any callers of this function
5. Create a PR with the cleanup
```

**Watch Devin:**
- Call the Sentry MCP to get issue details
- Navigate to the legacy function
- Refactor or remove the code
- Create a cleanup PR

### Phase 6: Discuss Automation (5 min)

Explain how this can be fully automated:

1. **Sentry Alert Rule**: Create an alert when issues match `TOMBSTONE_HIT:*`
2. **Webhook**: Alert triggers a webhook to your server
3. **Devin API**: Webhook calls Devin API to start a cleanup session

Show the example webhook code in `examples/sentry_webhook.py`.

---

## Files in This Demo

```
dead-code-demo-sentry/
├── app.py              # Main application (no tombstones initially)
├── legacy.py           # Legacy code with dead code candidates
├── README.md           # This file
├── requirements.txt    # Dependencies
├── devin_prompts/      # Ready-to-use Devin prompts
│   ├── 01_add_tombstones.md
│   └── 02_fix_from_sentry.md
└── examples/
    └── sentry_webhook.py   # Example automated trigger
```

---

## Troubleshooting

### Tombstones not appearing in Sentry
- Check that `SENTRY_DSN` is set correctly
- Verify the Sentry project is active
- Check Sentry's **Inbound Filters** aren't blocking messages

### Sentry MCP not working
- Verify the auth token has correct scopes
- Check the MCP config is correct
- Try the MCP in Devin's playground first

### "TOMBSTONE_HIT" issues not showing
- Make sure you ran the app with `--legacy` flag
- Check the function actually has the `@tombstone` decorator
- Look in Sentry's **Discover** tab for recent events

---

## Next Steps

After the workshop, participants can:
1. Apply this pattern to their own codebases
2. Set up automated Sentry → Devin workflows
3. Use the "never triggered" analysis for true dead code removal

For the "never triggered" flow (finding code that was tombstoned but never called), you'd need a batch job that:
1. Lists all `@tombstone` decorated functions in the codebase
2. Queries Sentry API for each one
3. Identifies functions with zero events over N days
4. Triggers Devin to remove those as confirmed dead code

This is more complex and typically done as a scheduled job rather than a live demo.
