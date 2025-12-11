"""
Tombstone Tracker - Records when potentially dead code is executed.

This module provides a decorator and utilities for tracking code execution
to identify truly dead code vs code that is rarely used.
"""

import os
import functools
import hashlib
from datetime import datetime
from typing import Callable, Optional, Any
from dataclasses import dataclass, field
import json

try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False


@dataclass
class TombstoneEvent:
    """Represents a single tombstone trigger event."""
    tombstone_id: str
    function_name: str
    file_path: str
    line_number: int
    triggered_at: datetime = field(default_factory=datetime.utcnow)
    context: dict = field(default_factory=dict)


class TombstoneTracker:
    """
    Tracks tombstone events and reports them to Supabase.
    
    Usage:
        tracker = TombstoneTracker()
        
        @tracker.tombstone("legacy_function")
        def some_old_function():
            pass
    """
    
    def __init__(
        self,
        supabase_url: Optional[str] = None,
        supabase_key: Optional[str] = None,
        project_name: str = "default",
        dry_run: bool = False,
    ):
        """
        Initialize the tombstone tracker.
        
        Args:
            supabase_url: Supabase project URL (or set SUPABASE_URL env var)
            supabase_key: Supabase anon key (or set SUPABASE_KEY env var)
            project_name: Name of the project being tracked
            dry_run: If True, only print events without sending to Supabase
        """
        self.project_name = project_name
        self.dry_run = dry_run
        self._client: Optional[Client] = None
        
        if not dry_run and SUPABASE_AVAILABLE:
            url = supabase_url or os.environ.get("SUPABASE_URL")
            key = supabase_key or os.environ.get("SUPABASE_KEY")
            
            if url and key:
                self._client = create_client(url, key)
    
    def _generate_tombstone_id(
        self, 
        function_name: str, 
        file_path: str, 
        line_number: int
    ) -> str:
        """Generate a unique ID for a tombstone based on its location."""
        content = f"{self.project_name}:{file_path}:{function_name}:{line_number}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def _record_event(self, event: TombstoneEvent) -> bool:
        """Record a tombstone event to Supabase."""
        if self.dry_run:
            print(f"[TOMBSTONE DRY RUN] {event.function_name} triggered at {event.triggered_at}")
            return True
        
        if not self._client:
            print(f"[TOMBSTONE LOCAL] {event.function_name} triggered at {event.triggered_at}")
            return False
        
        try:
            data = {
                "tombstone_id": event.tombstone_id,
                "project_name": self.project_name,
                "function_name": event.function_name,
                "file_path": event.file_path,
                "line_number": event.line_number,
                "triggered_at": event.triggered_at.isoformat(),
                "context": json.dumps(event.context),
            }
            
            self._client.table("tombstone_events").insert(data).execute()
            return True
        except Exception as e:
            print(f"[TOMBSTONE ERROR] Failed to record event: {e}")
            return False
    
    def tombstone(
        self,
        name: Optional[str] = None,
        reason: str = "Potentially unused code",
    ) -> Callable:
        """
        Decorator to mark a function as a tombstone candidate.
        
        When the decorated function is called, it records the event
        to track that this "potentially dead" code is actually being used.
        
        Args:
            name: Optional custom name for the tombstone
            reason: Reason why this code is suspected to be dead
        
        Returns:
            Decorated function that tracks execution
        """
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                # Get function location info
                function_name = name or func.__name__
                file_path = func.__code__.co_filename
                line_number = func.__code__.co_firstlineno
                
                # Generate tombstone ID
                tombstone_id = self._generate_tombstone_id(
                    function_name, file_path, line_number
                )
                
                # Create and record event
                event = TombstoneEvent(
                    tombstone_id=tombstone_id,
                    function_name=function_name,
                    file_path=file_path,
                    line_number=line_number,
                    context={"reason": reason},
                )
                self._record_event(event)
                
                # Execute the original function
                return func(*args, **kwargs)
            
            # Store tombstone metadata on the function
            wrapper._tombstone_id = None  # Will be set on first call
            wrapper._tombstone_reason = reason
            wrapper._is_tombstoned = True
            
            return wrapper
        return decorator
    
    def register_tombstone(
        self,
        tombstone_id: str,
        function_name: str,
        file_path: str,
        line_number: int,
        reason: str = "Potentially unused code",
    ) -> bool:
        """
        Register a tombstone in the database without triggering it.
        
        This is used during the initial tombstone insertion phase
        to record all potential dead code locations.
        """
        if self.dry_run:
            print(f"[TOMBSTONE DRY RUN] Registered: {function_name} in {file_path}")
            return True
        
        if not self._client:
            print(f"[TOMBSTONE LOCAL] Would register: {function_name} in {file_path}")
            return False
        
        try:
            data = {
                "tombstone_id": tombstone_id,
                "project_name": self.project_name,
                "function_name": function_name,
                "file_path": file_path,
                "line_number": line_number,
                "reason": reason,
                "registered_at": datetime.utcnow().isoformat(),
                "status": "active",
            }
            
            self._client.table("tombstones").upsert(data).execute()
            return True
        except Exception as e:
            print(f"[TOMBSTONE ERROR] Failed to register tombstone: {e}")
            return False


# Global tracker instance for convenience
_default_tracker: Optional[TombstoneTracker] = None


def get_tracker() -> TombstoneTracker:
    """Get or create the default tombstone tracker."""
    global _default_tracker
    if _default_tracker is None:
        _default_tracker = TombstoneTracker()
    return _default_tracker


def tombstone(
    name: Optional[str] = None,
    reason: str = "Potentially unused code",
) -> Callable:
    """
    Convenience decorator using the default tracker.
    
    Usage:
        from tombstone import tombstone
        
        @tombstone(reason="Deprecated in v2.0")
        def old_function():
            pass
    """
    return get_tracker().tombstone(name=name, reason=reason)
