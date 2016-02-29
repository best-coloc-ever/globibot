import json
import re

# Regular expression for comments
comment_re = re.compile(
    '(^)?[^\S\n]*/(?:\*(.*?)\*/[^\S\n]*|/[^\n]*)($)?',
    re.DOTALL | re.MULTILINE
)

def load(file):
    content = ''.join(file.readlines())

    match = comment_re.search(content)
    while match:
        content = content[:match.start()] + content[match.end():]
        match = comment_re.search(content)

    return json.loads(content)
