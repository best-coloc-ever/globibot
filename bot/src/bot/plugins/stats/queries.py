add_game_times = lambda count: '''
    insert into game_played_time (author_id, name, duration)
    values                       {}
    on conflict                  (author_id, name)
    do update set    duration = game_played_time.duration + EXCLUDED.duration
              where  game_played_time.author_id = EXCLUDED.author_id
                and  game_played_time.name = EXCLUDED.name
'''.format(','.join(['%s'] * count))

author_games = '''
    select id, author_id, name, duration, created_at from game_played_time
    where  author_id = %(author_id)s
'''

top_games = '''
    select  g.name,
        sum(g.duration),
        count(g.author_id),
        (select     author_id
         from       game_played_time
         where      name = g.name
            and     author_id in %(authors_id)s
         order by   duration desc
         limit      1)

    from        game_played_time as g
    where       author_id in %(authors_id)s
    group by    g.name
    order by    sum(g.duration) desc
    limit       %(limit)s
'''
