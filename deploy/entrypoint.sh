#!/bin/bash

/wait-for-it.sh mysql:3306 -- python3 /server/model/schema.py &

exec "$@"
