CREATE TABLE notes (
    id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    title varchar(120) NOT NULL,
    content varchar(10000) NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now()
);
