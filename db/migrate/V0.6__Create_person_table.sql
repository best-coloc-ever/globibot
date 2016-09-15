create table person (
    id              bigint  primary key,
    password        text    not null,
    password_salt   text    not null,
    created_at      timestamp without time zone default (now() at time zone 'utc')
);
