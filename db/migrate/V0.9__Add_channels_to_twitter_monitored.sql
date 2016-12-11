alter table twitter_monitored_channel
    add column channel_id bigint;

update twitter_monitored_channel
    set channel_id = server_id;

alter table twitter_monitored_channel
    alter column channel_id set not null;
