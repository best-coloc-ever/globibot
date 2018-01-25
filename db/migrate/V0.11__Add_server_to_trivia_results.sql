alter table trivia_result
    add column server_id bigint;

-- update twitter_monitored_channel
--     set channel_id = server_id;

-- alter table twitter_monitored_channel
--     alter column channel_id set not null;
