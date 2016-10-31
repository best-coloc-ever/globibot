add_game_times = lambda count: '''
    insert into     game_played_time (author_id, name, duration)
    values          {}
    on conflict     (author_id, name)
    do update set   duration = game_played_time.duration + EXCLUDED.duration
              where game_played_time.author_id = EXCLUDED.author_id
                and game_played_time.name = EXCLUDED.name
'''.format(','.join(['%s'] * count))

author_games = '''
    select          id, author_id, name, duration, created_at
        from        game_played_time
        where       author_id = %(author_id)s
        order by    duration desc
'''

top_games = '''
    select          name, sum(duration), count(author_id)
        from        game_played_time
        where       author_id in %(authors_id)s
        group by    name
        order by    sum(duration) desc
        limit       %(limit)s
'''
