create table twitch_monitored_channel(
    id          serial primary key,
    name        text   not null,
    server_id   bigint not null
);

alter table twitch_monitored_channel
    add constraint twitch_monitored_channel_unicity unique (name, server_id);
