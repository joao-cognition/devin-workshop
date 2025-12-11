# Dead Code Detection Demo with Sentry

A 10-minute workshop demo showing Devin + Sentry for automated dead code detection.

## The Flow

1. **Devin adds tombstones** to your code (live)
2. **Sentry shows the logs** when tombstoned code runs
3. **Sentry triggers Devin** automatically to clean up

---

## Pre-Setup (Do Before Workshop)

Complete these steps before the workshop so the live demo is smooth.

### 1. Create Sentry Project

1. Go to [sentry.io](https://sentry.io) → Create account or sign in
2. Create new project → Select **Python** → Name it `dead-code-demo`
3. Copy your **DSN** from Settings → Projects → Client Keys

### 2. Get Sentry Auth Token

1. Go to Settings → Auth Tokens → Create New Token
2. Name: `devin-mcp`
3. Scopes: `project:read`, `event:read`, `issue:read`
4. Copy the token

### 3. Enable Sentry MCP in Devin

Add this to your Devin MCP config:

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

### 4. Set Up Auto-Trigger (Sentry → Devin)

This makes Sentry automatically trigger Devin when a tombstone fires.

**In Sentry:**
1. Go to Alerts → Create Alert Rule
2. Condition: "The issue's title contains `TOMBSTONE_HIT:`"
3. Action: Send webhook to your endpoint

**Deploy the webhook** (see `examples/sentry_webhook.py`):
- Deploy to GCP Cloud Run, AWS Lambda, or any server
- Set `DEVIN_API_KEY` environment variable
- Point Sentry alert to your webhook URL

### 5. Set Environment Variable

```bash
export SENTRY_DSN="https://xxx@xxx.ingest.sentry.io/xxx"
```

---

## Live Demo (10 minutes)

### Step 1: Show the Code (1 min)

Show `legacy.py` - plain Python with some suspicious functions:
- `process_user_auth` - "TODO: Remove - replaced by OAuth2"
- `old_export_to_csv` - "Deprecated"
- `debug_print_request` - "FIXME: Remove before production"

**Key point:** "We think these might be dead code, but we're not sure."

### Step 2: Ask Devin to Add Tombstones (3 min)

Give Devin this single prompt:

```
In the dead-code-demo-sentry folder:

1. Create a tombstones.py module that:
   - Initializes Sentry using SENTRY_DSN env var
   - Has a @tombstone decorator that logs "TOMBSTONE_HIT: <function_name>" to Sentry when called

2. Add @tombstone decorators to these functions in legacy.py:
   - process_user_auth
   - old_export_to_csv  
   - debug_print_request
   - legacy_format_date
   - calculate_legacy_checksum

3. Call init_sentry() at the start of app.py
```

Watch Devin create the Sentry integration and add tombstones.

### Step 3: Trigger a Tombstone (2 min)

Run the app to trigger a tombstoned function:

```bash
python app.py --legacy
```

### Step 4: See it in Sentry (2 min)

Open Sentry dashboard → Issues → See `TOMBSTONE_HIT: legacy.process_user_auth`

**Key point:** "Now we have proof this 'dead' code is actually running!"

### Step 5: Watch Devin Get Triggered (2 min)

Because of the alert rule you set up:
1. Sentry sees the tombstone issue
2. Sends webhook to your endpoint
3. Webhook calls Devin API
4. New Devin session starts automatically to clean up the code

**Show:** The new Devin session that was auto-created, already working on fixing the legacy code.

---

## Files

```
dead-code-demo-sentry/
├── app.py              # Sample app (no Sentry code initially)
├── legacy.py           # Legacy functions to tombstone
├── requirements.txt    # Just sentry-sdk
└── examples/
    └── sentry_webhook.py   # Webhook for Sentry → Devin
```

---

## Troubleshooting

**Tombstones not in Sentry:** Check SENTRY_DSN is set correctly

**Webhook not triggering:** Check Sentry alert rule matches "TOMBSTONE_HIT:" and webhook URL is correct

**Devin not starting:** Check DEVIN_API_KEY is set in webhook environment
