create table twitter_oauth(
    id           bigint primary key,
    access_token text   not null,
    token_secret text   not null
);
