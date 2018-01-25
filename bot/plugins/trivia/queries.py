create_trivia_result = '''
    insert into trivia_result (
        user_id, topic, answer, stamp, server_id
    )
    values (
        %(user_id)s, %(topic)s, %(answer)s, %(stamp)s, %(server_id)s
    )
'''

get_count = '''
    select      count(*) from trivia_result
        where   user_id = %(user_id)s
            and server_id = %(server_id)s
'''

get_ranks = '''
    select          count(*) as c, user_id from trivia_result
        where       server_id = %(server_id)s
        group by    user_id
        order by    c desc
'''

get_ranks_topic = '''
    select          count(*) as c, user_id from trivia_result
        where       server_id = %(server_id)s
            and     topic = %(topic)s
        group by    user_id
        order by    c desc
'''
