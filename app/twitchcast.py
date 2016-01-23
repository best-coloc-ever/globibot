import requests
import json

SERVER = 'datcoloc.com'

def api_call(fn):

    def wrapped(*args, **kwargs):
        response = fn(*args, **kwargs)

        return ("Server: `{}` responded with a `{}`.\n"
                "Response: ```json\n{}\n```").format(
                    SERVER,
                    response.status_code,
                    json.dumps(response.json(), indent=4)
                )

    return wrapped

@api_call
def streams():
    return requests.get(
        'http://{}{}'.format(SERVER, '/streamer/streams')
    )

@api_call
def stream(stream_id):
    return requests.get(
        'http://{}{}'.format(SERVER, '/streamer/streams/{}'.format(stream_id))
    )

@api_call
def monitor(channel, quality):
    return requests.post(
        'http://{}{}'.format(SERVER, '/streamer/streams'),
        json={
            'channel': channel,
            'quality': quality
        }
    )

@api_call
def unmonitor(stream_id):
    return requests.delete(
        'http://{}{}'.format(SERVER, '/streamer/streams/{}'.format(stream_id))
    )

@api_call
def watch(stream_id):
    return requests.post(
        'http://{}{}'.format(SERVER, '/streamer/streams/{}/watch'.format(stream_id))
    )

@api_call
def unwatch(stream_id):
    return requests.post(
        'http://{}{}'.format(SERVER, '/streamer/streams/{}/unwatch'.format(stream_id))
    )
