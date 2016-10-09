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

add_user = '''
    insert into twitter_oauth (id, access_token, token_secret)
    values                    (%(id)s, %(token)s, %(secret)s)
'''

get_user = '''
    select      access_token, token_secret
        from    twitter_oauth
        where   id = %(id)s
'''

delete_user = '''
    delete from twitter_oauth
        where   id = %(id)s
'''
