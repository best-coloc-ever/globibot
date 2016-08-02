create type eval_behavior as enum (
    'manual',
    'auto',
    'off'
);

create table eval_setting(
    author_id   bigint          primary key,
    behavior    eval_behavior   not null    default 'manual'
);

create table eval_snippet(
    id          serial  primary key,
    author_id   bigint  not null,
    name        text    not null,
    language    text    not null,
    code        text    not null
);

create table eval_environment(
    id          serial  primary key,
    author_id   bigint,
    name        text    not null,
    language    text    not null,
    image       text    not null,
    dockerfile  text    not null
);

alter table eval_environment add constraint eval_environment_unicity unique (
    author_id, name
);
