CREATE TABLE IF NOT EXISTS taskRun (
    id VARCHAR(64) NOT NULL PRIMARY KEY UNIQUE,        -- Unique identifier for each task run
    task_id VARCHAR(64) NOT NULL,                       -- Foreign key to Task
    task_type VARCHAR(32) NOT NULL,                     -- Type of task (e.g., AppData, Review)
    task_name VARCHAR(128) NOT NULL,                    -- Name or description of the task
    scheduled DATETIME NOT NULL,                        -- When the task was scheduled
    created DATETIME NOT NULL,                          -- When the task run was created
    completed DATETIME,                                -- When the task run was completed
    runtime INTEGER NOT NULL,                           -- Total runtime of the task
    requests INTEGER NOT NULL,                          -- Number of requests processed
    requests_per_second DECIMAL(10,2) NOT NULL,         -- Average requests per second
    records INTEGER NOT NULL,                           -- Number of records processed
    records_per_second DECIMAL(10,2) NOT NULL,          -- Average records per second
    errors INTEGER,                                    -- Total errors encountered
    client_errors INTEGER,                             -- Number of client errors
    data_errors INTEGER,                               -- Number of data errors
    server_errors INTEGER,                             -- Number of server errors
    retries INTEGER,                                   -- Number of retries
    timeouts INTEGER,                                  -- Number of timeouts
    config_id VARCHAR(64) NOT NULL,                     -- Foreign key to Configuration
    force TINYINT(1) NOT NULL DEFAULT 0,                -- Flag indicating force execution
    status ENUM('PENDING', 'IN-PROGRESS', 'COMPLETE', 'FAILED', 'CANCELED') NOT NULL,
    INDEX idx_task_id (task_id),                        -- Index for task_id for quick lookups
    INDEX idx_task_type (task_type),                    -- Index for task_type to filter by type
    INDEX idx_config_id (config_id),                    -- Index for config_id for efficient joins
    INDEX idx_status (status),                          -- Index for status to filter by task run status
    FOREIGN KEY (task_id) REFERENCES task (id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (config_id) REFERENCES config (id) ON DELETE SET NULL ON UPDATE CASCADE
);
