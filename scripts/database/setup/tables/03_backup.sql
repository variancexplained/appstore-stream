CREATE TABLE IF NOT EXISTS backup (
    id VARCHAR(64) NOT NULL PRIMARY KEY UNIQUE,
    database_name VARCHAR(128) NOT NULL,
    backup_type ENUM('hourly', 'daily', 'weekly', 'monthly', 'annual', 'on-demand') NOT NULL,
    storage_type ENUM('local', 'cloud') NOT NULL,
    storage_location JSON NOT NULL,
    created DATETIME NOT NULL,
    expiration DATETIME NOT NULL,
    size BIGINT NOT NULL,
    status ENUM('completed', 'failed') NOT NULL,
    notes TEXT,
    INDEX idx_database_name (database_name),
    INDEX idx_backup_type (backup_type),
    INDEX idx_storage_type (storage_type),
    INDEX idx_created (created),
    INDEX idx_expiration (expiration),
    INDEX idx_status (status)
);
