add_game_time = '''
    insert into game_played_time (author_id, name, duration)
    values                       (%(author_id)s, %(name)s, %(duration)s)
    on conflict                  (author_id, name)
    do update set    duration = game_played_time.duration + %(duration)s
              where  game_played_time.author_id = %(author_id)s
                and  game_played_time.name = %(name)s
'''

author_games = '''
    select id, author_id, name, duration, created_at from game_played_time
    where  author_id = %(author_id)s
'''
