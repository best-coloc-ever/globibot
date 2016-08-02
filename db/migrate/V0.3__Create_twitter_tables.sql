create table twitter_monitored_channel(
    id          serial primary key,
    user_id     bigint not null,
    server_id   bigint not null
);

alter table twitter_monitored_channel
    add constraint twitter_monitored_channel_unicity unique (user_id, server_id);
