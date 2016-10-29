create table twitch_oauth(
    id      bigint  primary key,
    token   text    not null
);

create type twitch_notify_method as enum (
    'mention',
    'whisper'
);

create table twitch_notify(
    id      bigint                  not null,
    channel text                    not null,
    method  twitch_notify_method    not null     default 'mention',

    primary key(id, channel, method)
);
