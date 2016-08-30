CONTENT_LEN_LIMIT = 2000
CONTENT_TRUNCATED_MESSAGE = '`⚠ output too long`'
TRUNCATED_CONTENT_LEN = CONTENT_LEN_LIMIT - len(CONTENT_TRUNCATED_MESSAGE)

def truncated_content(content):
    if len(content) > CONTENT_LEN_LIMIT:
        return '{:.{}}\n{}'.format(
            content,
            TRUNCATED_CONTENT_LEN - 1, # counting the newline
            CONTENT_TRUNCATED_MESSAGE
        )
    else:
        return content

def code_block(str_or_list, max_lines=None, language=''):
    lines = str_or_list.split('\n') if type(str_or_list) is str else str_or_list

    if max_lines is not None:
        lines = lines[:max_lines]

    text = '\n'.join([line.rstrip() for line in lines])

    return '```{}\n{:.{}}\n```'.format(
        language,
        text.replace('```', "'''"),
        CONTENT_LEN_LIMIT - len(language) - 8 # 2 * newlines + 6 * `
    )

def pad_rows(rows, separator=' '):
    paddings = []
    colmun_count = len(rows[0])

    for i in range(colmun_count):
        paddings.append(max(map(lambda row: len(str(row[i])), rows)))

    return '\n'.join([
        separator.join([
            '{:{}}'.format(str(v), paddings[i])
            for i, v in enumerate(row)
        ])
        for row in rows
    ])

def format_sql_rows(rows):
    return pad_rows(rows, separator=' | ')

def mention(user_id):
    return '<@{}>'.format(user_id)

def channel(channel_id):
    return '<#{}>'.format(channel_id)
