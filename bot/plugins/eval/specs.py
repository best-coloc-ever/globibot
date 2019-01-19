from collections import namedtuple

import os

# http://highlightjs.readthedocs.io/en/latest/css-classes-reference.html#language-names-and-aliases
LANGUAGE_ALIASES = {
    'python': ('python', 'py', 'gyp'),
    'javascript': ('javascript', 'js', 'jsx'),
    'haskell': ('haskell', 'hs'),
    'golang': ('golang', 'go'),
    'rust': ('rust', 'rs'),
    'cpp': ('cpp', 'cc', 'hpp', 'hh'),
    'c': ('c', 'h'),
    'shell': ('shell', 'console', 'bash', 'sh', 'zsh'),
}

EvalSpec = namedtuple('EvalSpec', ['image', 'prepare', 'command'])

def file_eval_spec(image, extension, args):
    return EvalSpec(
        image=image,
        prepare=save_code_as_file(extension),
        command=lambda input_file: tuple(
            arg.format(file=input_file)
            for arg in args
        )
    )

def save_code_as_file(extension):

    async def run(directory, code):
        file_name = f'code.{extension}'
        file_path = os.path.join(directory, file_name)

        os.makedirs(directory, exist_ok=True)

        with open(file_path, 'w') as f:
            f.write(code)

        return file_name

    return run

EVALSPEC_PER_LANGUAGES = dict(
    python     = file_eval_spec('python:3.7',   'py',  ('python',     '{file}')),
    javascript = file_eval_spec('node:9.4',     'js',  ('node',       '{file}')),
    haskell    = file_eval_spec('haskell:8.2',  'hs',  ('runhaskell', '{file}')),
    golang     = file_eval_spec('golang:1.11',  'go',  ('bash', '-c', 'cp {file} /go && cd /go && go get -d ./... && go run {file}')),
    rust       = file_eval_spec('rust:1.30',    'rs',  ('bash', '-c', 'rustc {file} -o app && ./app')),
    cpp        = file_eval_spec('gcc:8.2',      'cpp', ('bash', '-c', 'g++ -std=c++17 -O3 {file} -o app && ./app')),
    c          = file_eval_spec('gcc:8.2',      'c',   ('bash', '-c', 'gcc -O3 {file} -o app && ./app')),
    shell      = file_eval_spec('busybox:1.28', 'sh',  ('sh',         '{file}')),
)

EVALSPEC_PER_ALIASES = {
    alias: image
    for language, image in EVALSPEC_PER_LANGUAGES.items()
    for alias in LANGUAGE_ALIASES[language]
}
