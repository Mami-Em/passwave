CREATE TABLE human (
    id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL,
    password VARCHAR NOT NULL
);

CREATE TABLE databae (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES human,
    nameUsed VARCHAR NOT NULL,
    appName VARCHAR NOT NULL,
    passwordUsed VARCHAR NOT NULL
);

