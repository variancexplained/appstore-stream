CREATE TABLE IF NOT EXISTS review (
    review_id VARCHAR(32) NOT NULL UNIQUE,
    reviewer_id VARCHAR(64) NOT NULL,
    app_id BIGINT NOT NULL,
    app_name VARCHAR(255) NOT NULL,
    category_id INTEGER NOT NULL,
    category VARCHAR(64) NOT NULL,
    title VARCHAR(255),
    content TEXT NOT NULL,
    review_length INTEGER NOT NULL,
    rating INTEGER NOT NULL,
    vote_count INTEGER NOT NULL,
    vote_sum INTEGER NOT NULL,
    vote_avg DECIMAL (5,2) NOT NULL,
    dt_review DATETIME NOT NULL,
    dt_extract DATETIME NOT NULL,
    PRIMARY KEY (review_id),
    INDEX idx_app_id (app_id),
    INDEX idx_reviewer_id (review_id),
    INDEX idx_category_id (category_id)
);