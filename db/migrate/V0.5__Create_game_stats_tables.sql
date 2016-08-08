create table game_played_time (
    id          serial  primary key,
    author_id   bigint  not null,
    name        text    not null,
    duration    int     not null,
    created_at  timestamp without time zone default (now() at time zone 'utc')
);

alter table game_played_time
    add constraint game_played_time_unicity unique (author_id, name);
