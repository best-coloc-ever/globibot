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
The bot configuration is read from a `config.json` file placed at the root of the project

See [`config.example.json`](/config.example.json) for the option list
