CREATE TABLE IF NOT EXISTS job (
    job_id VARCHAR(64) NOT NULL PRIMARY KEY UNIQUE,        -- Unique identifier for each job
    job_name VARCHAR(255) NOT NULL,
    category_id INTEGER NOT NULL,
    category VARCHAR(64) NOT NULL,
    dataset ENUM('APPDATA', 'REVIEW') NOT NULL,                     -- AppData, Reviews
    stage ENUM('EXTRACT', 'TRANSFORM', 'LOAD') NOT NULL,
    dt_created DATETIME NOT NULL,                          -- When the jobrun was created
    dt_scheduled DATETIME,                        -- When the jobrun was scheduled
    dt_started DATETIME,                        -- When the jobrun was started
    dt_ended DATETIME,                                -- When the jobrun ended
    progress: BIGINT,                                  -- Bookmark for resume purposes.
    runtime INTEGER NOT NULL,                           -- Total runtime of the jobrun
    request_count INTEGER NOT NULL DEFAULT 0,
    app_count INTEGER NOT NULL  DEFAULT 0,
    review_count INTEGER DEFAULT 0,
    request_throughput DECIMAL(7,2) DEFAULT 0,
    app_throughput DECIMAL(7,2) DEFAULT 0,
    review_throughput DECIMAL(7,2) DEFAULT 0,
    total_errors INTEGER NOT NULL DEFAULT 0,
    client_errors INTEGER NOT NULL DEFAULT 0,
    server_errors INTEGER NOT NULL DEFAULT 0,
    data_errors INTEGER NOT NULL DEFAULT 0,
    config_id VARCHAR(64),                             -- Foreign key to Configuration
    force_restart TINYINT(1) NOT NULL DEFAULT 0,       -- Flag indicating whether to restart rather than resume from prior run.
    status ENUM('CREATED', 'IN-PROGRESS', 'COMPLETE', 'FAILED', 'CANCELLED') NOT NULL,
    INDEX idx_category_id (category_id),                        -- Index for job_id for quick lookups
    INDEX idx_job_type (job_type),                    -- Index for job_type to filter by type
    INDEX idx_config_id (config_id),                    -- Index for config_id for efficient joins
    INDEX idx_status (status),                          -- Index for status to filter by job run status
    FOREIGN KEY (config_id) REFERENCES config (config_id) ON DELETE SET NULL ON UPDATE CASCADE

);
