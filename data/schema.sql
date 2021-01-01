CREATE TABLE IF NOT EXISTS suggestions(
    id serial,
    author bigint NOT NULL,
    message bigint,
    channel bigint,
    content text,
    status text,
    reason text,
    mod bigint,
    CONSTRAINT suggestions_pkey PRIMARY KEY (id)
);


