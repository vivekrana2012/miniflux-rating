-- Ratings Table
-- Maps generated blog hash IDs to Miniflux entry IDs

CREATE TABLE IF NOT EXISTS ratings (
    id VARCHAR(12) PRIMARY KEY,        -- Hash value generated from URL
    entry_id BIGINT NOT NULL,          -- Miniflux entry ID
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(entry_id)                   -- Ensure one entry is only evaluated once
);

-- Index for faster lookups by entry_id
CREATE INDEX IF NOT EXISTS idx_ratings_entry_id ON ratings(entry_id);
