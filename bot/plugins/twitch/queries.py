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
