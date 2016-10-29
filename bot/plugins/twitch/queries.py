get_monitored = '''
    select id, name, server_id
    from   twitch_monitored_channel
'''

add_monitored = '''
    insert into twitch_monitored_channel (name, server_id)
    values                               (%(name)s, %(server_id)s)
'''

remove_monitored = '''
    delete from twitch_monitored_channel
        where   name = %(name)s
            and server_id = %(server_id)s
'''

add_user = '''
    insert into twitch_oauth (id, token)
        values               (%(id)s, %(token)s)
'''

get_user = '''
    select      token
        from    twitch_oauth
        where   id = %(id)s
'''

delete_user = '''
    delete      from twitch_oauth
        where   id = %(id)s
'''

get_monitored_names = '''
    select      name
        from    twitch_monitored_channel
        where   server_id in %(server_ids)s
'''

get_notified = '''
    select      channel, method
        from    twitch_notify
        where   id = %(id)s
'''

user_notify_add = '''
    insert into twitch_notify (id, channel, method)
    values                    (%(id)s, %(channel)s, %(method)s)
'''

user_notify_remove = '''
    delete  from twitch_notify
    where   id = %(id)s
        and channel = %(channel)s
        and method = %(method)s
'''

get_subscribed_users = '''
    select      id
        from    twitch_notify
        where   channel = %(channel)s
            and method = %(method)s
'''

get_all_notify_whispers = '''
    select      id, channel
        from    twitch_notify
        where   method = 'whisper'
'''
