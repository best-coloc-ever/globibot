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
    select author_id, count(*) from log
        where       server_id = %(server_id)s
        group by    author_id
        order by    count(*) desc
        limit       %(limit)s
'''
