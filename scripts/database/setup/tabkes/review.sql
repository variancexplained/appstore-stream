CREATE TABLE review (
    id VARCHAR(32) NOT NULL UNIQUE,
    reviewer_id VARCHAR(64) NOT NULL,
    app_id BIGINT NOT NULL,
    app_name VARCHAR(255) NOT NULL,
    category_id INTEGER NOT NULL,    
    title VARCHAR(255),
    content TEXT NOT NULL,
    rating INTEGER NOT NULL,
    vote_count INTEGER NOT NULL,
    vote_sum INTEGER NOT NULL,
    date DATETIME NOT NULL,
    date_extracted DATETIME NOT NULL,
    PRIMARY KEY (id),
    INDEX idx_app_id (app_id),
    INDEX idx_category_id (category_id),
    FOREIGN KEY (category_id) REFERENCES category (id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (app_id) REFERENCES appdata (id) ON DELETE CASCADE ON UPDATE CASCADE

);