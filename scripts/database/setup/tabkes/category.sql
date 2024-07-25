CREATE TABLE Category (
    id INTEGER NOT NULL PRIMARY KEY UNIQUE,       -- Unique identifier for each category
    category VARCHAR(128) NOT NULL UNIQUE    -- Name of the category
);