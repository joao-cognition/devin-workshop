"""
Example: Sentry Webhook to Devin API

This script shows how to automatically trigger Devin when a tombstone
issue is created in Sentry.

Setup:
1. Deploy this as a web service (e.g., GCP Cloud Run, AWS Lambda, etc.)
2. In Sentry, create an Alert Rule:
   - Condition: Issue title contains "TOMBSTONE_HIT:"
   - Action: Send webhook to your deployed URL
3. Set DEVIN_API_KEY environment variable

When a tombstone fires, Sentry will call this webhook, which will
automatically start a Devin session to investigate and fix the issue.
"""

import os
import json
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

DEVIN_API_KEY = os.environ.get("DEVIN_API_KEY")
DEVIN_API_URL = "https://api.devin.ai/v1/sessions"


@app.route("/sentry-webhook", methods=["POST"])
def handle_sentry_webhook():
    """
    Handle incoming Sentry webhook when a tombstone issue is created.
    """
    if not DEVIN_API_KEY:
        return jsonify({"error": "DEVIN_API_KEY not configured"}), 500
    
    payload = request.json
    
    # Extract issue details from Sentry webhook payload
    # Note: Actual payload structure may vary - check Sentry docs
    issue_data = payload.get("data", {}).get("issue", {})
    issue_url = issue_data.get("web_url", "")
    issue_title = issue_data.get("title", "")
    
    # Only process tombstone issues
    if "TOMBSTONE_HIT:" not in issue_title:
        return jsonify({"status": "ignored", "reason": "not a tombstone issue"})
    
    # Create a Devin session to fix the issue
    prompt = f"""
A tombstone was triggered in our codebase and created a Sentry issue.

Sentry Issue URL: {issue_url}
Issue Title: {issue_title}

Please:
1. Use the 'sentry' MCP server's get_sentry_issue tool to fetch details
2. Find the corresponding function in the codebase
3. Analyze why this legacy code was called
4. Either remove the dead code or refactor it to use modern patterns
5. Create a PR with the cleanup

This is an automated request triggered by a Sentry alert.
"""
    
    try:
        response = requests.post(
            DEVIN_API_URL,
            headers={
                "Authorization": f"Bearer {DEVIN_API_KEY}",
                "Content-Type": "application/json",
            },
            json={"prompt": prompt},
            timeout=30,
        )
        response.raise_for_status()
        
        session_data = response.json()
        return jsonify({
            "status": "success",
            "devin_session": session_data.get("url", ""),
            "message": "Devin session started to fix tombstone issue",
        })
    
    except requests.RequestException as e:
        return jsonify({
            "status": "error",
            "message": str(e),
        }), 500


@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "healthy"})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)


# =============================================================================
# ALTERNATIVE: Simple script version (not a web server)
# =============================================================================

def check_and_trigger_devin_for_tombstones():
    """
    Alternative approach: Periodically check Sentry for new tombstone issues
    and trigger Devin for each one.
    
    This can be run as a cron job or scheduled task instead of using webhooks.
    """
    import os
    import requests
    
    SENTRY_TOKEN = os.environ.get("SENTRY_TOKEN")
    SENTRY_ORG = os.environ.get("SENTRY_ORG")
    SENTRY_PROJECT = os.environ.get("SENTRY_PROJECT")
    DEVIN_API_KEY = os.environ.get("DEVIN_API_KEY")
    
    # Query Sentry API for recent tombstone issues
    # Note: This is a simplified example - real implementation would need pagination
    sentry_api_url = f"https://sentry.io/api/0/projects/{SENTRY_ORG}/{SENTRY_PROJECT}/issues/"
    
    response = requests.get(
        sentry_api_url,
        headers={"Authorization": f"Bearer {SENTRY_TOKEN}"},
        params={"query": "TOMBSTONE_HIT:", "statsPeriod": "24h"},
    )
    
    issues = response.json()
    
    for issue in issues:
        if issue.get("status") == "unresolved":
            # Trigger Devin for this issue
            prompt = f"""
Fix this tombstone issue from Sentry:
URL: https://sentry.io/organizations/{SENTRY_ORG}/issues/{issue['id']}/
Title: {issue['title']}

Use the Sentry MCP to get details and create a PR to fix the legacy code.
"""
            requests.post(
                "https://api.devin.ai/v1/sessions",
                headers={"Authorization": f"Bearer {DEVIN_API_KEY}"},
                json={"prompt": prompt},
            )
            print(f"Triggered Devin for issue: {issue['title']}")
