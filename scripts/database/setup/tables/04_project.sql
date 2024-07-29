CREATE TABLE project (
    project_id INTEGER NOT NULL,
    dataset ENUM('AppData', 'Review') NOT NULL,
    category_id INTEGER NOT NULL,
    category VARCHAR(128) NOT NULL,
    project_priority INTEGER NOT NULL DEFAULT 3,
    bookmark INTEGER NOT NULL DEFAULT 0,
    n_jobs INTEGER NOT NULL DEFAULT 0,
    last_job_id INTEGER NOT NULL,
    last_job_ended DATETIME,
    last_job_status ENUM("CREATED", "SCHEDULED", "IN_PROGRESS", "COMPLETE", "TERMINATED", "CANCELLED") NOT NULL DEFAULT "CREATED",
    project_status ENUM('NOT_STARTED', 'ACTIVE', 'INACTIVE', 'PAUSED', 'CANCELLED') NOT NULL "NOT STARTED",
    INDEX idx_dataset (dataset)

);
