# Devin Prompt: Fix Legacy Code from Sentry Issue

Use this prompt after a tombstone has been triggered and you have a Sentry issue URL.

## Prompt

```
A tombstone was triggered in our codebase. Use the Sentry MCP to investigate and fix it.

Sentry Issue URL: [PASTE YOUR SENTRY ISSUE URL HERE]

Please:
1. Use the 'sentry' MCP server's get_sentry_issue tool to fetch details about this issue
2. Analyze the issue to understand:
   - Which function was called (from the TOMBSTONE_HIT message)
   - Where it was called from (from the stack trace)
   - Why it was marked as legacy (from the reason)
3. Find the corresponding function in the codebase
4. Decide the best action:
   - If truly dead code with no callers: Remove the function
   - If still needed: Refactor to use modern patterns
   - If unclear: Add a comment explaining the situation
5. Update any code that calls this function
6. Remove the @tombstone decorator after fixing
7. Create a PR with the cleanup
```

## Example Workflow

1. **Devin calls Sentry MCP:**
   ```
   get_sentry_issue(issue_id_or_url="https://sentry.io/organizations/xxx/issues/xxx/")
   ```

2. **Devin sees the issue details:**
   - Message: `TOMBSTONE_HIT: legacy.process_user_auth | reason=TODO: Remove - replaced by OAuth2`
   - Stack trace pointing to `app.py:35` calling `legacy.py:45`

3. **Devin analyzes and fixes:**
   - Finds `process_user_auth` in `legacy.py`
   - Sees it uses insecure MD5 hashing
   - Either removes it or replaces with modern auth

4. **Devin creates PR:**
   - Removes/refactors the legacy function
   - Updates callers
   - Removes the tombstone decorator
