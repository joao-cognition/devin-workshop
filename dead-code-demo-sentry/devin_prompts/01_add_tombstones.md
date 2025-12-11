# Devin Prompt: Add Tombstones to Legacy Code

Use this prompt to have Devin analyze the codebase and add Sentry-backed tombstone tracking.

## Prompt

```
In the dead-code-demo-sentry folder, I need you to:

1. Create a `tombstones.py` module that:
   - Initializes Sentry using the SENTRY_DSN environment variable
   - Defines a @tombstone decorator that logs to Sentry when decorated functions are called
   - The Sentry message should start with "TOMBSTONE_HIT:" followed by the function name and reason

2. In `legacy.py`, add @tombstone decorators to functions that look like dead code candidates:
   - Functions with "legacy", "old", "debug" in their names
   - Functions with comments mentioning "deprecated", "TODO: remove", "FIXME"

3. Update `app.py` to initialize Sentry at startup by calling init_sentry()

4. Create a PR with these changes

The tombstone decorator should look something like:
- Log a Sentry message with level "warning"
- Include the function name and reason in the message
- Still execute the original function normally
```

## Expected Output

Devin should create:

1. **tombstones.py** with:
```python
import os
from functools import wraps
import sentry_sdk

def init_sentry():
    dsn = os.environ.get("SENTRY_DSN")
    if dsn:
        sentry_sdk.init(dsn=dsn)

def tombstone(reason="potentially unused code"):
    def decorator(fn):
        name = f"{fn.__module__}.{fn.__qualname__}"
        
        @wraps(fn)
        def wrapper(*args, **kwargs):
            sentry_sdk.capture_message(
                f"TOMBSTONE_HIT: {name} | reason={reason}",
                level="warning"
            )
            return fn(*args, **kwargs)
        
        return wrapper
    return decorator
```

2. **Updated legacy.py** with decorators like:
```python
from tombstones import tombstone

@tombstone(reason="TODO: Remove - replaced by OAuth2")
def process_user_auth(credentials):
    ...
```

3. **Updated app.py** with:
```python
from tombstones import init_sentry

# At the start of main() or module level
init_sentry()
```
