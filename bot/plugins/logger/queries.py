create_log = '''
    insert into log (
        id, server_id, channel_id, author_id,
        content, stamp, attachments
    )
    values (
        %(id)s, %(server_id)s, %(channel_id)s, %(author_id)s,
        %(content)s, %(stamp)s, %(attachments)s
    )
'''

mark_deleted = '''
    update  log
    set     is_deleted = 't'
    where   id = (%(id)s)
'''

last_deleted_logs = '''
    select          content, attachments from log
        where       is_deleted = 't'
            and     author_id = (%(author_id)s)
        order by    stamp desc
        limit       (%(limit)s)
'''

last_edited_logs = '''
    select id, content, attachments from log
        where       id in (
            select          id
                from        log
                where       author_id = (%(author_id)s)
                group by    id
                having      count(id) > 1
            )
        order by    stamp desc
        limit       (%(limit)s)
'''

find_logs = '''
    select content  from log
        where       content ilike %(str)s
            and     author_id = %(author_id)s
        order by    stamp desc
        limit       %(limit)s
'''

most_logs = '''
    select author_id, count(distinct id), max(stamp) from log
        where       server_id = %(server_id)s
        group by    author_id
        order by    count(distinct id) desc
        limit       %(limit)s
'''

user_content = '''
    select          id, channel_id, server_id, content, is_deleted, stamp
        from        log
        where       author_id = %(author_id)s
            and     server_id in %(server_ids)s
        order by    stamp desc
'''

server_activity_per_day = '''
    select          count(*), count(distinct id),
                    count(case is_deleted when 't' then 1 else null end),
                    date_trunc('day', stamp) as stamp
        from        log
        where       extract('epoch' from stamp) > %(start)s
            and     server_id = %(server_id)s
        group by    date_trunc('day', stamp)
        order by    stamp
'''

server_activity_per_channel = '''
    select          count(*), count(distinct id),
                    count(case is_deleted when 't' then 1 else null end),
                    channel_id
        from        log
        where       extract('epoch' from stamp) > %(start)s
            and     server_id = %(server_id)s
        group by    channel_id
        order by    count(*)
'''

user_attachments = '''
    select      attachments
        from    log
        where   author_id = %(author_id)s
            and server_id in %(server_ids)s
            and attachments != '{}'
'''
