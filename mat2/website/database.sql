-- user table
CREATE TABLE IF NOT EXISTS User (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    role TEXT NOT NULL
);

-- adds admin and user for testing stuff
INSERT INTO User (username, email, password, role) VALUES ('admin', 'admin@admin.com', '1', 'Admin');
INSERT INTO User (username, email, password, role) VALUES ('user', 'user@user.com', '1', 'User');

CREATE TABLE IF NOT EXISTS Hash (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    hash TEXT NOT NULL,
);

