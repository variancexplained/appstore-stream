CREATE TABLE category_app (
    app_id INTEGER NOT NULL,
    category_id INTEGER NOT NULL,
    PRIMARY KEY (app_id, category_id),
    FOREIGN KEY (app_id) REFERENCES appdata(app_id),
    FOREIGN KEY (category_id) REFERENCES category(id)
);