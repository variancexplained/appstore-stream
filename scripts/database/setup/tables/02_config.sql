CREATE TABLE IF NOT EXISTS  config (
    id VARCHAR(64) NOT NULL PRIMARY KEY UNIQUE,   -- Unique identifier for the configuration
    name VARCHAR(128) NOT NULL,                   -- Name of the configuration
    description TEXT,                             -- Description of the configuration
    batch_size INTEGER NOT NULL,                  -- Batch size setting
    max_concurrency INTEGER NOT NULL,             -- Maximum concurrency level
    base_request_rate INTEGER NOT NULL,           -- Base request rate
    config JSON NOT NULL,                         -- Additional configuration in JSON format
    created DATETIME NOT NULL,                    -- Date and time when the configuration was created
    INDEX idx_name (name)                         -- Index on the name column for faster searches
);
