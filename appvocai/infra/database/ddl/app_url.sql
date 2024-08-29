CREATE TABLE app_url (
    app_id INTEGER NOT NULL,
    url_type VARCHAR(64) NOT NULL,
    url VARCHAR(255) NOT NULL,
    PRIMARY KEY (app_id, url_type),
    FOREIGN KEY (app_id) REFERENCES appdata(app_id)
);