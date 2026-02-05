PRAGMA foreign_keys = ON;


DROP TABLE IF EXISTS views;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS titles;


CREATE TABLE users (
  user_id TEXT PRIMARY KEY,
  signup_date TEXT NOT NULL,
  country TEXT,
  plan_type TEXT
);


CREATE TABLE titles (
  title_id TEXT PRIMARY KEY,
  title_name TEXT NOT NULL,
  content_type TEXT,
  genre TEXT,
  release_year INTEGER,
  maturity_rating TEXT
);


CREATE TABLE views (
  view_id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL,
  title_id TEXT NOT NULL,
  view_start TEXT NOT NULL,
  view_end TEXT NOT NULL,
  watch_minutes INTEGER NOT NULL,
  completed INTEGER NOT NULL CHECK (completed IN (0,1)),
  FOREIGN KEY (user_id) REFERENCES users(user_id),
  FOREIGN KEY (title_id) REFERENCES titles(title_id)
);
