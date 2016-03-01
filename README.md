# globibot
A bot for Discord

## Deploying
Can be deployed easily on any platform with docker:

```sh
docker build -t globibot .
docker run \
    --rm -it \
    -v $PWD:/app:ro \
    -p 8080:8080 \
    globibot
```

## Configuration
The bot configuration is read from a `config.yaml` file placed in the [bot](./bot)directory

See [`config.example.yaml`](./bot/config.example.yaml)
