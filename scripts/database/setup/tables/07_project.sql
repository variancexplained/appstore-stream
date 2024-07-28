CREATE TABLE project (
    id INTEGER NOT NULL,
    category_id INTEGER NOT NULL,
    category VARCHAR(128) NOT NULL,
    dataset ENUM('AppData', 'Review') NOT NULL,
    progress INTEGER NOT NULL DEFAULT 0,
    last_job_id VARCHAR(64),
    last_job_date DATETIME,
    INDEX idx_dataset (dataset)

);
