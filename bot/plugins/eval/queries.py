fetch_behaviors = 'select unnest(enum_range(null::eval_behavior))'

get_behavior = '''
    select      behavior
        from    eval_setting
        where   author_id = (%(author_id)s)
'''

set_behavior = '''
    insert into eval_setting (author_id, behavior)
    values                   (%(author_id)s, %(behavior)s)
    on conflict              (author_id)
    do update set   behavior = (%(behavior)s)
              where eval_setting.author_id = (%(author_id)s)
'''

set_default_behavior = '''
    insert into eval_setting (author_id)
    values                   (%(author_id)s)

'''

get_environment = '''
    select      id, author_id, name, language, image, dockerfile
        from    eval_environment
        where   (author_id = (%(author_id)s) or author_id is null)
            and language = (%(language)s)
'''

get_environments = '''
    select      id, author_id, name, language, image, dockerfile
        from    eval_environment
        where   (author_id = (%(author_id)s) or author_id is null)
'''

save_environment = '''
    insert into eval_environment (author_id, name, language, image, dockerfile)
    values                       (%(author_id)s, %(name)s, %(language)s, %(image)s, %(dockerfile)s)
    on conflict                  (author_id, name)
    do update set   dockerfile = %(dockerfile)s
              where     eval_environment.author_id  = %(author_id)s
                    and eval_environment.name = %(name)s
'''

set_language = '''
    update eval_environment
    set    language = %(language)s
    where  id = %(id)s
'''

get_snippet = '''
    select id, author_id, name, language, code
    from   eval_snippet
    where  author_id = %(author_id)s
    and    name = %(name)s
'''

get_snippets = '''
    select id, author_id, name, language, code
    from   eval_snippet
    where  author_id = %(author_id)s
'''

save_snippet = '''
    insert into eval_snippet (author_id, name, language, code)
    values                   (%(author_id)s, %(name)s, %(language)s, %(code)s)
'''
