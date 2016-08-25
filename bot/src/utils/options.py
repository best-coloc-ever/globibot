import argparse

def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('-p', '--plugin-path', help='Plugin directory')

    return parser.parse_args()
