# Devin Prompt: Slack-Triggered Dead Code Cleanup

This prompt is designed to be triggered automatically via Slack integration when monitoring alerts indicate dead code.

## Slack Workflow Setup

### Option 1: Devin Slack App Integration

If you have Devin's Slack integration enabled, you can trigger this workflow by mentioning Devin in a channel:

```
@Devin Dead code alert received for project [PROJECT_NAME]. 
Please check and remove confirmed dead code from [REPO_URL].
Monitoring period: 7 days.
```

### Option 2: Devin API Webhook

Set up a Slack workflow that calls the Devin API when an alert is received:

```bash
curl -X POST https://api.devin.ai/v1/sessions \
  -H "Authorization: Bearer $DEVIN_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Dead code cleanup triggered by monitoring alert.\n\nProject: PROJECT_NAME\nRepo: REPO_URL\n\nSteps:\n1. Check Supabase for tombstones never triggered in 7 days\n2. Remove confirmed dead code\n3. Create a PR\n4. Post results back to Slack channel #dead-code-alerts"
  }'
```

## Full Automated Flow

### 1. Alert Source (Choose One)

**Option A: Supabase Scheduled Function**
Create a Supabase Edge Function that runs daily to check for dead code:

```typescript
// supabase/functions/check-dead-code/index.ts
import { createClient } from '@supabase/supabase-js'

Deno.serve(async (req) => {
  const supabase = createClient(
    Deno.env.get('SUPABASE_URL')!,
    Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!
  )

  // Find tombstones registered > 7 days ago with no events
  const { data: deadCode } = await supabase
    .from('dead_code_candidates')
    .select('*')

  if (deadCode && deadCode.length > 0) {
    // Send to Slack
    await fetch(Deno.env.get('SLACK_WEBHOOK_URL')!, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        text: `Dead code alert: Found ${deadCode.length} functions that haven't been called in 7 days`,
        blocks: [
          {
            type: 'section',
            text: {
              type: 'mrkdwn',
              text: `*Dead Code Alert*\nFound ${deadCode.length} functions that haven't been called in 7 days.\n\nTrigger cleanup? /devin cleanup-dead-code`
            }
          }
        ]
      })
    })
  }

  return new Response(JSON.stringify({ checked: true, found: deadCode?.length || 0 }))
})
```

**Option B: GCP Cloud Scheduler + Cloud Function**
Set up a Cloud Scheduler job that triggers a Cloud Function to check Supabase and alert Slack.

### 2. Slack to Devin Integration

Create a Slack slash command `/devin-cleanup` that triggers the Devin API:

```python
# Example Slack bot handler
@app.command("/devin-cleanup")
def handle_cleanup_command(ack, body, client):
    ack()
    
    # Trigger Devin
    response = requests.post(
        "https://api.devin.ai/v1/sessions",
        headers={"Authorization": f"Bearer {DEVIN_API_KEY}"},
        json={
            "prompt": f"""
Dead code cleanup requested via Slack by {body['user_name']}.

Project: {body.get('text', 'dead-code-demo')}
Repo: https://github.com/your-org/your-repo

Steps:
1. Check Supabase for tombstones never triggered in 7 days
2. Remove confirmed dead code  
3. Create a PR
4. Report back with PR link
"""
        }
    )
    
    client.chat_postMessage(
        channel=body['channel_id'],
        text=f"Devin is working on dead code cleanup. Session: {response.json()['url']}"
    )
```

### 3. Devin Reports Back

After Devin creates the PR, it can post back to Slack using a webhook or the Slack MCP integration.
