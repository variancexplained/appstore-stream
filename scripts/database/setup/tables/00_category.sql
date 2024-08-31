CREATE TABLE category (
    id INTEGER NOT NULL PRIMARY KEY,
    category VARCHAR(128) NOT NULL,
    UNIQUE (id) -- Ensures the id is unique
);
