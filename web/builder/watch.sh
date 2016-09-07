#! /usr/bin/env bash

browser-sync start \
    --proxy https://web \
    --files /app/dist \
    --files /app/index.html \
    --files /app/styles.css \
    --no-open \
    --no-notify \
    &

webpack -p --watch
