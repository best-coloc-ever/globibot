get_credentials = '''
    select      password, password_salt
        from    person
        where   id = %(id)s
'''

get_person = '''
    select      *
        from    person
        where   id = %(id)s
'''

create_user = '''
    insert into person (id, password, password_salt)
                values (%(id)s, %(password)s, %(password_salt)s)
'''
