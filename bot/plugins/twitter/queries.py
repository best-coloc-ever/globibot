get_monitored = '''
    select id, user_id, server_id
    from   twitter_monitored_channel
'''

add_monitored = '''
    insert into twitter_monitored_channel (user_id, server_id)
    values                                (%(user_id)s, %(server_id)s)
'''

remove_monitored = '''
    delete from twitter_monitored_channel
        where   user_id = %(user_id)s
            and server_id = %(server_id)s
'''
