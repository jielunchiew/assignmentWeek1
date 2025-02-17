DROP TABLE IF EXISTS owners

CREATE TABLE owners (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    date_created TIMESTAMPTZ,
    date_modified TIMESTAMPTZ
);

DROP TABLE IF EXISTS pets

CREATE TABLE pets (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    owner_id INTEGER REFERENCES owners(id) ON DELETE SET NULL,
    breed VARCHAR(255),
    date_created TIMESTAMPTZ,
    date_modified TIMESTAMPTZ
);