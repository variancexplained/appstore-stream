CREATE TABLE project (
    project_id INTEGER NOT NULL,
    dataset ENUM('AppData', 'Review') NOT NULL,
    category_id INTEGER NOT NULL,
    category VARCHAR(128) NOT NULL,
    project_priority INTEGER NOT NULL DEFAULT 3,
    progress INTEGER NOT NULL DEFAULT 0,
    n_jobs INTEGER NOT NULL DEFAULT 0,
    last_job_id VARCHAR(64),
    dt_last_job DATETIME,
    project_status ENUM('NOT_STARTED', 'ACTIVE', 'INACTIVE', 'PAUSED', 'CANCELLED') NOT NULL,
    INDEX idx_dataset (dataset)

);
