CREATE TABLE appdata (
    app_id BIGINT NOT NULL PRIMARY KEY,
    app_name VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    category_id INTEGER NOT NULL,
    developer_id BIGINT NOT NULL,
    developer_name VARCHAR(255) NOT NULL,
    developer_view_url VARCHAR(255),
    seller_name VARCHAR(255) NOT NULL,
    seller_url VARCHAR(255),
    price DECIMAL(10,2) NOT NULL,
    currency VARCHAR(8),
    rating_average DECIMAL(3,2) NOT NULL,
    rating_average_current_version DECIMAL(3,2) NOT NULL,
    rating_count BIGINT NOT NULL,
    rating_count_current_version BIGINT NOT NULL,
    app_url VARCHAR(255),
    screenshot_urls JSON,
    release_date DATETIME NOT NULL,
    release_date_current_version DATETIME NOT NULL,
    version VARCHAR(8) NOT NULL,
    date_extracted DATETIME NOT NULL,
    INDEX idx_category_id (category_id),
    FOREIGN KEY (category_id) REFERENCES category (id) ON DELETE CASCADE ON UPDATE CASCADE
);