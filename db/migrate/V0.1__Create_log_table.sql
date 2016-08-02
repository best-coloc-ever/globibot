create table log(
    id              bigint                          not null,
    channel_id      bigint                          not null,
    author_id       bigint                          not null,
    server_id       bigint                          not null,
    content         text                            not null,
    is_deleted      boolean                         not null    default false,
    stamp           timestamp without time zone     not null,
    attachments     text[]                          not null
);

alter table log add constraint log_unicity unique (id, stamp);
