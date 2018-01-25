create table trivia_result(
    id          serial                          primary key,
    user_id     bigint                          not null,
    topic       text                            not null,
    answer      text                            not null,
    stamp       timestamp without time zone     not null
);

-- create table eval_snippet(
--     id          serial  primary key,
--     author_id   bigint  not null,
--     name        text    not null,
--     language    text    not null,
--     code        text    not null
-- );

-- create table eval_environment(
--     id          serial  primary key,
--     author_id   bigint,
--     name        text    not null,
--     language    text    not null,
--     image       text    not null,
--     dockerfile  text    not null
-- );

-- alter table eval_environment add constraint eval_environment_unicity unique (
--     author_id, name
-- );
