-- Tombstone Tracking Schema for Dead Code Detection
-- Run this in your Supabase SQL Editor to set up the tracking tables

-- Table to store registered tombstones (potential dead code locations)
CREATE TABLE IF NOT EXISTS tombstones (
    id BIGSERIAL PRIMARY KEY,
    tombstone_id TEXT UNIQUE NOT NULL,
    project_name TEXT NOT NULL,
    function_name TEXT NOT NULL,
    file_path TEXT NOT NULL,
    line_number INTEGER NOT NULL,
    reason TEXT DEFAULT 'Potentially unused code',
    registered_at TIMESTAMPTZ DEFAULT NOW(),
    status TEXT DEFAULT 'active' CHECK (status IN ('active', 'triggered', 'removed', 'kept')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Table to store tombstone trigger events (when code is actually executed)
CREATE TABLE IF NOT EXISTS tombstone_events (
    id BIGSERIAL PRIMARY KEY,
    tombstone_id TEXT NOT NULL,
    project_name TEXT NOT NULL,
    function_name TEXT NOT NULL,
    file_path TEXT NOT NULL,
    line_number INTEGER NOT NULL,
    triggered_at TIMESTAMPTZ DEFAULT NOW(),
    context JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for faster lookups
CREATE INDEX IF NOT EXISTS idx_tombstones_project ON tombstones(project_name);
CREATE INDEX IF NOT EXISTS idx_tombstones_status ON tombstones(status);
CREATE INDEX IF NOT EXISTS idx_tombstone_events_tombstone_id ON tombstone_events(tombstone_id);
CREATE INDEX IF NOT EXISTS idx_tombstone_events_triggered_at ON tombstone_events(triggered_at);

-- Enable Row Level Security
ALTER TABLE tombstones ENABLE ROW LEVEL SECURITY;
ALTER TABLE tombstone_events ENABLE ROW LEVEL SECURITY;

-- Allow public access for demo purposes (in production, use proper auth)
CREATE POLICY "Allow public read access on tombstones" ON tombstones FOR SELECT USING (true);
CREATE POLICY "Allow public insert access on tombstones" ON tombstones FOR INSERT WITH CHECK (true);
CREATE POLICY "Allow public update access on tombstones" ON tombstones FOR UPDATE USING (true);

CREATE POLICY "Allow public read access on tombstone_events" ON tombstone_events FOR SELECT USING (true);
CREATE POLICY "Allow public insert access on tombstone_events" ON tombstone_events FOR INSERT WITH CHECK (true);

-- View to easily find dead code (tombstones with no events after monitoring period)
CREATE OR REPLACE VIEW dead_code_candidates AS
SELECT 
    t.tombstone_id,
    t.project_name,
    t.function_name,
    t.file_path,
    t.line_number,
    t.reason,
    t.registered_at,
    t.status,
    COUNT(e.id) as trigger_count,
    MAX(e.triggered_at) as last_triggered
FROM tombstones t
LEFT JOIN tombstone_events e ON t.tombstone_id = e.tombstone_id
WHERE t.status = 'active'
GROUP BY t.id
HAVING COUNT(e.id) = 0
ORDER BY t.registered_at ASC;

-- View to see all tombstone activity
CREATE OR REPLACE VIEW tombstone_activity AS
SELECT 
    t.tombstone_id,
    t.project_name,
    t.function_name,
    t.file_path,
    t.line_number,
    t.reason,
    t.status,
    COUNT(e.id) as trigger_count,
    MIN(e.triggered_at) as first_triggered,
    MAX(e.triggered_at) as last_triggered
FROM tombstones t
LEFT JOIN tombstone_events e ON t.tombstone_id = e.tombstone_id
GROUP BY t.id
ORDER BY trigger_count DESC, t.registered_at ASC;
