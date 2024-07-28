CREATE TABLE IF NOT EXISTS  project (
    id INTEGER NOT NULL PRIMARY KEY UNIQUE,       -- Unique identifier for each category
    category VARCHAR(128) NOT NULL UNIQUE,    -- Name of the category
    priority INTEGER NOT NULL, DEFAULT 3
    scheduled DATETIME,
    started DATETIME ,
    last_job_end DATETIME,
    last_job_status ENUM('CREATED', 'IN-PROGRESS', 'COMPLETE', 'FAILED', 'CANCELLED') NOT NULL,
    job_count INTEGER DEFAULT 0,
    progress  BIGINT DEFAULT 0,                                  -- Bookmark for resume purposes.
    runtime INTEGER NOT NULL DEFAULT 0,                         -- Total runtime of the jobrun,
    request_count INTEGER NOT NULL DEFAULT 0,
    app_count INTEGER NOT NULL  DEFAULT 0,
    review_count INTEGER NOT NULL DEFAULT 0,
    request_throughput DECIMAL(7,2) DEFAULT 0,
    app_throughput DECIMAL(7,2) DEFAULT 0,
    total_latency DECIMAL(7,2) DEFAULT 0,
    ave_latency DECIMAL(7,2) DEFAULT 0,
    total_errors INTEGER NOT NULL DEFAULT 0,
    client_errors INTEGER NOT NULL DEFAULT 0,
    server_errors INTEGER NOT NULL DEFAULT 0,
    data_errors INTEGER NOT NULL DEFAULT 0,
);
