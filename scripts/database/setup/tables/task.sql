CREATE TABLE IF NOT EXISTS task (
    id VARCHAR(64) NOT NULL UNIQUE,
    task_type ENUM('AppData', 'Review') NOT NULL,
    task_name VARCHAR(255),
    category_id VARCHAR(4),
    created DATETIME,
    PRIMARY KEY (id),
    INDEX idx_category_id (category_id),
    INDEX idx_task_type (task_type),
    FOREIGN KEY (category_id) REFERENCES category (id) ON DELETE CASCADE ON UPDATE CASCADE
);