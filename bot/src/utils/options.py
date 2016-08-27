import argparse

def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('-p', '--plugin-path', help='Plugin directory')
    parser.add_argument('-c', '--config-path', help='Configration file')

    return parser.parse_args()
